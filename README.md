# RouteMind AI - 甄彬炜

> AI 物流分析工作室：**用一句话描述你的问题 → Agent 解析意图 → 生成可交互、可分享的分析工作台**

**在线体验**：https://routemind-ai-bdwr.onrender.com  
**测试账号**：`admin@routemind.local` / `Admin123!`

> Render 免费层会休眠，首次访问约 30–60 秒唤醒。

---

## 这个项目是什么

RouteMind 把「自然语言 → 分析报告」这条链路拆成：

```
用户意图 ──► Agent 解析 ──► 结构化配置 ──► 计算管线 ──► 分析应用
            (request_parser)   (filters+config)  (analytics)   (6 模块视图)
```

Agent 的产物不是一个静态报告，而是一个**可交互、可分享、可持久化**的工作台。

---

## 3 分钟演示

1. 登录 → 首页输入 `分析最近 30 天的延误，找出最差的承运商`
2. 观察 4 步进度条 → 报告页加载
3. 切换过滤器（时间范围 / 承运商 / 洲）→ 实时重算并自动保存
4. 点击地图上的国家 → 右侧面板显示该国指标
5. 切换到「地区」模式 → 城市青点 → 点击城市 → 高亮所属国家
6. 右上角 AI → 问「哪个承运商最差？」
7. Share → 生成只读链接
8. 刷新页面 → 左侧历史仍在

---

## 功能清单

### Agent 核心
- **自然语言解析**：识别时间范围、承运商、国家、洲、延误阈值、图表类型
- **上下文追问**：AI 助手支持「那国家呢？」「它的 OTIF 如何？」
- **结构化配置输出**：Agent 产出 `filters + config`，驱动下游全链路

### 分析应用（Agent 产物）
- 6 大模块：执行摘要 / 趋势 / 承运商与线路 / 地理风险 / 异常与在途 / 成本
- 核心 KPI：订单量、OTIF、延误率、ETA 准确率、P90 延误、营收
- 关联分析：承运商 × 延误原因矩阵、成本 vs 服务散点

### 可视化
- **全球风险地图**（ECharts）
  - 国家模式：所有有数据的国家按延误率着色
  - 地区模式：城市散点 + 选中城市时高亮所属国家
  - 支持缩放、平移、中英双语
- **Chart.js 图表**：延误趋势、状态分布、承运商对比、成本拆解

### 工作流
- 项目自动保存 + 版本历史（最近 50 版，可回滚）
- 只读分享链接
- CSV 导出（防注入）+ PDF 打印

### 数据管理（管理员）
- 数据库浏览 / 编辑 / CSV 上传替换 / 模拟增量
- 审计日志

### 平台
- 多用户、角色权限、中英双语、暗亮主题
- 登录限流、XSS / CSV 注入防护

---

## 技术栈

| 层 | 选型 | 原因 |
|---|---|---|
| 后端 | Flask 3 | 轻量、可读，单文件入口 |
| 数据库 | SQLite（WAL） | 单机零依赖，5 万条 < 100ms |
| 前端 | 原生 JS | 无构建工具，源码直接可读 |
| 图表 | Chart.js + ECharts | 趋势 + 地图，开箱即用 |
| 部署 | Render + Gunicorn | 免费层够用 |

---

## 本地运行

```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

export SECRET_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')"
export DEMO_MODE=0
python app.py
```

Windows PowerShell 用：

```powershell
$env:SECRET_KEY = python -c "import secrets;print(secrets.token_urlsafe(48))"
$env:DEMO_MODE = "0"
python app.py
```

打开 <http://127.0.0.1:5000/login>。首次启动会生成 5 万条合成订单（3–8 秒）。

---

## 项目结构

```
app.py              Flask 主应用：路由、认证、缓存
analytics.py        指标计算、过滤、聚合
data_generator.py   合成数据
request_parser.py   自然语言 → 配置
chat_modifier.py    AI 助手意图
templates/          index.html / auth.html
static/js/          app.js / auth.js
static/css/         style.css
```

---

## 设计取舍

**Agent 边界**：Agent 输出结构化配置而非代码。4 小时内稳定可控，每个下游模块有清晰扩展点。升级路径：把计算管线替换为 Agent 自主组合 SQL + 图表。

**数据策略**：完全合成，不依赖外部 API。报告结果按 filters 哈希缓存 30 秒，容量 64 槽 LRU。

**复杂度控制**：
- 前端不上框架 → 评委可直接读 Agent 意图处理逻辑
- 后端不拆微服务 → 5 分钟读懂全貌
- 地图用 ECharts → 免 token、免额度

---

## AI 工具使用

**VSCode + Copilot + DeepSeek**

| 工具 | 承担 |
|---|---|
| Copilot | inline 补全、样板代码、重复性 CSS/HTML |
| DeepSeek | 架构讨论、复杂 bug 排查、代码审查、安全分析 |
| 本人 | 产品决策、核心算法、边界测试、部署调试 |

核心分析逻辑、安全策略、产品取舍均人工完成，AI 提供方向，验证由人负责。

---

## 已知限制

- **Render 免费层数据不持久**：休眠/重部署后 SQLite 会重置，冷启动时自动重建种子数据
- 冷启动 30–60 秒
- 地图色阶用 P90 × 1.3 动态计算，极端数据下对比度会被压缩
- 意图解析覆盖 8 类，超出走兜底提示

---

## 许可证

教学 / 演示用途。商用请自行评估合规、安全与 SLA 要求。
