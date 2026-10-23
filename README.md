# RouteMind AI · 精简版 README

直接覆盖 `README.md` 即可。

```markdown
# RouteMind AI

AI 物流分析工作室：自然语言 → 可交互报告。Flask + 原生 JS + SQLite。

---

## 功能

- **自然语言分析**：一句话生成报告（延误、承运商、国家、在途风险、成本）
- **六大模块**：KPI 摘要、趋势、承运商/线路、地理风险、异常/在途、成本
- **全球地图**：国家按延误率着色；国家模式 / 地区模式切换；点击查看详情
- **工作流**：自动保存、版本历史、只读分享、CSV/PDF 导出
- **数据管理**：数据库浏览、管理员编辑、CSV 上传替换、增量模拟
- **平台**：多用户、角色权限、审计日志、中英双语、暗/亮主题、AI 问答

---

## 快速开始

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:SECRET_KEY = python -c "import secrets;print(secrets.token_urlsafe(48))"
$env:DEMO_MODE = "0"
python app.py
```

> Windows 不支持 gunicorn。生产用：`pip install waitress` + `python wsgi.py`

### macOS / Linux

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')"
export DEMO_MODE=0
python app.py
```

打开 <http://127.0.0.1:5000/login>

**默认管理员**：`admin@routemind.local` / `Admin123!`（**部署后立即修改**）

---

## 环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `SECRET_KEY` | — | **生产必填** |
| `DEMO_MODE` | `0` | `1` 时忘记密码重置链接只打到日志 |
| `DB_PATH` | `routemind.db` | SQLite 路径 |
| `DATA_SIZE` | `50000` | 首次生成的合成订单数 |
| `ENABLE_TICK` | `1` | 是否定时新增数据 |
| `FLASK_DEBUG` | `0` | 调试模式 |
| `PORT` | `5000` | 端口 |

---

## 项目结构

```
app.py              Flask 主应用
analytics.py        指标计算
data_generator.py   合成数据
request_parser.py   自然语言 → 配置
chat_modifier.py    AI 助手意图
templates/          index.html / auth.html
static/js/          app.js / auth.js
static/css/         style.css
```

---

## 主要 API

| 路径 | 说明 | 权限 |
|---|---|---|
| `POST /api/auth/login` | 登录（限流 10 次/分） | 公开 |
| `POST /api/analyze` | 自然语言 → 配置 | 登录 |
| `POST /api/report` | 计算报告（30s 缓存） | 登录 |
| `POST /api/map/focus` | 单国家/城市详情 | 登录 |
| `PUT /api/db/shipments/<id>` | 修改订单 | 管理员 |
| `POST /api/admin/upload-csv` | 上传替换数据集 | 管理员 |
| `GET /api/share/<token>` | 只读分享内容 | 公开 |

---

## CSV 上传要求

必填列：`shipment_id, ship_date, carrier, origin, destination, destination_country, status, shipping_cost`

- 日期：`YYYY-MM-DD`
- `status`：`Delivered` / `In Transit` / `Exception`
- 上限：50 万行 / 100 MB，UTF-8 编码

---

## 安全措施

- 密码：PBKDF2-SHA256；≥8 字符 + 大写 + 数字
- Session：HttpOnly + SameSite=Lax + 生产 Secure
- 登录限流、用户名白名单（防 XSS）、参数化 SQL
- CSV 注入防护、上传大小/行数限制
- 最后一个活跃管理员不可撤销/禁用
- 分享链接 128 位熵、审计日志

**生产清单**：`SECRET_KEY` + `DEMO_MODE=0` + HTTPS + Gunicorn/Waitress + 修改默认密码

---

## 常见问题

**Windows `export` 报错？** → PowerShell 用 `$env:VAR = "value"`

**`No module named 'fcntl'`？** → gunicorn 仅 Linux；Windows 用 `python wsgi.py`（需 `pip install waitress`）

**首次启动慢？** → 生成 5 万条数据约 3–8 秒；之后 <1 秒。减少量：`$env:DATA_SIZE = "10000"`（需先删 `routemind.db`）

**端口占用？** → `$env:PORT = "5001"`（需 `app.py` 末尾读取 `PORT`）

**地图不显示？** → 需能访问 `cdn.jsdelivr.net` 加载 `world.json`

**忘记管理员密码？**

```powershell
python -c "import sqlite3;from werkzeug.security import generate_password_hash;c=sqlite3.connect('routemind.db');c.execute('UPDATE users SET password_hash=? WHERE username=?',(generate_password_hash('NewPass123!'),'admin'));c.commit();c.close()"
```

**清空数据重来？** → 停止服务，删 `routemind.db`，重启

---

## 可选文件

**`wsgi.py`**（Windows 生产入口）

```python
from app import app
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000, threads=4)
```

**`run.ps1`**（Windows 一键启动）

```powershell
$env:DEMO_MODE = "0"
$env:SECRET_KEY = python -c "import secrets;print(secrets.token_urlsafe(48))"
$env:FLASK_DEBUG = "1"
python app.py
```

**`app.py` 末尾**（支持 PORT 变量）

```python
if __name__ == "__main__":
    ensure_initialized()
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        port=int(os.environ.get("PORT", "5000")),
        threaded=True,
        use_reloader=False,
    )
```