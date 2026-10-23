# RouteMind AI · Logistics Intelligence Studio

> **Atoms 风格 Demo** — 用自然语言驱动 Agent，把一句分析需求变成可交互、可分享、可持久化的物流分析工作台。
>
> 提交至 [ROOT AI Native 笔试](INTERVIEW.md) · 部署于 Render · 欢迎 star ⭐

[![Deploy](https://img.shields.io/badge/Live%20Demo-onrender.com-46E3B7)](https://routemind-ai-bdwr.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black)](https://flask.palletsprojects.com/)

---

## 目录

- [这是什么](#这是什么)
- [3 分钟演示](#3-分钟演示)
- [快速开始](#快速开始)
- [架构总览](#架构总览)
- [功能清单](#功能清单)
- [关键设计取舍](#关键设计取舍)
- [环境变量](#环境变量)
- [项目结构](#项目结构)
- [主要 API](#主要-api)
- [CSV 上传格式](#csv-上传格式)
- [安全措施](#安全措施)
- [已知限制](#已知限制)
- [面试说明文档](#面试说明文档)

---

## 这是什么

Atoms 的核心范式是 **Agent 驱动 + 端到端交付**。RouteMind 把这一范式落到"物流分析"场景：

> **用户输入一句话 → Agent 解析意图 → 计算指标 → 渲染可交互报告 → 自动保存为项目**

Agent 的产物不是静态 PDF，而是**可交互、可筛选、可分享、可持久化**的活工作台。

技术栈极简：**Flask + 原生 JS + SQLite + Chart.js + ECharts**。所有 Agent 相关逻辑直接写在 `app.js` / `app.py` 里，方便评审直接阅读。

---

## 3 分钟演示

1. **登录** → `admin@routemind.local` / `Admin123!`
2. **首页输入** `分析最近 30 天的延误，找出最差的承运商` → 点击「生成报告」
3. 观察 4 步进度条（理解需求 → 选择指标 → 准备报告 → 就绪）→ 报告加载
4. **切换过滤器**（时间 / 承运商 / 洲 / 国家 / 延误区间）→ 实时重算 + 自动保存
5. **点击地图国家** → 右侧详情面板联动（订单量 / 延误率 / OTIF / 收入）
6. 切到 **地区模式** → 点击城市点 → 高亮所属国家
7. **右上角 AI** → 问「哪个承运商最差？」→ 8 类意图 + 上下文追问
8. **Share** → 生成只读链接 → 无痕窗口验证
9. **App Builder**（`/builder`）→ 一句话生成可运行 HTML 应用，支持 2048 / 待办 / 物流面板等模板
10. **中英切换** + **暗亮主题** 全程生效

---

## 快速开始

### 一键部署到 Render（推荐）

1. Fork 本仓库
2. 在 Render 新建 **Web Service** → 连接你的 fork
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
5. 环境变量：
   - `SECRET_KEY` = 随机字符串（`python -c "import secrets;print(secrets.token_urlsafe(48))"`）
   - `DATA_SIZE` = `10000`（免费实例内存有限，建议从 1 万条起）
   - `ENABLE_TICK` = `0`（避免免费实例休眠期间后台线程被打断）
6. 部署完成后访问 `/login`

### 本地运行（macOS / Linux）

```bash
git clone https://github.com/ZhenBinWei-Sucy/routemind-ai.git
cd routemind-ai

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
export SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')"
export DEMO_MODE=1

python app.py
# → http://127.0.0.1:5000/login
```

### 本地运行（Windows PowerShell）

```powershell
git clone https://github.com/ZhenBinWei-Sucy/routemind-ai.git
cd routemind-ai

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
$env:SECRET_KEY = python -c "import secrets;print(secrets.token_urlsafe(48))"
$env:DEMO_MODE = "1"

python app.py
```

> Windows 生产环境：`pip install waitress` + `python wsgi.py`

**默认管理员**：`admin@routemind.local` / `Admin123!`（**部署后请立即修改**）

---

## 架构总览

```
┌──────────────────────────────────────────────────────────┐
│                     浏览器 (原生 JS)                      │
│                                                          │
│  index.html + app.js       ← 主工作台（报表 / 地图 / AI）│
│  builder.html + builder.js ← App Builder（LLM 生成 HTML）│
│  auth.html + auth.js       ← 登录 / 注册 / 重置密码     │
└───────────────┬──────────────────────────────────────────┘
                │ fetch / SSE
┌───────────────▼──────────────────────────────────────────┐
│                     Flask (app.py)                       │
│                                                          │
│  /api/analyze     自然语言 → 结构化 config               │
│  /api/report      config + filters → 聚合指标（LRU 缓存）│
│  /api/map/focus   单国家 / 城市详情                       │
│  /api/assistant   LLM 对话（用户自带 Key）               │
│  /api/builder/*   LLM 流式生成 HTML（SSE 转发）          │
│  /api/public/*    供生成的应用调用（只读、已脱敏、CORS） │
│                                                          │
│  analytics.py     纯函数指标计算（无副作用、可单测）     │
│  data_generator.py 合成订单生成（5 万条 / 3 秒）         │
└───────────────┬──────────────────────────────────────────┘
                │ sqlite3 (WAL)
┌───────────────▼──────────────────────────────────────────┐
│                  SQLite (routemind.db)                   │
│                                                          │
│  users / projects / project_versions / shares           │
│  shipments (5万+ 合成订单)                               │
│  audit_log / builder_*                                   │
└──────────────────────────────────────────────────────────┘
```

**关键设计**：

- **Agent 不生成代码，生成结构化配置**：4 小时窗口内稳定可控，每层下游都有清晰扩展点
- **纯函数计算**：`analytics.py` 所有函数都是 `shipments → metrics`，没有全局状态，易于测试和复用
- **缓存分层**：过滤器选项缓存 + 报告 LRU 缓存（TTL 30s / 64 条）
- **前端无框架**：原生 JS，方便评审直接读 Agent 意图分发逻辑

---

## 功能清单

### 核心分析

| 模块 | 能力 |
|---|---|
| 自然语言分析 | 一句话 → 结构化 config → 报告（4 步进度反馈） |
| KPI 摘要 | 订单量 / OTIF / 延误率 / ETA 准确率 / P90 延误 / 收入 |
| 趋势 | 延误率 / 延误量切换，折线 / 柱状切换 |
| 承运商 | 延误率 / OTIF / 每单成本 / 订单量，四选一 |
| 延误原因 | Top 8 原因分布 |
| 地理风险 | 全球地图（国家 / 地区双模式）+ 国家排名表 + 城市明细 |
| 异常 / 在途 | 异常订单表 + 在途风险订单表（剩余天数） |
| 成本 | 拆解（干线 / 燃油 / 附加 / 滞留）+ 成本 vs 服务散点 |
| 结论 | 自动生成 executive summary + 5 条下一步建议 |
| 附录 | 数据质量明细 + 最新 120 条订单 |

### 平台能力

- 注册 / 登录 / 修改密码 / 忘记密码（重置链接）
- 项目自动保存 + 版本历史 + 只读分享链接
- CSV 导出（防注入）/ PDF 打印
- 数据管理：浏览 / 编辑 / 删除订单，上传 CSV 替换，模拟增量
- 管理员：用户管理 / 审计日志 / 最后一个管理员保护
- 中英双语、暗 / 亮主题
- AI 助手：8 类意图 + 上下文追问 + LLM 兜底

### App Builder（Atoms 同类功能）

- 一句话生成完整可运行 HTML 应用（SSE 流式生成 + 实时预览）
- 无 Key 时自动切模板兜底（2048 / 待办 / 计算器 / 番茄钟 / 记账本 / 贪吃蛇 / 天气 / 物流面板）
- 用户自带 LLM Key，支持 OpenAI / DeepSeek / Kimi / 通义千问 / 智谱 / 硅基流动 / OpenRouter / 自定义
- 版本历史 + 分享链接 + 复制 / 下载
- 全站中英双语

---

## 关键设计取舍

### 1. Agent 输出结构化 config，而不是生成代码

**方案 A**：让 LLM 直接写 SQL / 生成报表代码
**方案 B**：让 LLM 输出 JSON config（`{title, date_range_days, min_delay_days, group_by}`）

选 B 的理由：

- 4 小时窗口内，方案 B 的**结果可控性**远高于 A（LLM 生成的 SQL 经常有语法陷阱，且脏数据会直接崩掉整个报表）
- 结构化 config 让每个下游模块（KPI / 图表 / 地图 / 建议文案）都有**清晰的扩展点**
- 用户可以在 UI 上手动修改 config（等价于"过滤器"），这是 A 无法实现的

### 2. 完全合成数据

不依赖外部 API（天气、真实运单、汇率），交付可预测。5 万条合成订单 3 秒内生成完毕，结构真实（承运商 × 国家 × 延误原因 的关联有偏置）。

### 3. 前端不上框架

评审能直接读 `app.js` 的意图分发逻辑，不用先看框架文档。代价是 UI 状态管理全靠手写，但对这个体量的应用是合理的。

### 4. 沙箱 iframe + CORS

App Builder 用 `sandbox="allow-scripts allow-forms allow-modals"`（不含 `allow-same-origin`）保证用户生成的代码**不能**读到父页面 session。副作用是 iframe 的 origin = null，跨域访问 `/api/public/*` 需要服务端加 CORS 头——已加。

---

## 环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `SECRET_KEY` | — | **生产必填**，session 签名 |
| `DEMO_MODE` | `0` | `1` 时重置密码链接只打到服务端日志 |
| `DB_PATH` | `routemind.db` | SQLite 路径 |
| `DATA_SIZE` | `50000` | 首次启动生成的合成订单数 |
| `ENABLE_TICK` | `1` | 是否后台定时增量 |
| `TICK_INTERVAL` | `600` | 增量间隔（秒） |
| `TICK_SIZE` | `500` | 每次增量条数 |
| `FLASK_DEBUG` | `0` | 调试模式 |
| `PORT` | `5000` | 端口 |

---

## 项目结构

```
.
├── app.py                 Flask 主应用（路由 / 认证 / 报告 / Builder）
├── analytics.py           纯函数指标计算
├── data_generator.py      合成数据生成
├── request_parser.py      自然语言 → 结构化 config
├── builder_templates.py   App Builder 兜底模板（无 Key 时用）
├── wsgi.py                WSGI 生产入口（Render / waitress）
├── requirements.txt
├── .env.example
├── INTERVIEW.md           笔试说明文档
├── templates/
│   ├── index.html         主工作台
│   ├── auth.html          登录 / 注册 / 重置
│   ├── builder.html       App Builder
│   └── shared.html        分享页
└── static/
    ├── css/
    │   ├── style.css
    │   └── builder.css
    └── js/
        ├── app.js
        ├── auth.js
        └── builder.js
```

---

## 主要 API

| 路径 | 方法 | 权限 | 说明 |
|---|---|---|---|
| `/api/auth/register` | POST | 公开 | 注册（限流 5/5min） |
| `/api/auth/login` | POST | 公开 | 登录（限流 10/min） |
| `/api/auth/logout` | POST | 登录 | 登出 |
| `/api/auth/forgot` | POST | 公开 | 忘记密码（恒定时间） |
| `/api/auth/reset` | POST | 公开 | 重置密码 |
| `/api/auth/change-password` | POST | 登录 | 修改密码 |
| `/api/analyze` | POST | 登录 | 自然语言 → config |
| `/api/report` | POST | 登录 | 聚合报告（LRU 缓存 30s） |
| `/api/map` | POST | 登录 | 地图数据 |
| `/api/map/focus` | POST | 登录 | 单国家 / 城市详情 |
| `/api/export` | POST | 登录 | CSV 导出（防注入） |
| `/api/dashboard` | GET | 登录 | 数据概览 |
| `/api/db/shipments` | GET | 登录 | 订单分页 |
| `/api/db/shipments/<id>` | PUT/DELETE | 管理员 | 编辑 / 删除 |
| `/api/admin/*` | GET/POST | 管理员 | 用户 / 数据集 / 审计 |
| `/api/builder/generate` | POST | 登录 | SSE 流式生成 HTML |
| `/api/builder/settings` | GET/POST | 登录 | LLM Key 配置（GET 不回明文） |
| `/api/public/*` | GET | 公开 | 供生成的应用调用（CORS，已脱敏） |
| `/api/share/<token>` | GET | 公开 | 只读分享内容 |

---

## CSV 上传格式

必填列：

```
shipment_id, ship_date, carrier, origin, destination,
destination_country, status, shipping_cost
```

- 日期：`YYYY-MM-DD`
- `status`：`Delivered` / `In Transit` / `Exception`
- 上限：50 万行 / 100 MB，UTF-8 编码
- 可自动补齐：`destination_country_code` / `destination_continent` / `destination_lon` / `destination_lat`

---

## 安全措施

- **密码**：PBKDF2-SHA256；≥8 字符 + 大写 + 数字
- **Session**：HttpOnly + SameSite=Lax + 生产 Secure
- **登录限流**：10 次/分钟/IP
- **注册限流**：5 次/5 分钟/IP
- **用户名白名单**：`^[a-zA-Z0-9_.-]{4,32}$`（防 XSS 注入）
- **参数化 SQL**：所有查询走占位符
- **CSV 注入防护**：`=+-@\t\r` 开头的内容会加 `'` 前缀
- **CSV 上传限制**：50 万行 / 100 MB / 严格字段校验
- **最后一个活跃管理员保护**：不可删除 / 禁用 / 撤销
- **API Key 安全**：`GET /api/builder/settings` 只返回 `***xxxx` 预览，不回明文
- **沙箱隔离**：用户生成的 HTML 在 `sandbox` iframe 中运行，无法读取父页面 session
- **重置密码 timing 恒定**：防止邮箱枚举
- **审计日志**：所有敏感操作入库

**生产部署清单**：

```
✅ 设置 SECRET_KEY 为强随机值
✅ DEMO_MODE=0
✅ 启用 HTTPS（Render 默认开启）
✅ 用 gunicorn / waitress（不用 debug server）
✅ 修改默认管理员密码
✅ 关闭 FLASK_DEBUG
```

---

## 已知限制

| 限制 | 说明 | 缓解 |
|---|---|---|
| Render 免费层数据不持久 | 实例休眠 / 重新部署后 SQLite 被重置 | 每次冷启动自动重建种子数据和默认管理员，演示功能不受影响；但用户注册的账号会丢失 |
| 冷启动 30–60 秒 | 免费实例特性 | 首次访问前先预热 |
| 地图色阶动态计算 | `vMax = P90 × 1.3`，极端数据下对比度会被压缩 | 可切换国家 / 地区模式看明细 |
| 意图解析 8 类 | 超出范围走兜底提示，非自由对话 | 提供快捷按钮覆盖常见问题 |
| 单 Worker | SQLite + 内存缓存，多 worker 会竞态 | Render 免费实例本来就是单 worker；生产建议升级 PostgreSQL + Redis |

---

## 面试说明文档

完整的笔试说明（实现思路、完成度、取舍、后续计划、AI 工具使用）见 **[INTERVIEW.md](INTERVIEW.md)**。

---

## License

MIT — 仅用于学习与演示。