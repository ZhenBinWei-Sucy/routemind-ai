import csv
import hashlib
import io
import json
import os
import re
import secrets
import sqlite3
import threading
import time
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import (Flask, render_template, request, jsonify, redirect,
                   url_for, Response, make_response)
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

app = Flask(__name__)

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("routemind")

# ── SECRET_KEY ────────────────────────────────────────────────
_secret = os.environ.get("SECRET_KEY")
if not _secret:
    if os.environ.get("FLASK_ENV") == "production" or os.environ.get("RENDER"):
        raise RuntimeError("SECRET_KEY env var is required in production")
    _secret = "routemind-demo-secret-change-me"

app.config["SECRET_KEY"] = _secret
app.config["DEMO_MODE"] = os.environ.get("DEMO_MODE", "0") == "1"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
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

# ★ LRU report cache
_report_cache = OrderedDict()
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
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        pass
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
    with _shipments_lock:
        _shipments_cache.extend(_row_tuple_to_dict(r) for r in rows)
    invalidate_filter_cache()
    invalidate_report_cache()


def get_cached():
    # ★ 返回副本，防止并发迭代时 list 大小变化
    with _shipments_lock:
        return list(_shipments_cache)


def invalidate_filter_cache():
    with _filter_cache_lock:
        _filter_cache["dirty"] = True


def invalidate_report_cache():
    with _report_cache_lock:
        _report_cache.clear()


# ── Report LRU cache ─────────────────────────────────────────
def _report_cache_get(key):
    with _report_cache_lock:
        entry = _report_cache.get(key)
        if not entry:
            return None
        ts, data = entry
        if time.time() - ts > REPORT_CACHE_TTL:
            _report_cache.pop(key, None)
            return None
        _report_cache.move_to_end(key)
        return data


def _report_cache_put(key, data):
    with _report_cache_lock:
        _report_cache[key] = (time.time(), data)
        _report_cache.move_to_end(key)
        while len(_report_cache) > REPORT_CACHE_MAX:
            _report_cache.popitem(last=False)


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
            logger.info(f"[tick] +{len(batch)} rows, total≈{len(_shipments_cache)}")
        except Exception as e:
            logger.exception("[tick] failed")


def start_tick():
    threading.Thread(target=_tick_worker, daemon=True).start()


def init_db():
    logger.info(f"[init_db] starting, DB_PATH={DB_PATH}")
    conn = get_conn()
    c = conn.cursor()
    existing = c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='shipments'"
    ).fetchone()
    if existing:
        cols = [row[1] for row in c.execute("PRAGMA table_info(shipments)").fetchall()]
        if "order_quantity" not in cols or "destination_lon" not in cols:
            logger.info("Rebuilding shipments table (schema upgrade)...")
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
    c.execute("""
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
    
    # ── App Builder 表（提前建好，供预置 Key 使用） ──
    c.execute("""CREATE TABLE IF NOT EXISTS builder_projects (
        id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS builder_versions (
        id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
        instruction TEXT, code TEXT NOT NULL, summary TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES builder_projects(id) ON DELETE CASCADE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS builder_shares (
        id TEXT PRIMARY KEY, project_id TEXT, title TEXT,
        code TEXT NOT NULL, views INTEGER DEFAULT 0, created_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS builder_settings (
        user_id INTEGER PRIMARY KEY, provider TEXT, base_url TEXT,
        api_key TEXT, model TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS project_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_project_chats ON project_chats(project_id, id)")
    
    conn.commit()

    count = c.execute("SELECT COUNT(*) FROM shipments").fetchone()[0]
    if count == 0:
        logger.info(f"Seeding {DATA_SIZE:,} synthetic shipments...")
        for batch in generate_shipments_batches(DATA_SIZE):
            placeholders = ",".join(["?"] * len(SHIPMENT_COLS))
            c.executemany(f"INSERT INTO shipments VALUES ({placeholders})", batch)
            conn.commit()
        logger.info("Seed complete.")

    admin = c.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not admin:
        c.execute(
            "INSERT INTO users (username, email, password_hash, is_admin, is_active, created_at) "
            "VALUES (?,?,?,?,?,?)",
            ("admin", "admin@routemind.local",
             generate_password_hash("Admin123!"), 1, 1, utc_now().isoformat()))
        conn.commit()

    # ── 预置 admin 的默认 LLM Key（评审期间免配） ──
    default_llm_key = os.environ.get("DEFAULT_LLM_KEY", "").strip()
    if default_llm_key:
        admin_row = c.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if admin_row:
            provider = os.environ.get("DEFAULT_LLM_PROVIDER", "gemini")
            base_url = os.environ.get(
                "DEFAULT_LLM_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai")
            model = os.environ.get("DEFAULT_LLM_MODEL", "gemini-3.5-flash-lite")

            exists = c.execute(
                "SELECT user_id FROM builder_settings WHERE user_id=?",
                (admin_row["id"],)).fetchone()

            if not exists:
                c.execute(
                    "INSERT INTO builder_settings (user_id, provider, base_url, api_key, model) "
                    "VALUES (?,?,?,?,?)",
                    (admin_row["id"], provider, base_url, default_llm_key, model))
                logger.info("[init_db] seeded default LLM key for admin")
            else:
                # ★ 关键修复：不管旧 key 是什么，强制覆盖为环境变量里的值
                c.execute(
                    "UPDATE builder_settings SET provider=?, base_url=?, api_key=?, model=? "
                    "WHERE user_id=?",
                    (provider, base_url, default_llm_key, model, admin_row["id"]))
                logger.info("[init_db] synced admin LLM key from env (forced)")
            conn.commit()

    conn.close()
    load_all_to_cache()


def ensure_initialized():
    global _init_done
    if _init_done:
        return
    with _init_lock:
        if _init_done:
            return
        init_db()
        if ENABLE_TICK:
            start_tick()
        _init_done = True


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
    return json.dumps(payload).replace("</", "<\\/")


# ── CORS for /api/public/* (iframe sandbox → origin=null 需要它) ──
@app.after_request
def _add_public_cors(resp):
    if request.path.startswith("/api/public/"):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Max-Age"] = "86400"
        resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


@app.route("/api/public/<path:_>", methods=["OPTIONS"])
def _public_preflight(_):
    return ("", 204)


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
    ip = request.remote_addr or "unknown"
    if not _rate_limit(f"register:{ip}", limit=5, window=300):
        return jsonify({"error": "Too many attempts. Try again later."}), 429

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
    t0 = time.time()
    ip = request.remote_addr or "unknown"
    if not _rate_limit(f"forgot:{ip}", limit=5, window=300):
        return jsonify({"error": "Too many attempts. Try again later."}), 429
    d = request.get_json() or {}
    e = (d.get("email") or "").strip().lower()

    token = None
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (e,)).fetchone()
    if row:
        token = secrets.token_urlsafe(32)
        expiry = (utc_now() + timedelta(hours=1)).isoformat()
        conn.execute("UPDATE users SET reset_token=?, reset_token_expiry=? WHERE id=?",
                     (token, expiry, row["id"]))
        conn.commit()
    conn.close()

    payload = {"ok": True, "message": "If this email exists, reset link generated."}
    if token and app.config["DEMO_MODE"]:
        url = f"{request.host_url.rstrip('/')}/reset/{token}"
        logger.info(f"[DEMO] reset link for {e}: {url}")

    # ★ 恒定时间，防邮箱枚举
    elapsed = time.time() - t0
    if elapsed < 0.25:
        time.sleep(0.25 - elapsed)

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

@app.route("/api/projects/<pid>/chats", methods=["GET"])
@login_required
def list_project_chats(pid):
    r = _owned_project(pid)
    if not r:
        return jsonify({"error": "not found"}), 404
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, content, created_at FROM project_chats "
        "WHERE project_id=? AND user_id=? ORDER BY id ASC",
        (pid, current_user.id)).fetchall()
    conn.close()
    return jsonify([dict(x) for x in rows])


@app.route("/api/projects/<pid>/chats", methods=["POST"])
@login_required
def add_project_chat(pid):
    r = _owned_project(pid)
    if not r:
        return jsonify({"error": "not found"}), 404
    d = request.get_json() or {}
    role = d.get("role")
    content = (d.get("content") or "").strip()
    if role not in ("user", "assistant"):
        return jsonify({"error": "invalid role"}), 400
    if not content:
        return jsonify({"error": "empty content"}), 400
    if len(content) > 4000:
        content = content[:4000]
    conn = get_conn()
    conn.execute(
        "INSERT INTO project_chats (project_id, user_id, role, content, created_at) "
        "VALUES (?,?,?,?,?)",
        (pid, current_user.id, role, content, utc_now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/projects/<pid>/versions", methods=["GET"])
@login_required
def list_project_versions(pid):
    r = _owned_project(pid)
    if not r:
        return jsonify({"error": "not found"}), 404
    conn = get_conn()
    rows = conn.execute(
        "SELECT version_id, created_at FROM project_versions "
        "WHERE project_id=? ORDER BY created_at DESC", (pid,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/projects/<pid>/versions/<vid>/restore", methods=["POST"])
@login_required
def restore_project_version(pid, vid):
    r = _owned_project(pid)
    if not r:
        return jsonify({"error": "not found"}), 404
    conn = get_conn()
    v = conn.execute(
        "SELECT * FROM project_versions WHERE version_id=? AND project_id=?",
        (vid, pid)).fetchone()
    if not v:
        conn.close()
        return jsonify({"error": "version not found"}), 404
    conn.close()
    return jsonify({
        "ok": True,
        "config": json.loads(v["config"] or "{}"),
        "filters": json.loads(v["filters"] or "{}"),
    })


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

ANALYZE_SYSTEM_PROMPT = """你是物流分析助手。用户用自然语言描述分析需求，你要解析出结构化配置。

【能力边界 — 极其重要】
如果用户的需求超出以下范围，返回 {"unsupported": true, "reason": "..."}
支持范围：
- 延误率/延误天数分析
- 承运商/国家/洲/线路对比
- 成本/收入/OTIF/ETA 分析
- 在途风险/异常订单
- 时间范围筛选（"最近N天"）

不支持：
- 数据里没有的字段（节日、天气、运输方式、品类...）
- 特定事件的时段对比（"排灯节期间"、"去年双11"）
- 与物流无关的问题（编程、天气、写作...）
- 因果分析（"为什么延误"→ 只能说相关原因分布）

例：
输入："分析印度排灯节的延误"
输出：{"unsupported": true, "reason": "数据中没有节假日标记，无法定位排灯节期间的数据。可改为分析印度的整体延误情况。"}

输入："写个 Python 爬虫"
输出：{"unsupported": true, "reason": "这是物流分析工作台，只能回答物流数据相关问题。"}

【返回格式 — 必须是纯 JSON，不要任何 markdown 包裹】
{
  "title": "简短的分析标题（≤20 字）",
  "date_range_days": 30,
  "min_delay_days": null,
  "max_delay_days": null,
  "group_by": ["carrier", "country"],
  "reasoning": "用一句话总结你对用户需求的理解（≤60 字）",
  "suggested_focus": "建议优先关注的 1-2 个关键指标（≤80 字）"
}

【字段规则】
- title：从需求提取，如"近30天延误分析"
- date_range_days：用户说"最近N天"→ N；"一个月"→30；"一周"→7；未提→30；范围 1-365
- min_delay_days：用户说"超过N天"→ N；未提→null；范围 0-365
- max_delay_days：用户说"少于N天"→ N；未提→null；范围 0-365
- group_by：必须包含 "carrier"/"country"/"continent"/"lane" 中至少一个
- reasoning：为什么这样解析
- suggested_focus：值得关注的点

只返回 JSON，不要任何其他文字。"""

@app.route("/api/analyze", methods=["POST"])
@login_required
def analyze():
    text = (request.get_json() or {}).get("prompt", "").strip()
    if not text:
        return jsonify(parse_request(""))

    base_config = parse_request(text)

    conn = get_conn()
    s = conn.execute("SELECT * FROM builder_settings WHERE user_id=?",
                     (current_user.id,)).fetchone()
    conn.close()

    if not s or not (s["api_key"] or "").strip():
        return jsonify(base_config)

    base_url = (s["base_url"] or "").strip().rstrip("/")
    if not base_url:
        return jsonify(base_config)
    endpoint = (base_url if base_url.endswith("/chat/completions")
                else base_url + "/chat/completions")

    try:
        r = _http.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {s['api_key'].strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": s["model"],
                "messages": [
                    {"role": "system", "content": ANALYZE_SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                "stream": False,
                "max_tokens": 500,
                "reasoning_effort": "minimal",
            },
            timeout=(5, 15),
        )
        if r.status_code != 200:
            logger.warning(f"[analyze] LLM {r.status_code}, fallback")
            return jsonify(base_config)

        data = r.json()
        content = ((data.get("choices") or [{}])[0]
                   .get("message", {}).get("content", "")).strip()

        m = re.search(r"\{[\s\S]*\}", content)
        if not m:
            logger.warning("[analyze] no JSON, fallback")
            return jsonify(base_config)

        try:
            llm_config = json.loads(m.group(0))
        except Exception:
            logger.warning("[analyze] invalid JSON, fallback")
            return jsonify(base_config)

        if not isinstance(llm_config, dict):
            return jsonify(base_config)

        if llm_config.get("unsupported"):
            reason = llm_config.get("reason") or "无法分析该需求"
            if not isinstance(reason, str):
                reason = "无法分析该需求"
            return jsonify({"unsupported": True, "reason": reason[:300]})

        merged = dict(base_config)

        t = llm_config.get("title")
        if isinstance(t, str) and t.strip():
            merged["title"] = t.strip()[:60]

        days = llm_config.get("date_range_days")
        if isinstance(days, (int, float)) and 1 <= days <= 365:
            merged["date_range_days"] = int(days)

        gb = llm_config.get("group_by")
        if isinstance(gb, list):
            valid = {"carrier", "country", "continent", "lane"}
            filtered = [x for x in gb if isinstance(x, str) and x in valid]
            if filtered:
                merged["group_by"] = filtered

        for k in ("min_delay_days", "max_delay_days"):
            v = llm_config.get(k)
            if v is None:
                merged[k] = None
            elif isinstance(v, (int, float)) and 0 <= v <= 365:
                merged[k] = int(v)

        rs = llm_config.get("reasoning")
        if isinstance(rs, str) and rs.strip():
            merged["reasoning"] = rs.strip()[:200]

        sf = llm_config.get("suggested_focus")
        if isinstance(sf, str) and sf.strip():
            merged["suggested_focus"] = sf.strip()[:200]

        logger.info(f"[analyze] LLM config ok: title={merged.get('title')}")
        return jsonify(merged)

    except Exception as e:
        logger.warning(f"[analyze] error: {type(e).__name__}: {e}")
        return jsonify(base_config)


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

    # 注意：
    # - main_f：用于 metrics / 图表 / exceptions（受延误区间约束，但 In Transit / Exception 保留）
    # - base_f：用于状态饼图 / 趋势 / 地图（不受延误区间约束）
    main_f = apply_filters(ships, filters)
    base_filters = {k: v for k, v in filters.items()
                    if k not in ("min_delay_days", "max_delay_days")}
    base_f = apply_filters(ships, base_filters)

    metrics = calculate_metrics(main_f)
    status_dist = get_status_distribution(base_f)
    trend = get_delay_trend(base_f, int(filters.get("date_range_days") or 30))
    carriers = group_by(main_f, "carrier")
    countries = get_country_stats(base_f)
    continents = get_continent_stats(base_f)
    reasons = get_delay_reasons(main_f)
    lanes = get_lane_stats(base_f)
    reason_matrix = get_reason_carrier_matrix(main_f)
    cost_bd = get_cost_breakdown(main_f)
    range_stats = get_delay_range_stats(
        base_f, filters.get("min_delay_days"), filters.get("max_delay_days"))
    data_quality = get_data_quality(main_f)

    map_countries = countries
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

    cached = _report_cache_get(key)
    if cached is not None:
        return jsonify(cached)

    data = _compute_report(filters)
    _report_cache_put(key, data)
    return jsonify(data)


# ============================================================
# Map
# ============================================================

@app.route("/api/map", methods=["POST"])
@login_required
def map_data():
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

    filters = d.get("filters") or {}
    if not filters and d.get("date_range_days"):
        filters = {"date_range_days": d["date_range_days"]}

    ships = apply_filters(get_cached(), filters)

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
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "not found"}), 404
    # ★ 若即将删除的是一个活跃管理员，检查是否是最后一个
    if row["is_active"] and row["is_admin"]:
        active_admins = conn.execute(
            "SELECT COUNT(*) FROM users WHERE is_admin=1 AND is_active=1").fetchone()[0]
        if active_admins <= 1:
            conn.close()
            return jsonify({"error": "Cannot delete the last active admin."}), 400
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    log_action(current_user.id, "user_delete", f"uid={uid} user={row['username']}")
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


# ── 模块级初始化 ──
logger.info("[startup] running ensure_initialized...")
try:
    ensure_initialized()
    logger.info("[startup] ensure_initialized OK")
except Exception as e:
    logger.exception(f"[startup] ensure_initialized FAILED: {e}")


# =============================================================
# App Builder — 应用生成模块
# =============================================================
import requests as _http

BUILDER_SYSTEM_PROMPT = """你是前端工程师。根据用户需求生成完整的单文件 HTML 应用。

【硬性规则 — 违反任意一条即为失败】
1. 只输出一个 ```html 代码块，代码块前后不要任何文字、解释、markdown 标记
2. 输出必须是完整可运行的 HTML（含 <!DOCTYPE html>、<html>、<head>、<body>）
3. CSS/JS 全部内联，不引用外部 JS（除非 CDN 加载 Chart.js/ECharts）
4. 界面语言跟随用户需求
5. 所有 onclick/onkeydown 引用的函数必须先用 function 声明
6. 功能必须真实可交互，不能有占位符、TODO、注释代替实现
7. 应用要能独立运行，不依赖父页面

【数据持久化 — 极其重要】
8. 所有用户数据（列表、分数、设置、进度）必须用 localStorage 保存
9. localStorage 必须用 try/catch 包住（沙箱可能拒绝）
10. 初始化必须先 loadData() 从 localStorage 读，操作后立刻 saveData()
11. 不能只放内存，否则刷新就丢

标准模式：
```javascript
function loadData() {
  try { return JSON.parse(localStorage.getItem('myapp-key')) || []; }
  catch (e) { return []; }
}
function saveData(v) {
  try { localStorage.setItem('myapp-key', JSON.stringify(v)); }
  catch (e) {}
}
═══════════════════════════════════════════════════════
【待办清单 — 必须全部实现以下 8 项，缺一项即为失败】
═══════════════════════════════════════════════════════
当用户要"待办/清单/todo/任务管理"时，必须包含：
✅ 1. 添加任务：输入框 + 添加按钮 + Enter 也能添加
✅ 2. 任务改名：每行有"编辑"按钮，点击变成输入框，回车/保存按钮确认
✅ 3. 勾选完成：复选框，完成的文字变灰 + 删除线
✅ 4. 删除任务：每行有"删除"按钮
✅ 5. 三个筛选入口：「全部」「未完成」「已完成」三个按钮，点击切换过滤
✅ 6. 空任务不能添加：input.trim() 为空时弹提示（toast/alert），不能静默失败
✅ 7. localStorage 持久化：任务列表、每项的 text/done 状态、当前筛选状态都要存
✅ 8. 刷新后完整恢复：任务内容、完成状态、改名后的名称都要回来

参考结构（必须用类似的 state 结构，但代码可自由发挥）：

state: { todos: [{id, text, done}], filter: 'all'|'active'|'done' }

修改任何 state 后立刻 saveData()

初始化时先 loadData() 恢复 state，再 render()

═══════════════════════════════════════════════════════
【2048 — 必须全部实现以下 6 项】
═══════════════════════════════════════════════════════
✅ 1. 4×4 棋盘 + 随机生成 2 或 4
✅ 2. 方向键 + WASD + 触屏滑动 控制
✅ 3. 数字合并计分
✅ 4. 新游戏按钮
✅ 5. 最高分用 localStorage 保存（key: '2048-best'）
✅ 6. 当前棋盘和分数用 localStorage 保存（key: '2048-state'），刷新后恢复

═══════════════════════════════════════════════════════
【贪吃蛇 — 必须全部实现】
═══════════════════════════════════════════════════════
✅ 1. 方向键 + WASD 控制
✅ 2. 得分显示 + 最高分 localStorage 保存
✅ 3. 食物随机生成，吃到加分，撞墙/撞自己游戏结束
✅ 4. 暂停按钮（可选但推荐）

═══════════════════════════════════════════════════════
【计算器 / 番茄钟 / 记账本 / 天气】
═══════════════════════════════════════════════════════

计算器：四则运算 + 清除 + 错误处理 + 状态 localStorage 保存

番茄钟：25 分钟工作 + 5 分钟休息循环 + 开始/暂停/重置 + 可修改时间 + 状态 localStorage 保存

记账本：收入/支出 + 分类统计 + 添加/删除 + localStorage 保存

天气：城市选择 + 温度/湿度/风速 + 选中城市 localStorage 保存

【颜色/主题 — 由你理解并实现】
用户说"紫色"、"金黄色"、"BT21 的颜色"、"赛博朋克风"等，
你必须自己根据对这些概念的理解选择具体的 CSS 色值实现。
不要询问，不要返回原代码，直接用你理解的色值改。

【修改请求 — 如果你是回应修改】
M1. 输出必须是完整新版本 HTML
M2. 必须基于当前代码修改，不是重新生成
M3. 不能返回原代码 — 用户能明显看到代码不同
M4. 原有所有功能必须完整保留
M5. 用户要求的功能必须真实实现
M6. 修改完自检：新功能在吗？旧功能在吗？能跑吗？

【RouteMind 物流数据接口 — 同源、无需鉴权】
涉及"物流""订单""数据面板"时，调用真实接口（相对路径）：

fetch('/api/public/dashboard') → {total, status_distribution, carriers, continents}

fetch('/api/public/shipments?page=1&per_page=20') → {rows, total, page, pages}

fetch('/api/public/filters') → {carriers, countries, statuses}"""


def _init_builder_tables():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS builder_projects (
        id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS builder_versions (
        id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
        instruction TEXT, code TEXT NOT NULL, summary TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES builder_projects(id) ON DELETE CASCADE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS builder_shares (
        id TEXT PRIMARY KEY, project_id TEXT, title TEXT,
        code TEXT NOT NULL, views INTEGER DEFAULT 0, created_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS builder_settings (
        user_id INTEGER PRIMARY KEY, provider TEXT, base_url TEXT,
        api_key TEXT, model TEXT)""")
    conn.commit()
    conn.close()


_init_builder_tables()


@app.route("/builder")
@login_required
def builder_page():
    return render_template("builder.html",
                           app_state_json=_app_state(current_user, ""))


@app.route("/api/builder/projects", methods=["GET"])
@login_required
def builder_list_projects():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM builder_projects WHERE user_id=? ORDER BY updated_at DESC",
        (current_user.id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/builder/projects/<pid>/versions", methods=["GET"])
@login_required
def builder_list_versions(pid):
    conn = get_conn()
    own = conn.execute(
        "SELECT id FROM builder_projects WHERE id=? AND user_id=?",
        (pid, current_user.id)).fetchone()
    if not own:
        conn.close()
        return jsonify({"error": "not found"}), 404
    rows = conn.execute(
        "SELECT id, instruction, summary, created_at FROM builder_versions "
        "WHERE project_id=? ORDER BY created_at DESC, rowid DESC", (pid,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/builder/versions/<vid>/code", methods=["GET"])
@login_required
def builder_get_version_code(vid):
    conn = get_conn()
    row = conn.execute(
        "SELECT v.id, v.code, p.user_id FROM builder_versions v "
        "JOIN builder_projects p ON p.id = v.project_id "
        "WHERE v.id = ?", (vid,)).fetchone()
    conn.close()
    if not row or row["user_id"] != current_user.id:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": row["id"], "code": row["code"] or ""})


@app.route("/api/builder/versions", methods=["POST"])
@login_required
def builder_save_version():
    d = request.get_json() or {}
    project_id = d.get("project_id") or str(uuid.uuid4())[:8]
    now = utc_now().isoformat()
    conn = get_conn()
    if not d.get("project_id"):
        conn.execute(
            "INSERT INTO builder_projects (id, user_id, title, created_at, updated_at) "
            "VALUES (?,?,?,?,?)",
            (project_id, current_user.id,
             d.get("title") or "Untitled", now, now))
    else:
        conn.execute(
            "UPDATE builder_projects SET updated_at=? WHERE id=? AND user_id=?",
            (now, project_id, current_user.id))
    vid = str(uuid.uuid4())[:10]
    conn.execute(
        "INSERT INTO builder_versions (id, project_id, instruction, code, summary, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (vid, project_id, d.get("instruction"),
         d.get("code"), d.get("summary", ""), now))
    conn.commit()
    conn.close()
    return jsonify({"project_id": project_id, "version_id": vid})


@app.route("/api/builder/settings", methods=["GET", "POST"])
@login_required
def builder_settings():
    if request.method == "POST":
        d = request.get_json() or {}
        conn = get_conn()
        row = conn.execute("SELECT * FROM builder_settings WHERE user_id=?",
                           (current_user.id,)).fetchone()
        provider = d.get("provider", row["provider"] if row else "")
        base_url = d.get("base_url", row["base_url"] if row else "")
        model = d.get("model", row["model"] if row else "")

        # 语义：
        # - body 中包含 "api_key" 字段 → 覆盖（空字符串则清空）
        # - body 中不含 "api_key" 字段 → 保留原值
        if "api_key" in d:
            api_key = d.get("api_key") or ""
        else:
            api_key = row["api_key"] if row else ""

        if d.get("clear"):
            provider = ""
            base_url = ""
            model = ""
            api_key = ""

        conn.execute(
            "INSERT OR REPLACE INTO builder_settings "
            "(user_id, provider, base_url, api_key, model) VALUES (?,?,?,?,?)",
            (current_user.id, provider, base_url, api_key, model))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})

    conn = get_conn()
    row = conn.execute("SELECT * FROM builder_settings WHERE user_id=?",
                       (current_user.id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"configured": False})
    key = row["api_key"] or ""
    # ★ 不回传明文 API Key
    return jsonify({
        "configured": bool(key),
        "provider": row["provider"],
        "base_url": row["base_url"],
        "model": row["model"],
        "api_key_preview": ("***" + key[-4:]) if key else "",
    })


@app.route("/api/builder/settings/test", methods=["POST"])
@login_required
def builder_settings_test():
    d = request.get_json() or {}
    base = (d.get("base_url") or "").strip().rstrip("/")
    key = (d.get("api_key") or "").strip()
    model = (d.get("model") or "").strip()

    # ★ 允许"使用已保存的 key" 进行测试
    if d.get("use_saved_key") and not key:
        conn = get_conn()
        row = conn.execute(
            "SELECT api_key FROM builder_settings WHERE user_id=?",
            (current_user.id,)).fetchone()
        conn.close()
        if row:
            key = (row["api_key"] or "").strip()

    if not base or not key or not model:
        return jsonify({"ok": False, "error": "Missing base_url / api_key / model"})
    if base.endswith("/chat/completions"):
        endpoint = base
    else:
        endpoint = base + "/chat/completions"
    try:
        r = _http.post(
            endpoint,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": "hi"}],
                  "max_tokens": 5},
            timeout=(10, 30),
        )
        if r.status_code != 200:
            return jsonify({"ok": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"})
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"})


@app.route("/api/builder/projects/<pid>", methods=["DELETE"])
@login_required
def builder_delete_project(pid):
    conn = get_conn()
    own = conn.execute(
        "SELECT id FROM builder_projects WHERE id=? AND user_id=?",
        (pid, current_user.id),
    ).fetchone()
    if not own:
        conn.close()
        return jsonify({"error": "not found"}), 404
    conn.execute("DELETE FROM builder_versions WHERE project_id=?", (pid,))
    conn.execute("DELETE FROM builder_projects WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/builder/share", methods=["POST"])
@login_required
def builder_share():
    d = request.get_json() or {}
    code = d.get("code")
    if not code:
        return jsonify({"error": "no code"}), 400
    sid = secrets.token_urlsafe(8)
    conn = get_conn()
    conn.execute(
        "INSERT INTO builder_shares (id, project_id, title, code, created_at) "
        "VALUES (?,?,?,?,?)",
        (sid, d.get("project_id"), d.get("title"), code, utc_now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"url": f"/s/{sid}"})


@app.route("/s/<sid>")
def shared_app(sid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM builder_shares WHERE id=?", (sid,)).fetchone()
    if not row:
        conn.close()
        return "Share link not found", 404
    conn.execute("UPDATE builder_shares SET views = views + 1 WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return render_template("shared.html", code=row["code"], title=row["title"])


# ============================================================
# 公开 API：供生成的 app 在 iframe 中调用（无需登录，只读脱敏）
# ============================================================

@app.route("/api/public/dashboard", methods=["GET"])
def public_dashboard():
    ships = get_cached()
    total = len(ships)
    status_dist = {"Delivered": 0, "In Transit": 0, "Exception": 0}
    carrier_counts = {}
    continent_counts = {}

    for s in ships:
        st = s.get("status")
        if st in status_dist:
            status_dist[st] += 1
        c = s.get("carrier")
        if c:
            carrier_counts[c] = carrier_counts.get(c, 0) + 1
        ct = s.get("destination_continent")
        if ct:
            continent_counts[ct] = continent_counts.get(ct, 0) + 1

    return jsonify({
        "total": total,
        "status_distribution": status_dist,
        "carriers": [{"name": k, "count": v} for k, v in
                     sorted(carrier_counts.items(), key=lambda kv: -kv[1])],
        "continents": [{"name": k, "count": v} for k, v in
                       sorted(continent_counts.items(), key=lambda kv: -kv[1])],
    })


@app.route("/api/public/shipments", methods=["GET"])
def public_shipments():
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(10, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    carrier = request.args.get("carrier", "").strip()
    country = request.args.get("country", "").strip()
    status = request.args.get("status", "").strip()

    ships = get_cached()
    filtered = ships
    if carrier:
        filtered = [s for s in filtered if s.get("carrier") == carrier]
    if country:
        filtered = [s for s in filtered if s.get("destination_country") == country]
    if status:
        filtered = [s for s in filtered if s.get("status") == status]

    total = len(filtered)
    rows = filtered[offset:offset + per_page]

    allowed = ["shipment_id", "carrier", "destination", "destination_country",
               "destination_continent", "status", "priority", "ship_date",
               "expected_delivery_date", "actual_delivery_date",
               "delay_reason", "shipping_cost"]

    return jsonify({
        "rows": [{k: r.get(k) for k in allowed} for r in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    })


@app.route("/api/public/filters", methods=["GET"])
def public_filters():
    ships = get_cached()
    carriers = sorted(set(s.get("carrier") for s in ships if s.get("carrier")))
    countries = sorted(set(s.get("destination_country") for s in ships
                           if s.get("destination_country")))
    return jsonify({
        "carriers": carriers,
        "countries": countries,
        "statuses": ["Delivered", "In Transit", "Exception"],
    })


ASSISTANT_SYSTEM_PROMPT = """你是 RouteMind 的物流数据分析助手。用户问题会附带一份当前数据集的结构化快照（JSON）。

【数据源清单 — 你手里有什么】
- current_filters：当前筛选状态（date_range_days / carrier / country / continent / min_delay_days）
- metrics：全局指标（total_shipments / delay_rate / on_time_rate / otif_rate / avg_delay_days / p90_delay_days / in_transit_count / at_risk_count / revenue / avg_cost_per_shipment）
- top_carriers[]：每个承运商 name / delay_rate / otif_rate / avg_cost_per_shipment / shipments
- top_countries[]：每个国家 name / delay_rate / otif_rate / shipments / revenue
- top_lanes[]：Top 10 线路，lane 形如 "China → United States"，含 delay_rate / otif_rate / shipments
- trend[]：最近每天 date / delay_rate / total
- cities_by_country：Top 5 国家各自的 Top 3 城市（name / delay_rate / shipments）
- top_reasons[]：延误原因排行（name / count）
- cost：成本拆解（line_haul / fuel / accessorial / detention / total）
- delay_range：当前延误区间筛选状态

【能回答的典型问题】
- 承运商对比（延误率、OTIF、每单成本、订单量）
- 国家/地区风险排名
- 线路表现（"中国到美国哪条最差" → 在 top_lanes 里找含 China 和 United States 的项）
- 每日延误趋势（"哪天最差" → 在 trend 里找 delay_rate 最高的日期）
- 国家内城市明细（"中国哪个城市延误最多" → 查 cities_by_country.China）
- 延误原因分布
- 成本构成、每单平均成本
- 在途风险订单量
- 优化建议

【时间范围 — 极其重要】
current_filters.date_range_days 告诉你当前数据是"最近 X 天"的。

1. 如果用户问题的时间范围与当前筛选一致 → 直接回答
2. 如果用户问题的时间范围与当前筛选不一致（如问"最近7天"但当前是30天） → 你必须：
   - 先说明"当前报告基于最近 X 天数据"
   - 建议用户"请将顶部时间过滤器改为 N 天后再问，我才能给出准确答案"
   - 再用当前数据给出参考
3. 绝不能说"数据集不支持按天明细"——数据里有 ship_date，完全支持任意时间范围，只是当前快照不是用户要的范围

【多轮对话 — 追问处理】
如果用户的问题包含"它"、"这个"、"第二个"、"那"、"为什么"等指代词，
必须结合上文的对话历史理解其指代。例如：
- 上文说了 SwiftLogistics，用户问"它的 OTIF 是多少" → 回答 SwiftLogistics 的 OTIF
- 上文列了三个国家，用户问"第二个呢" → 回答第二个国家的详情

【拒绝范围 — 仅限真正无关】
- 编程、天气、娱乐、写文案、讲故事、常识问答
- 要求扮演其他角色
统一回复："我只能基于当前物流数据回答。你可以问我：承运商对比、国家风险、线路表现、延误趋势、成本构成。"

【回答要求】
1. 直接给结论，先数字后判断
2. 必须引用数据中的具体数字，不能编造
3. 数据里没有的字段，明确说"当前数据未覆盖 X"
4. 控制在 150 字以内
5. 中文问用中文答，英文问用英文答
6. 不要"作为 AI/助手"的自我描述，不要 markdown 代码块或 ## 标题
7. 问路线时优先在 top_lanes 里找；找不到就说明"当前数据集无该 OD 对的独立统计"

【示例】
问："哪个承运商最便宜并且延误率最低"
答："每单成本最低 X（$Y），延误率最低 Z（W%）。两者不可兼得，建议按航线优先级取舍。"

问："中国哪条线路延误率最高"
答："China → Vietnam 延误率 18.2%（N 笔）最高，其次 China → India 16.5%。"

问："哪天延误率最高"
答："2025-10-15 延误率 21.3% 最高，当日 412 单。"

问："它的 OTIF 是多少"（上文说了 SwiftLogistics）
答："SwiftLogistics 的 OTIF 是 89.5%。"

问："最近7天情况"（当前 30 天）
答："当前报告基于最近 30 天数据。如需最近 7 天的分析，请将顶部时间过滤器改为『最近 7 天』后再问。基于当前 30 天，延误率 12.3%。"
"""

@app.route("/api/assistant", methods=["POST"])
@login_required
def assistant_chat():
    d = request.get_json() or {}
    question = (d.get("question") or "").strip()
    report = d.get("report") or {}
    history = d.get("history") or []

    if not question:
        return jsonify({"error": "question required"}), 400
    if len(question) > 2000:
        question = question[:2000]
    if not isinstance(history, list):
        history = []
    if not report or not report.get("metrics"):
        return jsonify({"error": "no report data", "fallback": True}), 200

    metrics = report.get("metrics") or {}
    carriers = report.get("carriers") or []
    countries = report.get("countries") or []
    lanes = report.get("lanes") or []
    trend = report.get("trend") or []
    reasons = report.get("delay_reasons") or []
    cost = report.get("cost_breakdown") or {}
    ranges = report.get("range_stats") or {}
    map_cities = report.get("map_cities") or []
    filters = report.get("filters") or {}

    # 城市聚合：Top 5 国家各 Top 3 城市
    cities_by_country = {}
    for country in countries[:5]:
        cname = country.get("name")
        if not cname:
            continue
        city_list = [
            c for c in map_cities
            if c.get("country") == cname and c.get("delay_rate") is not None
        ]
        city_list.sort(key=lambda x: x.get("delay_rate") or 0, reverse=True)
        cities_by_country[cname] = [
            {"name": c.get("name"),
             "delay_rate": c.get("delay_rate"),
             "shipments": c.get("total_shipments")}
            for c in city_list[:3]
        ]

    # trend 精简
    trend_clean = [
        {"date": p.get("date"),
         "delay_rate": p.get("delay_rate"),
         "total": p.get("total")}
        for p in trend if (p.get("total") or 0) > 0
    ]
    if len(trend_clean) > 30:
        trend_clean = trend_clean[-30:]

    # min_delay_days 规范化为 int 或 None
    raw_min = filters.get("min_delay_days")
    if raw_min in (None, ""):
        min_delay_val = None
    else:
        try:
            min_delay_val = int(raw_min)
        except (ValueError, TypeError):
            min_delay_val = None

    context = {
        "current_filters": {
            "date_range_days": filters.get("date_range_days", 30),
            "carrier": filters.get("carrier") or "",
            "country": filters.get("country") or "",
            "continent": filters.get("continent") or "",
            "min_delay_days": min_delay_val,
        },
        "metrics": {k: metrics.get(k) for k in [
            "total_shipments", "delivered_count", "delayed_count",
            "in_transit_count", "exception_count", "delay_rate",
            "on_time_rate", "otif_rate", "eta_accuracy_rate",
            "avg_delay_days", "p90_delay_days", "at_risk_count",
            "revenue", "avg_cost_per_shipment",
        ]},
        "top_carriers": [
            {"name": c.get("name"),
             "delay_rate": c.get("delay_rate"),
             "otif_rate": c.get("otif_rate"),
             "avg_cost_per_shipment": c.get("avg_cost_per_shipment"),
             "shipments": c.get("total_shipments")}
            for c in carriers[:8]
        ],
        "top_countries": [
            {"name": c.get("name"),
             "delay_rate": c.get("delay_rate"),
             "otif_rate": c.get("otif_rate"),
             "shipments": c.get("total_shipments"),
             "revenue": c.get("revenue")}
            for c in countries[:8]
        ],
        "top_lanes": [
            {"lane": l.get("lane"),
             "delay_rate": l.get("delay_rate"),
             "otif_rate": l.get("otif_rate"),
             "shipments": l.get("total_shipments")}
            for l in lanes[:10]
        ],
        "trend": trend_clean,
        "cities_by_country": cities_by_country,
        "top_reasons": [
            {"name": r.get("name"), "count": r.get("count")}
            for r in reasons[:8]
        ],
        "cost": cost,
        "delay_range": ranges,
    }

    conn = get_conn()
    s = conn.execute("SELECT * FROM builder_settings WHERE user_id=?",
                     (current_user.id,)).fetchone()
    conn.close()

    if not s or not (s["api_key"] or "").strip():
        return jsonify({"error": "未配置 API Key", "fallback": True}), 200

    base_url = (s["base_url"] or "").strip().rstrip("/")
    if not base_url:
        return jsonify({"error": "Base URL 未配置", "fallback": True}), 200
    endpoint = (base_url if base_url.endswith("/chat/completions")
                else base_url + "/chat/completions")

    # 拼 messages：system + 历史 + 当前问题（带 context）
    messages = [{"role": "system", "content": ASSISTANT_SYSTEM_PROMPT}]
    for h in history[-6:]:
        if not isinstance(h, dict):
            continue
        h_role = h.get("role")
        h_content = (h.get("content") or "").strip()
        if h_role not in ("user", "assistant") or not h_content:
            continue
        if len(h_content) > 800:
            h_content = h_content[:800]
        messages.append({"role": h_role, "content": h_content})

    messages.append({
        "role": "user",
        "content": (
            f"当前物流数据快照：\n{json.dumps(context, ensure_ascii=False)}\n\n"
            f"用户问题：{question}"
        ),
    })

    try:
        r = _http.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {s['api_key'].strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": s["model"],
                "messages": messages,
                "stream": False,
                "max_tokens": 500,
                "temperature": 0.2,
                "reasoning_effort": "medium",
            },
            timeout=(10, 45),
        )
        if r.status_code != 200:
            logger.warning(f"[assistant] LLM {r.status_code}")
            return jsonify({"error": f"LLM {r.status_code}", "fallback": True}), 200
        data = r.json()
        answer = ((data.get("choices") or [{}])[0]
                  .get("message", {}).get("content", "")).strip()
        if not answer:
            return jsonify({"error": "empty answer", "fallback": True}), 200
        return jsonify({"answer": answer})
    except Exception as e:
        logger.warning(f"[assistant] error: {type(e).__name__}: {e}")
        return jsonify({"error": f"{type(e).__name__}: {e}", "fallback": True}), 200
    
@app.route("/api/report/insights", methods=["POST"])
@login_required
def report_insights():
    d = request.get_json() or {}
    report = d.get("report") or {}
    if not report or not report.get("metrics"):
        return jsonify({"error": "no report", "fallback": True}), 200

    conn = get_conn()
    s = conn.execute("SELECT * FROM builder_settings WHERE user_id=?",
                     (current_user.id,)).fetchone()
    conn.close()

    if not s or not (s["api_key"] or "").strip():
        return jsonify({"error": "no key", "fallback": True}), 200

    metrics = report.get("metrics") or {}
    carriers = (report.get("carriers") or [])[:5]
    countries = (report.get("countries") or [])[:5]
    reasons = (report.get("delay_reasons") or [])[:5]
    lanes = (report.get("lanes") or [])[:3]
    cost = report.get("cost_breakdown") or {}
    ranges = report.get("range_stats") or {}

    context = {
        "metrics": {k: metrics.get(k) for k in [
            "total_shipments", "delivered_count", "delayed_count",
            "in_transit_count", "exception_count", "delay_rate",
            "on_time_rate", "otif_rate", "eta_accuracy_rate",
            "avg_delay_days", "p90_delay_days", "at_risk_count",
            "revenue", "avg_cost_per_shipment",
        ]},
        "top_carriers": [
            {"name": c.get("name"), "delay_rate": c.get("delay_rate"),
             "otif_rate": c.get("otif_rate"),
             "shipments": c.get("total_shipments")}
            for c in carriers
        ],
        "top_countries": [
            {"name": c.get("name"), "delay_rate": c.get("delay_rate"),
             "shipments": c.get("total_shipments"),
             "revenue": c.get("revenue")}
            for c in countries
        ],
        "top_reasons": [{"name": r.get("name"), "count": r.get("count")}
                        for r in reasons],
        "top_lanes": [{"lane": l.get("lane"),
                       "delay_rate": l.get("delay_rate"),
                       "shipments": l.get("total_shipments")}
                      for l in lanes],
        "cost": cost,
        "delay_range": ranges,
    }

    lang = (d.get("lang") or "zh").lower()
    is_zh = lang.startswith("zh")

    system_msg = (
        "你是物流数据分析专家。基于用户提供的结构化数据，输出专业的结论与建议。"
        if is_zh else
        "You are a logistics data analyst. Based on the structured data provided, "
        "output professional conclusions and recommendations."
    )

    user_msg = f"""{"请用中文回答。" if is_zh else "Please respond in English."}

【数据】
{json.dumps(context, ensure_ascii=False, indent=2)}

【输出格式 — 严格返回 JSON，不要 markdown 包裹】
{{
  "summary": "一段话总结核心发现，必须包含至少 2 个具体数字，≤100 字",
  "findings": [
    "关键发现 1：必须引用数据中的具体数字",
    "关键发现 2：必须引用数据中的具体数字",
    "关键发现 3：必须引用数据中的具体数字"
  ],
  "recommendations": [
    "建议 1：具体动作 + 预期效果",
    "建议 2：具体动作 + 预期效果",
    "建议 3：具体动作 + 预期效果"
  ]
}}

【规则】
1. 只能使用数据中的数字，不能编造
2. findings 和 recommendations 各 3-5 条
3. recommendations 要具体可执行（不是"加强管理"这种空话）
4. 数据中缺失的字段不要提
5. 只输出 JSON，不要任何解释文字"""

    base_url = (s["base_url"] or "").strip().rstrip("/")
    if not base_url:
        return jsonify({"error": "no base_url", "fallback": True}), 200
    endpoint = (base_url if base_url.endswith("/chat/completions")
                else base_url + "/chat/completions")

    try:
        r = _http.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {s['api_key'].strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": s["model"],
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                "stream": False,
                "max_tokens": 1200,
                "reasoning_effort": "low",
            },
            timeout=(10, 45),
        )
        if r.status_code != 200:
            logger.warning(f"[insights] LLM {r.status_code}")
            return jsonify({"error": f"LLM {r.status_code}", "fallback": True}), 200

        data = r.json()
        content = ((data.get("choices") or [{}])[0]
                   .get("message", {}).get("content", "")).strip()

        m = re.search(r"\{[\s\S]*\}", content)
        if not m:
            return jsonify({"error": "no json", "fallback": True}), 200

        try:
            insights = json.loads(m.group(0))
        except Exception:
            return jsonify({"error": "invalid json", "fallback": True}), 200

        if not isinstance(insights, dict):
            return jsonify({"error": "bad shape", "fallback": True}), 200

        summary = insights.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            return jsonify({"error": "bad summary", "fallback": True}), 200
        summary = summary.strip()[:500]

        findings = insights.get("findings") or []
        recs = insights.get("recommendations") or []
        if not isinstance(findings, list):
            findings = []
        if not isinstance(recs, list):
            recs = []

        clean_findings = []
        for x in findings[:5]:
            if isinstance(x, str) and x.strip():
                clean_findings.append(x.strip()[:300])

        clean_recs = []
        for x in recs[:5]:
            if isinstance(x, str) and x.strip():
                clean_recs.append(x.strip()[:300])

        logger.info(f"[insights] ok: {len(clean_findings)} findings, {len(clean_recs)} recs")
        return jsonify({
            "summary": summary,
            "findings": clean_findings,
            "recommendations": clean_recs,
        })

    except Exception as e:
        logger.warning(f"[insights] error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e), "fallback": True}), 200

@app.route("/api/builder/generate", methods=["POST"])
@login_required
def builder_generate():
    d = request.get_json() or {}
    instruction = (d.get("instruction") or "").strip()
    current_code = d.get("current_code") or ""
    if not instruction:
        return jsonify({"error": "instruction required"}), 400

    conn = get_conn()
    s = conn.execute("SELECT * FROM builder_settings WHERE user_id=?",
                     (current_user.id,)).fetchone()
    conn.close()

    has_key = bool(s and (s["api_key"] or "").strip())

    from builder_templates import match_template, validate_modification

    def sse(obj):
        return b"data: " + json.dumps(obj, ensure_ascii=False).encode("utf-8") + b"\n\n"

    # ══════════════════════════════════════════════════════════
    # 修改请求：必须走 LLM，不允许模板假装修改
    # ══════════════════════════════════════════════════════════
    if current_code and not has_key:
        return jsonify({
            "error": "当前未配置模型 API Key，无法执行代码修改。"
                     "请在右上角『设置』中配置模型后再试。"
        }), 400

    # ══════════════════════════════════════════════════════════
    # 首次生成 + 无 Key：只能走模板兜底
    # ══════════════════════════════════════════════════════════
    if not has_key:
        tpl_code, tpl_name = match_template(instruction)
        if tpl_code:
            logger.info(f"[generate] no key, template fallback: {tpl_name}")

            def tpl_stream():
                payload = {"choices": [{"delta": {
                    "content": "```html\n" + tpl_code + "\n```"
                }}]}
                yield b"data: " + json.dumps(payload, ensure_ascii=False).encode("utf-8") + b"\n\n"
                yield b"data: [DONE]\n\n"
            return Response(
                tpl_stream(),
                mimetype="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no",
                         "Connection": "close"},
            )
        return jsonify({
            "error": "未配置 API Key，无法生成自定义应用。"
                     "可试内置模板：2048 / 待办 / 计算器 / 番茄钟 / 记账本 / 贪吃蛇 / 天气 / 物流面板"
        }), 400

    # ══════════════════════════════════════════════════════════
    # 有 Key：首次生成和修改都走 LLM
    # ══════════════════════════════════════════════════════════
    base_url = (s["base_url"] or "").strip().rstrip("/")
    if not base_url:
        return jsonify({"error": "Base URL 未配置"}), 400
    endpoint = (base_url if base_url.endswith("/chat/completions")
                else base_url + "/chat/completions")

    api_key = (s["api_key"] or "").strip()
    model = (s["model"] or "").strip()
    if not api_key or not model:
        return jsonify({"error": "API Key 或模型未配置"}), 400

    MAX_CODE_LEN = 80000
    if current_code and len(current_code) > MAX_CODE_LEN:
        half = MAX_CODE_LEN // 2
        current_code = (current_code[:half]
                        + "\n<!-- ...middle truncated... -->\n"
                        + current_code[-half:])

    def build_messages(attempt=1, prev_errors=None):
        msgs = [{"role": "system", "content": BUILDER_SYSTEM_PROMPT}]

        if current_code:
            # 修改模式
            err_hint = ""
            if prev_errors:
                err_hint = (
                    f"⚠️ 上一次修改失败，原因：\n"
                    + "\n".join(f"- {e}" for e in prev_errors)
                    + "\n\n这次必须真正修改到位。\n\n"
                )
            content = (
                f"{err_hint}"
                f"当前代码（基准）：\n```html\n{current_code}\n```\n\n"
                f"用户要求修改：{instruction}\n\n"
                f"【必须遵守】\n"
                f"1. 输出完整的新版本 HTML（从 <!DOCTYPE html> 到 </html>）\n"
                f"2. 必须基于当前代码修改，不是重新生成\n"
                f"3. 用户要求的功能必须真实实现\n"
                f"4. 原有功能完整保留\n"
                f"5. 代码必须有明显变化\n"
                f"6. 只输出 ```html 代码块"
            )
            msgs.append({"role": "user", "content": content})
        else:
            # 首次生成模式
            content = (
                f"用户需求：{instruction}\n\n"
                f"请按以下要求生成完整应用：\n"
                f"1. 输出完整可运行的 HTML（含 <!DOCTYPE html>、<html>、<head>、<body>）\n"
                f"2. CSS/JS 全部内联，不依赖外部资源（除非 CDN 加载 Chart.js）\n"
                f"3. 界面语言跟随用户需求\n"
                f"4. 所有用户数据必须用 localStorage 持久化（用 try/catch 包住）\n"
                f"5. 初始化先 load，操作后立刻 save\n"
                f"6. 所有 onclick 引用的函数必须先用 function 声明\n"
                f"7. 功能真实可交互，不要占位符\n"
                f"8. 只输出一个 ```html 代码块，不要任何解释文字"
            )
            msgs.append({"role": "user", "content": content})
        return msgs

    def call_llm(msgs, max_tokens=12000):
        r = _http.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": msgs,
                "stream": False,
                "max_tokens": max_tokens,
                "reasoning_effort": "medium",
            },
            timeout=(15, 180),
        )
        if r.status_code != 200:
            raise RuntimeError(f"LLM HTTP {r.status_code}: {r.text[:300]}")
        data = r.json()
        return (data.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""

    def extract_html(raw):
        if not raw:
            return None
        m = re.search(r"```html\s*([\s\S]*?)(```|$)", raw, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        if "<!DOCTYPE" in raw or "<html" in raw:
            start = raw.find("<")
            if start != -1:
                return raw[start:].strip()
        return None

    def stream():
        final_html = None
        last_errors = None

        for attempt in range(1, 4):
            yield sse({"stage": "attempt", "attempt": attempt})
            try:
                raw = call_llm(build_messages(attempt, last_errors))
            except Exception as e:
                logger.exception(f"[generate] attempt {attempt} failed: {e}")
                last_errors = [f"模型调用异常: {e}"]
                if attempt == 3:
                    break
                yield sse({"stage": "retry", "reason": str(e)})
                continue

            html = extract_html(raw)
            if not html or "<html" not in html.lower():
                last_errors = ["模型未返回有效的 HTML 代码块"]
                if attempt == 3:
                    break
                yield sse({"stage": "retry", "reason": "未返回完整 HTML"})
                continue

            # ══════════════════════════════════════════════════
            # 首次生成：也做验证（Isabella 逐条验收标准）
            # ══════════════════════════════════════════════════
            if not current_code:
                from builder_templates import validate_first_generation
                errors = validate_first_generation(instruction, html)
                if not errors:
                    logger.info(f"[generate] first-gen attempt {attempt} passed")
                    final_html = html
                    break

                logger.warning(f"[generate] first-gen attempt {attempt} failed: {errors}")
                last_errors = errors
                yield sse({"stage": "retry", "reason": "；".join(errors)})
                continue

            # ══════════════════════════════════════════════════
            # 修改：验证
            # ══════════════════════════════════════════════════
            errors = validate_modification(current_code, html, instruction)
            if not errors:
                logger.info(f"[generate] modify attempt {attempt} passed")
                final_html = html
                break

            logger.warning(f"[generate] modify attempt {attempt} failed: {errors}")
            last_errors = errors
            yield sse({"stage": "retry", "reason": "；".join(errors)})

        # ══════════════════════════════════════════════════════
        # LLM 三次都失败 → 首次生成可以模板兜底
        # ══════════════════════════════════════════════════════
        if not final_html:
            if not current_code:
                tpl_code, tpl_name = match_template(instruction)
                if tpl_code:
                    logger.warning(
                        f"[generate] LLM failed 3x, fallback to: {tpl_name}")
                    yield sse({"stage": "fallback",
                               "reason": f"AI 生成失败，已使用内置 {tpl_name} 模板"})
                    final_html = tpl_code
                else:
                    yield sse({"error": (
                        f"AI 生成失败（原因：{'；'.join(last_errors or ['未知'])}）。\n"
                        "建议：换个说法重试，或在设置中切换到 gemini-3.5-flash（能力更强）"
                    )})
                    yield b"data: [DONE]\n\n"
                    return
            else:
                yield sse({"error": (
                    f"无法完成此修改（原因：{'；'.join(last_errors or ['未知'])}）。\n"
                    "建议：\n"
                    "1. 换个说法重试一次\n"
                    "2. 或点击『新建应用』重新生成\n"
                    "3. 或在设置中切换到 gemini-3.5-flash（能力更强）"
                )})
                yield b"data: [DONE]\n\n"
                return

        # 模拟流式输出
        wrapped = "```html\n" + final_html + "\n```"
        chunk_size = 200
        for i in range(0, len(wrapped), chunk_size):
            chunk = wrapped[i:i+chunk_size]
            yield sse({"choices": [{"delta": {"content": chunk}}]})
            time.sleep(0.003)

        yield b"data: [DONE]\n\n"

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream; charset=utf-8",
            "Connection": "close",
        },
    )


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        port=int(os.environ.get("PORT", "5000")),
        threaded=True,
        use_reloader=False,
    )