# RouteMind AI

> **AI 驱动的物流分析工作台** — 用一句话把原始运单数据变成可交互、可分享的分析报告。

[![Live Demo](https://img.shields.io/badge/Live%20Demo-onrender.com-46E3B7)](https://routemind-ai-bdwr.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black)](https://flask.palletsprojects.com/)

**在线体验**：https://routemind-ai-bdwr.onrender.com
**测试账号**：`admin@routemind.local` / `Admin123!`

---

## 简介

RouteMind 是一个自然语言驱动的物流分析平台：输入"分析最近 30 天的延误，找出最差的承运商"，系统自动解析意图、计算指标、渲染可交互报告，并保存为可分享的项目。

- **Agent 驱动**：自然语言 → 结构化 config → 报告
- **可交互**：过滤器实时重算、地图钻取、图表切换
- **可持久化**：自动保存、版本历史、只读分享
- **App Builder**：内置 LLM 应用生成器，一句话生成可运行 HTML

技术栈：Flask + 原生 JS + SQLite + Chart.js + ECharts。

---

## 快速开始

### 部署到 Render

1. Fork 本仓库
2. 在 Render 新建 Web Service，连接 fork
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
5. 环境变量：
   - `SECRET_KEY` = 随机字符串（`python -c "import secrets;print(secrets.token_urlsafe(48))"`）
   - `DATA_SIZE` = `10000`
   - `ENABLE_TICK` = `0`

### 本地运行

```bash
git clone https://github.com/ZhenBinWei-Sucy/routemind-ai.git
cd routemind-ai

python3 -m venv venv
source venv/bin/activate      # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env
export SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')"
export DEMO_MODE=1

python app.py
# → http://127.0.0.1:5000/login
```

> Windows 生产环境：`pip install waitress && python wsgi.py`

---

## 功能

**分析工作台**

- 自然语言 → 报告（4 步进度反馈）
- KPI：订单量 / OTIF / 延误率 / ETA 准确率 / P90 延误 / 收入
- 趋势图（延误率 / 数量、折线 / 柱状切换）
- 承运商对比（延误率 / OTIF / 每单成本 / 订单量）
- 全球风险地图（国家 / 地区双模式，点击钻取）
- 异常订单 / 在途风险表
- 成本拆解 + 成本 vs 服务散点
- 自动生成的执行摘要 + 建议

**平台能力**

- 注册 / 登录 / 修改密码 / 忘记密码
- 项目自动保存 + 版本历史 + 只读分享
- CSV 导出（防注入）/ PDF 打印
- 数据管理：编辑 / 上传 CSV / 定时增量
- 管理员：用户管理 / 审计日志
- 中英双语、暗亮主题
- AI 助手（8 类意图 + LLM 兜底）

**App Builder**

- 一句话生成完整 HTML 应用（SSE 流式 + 实时预览）
- 支持 OpenAI / DeepSeek / Kimi / 通义千问 / 智谱 / 硅基流动 / OpenRouter
- 无 Key 时 8 个模板兜底（2048 / 待办 / 计算器 / 番茄钟 / 记账本 / 贪吃蛇 / 天气 / 物流面板）
- 版本历史 + 分享

---

## 架构

```
浏览器 (原生 JS)
  │
  ├── index.html     主工作台
  ├── builder.html   App Builder
  └── auth.html      登录/注册
  │ fetch / SSE
  ▼
Flask (app.py)
  ├── /api/analyze      自然语言 → config
  ├── /api/report       config → 聚合指标（LRU 缓存）
  ├── /api/map/focus    单国/城市详情
  ├── /api/assistant    LLM 对话
  ├── /api/builder/*    SSE 流式生成
  └── /api/public/*     供生成的应用调用（CORS，已脱敏）
  │
  ├── analytics.py      纯函数指标计算
  └── data_generator.py 合成订单生成
  │ sqlite3 (WAL)
  ▼
SQLite (routemind.db)
```

**关键设计**

- Agent 输出结构化 config 而非 SQL，每层下游有清晰扩展点
- `analytics.py` 全为纯函数（`shipments → metrics`），易测易复用
- 缓存分层：过滤器缓存 + 报告 LRU（TTL 30s / 64 条）
- 前端无框架，Agent 意图分发逻辑直接可读

---

## 项目结构

```
.
├── app.py                 Flask 主应用
├── analytics.py           指标计算
├── data_generator.py      合成数据
├── request_parser.py      自然语言 → config
├── builder_templates.py   App Builder 兜底模板
├── wsgi.py                WSGI 生产入口
├── requirements.txt
├── templates/             index / auth / builder / shared
└── static/
    ├── css/               style.css / builder.css
    └── js/                app.js / auth.js / builder.js
```

---

## 环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `SECRET_KEY` | — | **生产必填** |
| `DEMO_MODE` | `0` | `1` = 重置链接只打到日志 |
| `DB_PATH` | `routemind.db` | SQLite 路径 |
| `DATA_SIZE` | `50000` | 首次生成的订单数 |
| `ENABLE_TICK` | `1` | 后台定时增量 |
| `TICK_INTERVAL` | `600` | 增量间隔（秒） |
| `TICK_SIZE` | `500` | 每次增量条数 |
| `PORT` | `5000` | 端口 |

---

## 主要 API

| 路径 | 方法 | 权限 | 说明 |
|---|---|---|---|
| `/api/auth/login` | POST | 公开 | 登录（限流 10/min） |
| `/api/analyze` | POST | 登录 | 自然语言 → config |
| `/api/report` | POST | 登录 | 聚合报告（LRU 缓存） |
| `/api/map/focus` | POST | 登录 | 单国/城市详情 |
| `/api/export` | POST | 登录 | CSV 导出 |
| `/api/db/shipments/<id>` | PUT/DELETE | 管理员 | 编辑 / 删除 |
| `/api/builder/generate` | POST | 登录 | SSE 流式生成 HTML |
| `/api/public/*` | GET | 公开 | 供生成应用调用（已脱敏） |
| `/api/share/<token>` | GET | 公开 | 只读分享 |

---

## 安全措施

- 密码：PBKDF2-SHA256；≥8 字符 + 大写 + 数字
- Session：HttpOnly + SameSite=Lax + 生产 Secure
- 登录限流 10/min、注册限流 5/5min
- 用户名白名单 `^[a-zA-Z0-9_.-]{4,32}$`（防 XSS）
- 参数化 SQL、CSV 注入防护、上传限制
- 最后一个活跃管理员不可删除 / 禁用
- LLM API Key 仅返回 `***xxxx` 预览，不回明文
- 用户生成的代码在沙箱 iframe 中运行，无法读父页面 session
- 重置密码 timing 恒定（防邮箱枚举）

---

## 已知限制

| 限制 | 说明 |
|---|---|
| Render 免费层数据不持久 | 实例休眠后 SQLite 重置，种子数据自动重建；用户注册账号会丢失 |
| 冷启动 30–60 秒 | 免费实例特性 |
| 单 worker | SQLite + 内存缓存需单 worker |
| 意图解析 8 类 | 超出范围走兜底（有 LLM Key 时走 LLM） |

---

## License

MIT