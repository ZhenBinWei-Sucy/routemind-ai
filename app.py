import csv
import hashlib
import io
import json
import os
import re                       # ← 必须保留
import secrets
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import (Flask, render_template, request, jsonify, redirect,
                   url_for, Response)
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash

from data_generator import (generate_shipments_batches, generate_incremental_batch,
                             COUNTRIES, CONTINENT_VIEWS)
from analytics import (
    calculate_metrics, apply_filters, group_by, get_delay_trend,
    get_delay_days, get_status_distribution, get_country_stats,
    get_continent_stats, get_city_stats, get_delay_reasons,
    get_delay_range_stats, get_lane_stats, get_reason_carrier_matrix,
    get_cost_breakdown, get_at_risk_shipments, get_data_quality,
    is_delayed,
)
from request_parser import parse_request, parse_followup, SUPPORTED_HINT
from chat_modifier import apply_chat_modification

app = Flask(__name__)

# ── SECRET_KEY ────────────────────────────────────────────────
_secret = os.environ.get("SECRET_KEY")
if not _secret:
    if os.environ.get("FLASK_ENV") == "production" or os.environ.get("RENDER"):
        raise RuntimeError("SECRET_KEY env var is required in production")
    _secret = "routemind-demo-secret-change-me"

app.config["SECRET_KEY"] = _secret
app.config["DEMO_MODE"] = os.environ.get("DEMO_MODE", "0") == "1"   # 默认关闭
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024                  # 100MB
app.config.update(
    SESSION_COOKIE_SECURE=(os.environ.get("FLASK_ENV") == "production"
                           or bool(os.environ.get("RENDER"))),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
DB_PATH = os.environ.get("DB_PATH", "routemind.db")
TICK_INTERVAL = int(os.environ.get("TICK_INTERVAL", "600"))
TICK_SIZE = int(os.environ.get("TICK_SIZE", "500"))
MAX_CSV_ROWS = 500_000
DATA_SIZE = int(os.environ.get("DATA_SIZE", "50000"))
ENABLE_TICK = os.environ.get("ENABLE_TICK", "1") == "1"

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{4,32}$")

login_manager = LoginManager(app)
login_manager.login_view = "login_page"

_shipments_cache = []
_shipments_lock = threading.Lock()
_last_tick_at = [None]

_filter_cache = {"data": None, "dirty": True}
_filter_cache_lock = threading.Lock()

_report_cache = {}
_report_cache_lock = threading.Lock()
REPORT_CACHE_TTL = 30
REPORT_CACHE_MAX = 64

_init_done = False
_init_lock = threading.Lock()


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── 安全转换 & CSV 转义 ──────────────────────────────────────
def _safe_int(v, default=None):
    try:
        return int(v) if v not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _safe_float(v, default=None):
    try:
        return float(v) if v not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _csv_safe(v):
    s = "" if v is None else str(v)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


# ── 登录限流 ─────────────────────────────────────────────────
_login_attempts = {}
_login_lock = threading.Lock()


def _rate_limit(key, limit=10, window=60):
    now = time.time()
    with _login_lock:
        arr = [t for t in _login_attempts.get(key, []) if now - t < window]
        if len(arr) >= limit:
            return False
        arr.append(now)
        _login_attempts[key] = arr
    return True


# ── 密码策略 ─────────────────────────────────────────────────
def _pw_ok(p):
    return len(p) >= 8 and bool(re.search(r"[A-Z]", p)) and bool(re.search(r"\d", p))

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


SHIPMENT_COLS = [
    "shipment_id", "ship_date", "expected_delivery_date", "actual_delivery_date",
    "estimated_arrival", "carrier", "origin", "origin_country",
    "destination", "destination_country", "destination_country_code",
    "destination_continent", "destination_lon", "destination_lat",
    "status", "priority", "sla_days", "order_quantity", "delivered_quantity",
    "line_haul_cost", "fuel_surcharge", "accessorial_charges", "detention_cost",
    "shipping_cost", "delay_reason",
]


def _row_to_dict(r):
    return {k: r[k] for k in SHIPMENT_COLS}


def _row_tuple_to_dict(t):
    return dict(zip(SHIPMENT_COLS, t))


def load_all_to_cache():
    global _shipments_cache
    conn = get_conn()
    rows = conn.execute("SELECT * FROM shipments").fetchall()
    conn.close()
    with _shipments_lock:
        _shipments_cache = [_row_to_dict(r) for r in rows]
    invalidate_filter_cache()
    invalidate_report_cache()


def append_shipments(rows):
    if not rows:
        return
    conn = get_conn()
    try:
        placeholders = ",".join(["?"] * len(SHIPMENT_COLS))
        conn.executemany(f"INSERT OR IGNORE INTO shipments VALUES ({placeholders})", rows)
        conn.commit()
    finally:
        conn.close()
    # data_generator 现在用 uuid 前缀 → ID 不会冲突，可安全全部 append
    with _shipments_lock:
        _shipments_cache.extend(_row_tuple_to_dict(r) for r in rows)
    invalidate_filter_cache()
    invalidate_report_cache()


def get_cached():
    with _shipments_lock:
        return _shipments_cache


def invalidate_filter_cache():
    with _filter_cache_lock:
        _filter_cache["dirty"] = True


def invalidate_report_cache():
    with _report_cache_lock:
        _report_cache["key"] = None
        _report_cache["data"] = None


def get_filter_options_data():
    with _filter_cache_lock:
        if not _filter_cache["dirty"] and _filter_cache["data"] is not None:
            return _filter_cache["data"]
    ships = get_cached()
    carriers = set()
    continents = set()
    countries = set()
    country_continents = {}
    for s in ships:
        if s.get("carrier"):
            carriers.add(s["carrier"])
        if s.get("destination_country"):
            countries.add(s["destination_country"])
            if s.get("destination_continent"):
                country_continents.setdefault(
                    s["destination_country"], s["destination_continent"])
        if s.get("destination_continent"):
            continents.add(s["destination_continent"])
    all_cities = get_city_stats(ships)
    data = {
        "carriers": sorted(carriers),
        "countries": sorted(countries),
        "continents": sorted(continents),
        "country_continents": country_continents,
        "priorities": ["Standard", "Express", "Critical"],
        "total": len(ships),
        "all_cities": all_cities,
        "last_updated": _last_tick_at[0],
        "continent_views": CONTINENT_VIEWS,
        "country_views": {c["name"]: {"center": c["center"], "zoom": c["zoom"]}
                          for c in COUNTRIES},
    }
    with _filter_cache_lock:
        _filter_cache["data"] = data
        _filter_cache["dirty"] = False
    return data


def _get_all_cities_with_flag(filtered_ships):
    """全量城市 + in_filter 标记"""
    opts = get_filter_options_data()
    all_cities = opts.get("all_cities", [])
    filtered_keys = set(
        (s.get("destination"), s.get("destination_country"))
        for s in filtered_ships
    )
    result = []
    for city in all_cities:
        key = (city["name"], city.get("country"))
        c = dict(city)
        c["in_filter"] = key in filtered_keys
        result.append(c)
    return result


def _tick_worker():
    while True:
        time.sleep(TICK_INTERVAL)
        try:
            batch = generate_incremental_batch(TICK_SIZE)
            append_shipments(batch)
            _last_tick_at[0] = utc_now().isoformat()
            print(f"[tick] +{len(batch)} rows, total≈{len(_shipments_cache)}")
        except Exception as e:
            print("[tick] failed:", e)


def start_tick():
    threading.Thread(target=_tick_worker, daemon=True).start()


def init_db():
    conn = get_conn()
    c = conn.cursor()
    existing = c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='shipments'"
    ).fetchone()
    if existing:
        cols = [row[1] for row in c.execute("PRAGMA table_info(shipments)").fetchall()]
        if "order_quantity" not in cols or "destination_lon" not in cols:
            print("Rebuilding shipments table (schema upgrade)...")
            c.execute("DROP TABLE IF EXISTS shipments")
            conn.commit()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            reset_token TEXT,
            reset_token_expiry TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            prompt TEXT,
            config TEXT,
            filters TEXT,
            summary TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS project_versions (
            version_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            config TEXT, filters TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS shares (
            token TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, action TEXT NOT NULL, detail TEXT, created_at TEXT NOT NULL
        )
    """)
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS shipments (
            shipment_id TEXT PRIMARY KEY,
            ship_date TEXT,
            expected_delivery_date TEXT,
            actual_delivery_date TEXT,
            estimated_arrival TEXT,
            carrier TEXT,
            origin TEXT,
            origin_country TEXT,
            destination TEXT,
            destination_country TEXT,
            destination_country_code TEXT,
            destination_continent TEXT,
            destination_lon REAL,
            destination_lat REAL,
            status TEXT,
            priority TEXT,
            sla_days INTEGER,
            order_quantity INTEGER,
            delivered_quantity INTEGER,
            line_haul_cost REAL,
            fuel_surcharge REAL,
            accessorial_charges REAL,
            detention_cost REAL,
            shipping_cost REAL,
            delay_reason TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_shipments_ship_date ON shipments(ship_date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_shipments_carrier ON shipments(carrier)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_shipments_country ON shipments(destination_country)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_shipments_continent ON shipments(destination_continent)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id, updated_at DESC)")
    conn.commit()

    count = c.execute("SELECT COUNT(*) FROM shipments").fetchone()[0]
    if count == 0:
        print(f"Seeding {DATA_SIZE:,} synthetic shipments...")
        for batch in generate_shipments_batches(DATA_SIZE):
            placeholders = ",".join(["?"] * len(SHIPMENT_COLS))
            c.executemany(f"INSERT INTO shipments VALUES ({placeholders})", batch)
            conn.commit()
        print("Seed complete.")

    admin = c.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not admin:
        c.execute(
            "INSERT INTO users (username, email, password_hash, is_admin, is_active, created_at) "
            "VALUES (?,?,?,?,?,?)",
            ("admin", "admin@routemind.local",
             generate_password_hash("Admin123!"), 1, 1, utc_now().isoformat()))
        conn.commit()
    conn.close()
    load_all_to_cache()


class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.email = row["email"]
        self.password_hash = row["password_hash"]
        self.is_admin = bool(row["is_admin"])
        self._is_active = bool(row["is_active"])

    def get_id(self): return str(self.id)

    @property
    def is_active(self): return self._is_active


@login_manager.user_loader
def load_user(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (int(user_id),)).fetchone()
    conn.close()
    if row and row["is_active"]:
        return User(row)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({"error": "authentication required"}), 401
    return redirect(url_for("login_page"))


def admin_required(f):
    @wraps(f)
    @login_required
    def d(*a, **k):
        if not current_user.is_admin:
            return jsonify({"error": "admin required"}), 403
        return f(*a, **k)
    return d


def log_action(uid, action, detail=""):
    conn = get_conn()
    conn.execute("INSERT INTO audit_log (user_id, action, detail, created_at) VALUES (?,?,?,?)",
                 (uid, action, detail, utc_now().isoformat()))
    conn.commit()
    conn.close()


def _app_state(user, token=""):
    payload = {"user": None, "sharedToken": token or ""}
    if user is not None:
        payload["user"] = {
            "id": user.id, "username": user.username,
            "email": user.email, "is_admin": bool(user.is_admin),
        }
    # 把 </ 转义，防止提前闭合 <script> 标签
    return json.dumps(payload).replace("</", "<\\/")


@app.route("/")
@login_required
def index():
    return render_template("index.html", user=current_user,
                           app_state_json=_app_state(current_user, ""))


@app.route("/login")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("auth.html", mode="login", reset_token=None)


@app.route("/register")
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("auth.html", mode="register", reset_token=None)


@app.route("/reset/<token>")
def reset_page(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("auth.html", mode="reset", reset_token=token)


@app.route("/share/<token>")
def shared_view(token):
    conn = get_conn()
    r = conn.execute("SELECT project_id FROM shares WHERE token=?", (token,)).fetchone()
    conn.close()
    if not r:
        return "Share link not found", 404
    return render_template("index.html", user=None,
                           app_state_json=_app_state(None, token))


@app.route("/api/auth/register", methods=["POST"])
def register():
    d = request.get_json() or {}
    u = (d.get("username") or "").strip()
    e = (d.get("email") or "").strip().lower()
    p = d.get("password") or ""
    c = d.get("confirm") or ""
    if not u or not e or not p:
        return jsonify({"error": "All fields are required."}), 400
    if not USERNAME_RE.match(u):
        return jsonify({"error": "Username must be 4-32 chars: letters, digits, _ . -"}), 400
    if not _pw_ok(p):
        return jsonify({"error": "Password must be ≥8 chars with an uppercase letter and a digit."}), 400
    if p != c:
        return jsonify({"error": "Passwords do not match."}), 400
    if "@" not in e:
        return jsonify({"error": "Invalid email."}), 400
    conn = get_conn()
    if conn.execute("SELECT id FROM users WHERE username=?", (u,)).fetchone():
        conn.close()
        return jsonify({"error": "Username already taken."}), 409
    if conn.execute("SELECT id FROM users WHERE email=?", (e,)).fetchone():
        conn.close()
        return jsonify({"error": "Email already registered."}), 409
    conn.execute(
        "INSERT INTO users (username, email, password_hash, is_admin, is_active, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (u, e, generate_password_hash(p), 0, 1, utc_now().isoformat()))
    conn.commit()
    uid = conn.execute("SELECT id FROM users WHERE username=?", (u,)).fetchone()["id"]
    conn.close()
    log_action(uid, "register", f"user={u}")
    return jsonify({"ok": True, "message": "Account created."})


@app.route("/api/auth/login", methods=["POST"])
def login():
    ip = request.remote_addr or "unknown"
    if not _rate_limit(f"login:{ip}", limit=10, window=60):
        return jsonify({"error": "Too many attempts. Try again later."}), 429
    d = request.get_json() or {}
    ident = (d.get("identifier") or d.get("email") or "").strip()
    p = d.get("password") or ""
    if not ident:
        return jsonify({"error": "Email or username required."}), 400
    conn = get_conn()
    row = None
    if "@" in ident:
        row = conn.execute("SELECT * FROM users WHERE email=?", (ident.lower(),)).fetchone()
    else:
        row = conn.execute("SELECT * FROM users WHERE username=?", (ident,)).fetchone()
        if not row:
            row = conn.execute("SELECT * FROM users WHERE email=?", (ident.lower(),)).fetchone()
    conn.close()
    if not row or not check_password_hash(row["password_hash"], p):
        return jsonify({"error": "Invalid credentials."}), 401
    if not row["is_active"]:
        return jsonify({"error": "Account disabled."}), 403
    login_user(User(row), remember=bool(d.get("remember")))
    log_action(row["id"], "login", f"user={row['username']}")
    return jsonify({"ok": True, "is_admin": bool(row["is_admin"])})


@app.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    uid = current_user.id
    logout_user()
    log_action(uid, "logout")
    return jsonify({"ok": True})


@app.route("/api/auth/forgot", methods=["POST"])
def forgot_password():
    ip = request.remote_addr or "unknown"
    if not _rate_limit(f"forgot:{ip}", limit=5, window=300):
        return jsonify({"error": "Too many attempts. Try again later."}), 429
    d = request.get_json() or {}
    e = (d.get("email") or "").strip().lower()
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (e,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"ok": True, "message": "If this email exists, reset link generated."})
    token = secrets.token_urlsafe(32)
    expiry = (utc_now() + timedelta(hours=1)).isoformat()
    conn.execute("UPDATE users SET reset_token=?, reset_token_expiry=? WHERE id=?",
                 (token, expiry, row["id"]))
    conn.commit()
    conn.close()
    url = f"{request.host_url.rstrip('/')}/reset/{token}"
    payload = {"ok": True, "message": "Reset link generated."}
    if app.config["DEMO_MODE"]:
        # 只在服务端日志打印，不返回给 client
        print(f"[DEMO] reset link for {e}: {url}")
    return jsonify(payload)


@app.route("/api/auth/reset", methods=["POST"])
def reset_password():
    d = request.get_json() or {}
    t = d.get("token") or ""
    p = d.get("password") or ""
    if not _pw_ok(p):
        return jsonify({"error": "Password must be ≥8 chars with an uppercase letter and a digit."}), 400
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE reset_token=?", (t,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Invalid or expired token."}), 400
    exp = datetime.fromisoformat(row["reset_token_expiry"]) if row["reset_token_expiry"] else None
    if not exp or utc_now() > exp:
        conn.close()
        return jsonify({"error": "Token expired."}), 400
    conn.execute("UPDATE users SET password_hash=?, reset_token=NULL, reset_token_expiry=NULL WHERE id=?",
                 (generate_password_hash(p), row["id"]))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "message": "Password updated."})


@app.route("/api/auth/change-password", methods=["POST"])
@login_required
def change_password():
    d = request.get_json() or {}
    old, new, cf = d.get("old_password") or "", d.get("new_password") or "", d.get("confirm") or ""
    if not old or not new:
        return jsonify({"error": "All fields required."}), 400
    if new != cf:
        return jsonify({"error": "Passwords do not match."}), 400
    if len(new) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (current_user.id,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], old):
        conn.close()
        return jsonify({"error": "Current password incorrect."}), 400
    conn.execute("UPDATE users SET password_hash=? WHERE id=?",
                 (generate_password_hash(new), current_user.id))
    conn.commit()
    conn.close()
    log_action(current_user.id, "password_change")
    return jsonify({"ok": True})


@app.route("/api/projects", methods=["GET"])
@login_required
def list_projects():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, title, prompt, config, filters, summary, created_at, updated_at "
        "FROM projects WHERE user_id=? ORDER BY updated_at DESC",
        (current_user.id,)).fetchall()
    conn.close()
    return jsonify([{
        "id": r["id"], "title": r["title"], "prompt": r["prompt"],
        "config": json.loads(r["config"] or "{}"),
        "filters": json.loads(r["filters"] or "{}"),
        "summary": r["summary"] or "",
        "created_at": r["created_at"], "updated_at": r["updated_at"],
    } for r in rows])


@app.route("/api/projects", methods=["POST"])
@login_required
def create_project():
    d = request.get_json() or {}
    pid = str(uuid.uuid4())[:8]
    now = utc_now().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO projects (id, user_id, title, prompt, config, filters, summary, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (pid, current_user.id, d.get("title", "Untitled"), d.get("prompt", ""),
         json.dumps(d.get("config", {})), json.dumps(d.get("filters", {})),
         d.get("summary", ""), now, now))
    conn.commit()
    conn.close()
    return jsonify({"id": pid})


def _owned_project(pid):
    conn = get_conn()
    r = conn.execute("SELECT * FROM projects WHERE id=? AND user_id=?",
                     (pid, current_user.id)).fetchone()
    conn.close()
    return r


@app.route("/api/projects/<pid>", methods=["GET"])
@login_required
def get_project(pid):
    r = _owned_project(pid)
    if not r:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": r["id"], "title": r["title"], "prompt": r["prompt"],
        "config": json.loads(r["config"] or "{}"),
        "filters": json.loads(r["filters"] or "{}"),
        "summary": r["summary"] or "",
    })


@app.route("/api/projects/<pid>", methods=["PUT"])
@login_required
def update_project(pid):
    r = _owned_project(pid)
    if not r:
        return jsonify({"error": "not found"}), 404
    d = request.get_json() or {}
    now = utc_now().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO project_versions (version_id, project_id, config, filters, created_at) "
        "VALUES (?,?,?,?,?)",
        (str(uuid.uuid4())[:10], pid, r["config"], r["filters"], now))
    conn.execute(
        "UPDATE projects SET title=?, config=?, filters=?, summary=?, updated_at=? WHERE id=?",
        (d.get("title", r["title"]), json.dumps(d.get("config", {})),
         json.dumps(d.get("filters", {})), d.get("summary", r["summary"] or ""), now, pid))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/projects/<pid>", methods=["DELETE"])
@login_required
def delete_project(pid):
    r = _owned_project(pid)
    if not r:
        return jsonify({"error": "not found"}), 404
    conn = get_conn()
    conn.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    log_action(current_user.id, "project_delete", f"project={pid}")
    return jsonify({"ok": True})


@app.route("/api/projects/<pid>/share", methods=["POST"])
@login_required
def create_share(pid):
    r = _owned_project(pid)
    if not r:
        return jsonify({"error": "not found"}), 404
    token = secrets.token_urlsafe(16)
    conn = get_conn()
    conn.execute("INSERT INTO shares VALUES (?,?,?)",
                 (token, pid, utc_now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"token": token, "url": f"/share/{token}"})


@app.route("/api/share/<token>", methods=["GET"])
def get_shared(token):
    conn = get_conn()
    r = conn.execute(
        "SELECT p.* FROM shares s JOIN projects p ON p.id=s.project_id WHERE s.token=?",
        (token,)).fetchone()
    conn.close()
    if not r:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": r["id"], "title": r["title"], "prompt": r["prompt"],
        "config": json.loads(r["config"] or "{}"),
        "filters": json.loads(r["filters"] or "{}"),
        "summary": r["summary"] or "",
        "readonly": True,
    })


@app.route("/api/analyze", methods=["POST"])
@login_required
def analyze():
    text = (request.get_json() or {}).get("prompt", "")
    return jsonify(parse_request(text))


@app.route("/api/followup", methods=["POST"])
@login_required
def followup():
    d = request.get_json() or {}
    updates = parse_followup(d.get("text", ""), d.get("filters", {}))
    if not updates:
        return jsonify({"updated": False, "message": SUPPORTED_HINT})
    return jsonify({"updated": True,
                    "filters": {**d.get("filters", {}), **updates},
                    "changes": updates})


@app.route("/api/filters", methods=["GET"])
@login_required
def filter_options():
    return jsonify(get_filter_options_data())


def _build_summary(m):
    if not m["total_shipments"]:
        return json.dumps({})
    return json.dumps({
        "delay_rate": m["delay_rate"],
        "otif_rate": m["otif_rate"],
        "shipments": m["total_shipments"],
    })


def _insights_struct(m, carriers, countries, reasons, range_stats, lanes):
    findings = []
    if m["delivered_count"]:
        findings.append({"type": "quality", "delay_rate": m["delay_rate"],
                         "on_time_rate": m["on_time_rate"], "otif_rate": m["otif_rate"]})
    if m["p90_delay_days"] is not None:
        findings.append({"type": "p90", "p90": m["p90_delay_days"],
                         "avg": m["avg_delay_days"]})
    if m["eta_accuracy_rate"] is not None:
        findings.append({"type": "eta", "rate": m["eta_accuracy_rate"]})
    worst_c = carriers[0] if carriers else None
    if worst_c and worst_c.get("delay_rate") is not None:
        findings.append({"type": "worst_carrier", "name": worst_c["name"],
                         "delay_rate": worst_c["delay_rate"],
                         "shipments": worst_c["total_shipments"]})
    worst_ct = countries[0] if countries else None
    if worst_ct and worst_ct.get("delay_rate") is not None:
        findings.append({"type": "worst_country", "name": worst_ct["name"],
                         "delay_rate": worst_ct["delay_rate"],
                         "revenue": worst_ct["revenue"]})
    if reasons:
        findings.append({"type": "top_reason", "name": reasons[0]["name"],
                         "count": reasons[0]["count"]})
    if range_stats and range_stats.get("active") and range_stats["total_delayed"]:
        findings.append({"type": "range", "min": range_stats["range_min"],
                         "max": range_stats["range_max"],
                         "pct_delayed": range_stats["pct_of_delayed"],
                         "pct_total": range_stats["pct_of_total"]})
    if lanes:
        worst_lane = max(lanes, key=lambda x: x["delay_rate"] if x["delay_rate"] is not None else -1)
        if worst_lane.get("delay_rate") is not None:
            findings.append({"type": "worst_lane", "lane": worst_lane["lane"],
                             "delay_rate": worst_lane["delay_rate"]})
    if m["at_risk_count"]:
        findings.append({"type": "at_risk", "count": m["at_risk_count"]})
    return findings


def _compute_report(filters):
    ships = get_cached()
    main_f = apply_filters(ships, filters)
    base_filters = {k: v for k, v in filters.items()
                    if k not in ("min_delay_days", "max_delay_days")}
    base_f = apply_filters(ships, base_filters)

    metrics = calculate_metrics(main_f)
    status_dist = get_status_distribution(base_f)
    trend = get_delay_trend(base_f, int(filters.get("date_range_days") or 30))
    carriers = group_by(main_f, "carrier")
    countries = get_country_stats(base_f)  # 供图表/表格
    continents = get_continent_stats(base_f)
    reasons = get_delay_reasons(main_f)
    lanes = get_lane_stats(base_f)
    reason_matrix = get_reason_carrier_matrix(main_f)
    cost_bd = get_cost_breakdown(main_f)
    range_stats = get_delay_range_stats(
        base_f, filters.get("min_delay_days"), filters.get("max_delay_days"))
    data_quality = get_data_quality(main_f)

    # 供地图使用的数据（合并到 report 里，避免二次请求 /api/map）
    map_countries = countries  # 已按 delay_rate 排序
    map_cities = _get_all_cities_with_flag(base_f)

    threshold = filters.get("min_delay_days")
    threshold = int(threshold) if threshold not in (None, "") else 3
    exceptions = []
    for s in main_f:
        dd = get_delay_days(s)
        if dd is not None and dd >= threshold:
            exceptions.append({**s, "delay_days": dd})
    exceptions.sort(key=lambda x: x["delay_days"], reverse=True)

    at_risk = get_at_risk_shipments(base_f, limit=30)
    all_recent = sorted(main_f, key=lambda s: s.get("ship_date") or "", reverse=True)[:120]

    return {
        "metrics": metrics,
        "range_stats": range_stats,
        "status_distribution": status_dist,
        "trend": trend,
        "carriers": carriers[:8],
        "countries": countries,
        "continents": continents,
        "lanes": lanes,
        "reason_matrix": reason_matrix,
        "delay_reasons": reasons[:8],
        "cost_breakdown": cost_bd,
        "data_quality": data_quality,
        "at_risk": at_risk,
        "exceptions": exceptions[:80],
        "all_shipments": all_recent,
        "map_countries": map_countries,
        "map_cities": map_cities,
        "findings": _insights_struct(metrics, carriers, countries, reasons, range_stats, lanes),
        "summary_line": _build_summary(metrics),
        "total_in_cache": len(ships),
        "last_updated": _last_tick_at[0],
    }


def _filters_cache_key(filters):
    s = json.dumps(filters, sort_keys=True, default=str)
    return hashlib.md5(s.encode()).hexdigest()


@app.route("/api/report", methods=["POST"])
@login_required
def report():
    d = request.get_json() or {}
    filters = d.get("filters", {})
    key = _filters_cache_key(filters)
    now = time.time()

    with _report_cache_lock:
        if (_report_cache["key"] == key
                and _report_cache["data"] is not None
                and now - _report_cache["ts"] < REPORT_CACHE_TTL):
            return jsonify(_report_cache["data"])

    data = _compute_report(filters)

    with _report_cache_lock:
        _report_cache["key"] = key
        _report_cache["data"] = data
        _report_cache["ts"] = now

    return jsonify(data)


# ============================================================
# Map
# ============================================================

@app.route("/api/map", methods=["POST"])
@login_required
def map_data():
    """仅当地图 filter（m-continent/m-country）变化时调用。"""
    d = request.get_json() or {}
    filters = d.get("filters", {})
    level = d.get("level", "world")

    clean = {k: v for k, v in filters.items()
             if k not in ("min_delay_days", "max_delay_days")}
    all_ships = get_cached()
    filtered = apply_filters(all_ships, clean)

    countries = get_country_stats(filtered)
    cities = _get_all_cities_with_flag(filtered)

    return jsonify({
        "level": level,
        "countries": countries,
        "cities": cities,
        "total": len(filtered),
    })


@app.route("/api/map/focus", methods=["POST"])
@login_required
def map_focus():
    d = request.get_json() or {}
    focus_type = (d.get("focus_type") or "country").lower()
    focus_name = (d.get("focus_name") or "").strip()
    if not focus_name:
        return jsonify({"error": "focus_name is required"}), 400

    # 优先使用 filters（若前端传了），否则回退到 date_range_days
    filters = d.get("filters") or {}
    if not filters and d.get("date_range_days"):
        filters = {"date_range_days": d["date_range_days"]}

    ships = apply_filters(get_cached(), filters)
    print(f"[focus] type={focus_type} name={focus_name!r} "
          f"filters={filters} total_ships={len(ships)}")

    focus_metrics = None
    cities = []
    country_of_focus = None

    if focus_type == "country":
        country_ships = [s for s in ships
                         if s.get("destination_country") == focus_name]
        if not country_ships:
            fname_lower = focus_name.lower()
            country_ships = [s for s in ships
                             if (s.get("destination_country") or "").lower() == fname_lower]
        if country_ships:
            focus_metrics = calculate_metrics(country_ships)
            cities = get_city_stats(country_ships, country=focus_name)
            country_of_focus = focus_name

    elif focus_type == "city":
        city_ships = [s for s in ships if s.get("destination") == focus_name]
        if not city_ships:
            fname_lower = focus_name.lower()
            city_ships = [s for s in ships
                         if (s.get("destination") or "").lower() == fname_lower]
        if city_ships:
            focus_metrics = calculate_metrics(city_ships)
            country_of_focus = city_ships[0].get("destination_country")
            if country_of_focus:
                country_ships = [s for s in ships
                                if s.get("destination_country") == country_of_focus]
                cities = get_city_stats(country_ships, country=country_of_focus)

    if focus_metrics is None:
        focus_metrics = calculate_metrics([])

    return jsonify({
        "focus_type": focus_type,
        "focus_name": focus_name,
        "country": country_of_focus,
        "focus_metrics": focus_metrics,
        "cities": cities,
    })

@app.route("/api/export", methods=["POST"])
@login_required
def export_csv():
    d = request.get_json() or {}
    ships = apply_filters(get_cached(), d.get("filters", {}))
    t = d.get("filters", {}).get("min_delay_days")
    t = _safe_int(t, 3)
    rows = [s for s in ships if (get_delay_days(s) or 0) >= t]
    headers = ["shipment_id", "carrier", "destination", "destination_country",
               "destination_continent", "status", "priority",
               "expected_delivery_date", "actual_delivery_date",
               "delay_reason", "shipping_cost"]
    lines = [",".join(headers)]
    for s in rows:
        lines.append(",".join(_csv_safe(s.get(h, "")) for h in headers))
    return Response("\n".join(lines), mimetype="text/csv",
                    headers={"Content-Disposition":
                             "attachment; filename=routemind_exceptions.csv"})


# ============================================================
# Dashboard
# ============================================================

@app.route("/api/dashboard", methods=["GET"])
@login_required
def api_dashboard():
    ships = get_cached()
    total = len(ships)
    status_dist = {"Delivered": 0, "In Transit": 0, "Exception": 0}
    carrier_counts = {}
    continent_counts = {}
    missing_expected = 0
    missing_actual = 0
    invalid_status = 0

    for s in ships:
        st = s.get("status")
        if st in status_dist:
            status_dist[st] += 1
        else:
            invalid_status += 1
        c = s.get("carrier")
        if c:
            carrier_counts[c] = carrier_counts.get(c, 0) + 1
        ct = s.get("destination_continent")
        if ct:
            continent_counts[ct] = continent_counts.get(ct, 0) + 1
        if not s.get("expected_delivery_date"):
            missing_expected += 1
        if st == "Delivered" and not s.get("actual_delivery_date"):
            missing_actual += 1

    carriers = [{"name": k, "count": v} for k, v in
                sorted(carrier_counts.items(), key=lambda kv: -kv[1])]
    continents = [{"name": k, "count": v} for k, v in
                  sorted(continent_counts.items(), key=lambda kv: -kv[1])]

    valid = total - missing_expected - missing_actual
    quality = round(valid / total * 100, 1) if total else None

    return jsonify({
        "total": total,
        "last_updated": _last_tick_at[0],
        "status_distribution": status_dist,
        "carriers": carriers,
        "continents": continents,
        "data_quality": {
            "missing_expected": missing_expected,
            "missing_actual": missing_actual,
            "invalid_status": invalid_status,
            "quality_pct": quality,
        },
    })


# ============================================================
# Database (paginated CRUD)
# ============================================================

@app.route("/api/db/shipments", methods=["GET"])
@login_required
def db_list_shipments():
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(200, max(10, int(request.args.get("per_page", 50))))
    offset = (page - 1) * per_page

    carrier = request.args.get("carrier", "").strip()
    country = request.args.get("country", "").strip()
    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    where, params = [], []
    if carrier:
        where.append("carrier = ?")
        params.append(carrier)
    if country:
        where.append("destination_country = ?")
        params.append(country)
    if status:
        where.append("status = ?")
        params.append(status)
    if search and len(search) >= 2:
        where.append("(shipment_id LIKE ? OR destination LIKE ? OR carrier LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like])

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    conn = get_conn()
    total = conn.execute(f"SELECT COUNT(*) FROM shipments {where_sql}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM shipments {where_sql} "
        f"ORDER BY ship_date DESC, shipment_id LIMIT ? OFFSET ?",
        params + [per_page, offset]).fetchall()
    conn.close()

    return jsonify({
        "rows": [_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "is_admin": bool(current_user.is_admin),
    })


@app.route("/api/db/shipments/<sid>", methods=["PUT"])
@admin_required
def db_update_shipment(sid):
    data = request.get_json() or {}
    allowed = ["carrier", "destination", "destination_country",
               "destination_continent", "status", "priority",
               "expected_delivery_date", "actual_delivery_date",
               "delay_reason", "shipping_cost", "order_quantity",
               "delivered_quantity"]
    updates = {k: data[k] for k in allowed if k in data}
    if not updates:
        return jsonify({"error": "No editable fields"}), 400

    if "status" in updates and updates["status"] not in ("Delivered", "In Transit", "Exception"):
        return jsonify({"error": "Invalid status"}), 400

    if "destination_country" in updates:
        known = set(s.get("destination_country") for s in get_cached())
        if updates["destination_country"] not in known:
            return jsonify({"error": f"Unknown country: {updates['destination_country']}"}), 400

    for df in ("expected_delivery_date", "actual_delivery_date"):
        if df in updates and updates[df]:
            try:
                datetime.strptime(updates[df], "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": f"Invalid {df}"}), 400

    for nf in ("shipping_cost", "order_quantity", "delivered_quantity"):
        if nf in updates and updates[nf] is not None:
            try:
                if nf == "shipping_cost":
                    float(updates[nf])
                else:
                    int(updates[nf])
            except (TypeError, ValueError):
                return jsonify({"error": f"Invalid {nf}"}), 400

    conn = get_conn()
    sets = ", ".join(f"{k} = ?" for k in updates.keys())
    conn.execute(f"UPDATE shipments SET {sets} WHERE shipment_id = ?",
                 (*updates.values(), sid))
    conn.commit()
    conn.close()

    with _shipments_lock:
        for i, s in enumerate(_shipments_cache):
            if s["shipment_id"] == sid:
                _shipments_cache[i] = {**s, **updates}
                break

    invalidate_filter_cache()
    invalidate_report_cache()
    log_action(current_user.id, "db_update", f"shipment={sid}")
    return jsonify({"ok": True})

@admin_required
def db_update_shipment(sid):
    data = request.get_json() or {}
    allowed = ["carrier", "destination", "destination_country",
               "destination_continent", "status", "priority",
               "expected_delivery_date", "actual_delivery_date",
               "delay_reason", "shipping_cost", "order_quantity",
               "delivered_quantity"]
    updates = {k: data[k] for k in allowed if k in data}
    if not updates:
        return jsonify({"error": "No editable fields"}), 400

    if "status" in updates and updates["status"] not in ("Delivered", "In Transit", "Exception"):
        return jsonify({"error": "Invalid status"}), 400

    if "destination_country" in updates:
        known = set(s.get("destination_country") for s in get_cached())
        if updates["destination_country"] not in known:
            return jsonify({"error": f"Unknown country: {updates['destination_country']}"}), 400

    for df in ("expected_delivery_date", "actual_delivery_date"):
        if df in updates and updates[df]:
            try:
                datetime.strptime(updates[df], "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": f"Invalid {df}"}), 400

    for nf in ("shipping_cost", "order_quantity", "delivered_quantity"):
        if nf in updates and updates[nf] is not None:
            try:
                if nf == "shipping_cost":
                    float(updates[nf])
                else:
                    int(updates[nf])
            except (TypeError, ValueError):
                return jsonify({"error": f"Invalid {nf}"}), 400

    conn = get_conn()
    sets = ", ".join(f"{k} = ?" for k in updates.keys())
    conn.execute(f"UPDATE shipments SET {sets} WHERE shipment_id = ?",
                 (*updates.values(), sid))
    conn.commit()
    conn.close()

    with _shipments_lock:
        for i, s in enumerate(_shipments_cache):
            if s["shipment_id"] == sid:
                _shipments_cache[i] = {**s, **updates}
                break

    invalidate_filter_cache()
    invalidate_report_cache()
    log_action(current_user.id, "db_update", f"shipment={sid}")
    return jsonify({"ok": True})


@app.route("/api/db/shipments/<sid>", methods=["DELETE"])
@admin_required
def db_delete_shipment(sid):
    conn = get_conn()
    row = conn.execute("SELECT shipment_id FROM shipments WHERE shipment_id = ?",
                       (sid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "not found"}), 404
    conn.execute("DELETE FROM shipments WHERE shipment_id = ?", (sid,))
    conn.commit()
    conn.close()

    with _shipments_lock:
        _shipments_cache[:] = [s for s in _shipments_cache
                                if s["shipment_id"] != sid]

    invalidate_filter_cache()
    invalidate_report_cache()
    log_action(current_user.id, "db_delete", f"shipment={sid}")
    return jsonify({"ok": True})


# ============================================================
# Admin
# ============================================================

@app.route("/api/admin/stats", methods=["GET"])
@admin_required
def admin_stats():
    conn = get_conn()
    stats = {
        "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "projects": conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
        "shipments": conn.execute("SELECT COUNT(*) FROM shipments").fetchone()[0],
    }
    conn.close()
    return jsonify(stats)


@app.route("/api/admin/users", methods=["GET"])
@admin_required
def admin_users():
    page = max(1, int(request.args.get("page", 1)))
    per = 20
    off = (page - 1) * per
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    rows = conn.execute(
        "SELECT id, username, email, is_admin, is_active, created_at "
        "FROM users ORDER BY id LIMIT ? OFFSET ?", (per, off)).fetchall()
    conn.close()
    return jsonify({"total": total, "page": page,
                    "pages": (total + per - 1) // per,
                    "users": [dict(r) for r in rows]})


@app.route("/api/admin/users/<int:uid>/toggle-active", methods=["POST"])
@admin_required
def admin_toggle_active(uid):
    if uid == current_user.id:
        return jsonify({"error": "Cannot disable yourself."}), 400
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "not found"}), 404
    # 若即将禁用的是一个活跃管理员，检查是否是最后一个
    if row["is_active"] and row["is_admin"]:
        active_admins = conn.execute(
            "SELECT COUNT(*) FROM users WHERE is_admin=1 AND is_active=1").fetchone()[0]
        if active_admins <= 1:
            conn.close()
            return jsonify({"error": "Cannot disable the last active admin."}), 400
    ns = 0 if row["is_active"] else 1
    conn.execute("UPDATE users SET is_active=? WHERE id=?", (ns, uid))
    conn.commit()
    conn.close()
    log_action(current_user.id, "user_toggle_active", f"uid={uid} -> {bool(ns)}")
    return jsonify({"ok": True, "is_active": bool(ns)})


@app.route("/api/admin/users/<int:uid>/toggle-admin", methods=["POST"])
@admin_required
def admin_toggle_admin(uid):
    if uid == current_user.id:
        return jsonify({"error": "Cannot change own role."}), 400
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "not found"}), 404
    if row["is_admin"]:
        admin_count = conn.execute(
            "SELECT COUNT(*) FROM users WHERE is_admin=1 AND is_active=1").fetchone()[0]
        if admin_count <= 1:
            conn.close()
            return jsonify({"error": "Cannot revoke the last active admin."}), 400
    ns = 0 if row["is_admin"] else 1
    conn.execute("UPDATE users SET is_admin=? WHERE id=?", (ns, uid))
    conn.commit()
    conn.close()
    log_action(current_user.id, "user_toggle_admin", f"uid={uid} -> {bool(ns)}")
    return jsonify({"ok": True, "is_admin": bool(ns)})


@app.route("/api/admin/users/<int:uid>", methods=["DELETE"])
@admin_required
def admin_delete_user(uid):
    if uid == current_user.id:
        return jsonify({"error": "Cannot delete yourself."}), 400
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


def _make_shipment_row(r, i, has_country, has_code, has_cont):
    sid = (r.get("shipment_id") or "").strip()
    country = r.get("destination_country") if has_country else "Unknown"
    if not country:
        country = "Unknown"
    lookup = next((c for c in COUNTRIES if c["name"] == country), None)

    cost = _safe_float(r.get("shipping_cost"))
    if cost is None and r.get("shipping_cost"):
        return None, f"Row {i}: invalid cost"

    try:
        lon = _safe_float(r.get("destination_lon"))
        lat = _safe_float(r.get("destination_lat"))
    except Exception:
        lon = lat = None
    if lon is None and lookup and lookup["cities"]:
        lon = lookup["cities"][0]["lon"]
    if lat is None and lookup and lookup["cities"]:
        lat = lookup["cities"][0]["lat"]

    oq = _safe_int(r.get("order_quantity"), 1)
    dq = _safe_int(r.get("delivered_quantity"),
                   oq if r.get("status") == "Delivered" else 0)

    continent = r.get("destination_continent") if has_cont else (
        lookup["continent"] if lookup else "Unknown")

    row_tuple = (
        sid, r.get("ship_date"), r.get("expected_delivery_date"),
        r.get("actual_delivery_date") or None,
        r.get("estimated_arrival") or None,
        r.get("carrier"), r.get("origin"),
        r.get("origin_country") or "Unknown",
        r.get("destination"), country,
        r.get("destination_country_code") if has_code else (
            lookup["code"] if lookup else ""),
        continent, lon, lat,
        r.get("status"), r.get("priority") or "Standard",
        _safe_int(r.get("sla_days")),
        oq, dq,
        _safe_float(r.get("line_haul_cost")),
        _safe_float(r.get("fuel_surcharge")),
        _safe_float(r.get("accessorial_charges")),
        _safe_float(r.get("detention_cost")),
        cost, r.get("delay_reason") or None,
    )
    return row_tuple, None


@app.route("/api/admin/upload-csv", methods=["POST"])
@admin_required
def admin_upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file."}), 400
    file = request.files["file"]
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only .csv."}), 400
    if file.content_length and file.content_length > app.config["MAX_CONTENT_LENGTH"]:
        return jsonify({"error": "File too large (max 100MB)."}), 413
    try:
        raw = file.stream.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return jsonify({"error": "UTF-8 required."}), 400

    line_count = raw.count("\n")
    if line_count > MAX_CSV_ROWS:
        return jsonify({
            "error": f"File has {line_count:,} lines, exceeds limit of {MAX_CSV_ROWS:,}."
        }), 413

    reader = csv.DictReader(io.StringIO(raw))
    fields = set(reader.fieldnames or [])
    required_min = {"shipment_id", "ship_date", "carrier", "origin",
                    "destination", "destination_country", "status", "shipping_cost"}
    if not required_min.issubset(fields):
        return jsonify({
            "error": f"Missing columns: {', '.join(sorted(required_min - fields))}"
        }), 400

    has_country = "destination_country" in fields
    has_code = "destination_country_code" in fields
    has_cont = "destination_continent" in fields

    VALID_STATUS = {"Delivered", "In Transit", "Exception"}
    DATE_FIELDS = ("ship_date", "expected_delivery_date",
                   "actual_delivery_date", "estimated_arrival")

    rows, errors, seen = [], [], set()
    for i, r in enumerate(reader, start=2):
        sid = (r.get("shipment_id") or "").strip()
        if not sid or sid in seen:
            errors.append(f"Row {i}: missing/dup ID")
            continue
        st = r.get("status")
        if st not in VALID_STATUS:
            errors.append(f"Row {i}: invalid status {st!r}")
            continue
        bad_date = False
        for df in DATE_FIELDS:
            v = r.get(df)
            if v:
                try:
                    datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    errors.append(f"Row {i}: invalid {df} {v!r}")
                    bad_date = True
                    break
        if bad_date:
            continue
        seen.add(sid)
        try:
            row_tuple, err = _make_shipment_row(r, i, has_country, has_code, has_cont)
        except Exception as e:
            errors.append(f"Row {i}: {e}")
            continue
        if err:
            errors.append(err)
            continue
        rows.append(row_tuple)

    if not rows:
        return jsonify({"error": "No valid rows.", "details": errors[:20]}), 400

    conn = get_conn()
    try:
        conn.execute("BEGIN")
        conn.execute("DELETE FROM shipments")
        placeholders = ",".join(["?"] * len(SHIPMENT_COLS))
        conn.executemany(f"INSERT INTO shipments VALUES ({placeholders})", rows)
        conn.execute("COMMIT")
    except Exception as e:
        conn.execute("ROLLBACK")
        conn.close()
        return jsonify({"error": f"Import failed: {e}"}), 500
    conn.close()

    with _shipments_lock:
        _shipments_cache.clear()
        _shipments_cache.extend(_row_tuple_to_dict(r) for r in rows)
    invalidate_filter_cache()
    invalidate_report_cache()

    log_action(current_user.id, "csv_upload",
               f"imported={len(rows)} skipped={len(errors)}")
    return jsonify({"ok": True, "imported": len(rows),
                    "error_count": len(errors), "errors": errors[:20]})

@app.route("/api/admin/simulate-tick", methods=["POST"])
@admin_required
def admin_simulate_tick():
    batch = generate_incremental_batch(TICK_SIZE)
    append_shipments(batch)
    _last_tick_at[0] = utc_now().isoformat()
    return jsonify({"ok": True, "added": len(batch),
                    "total": len(get_cached())})


@app.route("/api/admin/audit", methods=["GET"])
@admin_required
def admin_audit():
    conn = get_conn()
    rows = conn.execute("""
        SELECT a.*, u.username FROM audit_log a
        LEFT JOIN users u ON u.id = a.user_id
        ORDER BY a.id DESC LIMIT 100
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    start_tick()
    app.run(debug=True, port=5000, threaded=True, use_reloader=False)