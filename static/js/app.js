// =============================================================
// RouteMind AI — main SPA controller
// =============================================================

(function bootstrap() {
  const el = document.getElementById("app-state");
  let payload = { user: null, sharedToken: "" };
  if (el && el.textContent.trim()) {
    try { payload = JSON.parse(el.textContent.trim()); }
    catch (e) { console.error("Bad #app-state:", e); }
  }
  window.CURRENT_USER = payload.user || null;
  window.SHARED_TOKEN = payload.sharedToken || "";
})();

// =============================================================
// i18n dictionary
// =============================================================
const I18N = {
  en: {
    "brand.sub": "AI Logistics Studio",
    "nav.home": "Home",
    "nav.dashboard": "Data Dashboard",
    "nav.database": "Database",
    "nav.settings": "Settings",
    "nav.admin": "Admin",
    "nav.logout": "Sign Out",
    "nav.ai": "AI",
    "shared.note": "Shared read-only view",
    "topbar.fresh": "Loading…",
    "topbar.waiting": "Waiting for live updates",
    "topbar.freshAt": "Updated {ago}",
    "topbar.freshSec": "{n}s ago",
    "topbar.freshMin": "{n}m ago",
    "topbar.freshHour": "{n}h ago",

    "tabs.report": "Report",
    "tabs.data": "Data",

    "home.greeting": "What do you want to investigate?",
    "home.sub": "Describe your logistics question in natural language.",
    "home.placeholder": "e.g. Analyze the last 30 days of delays, find carriers with highest delay rate, compare countries.",
    "home.templates": "Quick examples:",
    "home.generate": "Generate Report",
    "home.newAnalysis": "New Analysis",

    "brand.sub": "AI Logistics Studio",
    "builderHero.title": "Want to build a small app? Try App Builder",
    "builderHero.subtitle": "Describe in one sentence — AI generates complete runnable HTML in real time. Chat is the iteration, versions auto-save.",
    "builderHero.cta": "Open App Builder",

    "history.title": "Projects",
    "history.empty": "No projects yet.",
    "history.loading": "Loading…",
    "history.openFailed": "Open failed: ",
    "history.today": "Today",
    "history.yesterday": "Yesterday",
    "history.week": "This Week",
    "history.older": "Older",

    "tpl.delay.title": "Shipment Delay",
    "tpl.carrier.title": "Carrier Performance",
    "tpl.country.title": "Country Risk",
    "tpl.transit.title": "In-Transit Risk",

    "gen.s1": "Understanding request",
    "gen.s2": "Selecting metrics",
    "gen.s3": "Preparing report",
    "gen.s4": "Ready to review",

    "filter.date": "Date Range",
    "filter.d7": "Last 7 days",
    "filter.d30": "Last 30 days",
    "filter.d60": "Last 60 days",
    "filter.d90": "Last 90 days",
    "filter.d120": "Last 120 days",
    "filter.carrier": "Carrier",
    "filter.priority": "Priority",
    "filter.continent": "Continent",
    "filter.country": "Country",
    "filter.statusLabel": "Status",
    "filter.search": "Search",
    "filter.all": "All carriers",
    "filter.allPriority": "All priorities",
    "filter.allContinent": "All continents",
    "filter.allCountry": "All countries",
    "filter.allStatus": "All statuses",
    "filter.status.delivered": "Delivered",
    "filter.status.transit": "In Transit",
    "filter.status.exception": "Exception",
    "filter.minDelay": "Min Delay (days)",
    "filter.maxDelay": "Max Delay (days)",
    "filter.none": "No limit",

    "loading.prepare": "Preparing request",
    "loading.received": "Data received",
    "loading.kpi": "Computing metrics",
    "loading.charts": "Rendering charts",
    "loading.tables": "Rendering tables",
    "loading.map": "Loading map",
    "loading.done": "Ready",

    "data.total": "Total",
    "data.delivered": "Delivered",
    "data.delayed": "Delayed",
    "data.inTransit": "In Transit",
    "data.exception": "Exception",
    "table.priority": "Priority",

    "dq.total": "Total Records",
    "dq.missingExpected": "Missing Expected",
    "dq.missingActual": "Missing Actual",
    "dq.quality": "Quality",

    "dashboard.title": "Data Dashboard",
    "dashboard.sub": "Overview of the current shipment dataset.",
    "dashboard.total": "Total Shipments",
    "dashboard.lastUpdated": "Last Updated",
    "dashboard.quality": "Data Quality",
    "dashboard.missing": "Missing Fields",
    "dashboard.statusDist": "Status Distribution",
    "dashboard.carrierDist": "By Carrier",
    "dashboard.continentDist": "By Continent",
    "dashboard.qualityDetail": "Data Quality Detail",
    "dashboard.quickActions": "Admin Quick Actions",
    "dashboard.adminOnly": "Available to administrators",
    "dashboard.goAdmin": "Go to Admin Console",
    "dashboard.missingExpected": "Missing Expected Date",
    "dashboard.missingActual": "Missing Actual Date",
    "dashboard.invalidStatus": "Invalid Status",
    "dashboard.validRatio": "Valid Ratio",

    "database.title": "Database",
    "database.sub": "Browse all shipments in the current dataset.",
    "database.searchPlaceholder": "Search by ID / carrier / city...",
    "database.actions": "Actions",
    "database.edit": "Edit",
    "database.delete": "Delete",
    "database.editTitle": "Edit Shipment",
    "database.cancel": "Cancel",
    "database.saveChanges": "Save Changes",
    "database.perPage": "Per page:",
    "database.total": "{n} records",
    "database.saveSuccess": "Shipment updated",
    "database.saveFailed": "Save failed: ",
    "database.deleteConfirm": "Delete this shipment?",
    "database.deleteSuccess": "Shipment deleted",
    "database.deleteFailed": "Delete failed: ",
    "database.failedLoad": "Failed to load database",
    "database.readonlyHint": "Read-only. Only administrators can edit.",

    "ch.summary.title": "Executive Summary",
    "ch.summary.sub": "Key metrics at a glance",
    "ch.trend.title": "Trend & Structure",
    "ch.trend.sub": "How is the operation moving?",
    "ch.carrier.title": "Carrier & Lane Performance",
    "ch.carrier.sub": "Who is performing and who is not",
    "ch.geo.title": "Geographic Risk",
    "ch.geo.sub": "Where are the operational hotspots?",
    "ch.exception.title": "Exceptions & At-Risk",
    "ch.exception.sub": "What needs immediate attention?",
    "ch.cost.title": "Cost & Efficiency",
    "ch.cost.sub": "Where is the money going?",
    "ch.conclusion.title": "Conclusions & Recommendations",
    "ch.conclusion.sub": "Findings, evidence, and next steps",
    "ch.appendix.title": "Appendix",
    "ch.appendix.sub": "All shipments & data quality",

    "kpi.total": "Shipments",
    "kpi.totalHint": "Filtered orders",
    "kpi.otif": "OTIF",
    "kpi.otifHint": "On-time + in-full / delivered",
    "kpi.delay": "Delay Rate",
    "kpi.delayHint": "Delayed / delivered",
    "kpi.eta": "ETA Accuracy (±1d)",
    "kpi.etaHint": "Accurate ETA / delivered",
    "kpi.p90": "P90 Delay",
    "kpi.p90Hint": "Worst 10% delay days",
    "kpi.revenue": "Revenue",
    "kpi.revenueHint": "Total shipping cost",

    "chart.trend": "Delay Trend",
    "chart.trendNote": "Ignores delay-range filter",
    "chart.status": "Status Distribution",
    "chart.statusNote": "Ignores delay-range filter",
    "chart.carrier": "Carrier Performance",
    "chart.reasons": "Delay Reasons",
    "chart.m.delay": "Delay Rate",
    "chart.m.otif": "OTIF",
    "chart.m.cost": "Cost/Shipment",
    "chart.m.volume": "Volume",
    "chart.line": "Line",
    "chart.bar": "Bar",
    "chart.map": "Global Risk Map",
    "chart.mapHint": "Click a country to inspect details",
    "chart.mapHintCountry": "Showing cities in this country",
    "chart.costBreakdown": "Cost Breakdown",
    "chart.costVsService": "Cost vs Service",
    "chart.costVsServiceNote": "X = cost/shipment · Y = delay rate · Bubble size = volume · Bottom-left is best",
    "chart.costLegend": "Cost ($)",
    "chart.serviceLegend": "Delay Rate (%)",

    "trend.mode.rate": "Delay Rate",
    "trend.mode.count": "Delayed Count",

    "range.title": "Delay range",
    "range.shipments": "Shipments in range",
    "range.pctDelayed": "of all delayed",
    "range.pctTotal": "of total",

    "table.lanes": "Top Lanes (Origin → Destination)",
    "table.lane": "Lane",
    "table.countryRank": "Country Ranking",
    "table.cityDetail": "City Breakdown",
    "table.city": "City",
    "table.selectCountry": "Select a country on the map",
    "table.rank": "#",
    "table.country": "Country",
    "table.continent": "Continent",
    "table.shipments": "Shipments",
    "table.delayRate": "Delay Rate",
    "table.otifShort": "OTIF",
    "table.ontimeShort": "On-time",
    "table.ontimeCol": "On-time?",
    "table.revenue": "Revenue",
    "table.status": "Status",
    "table.carrier": "Carrier",
    "table.expected": "Expected",
    "table.actual": "Actual",
    "table.delay": "Delay",
    "table.reason": "Reason",
    "table.shipDate": "Ship Date",
    "table.atRisk": "At-Risk In-Transit",
    "table.daysLeft": "Days Left",
    "table.risk": "Risk",
    "table.exceptions": "Exception Shipments",
    "table.search": "Search ID / carrier / country...",
    "table.all": "All Shipments (latest 120)",
    "table.dataQuality": "Data Quality",

    "report.empty": "Generate a report to see the conclusions.",
    "report.volume": "Volume",
    "report.quality": "Quality",
    "report.p90": "Tail Risk",
    "report.eta": "ETA Accuracy",
    "report.worstCarrier": "Worst Carrier",
    "report.worstCountry": "Highest-Risk Country",
    "report.topReason": "Top Delay Reason",
    "report.range": "Delay Range",
    "report.worstLane": "Worst Lane",
    "report.atRisk": "At-Risk",
    "report.nextSteps": "Next Steps",
    "report.disclaimer": "> Correlational statistics only; not causal conclusions.",
    "report.step1": "Review {carrier} performance ({rate}% delay over {count} shipments)",
    "report.step2": "Investigate {country} customs & delivery (delay rate {rate}%)",
    "report.step3": "Set alerts for shipments delayed ≥ 5 days",
    "report.step4": "Prioritize {count} at-risk in-transit shipments",
    "report.step5": "Review lane {lane} for recurring issues ({rate}% delay)",

    "cost.lineHaul": "Line Haul",
    "cost.fuel": "Fuel",
    "cost.accessorial": "Accessorial",
    "cost.detention": "Detention",
    "cost.avgPerShipment": "Avg per Shipment",

    "map.reset": "Reset",
    "map.detail.shipments": "Shipments",
    "map.detail.delay": "Delay Rate",
    "map.detail.revenue": "Revenue",
    "map.detail.otif": "OTIF",
    "map.legend.high": "High",
    "map.legend.low": "Low",
    "map.focus": "Focus",
    "map.focusHint": "location total · ignores active filters",
    "map.loading": "Loading details…",
    "map.outsideFilter": "(outside filter)",
    "map.mode.country": "Country",
    "map.mode.city": "City",
    "map.hintCountry": "Click a country to see data",
    "map.hintCity": "Click a city point to see data",

    "chat.title": "AI Assistant",
    "chat.hint": "Ask anything about the current data",
    "chat.placeholder": "e.g. Which carrier is worst?",
    "chat.welcome": "Hi, I'm RouteMind Assistant. Ask about delays, carrier performance, country risks, revenue, or costs.",
    "chat.fallback": "I'm not sure what you mean. Try one of these:",
    "chat.noData": "Generate a report first so I can analyze the data.",

    "ws.save": "Save",
    "ws.versions": "Versions",
    "ws.share": "Share",
    "ws.exportCsv": "CSV",
    "ws.exportPdf": "PDF",
    "ws.unsaved": "Unsaved",
    "ws.saved": "Saved",

    "settings.title": "Settings",
    "settings.sub": "Manage your account and preferences.",
    "settings.profile": "Profile",
    "settings.username": "Username",
    "settings.email": "Email",
    "settings.role": "Role",
    "settings.changePw": "Change Password",
    "settings.currentPw": "Current password",
    "settings.newPw": "New password",
    "settings.confirmPw": "Confirm new password",
    "settings.updatePw": "Update Password",
    "settings.admin": "Admin",
    "settings.user": "User",
    "settings.strength": "Strength",
    "settings.weak": "Weak",
    "settings.fair": "Fair",
    "settings.good": "Good",
    "settings.strong": "Strong",

    "admin.title": "Admin Console",
    "admin.sub": "Manage users, dataset, and audit trail.",
    "admin.users": "Users",
    "admin.projects": "Projects",
    "admin.colUser": "Username",
    "admin.colEmail": "Email",
    "admin.colRole": "Role",
    "admin.colStatus": "Status",
    "admin.colActions": "Actions",
    "admin.dataset": "Dataset",
    "admin.datasetHelp": "Upload a CSV to replace the current shipment dataset.",
    "admin.upload": "Upload & Replace",
    "admin.simulate": "Simulate +500 rows",
    "admin.audit": "Audit Log",
    "admin.auditHint": "Last 100 events",
    "admin.colTime": "Time",
    "admin.colUserShort": "User",
    "admin.colAction": "Action",
    "admin.colDetail": "Detail",
    "admin.active": "Active",
    "admin.disabled": "Disabled",
    "admin.enable": "Enable",
    "admin.disable": "Disable",
    "admin.makeAdmin": "Make Admin",
    "admin.revokeAdmin": "Revoke",
    "admin.delete": "Delete",
    "admin.prev": "Prev",
    "admin.next": "Next",
    "admin.roleAdmin": "ADMIN",
    "admin.roleUser": "USER",

    "common.refresh": "Refresh",
    "common.na": "N/A",
    "common.save": "Save",
    "common.close": "Close",

    "toast.readonly": "Read-only view",
    "toast.noProject": "No report loaded",
    "toast.saveFirst": "Save the report first",
    "toast.notFound": "Not found",
    "toast.deleted": "Deleted",
    "toast.invalidShare": "Invalid share link",
    "toast.selectCsv": "Select a CSV file first",
    "toast.csvImported": "CSV imported",
    "toast.csvUploadFailed": "Upload failed: ",
    "toast.adminFailed": "Failed to load admin data",
    "toast.computeFailed": "Compute failed",
    "toast.passwordMismatch": "Passwords do not match",
    "toast.passwordWeak": "Password does not meet requirements",
    "toast.passwordUpdated": "Password updated",
    "toast.missingFields": "Please fill in all fields",
    "toast.copied": "Copied: ",
    "toast.saved": "Saved",
    "toast.workspaceReady": "Report ready",
    "toast.genFailed": "Generation failed: ",
    "toast.newRows": "new rows added",
    "toast.deleteProject": "Delete this analysis?",
    "toast.deleteUser": "Delete this user?",
    "toast.selectPrompt": "Please enter an analysis goal",
    "toast.versionRestored": "Version restored",
    "toast.noVersions": "No versions yet",
    "toast.unsavedWarning": "You have unsaved changes. Leave anyway?",
    "toast.cityModeHint": "Switch to City mode to click city points",

    "qa.opt.delay": "Delay situation",
    "qa.opt.carrier": "Worst carrier",
    "qa.opt.country": "Highest-delay country",
    "qa.opt.revenue": "Total revenue",
    "qa.opt.cost": "Cost breakdown",
    "qa.opt.otif": "OTIF performance",
    "qa.opt.atrisk": "At-risk shipments",
    "qa.opt.optimize": "How to optimize",
    "qa.delay": "Delay rate **{delay_rate}%** ({delayed} of {total} shipments). Average delay **{avg} days**, P90 **{p90} days**. Top reason: **{reason}**.",
    "qa.carrier": "Worst carrier: **{worst}** ({worstRate}% delay). Best: **{best}** ({bestRate}%).",
    "qa.country": "Highest-delay country: **{name}** ({rate}% delay, {count} shipments).",
    "qa.revenue": "Total shipping revenue: **${revenue}**. Avg cost/shipment: **${avgCost}**.",
    "qa.cost": "Line haul **${lineHaul}** · Fuel **${fuel}** · Accessorial **${accessorial}** · Detention **${detention}**.",
    "qa.otif": "OTIF rate is **{rate}%** ({count} shipments on-time + in-full out of {delivered} delivered).",
    "qa.atrisk": "There are **{count}** in-transit shipments at risk of missing their SLA.",
    "qa.optimize": "Recommendations:\n1. Review **{worstCarrier}** performance ({worstCarrierRate}% delay)\n2. Focus on **{worstCountry}** clearance & delivery ({worstCountryRate}% delay)\n3. Set alerts for shipments delayed ≥ 5 days\n4. Address top reason: **{topReason}**",
  },
  zh: {
    "brand.sub": "AI 物流智能工作室",
    "nav.home": "首页",
    "nav.dashboard": "数据面板",
    "nav.database": "数据库",
    "nav.settings": "设置",
    "nav.admin": "管理员",
    "nav.logout": "退出登录",
    "nav.ai": "AI 助手",
    "shared.note": "只读分享视图",
    "topbar.fresh": "加载中…",
    "topbar.waiting": "等待实时更新",
    "topbar.freshAt": "更新于 {ago}",
    "topbar.freshSec": "{n} 秒前",
    "topbar.freshMin": "{n} 分钟前",
    "topbar.freshHour": "{n} 小时前",

    "tabs.report": "报告",
    "tabs.data": "数据",

    "home.greeting": "你想调查什么？",
    "home.sub": "用自然语言描述你的物流分析问题。",
    "home.placeholder": "例如：分析最近 30 天的物流延误情况，找出延误最多的承运商，比较不同国家的表现。",
    "home.templates": "快捷示例：",
    "home.generate": "生成报告",
    "home.newAnalysis": "新建分析",

    "brand.sub": "AI 物流智能工作室",
    "builderHero.title": "想做个小应用？试试 App Builder",
    "builderHero.subtitle": "用一句话描述需求，AI 实时生成完整可运行的 HTML。对话即迭代，版本自动存档。",
    "builderHero.cta": "打开 App Builder",

    "history.title": "项目",
    "history.empty": "暂无项目。",
    "history.loading": "正在加载…",
    "history.openFailed": "打开失败：",
    "history.today": "今天",
    "history.yesterday": "昨天",
    "history.week": "本周",
    "history.older": "更早",

    "tpl.delay.title": "物流延误",
    "tpl.carrier.title": "承运商表现",
    "tpl.country.title": "国家风险",
    "tpl.transit.title": "在途风险",

    "gen.s1": "理解需求",
    "gen.s2": "选择指标",
    "gen.s3": "准备报告",
    "gen.s4": "准备就绪",

    "filter.date": "时间范围",
    "filter.d7": "最近 7 天",
    "filter.d30": "最近 30 天",
    "filter.d60": "最近 60 天",
    "filter.d90": "最近 90 天",
    "filter.d120": "最近 120 天",
    "filter.carrier": "承运商",
    "filter.priority": "优先级",
    "filter.continent": "洲",
    "filter.country": "国家",
    "filter.statusLabel": "状态",
    "filter.search": "搜索",
    "filter.all": "全部承运商",
    "filter.allPriority": "全部优先级",
    "filter.allContinent": "全部洲",
    "filter.allCountry": "全部国家",
    "filter.allStatus": "全部状态",
    "filter.status.delivered": "已送达",
    "filter.status.transit": "在途",
    "filter.status.exception": "异常",
    "filter.minDelay": "最低延误天数",
    "filter.maxDelay": "最高延误天数",
    "filter.none": "不限",

    "loading.prepare": "正在准备请求",
    "loading.received": "数据已接收",
    "loading.kpi": "计算关键指标",
    "loading.charts": "渲染图表",
    "loading.tables": "渲染表格",
    "loading.map": "加载地图",
    "loading.done": "完成",

    "data.total": "总订单",
    "data.delivered": "已送达",
    "data.delayed": "延误",
    "data.inTransit": "在途",
    "data.exception": "异常",
    "table.priority": "优先级",

    "dq.total": "总记录",
    "dq.missingExpected": "缺失预计日期",
    "dq.missingActual": "缺失实际日期",
    "dq.quality": "数据质量",

    "dashboard.title": "数据面板",
    "dashboard.sub": "当前订单数据集概览。",
    "dashboard.total": "总订单量",
    "dashboard.lastUpdated": "最后更新",
    "dashboard.quality": "数据质量",
    "dashboard.missing": "缺失字段",
    "dashboard.statusDist": "状态分布",
    "dashboard.carrierDist": "按承运商",
    "dashboard.continentDist": "按洲",
    "dashboard.qualityDetail": "数据质量明细",
    "dashboard.quickActions": "管理员快捷操作",
    "dashboard.adminOnly": "仅管理员可用",
    "dashboard.goAdmin": "前往管理后台",
    "dashboard.missingExpected": "缺失预计日期",
    "dashboard.missingActual": "缺失实际日期",
    "dashboard.invalidStatus": "无效状态",
    "dashboard.validRatio": "有效占比",

    "database.title": "数据库",
    "database.sub": "浏览当前订单数据集。",
    "database.searchPlaceholder": "按 ID / 承运商 / 城市搜索...",
    "database.actions": "操作",
    "database.edit": "编辑",
    "database.delete": "删除",
    "database.editTitle": "编辑订单",
    "database.cancel": "取消",
    "database.saveChanges": "保存修改",
    "database.perPage": "每页：",
    "database.total": "共 {n} 条",
    "database.saveSuccess": "订单已更新",
    "database.saveFailed": "保存失败：",
    "database.deleteConfirm": "确定删除此订单？",
    "database.deleteSuccess": "订单已删除",
    "database.deleteFailed": "删除失败：",
    "database.failedLoad": "加载数据库失败",
    "database.readonlyHint": "只读。仅管理员可编辑。",

    "ch.summary.title": "执行摘要",
    "ch.summary.sub": "关键指标一览",
    "ch.trend.title": "趋势与结构",
    "ch.trend.sub": "整体趋势如何？",
    "ch.carrier.title": "承运商与线路表现",
    "ch.carrier.sub": "谁表现好，谁表现差",
    "ch.geo.title": "地理风险",
    "ch.geo.sub": "运营热点在哪里？",
    "ch.exception.title": "异常与风险订单",
    "ch.exception.sub": "哪些需要立即关注？",
    "ch.cost.title": "成本与效率",
    "ch.cost.sub": "钱花在哪里了？",
    "ch.conclusion.title": "结论与建议",
    "ch.conclusion.sub": "发现、证据与下一步",
    "ch.appendix.title": "附录",
    "ch.appendix.sub": "全部订单与数据质量",

    "kpi.total": "订单量",
    "kpi.totalHint": "筛选后订单",
    "kpi.otif": "OTIF",
    "kpi.otifHint": "准时且完整 / 已送达",
    "kpi.delay": "延误率",
    "kpi.delayHint": "延误包裹 / 已送达",
    "kpi.eta": "ETA 准确率 (±1天)",
    "kpi.etaHint": "ETA 偏差 ≤1 天 / 已送达",
    "kpi.p90": "P90 延误天数",
    "kpi.p90Hint": "最差 10% 的延误天数",
    "kpi.revenue": "运费收入",
    "kpi.revenueHint": "总运输成本",

    "chart.trend": "延误趋势",
    "chart.trendNote": "趋势不受延误区间筛选影响",
    "chart.status": "状态分布",
    "chart.statusNote": "不受延误区间筛选影响",
    "chart.carrier": "承运商表现",
    "chart.reasons": "延误原因",
    "chart.m.delay": "延误率",
    "chart.m.otif": "OTIF",
    "chart.m.cost": "每单成本",
    "chart.m.volume": "订单量",
    "chart.line": "折线",
    "chart.bar": "柱状",
    "chart.map": "全球风险地图",
    "chart.mapHint": "点击国家查看详情",
    "chart.mapHintCountry": "当前展示该国家内城市",
    "chart.costBreakdown": "成本拆解",
    "chart.costVsService": "成本 vs 服务",
    "chart.costVsServiceNote": "X = 每单成本 · Y = 延误率 · 气泡大小 = 订单量 · 左下角最优",
    "chart.costLegend": "成本 ($)",
    "chart.serviceLegend": "延误率 (%)",

    "trend.mode.rate": "延误率",
    "trend.mode.count": "延误数量",

    "range.title": "延误区间",
    "range.shipments": "区间订单",
    "range.pctDelayed": "占所有延误",
    "range.pctTotal": "占总订单",

    "table.lanes": "热门线路（起点 → 终点）",
    "table.lane": "线路",
    "table.countryRank": "国家排名",
    "table.cityDetail": "城市明细",
    "table.city": "城市",
    "table.selectCountry": "请在地图上选择国家",
    "table.rank": "排名",
    "table.country": "国家",
    "table.continent": "洲",
    "table.shipments": "订单量",
    "table.delayRate": "延误率",
    "table.otifShort": "OTIF",
    "table.ontimeShort": "准时率",
    "table.ontimeCol": "是否准时",
    "table.revenue": "收入",
    "table.status": "状态",
    "table.carrier": "承运商",
    "table.expected": "预计送达",
    "table.actual": "实际送达",
    "table.delay": "延误",
    "table.reason": "原因",
    "table.shipDate": "发货日期",
    "table.atRisk": "在途风险订单",
    "table.daysLeft": "剩余天数",
    "table.risk": "风险",
    "table.exceptions": "异常订单",
    "table.search": "按 ID / 承运商 / 国家搜索...",
    "table.all": "全部订单（最新 120）",
    "table.dataQuality": "数据质量",

    "report.empty": "生成报告后显示结论。",
    "report.volume": "订单规模",
    "report.quality": "服务质量",
    "report.p90": "尾部风险",
    "report.eta": "ETA 准确率",
    "report.worstCarrier": "最差承运商",
    "report.worstCountry": "高风险国家",
    "report.topReason": "主要延误原因",
    "report.range": "延误区间",
    "report.worstLane": "最差线路",
    "report.atRisk": "在途风险",
    "report.nextSteps": "下一步建议",
    "report.disclaimer": "> 以上为统计描述与相关性提示，不构成因果结论。",
    "report.step1": "审查 {carrier} 的承运表现（延误率 {rate}%，共 {count} 单）",
    "report.step2": "核查 {country} 的清关与配送（延误率 {rate}%）",
    "report.step3": "对延误 ≥ 5 天的订单建立预警",
    "report.step4": "优先处理 {count} 个在途风险订单",
    "report.step5": "复核线路 {lane} 的重复性问题（延误率 {rate}%）",

    "cost.lineHaul": "干线运费",
    "cost.fuel": "燃油附加",
    "cost.accessorial": "附加费",
    "cost.detention": "滞留费",
    "cost.avgPerShipment": "每单平均成本",

    "map.reset": "重置",
    "map.detail.shipments": "订单量",
    "map.detail.delay": "延误率",
    "map.detail.revenue": "收入",
    "map.detail.otif": "OTIF",
    "map.legend.high": "高",
    "map.legend.low": "低",
    "map.focus": "聚焦",
    "map.focusHint": "该位置全量历史 · 忽略当前筛选",
    "map.loading": "加载详情中…",
    "map.outsideFilter": "（筛选外）",
    "map.mode.country": "国家",
    "map.mode.city": "地区",
    "map.hintCountry": "点击国家查看数据",
    "map.hintCity": "点击地区点查看数据",

    "chat.title": "AI 助手",
    "chat.hint": "针对当前数据随时提问",
    "chat.placeholder": "例如：哪个承运商最差？",
    "chat.welcome": "你好，我是 RouteMind 助手。针对当前数据，你可以问我延误情况、承运商表现、国家风险、收入或成本。",
    "chat.fallback": "我不太确定你想问什么。可以试试以下问题：",
    "chat.noData": "请先生成报告，我才能分析数据。",

    "ws.save": "保存",
    "ws.versions": "版本历史",
    "ws.share": "分享",
    "ws.exportCsv": "CSV",
    "ws.exportPdf": "PDF",
    "ws.unsaved": "未保存",
    "ws.saved": "已保存",

    "settings.title": "设置",
    "settings.sub": "管理你的账户与偏好。",
    "settings.profile": "个人资料",
    "settings.username": "用户名",
    "settings.email": "邮箱",
    "settings.role": "角色",
    "settings.changePw": "修改密码",
    "settings.currentPw": "当前密码",
    "settings.newPw": "新密码",
    "settings.confirmPw": "确认新密码",
    "settings.updatePw": "更新密码",
    "settings.admin": "管理员",
    "settings.user": "用户",
    "settings.strength": "强度",
    "settings.weak": "弱",
    "settings.fair": "一般",
    "settings.good": "良好",
    "settings.strong": "强",

    "admin.title": "管理后台",
    "admin.sub": "管理用户、数据集与审计日志。",
    "admin.users": "用户",
    "admin.projects": "项目",
    "admin.colUser": "用户名",
    "admin.colEmail": "邮箱",
    "admin.colRole": "角色",
    "admin.colStatus": "状态",
    "admin.colActions": "操作",
    "admin.dataset": "数据集",
    "admin.datasetHelp": "上传 CSV 替换当前订单数据集。",
    "admin.upload": "上传并替换",
    "admin.simulate": "模拟 +500 条",
    "admin.audit": "审计日志",
    "admin.auditHint": "最近 100 条事件",
    "admin.colTime": "时间",
    "admin.colUserShort": "用户",
    "admin.colAction": "操作",
    "admin.colDetail": "详情",
    "admin.active": "启用",
    "admin.disabled": "已禁用",
    "admin.enable": "启用",
    "admin.disable": "禁用",
    "admin.makeAdmin": "设为管理员",
    "admin.revokeAdmin": "撤销管理员",
    "admin.delete": "删除",
    "admin.prev": "上一页",
    "admin.next": "下一页",
    "admin.roleAdmin": "管理员",
    "admin.roleUser": "用户",

    "common.refresh": "刷新",
    "common.na": "N/A",
    "common.save": "保存",
    "common.close": "关闭",

    "toast.readonly": "只读模式",
    "toast.noProject": "未加载报告",
    "toast.saveFirst": "请先保存报告",
    "toast.notFound": "未找到",
    "toast.deleted": "已删除",
    "toast.invalidShare": "分享链接无效",
    "toast.selectCsv": "请先选择 CSV 文件",
    "toast.csvImported": "CSV 已导入",
    "toast.csvUploadFailed": "上传失败：",
    "toast.adminFailed": "加载管理数据失败",
    "toast.computeFailed": "计算失败",
    "toast.passwordMismatch": "两次密码不一致",
    "toast.passwordWeak": "密码不符合要求",
    "toast.passwordUpdated": "密码已更新",
    "toast.missingFields": "请填写所有字段",
    "toast.copied": "已复制：",
    "toast.saved": "已保存",
    "toast.workspaceReady": "报告已生成",
    "toast.genFailed": "生成失败：",
    "toast.newRows": "条新数据已添加",
    "toast.deleteProject": "确定删除此分析？",
    "toast.deleteUser": "确定删除此用户？",
    "toast.selectPrompt": "请输入分析目标",
    "toast.versionRestored": "版本已恢复",
    "toast.noVersions": "暂无历史版本",
    "toast.unsavedWarning": "有未保存的修改，确定离开？",
    "toast.cityModeHint": "请切换到「地区」模式再点击城市点",

    "qa.opt.delay": "延误情况",
    "qa.opt.carrier": "最差承运商",
    "qa.opt.country": "延误率最高国家",
    "qa.opt.revenue": "总收入",
    "qa.opt.cost": "成本构成",
    "qa.opt.otif": "OTIF 表现",
    "qa.opt.atrisk": "在途风险订单",
    "qa.opt.optimize": "如何优化",
    "qa.delay": "当前延误率 **{delay_rate}%**（共 {total} 个包裹）。平均延误 **{avg} 天**，P90 为 **{p90} 天**。主要延误原因：**{reason}**。",
    "qa.carrier": "表现最差的承运商：**{worst}**（延误率 {worstRate}%）。表现最好：**{best}**（{bestRate}%）。",
    "qa.country": "延误率最高的国家：**{name}**（{rate}%，{count} 个包裹）。",
    "qa.revenue": "当前筛选范围内总收入：**${revenue}**。每单平均成本：**${avgCost}**。",
    "qa.cost": "干线运费 **${lineHaul}** · 燃油附加 **${fuel}** · 附加费 **${accessorial}** · 滞留费 **${detention}**。",
    "qa.otif": "OTIF 达成率 **{rate}%**（{delivered} 个已送达订单中 {count} 个准时且完整）。",
    "qa.atrisk": "当前有 **{count}** 个在途订单存在 SLA 违约风险。",
    "qa.optimize": "优化建议：\n1. 审查 **{worstCarrier}** 的承运表现（延误率 {worstCarrierRate}%）\n2. 关注 **{worstCountry}** 的清关与配送（延误率 {worstCountryRate}%）\n3. 对延误 ≥ 5 天的订单建立预警\n4. 优先处理主要延误原因：**{topReason}**",
  }
};

// =============================================================
// Value translations
// =============================================================
const VALUE_TRANSLATIONS = {
  carrier: {
    "SwiftLogistics": "迅捷物流",
    "GlobalFreight": "环球货运",
    "ExpressLine": "速达航线",
    "OceanBridge": "海洋桥运",
    "SkyCargo": "空天货运",
  },
  continent: {
    "Asia": "亚洲", "Europe": "欧洲", "North America": "北美洲",
    "Middle East": "中东", "Oceania": "大洋洲", "Unknown": "未知",
  },
  country: {
    "United States": "美国", "Canada": "加拿大", "Mexico": "墨西哥",
    "China": "中国", "Japan": "日本", "South Korea": "韩国",
    "Singapore": "新加坡", "Vietnam": "越南", "India": "印度",
    "Germany": "德国", "Netherlands": "荷兰", "United Kingdom": "英国",
    "France": "法国", "United Arab Emirates": "阿联酋",
    "Saudi Arabia": "沙特阿拉伯", "Australia": "澳大利亚",
    "Unknown": "未知",
  },
  status: { "Delivered": "已送达", "In Transit": "在途", "Exception": "异常" },
  reason: {
    "Weather": "天气", "Customs Clearance": "清关",
    "Capacity Constraint": "运力不足", "Address Issue": "地址问题",
    "Unknown": "未知", "Carrier Delay": "承运商延误", "Port Congestion": "港口拥堵",
  },
  priority: { "Standard": "标准", "Express": "加急", "Critical": "紧急" },
  city: {
    "Los Angeles": "洛杉矶", "New York": "纽约", "Chicago": "芝加哥",
    "Houston": "休斯顿", "Seattle": "西雅图", "Miami": "迈阿密",
    "Toronto": "多伦多", "Vancouver": "温哥华", "Montreal": "蒙特利尔",
    "Calgary": "卡尔加里", "Mexico City": "墨西哥城",
    "Guadalajara": "瓜达拉哈拉", "Monterrey": "蒙特雷",
    "Shanghai": "上海", "Shenzhen": "深圳", "Guangzhou": "广州",
    "Ningbo": "宁波", "Hong Kong": "香港", "Qingdao": "青岛",
    "Tianjin": "天津", "Tokyo": "东京", "Yokohama": "横滨",
    "Osaka": "大阪", "Busan": "釜山", "Seoul": "首尔",
    "Incheon": "仁川", "Singapore": "新加坡",
    "Ho Chi Minh": "胡志明市", "Hanoi": "河内", "Haiphong": "海防",
    "Mumbai": "孟买", "Delhi": "德里", "Chennai": "金奈",
    "Hamburg": "汉堡", "Berlin": "柏林", "Munich": "慕尼黑",
    "Frankfurt": "法兰克福", "Rotterdam": "鹿特丹",
    "Amsterdam": "阿姆斯特丹", "London": "伦敦",
    "Manchester": "曼彻斯特", "Paris": "巴黎", "Marseille": "马赛",
    "Dubai": "迪拜", "Abu Dhabi": "阿布扎比",
    "Riyadh": "利雅得", "Jeddah": "吉达",
    "Sydney": "悉尼", "Melbourne": "墨尔本", "Perth": "珀斯",
    "Unknown": "未知",
  },
};

const TITLE_TRANSLATIONS = {
  "Shipment Delay Analysis": "物流延误分析",
  "Carrier Performance Analysis": "承运商表现分析",
  "Country Risk Analysis": "国家风险分析",
  "In-Transit Risk Analysis": "在途风险分析",
  "Lane Performance Analysis": "线路表现分析",
  "Untitled": "未命名",
};

const ZH_TO_EN_COUNTRY = Object.fromEntries(
  Object.entries(VALUE_TRANSLATIONS.country).map(([en, zh]) => [zh, en])
);

// ECharts GeoJSON 里可能出现的国家名别名
const COUNTRY_ALIASES = {
  "USA": "United States",
  "US": "United States",
  "United States of America": "United States",
  "U.S.": "United States",
  "UK": "United Kingdom",
  "Great Britain": "United Kingdom",
  "U.K.": "United Kingdom",
  "UAE": "United Arab Emirates",
  "Korea": "South Korea",
  "Republic of Korea": "South Korea",
  "Dem. Rep. Korea": "North Korea",
  "Dem. Rep. Congo": "DR Congo",
  "Cote d'Ivoire": "Ivory Coast",
  "Côte d'Ivoire": "Ivory Coast",
};

const DEFAULT_COUNTRY_CONTINENTS = {
  "United States": "North America", "Canada": "North America",
  "Mexico": "North America", "China": "Asia", "Japan": "Asia",
  "South Korea": "Asia", "Singapore": "Asia", "Vietnam": "Asia",
  "India": "Asia", "Germany": "Europe", "Netherlands": "Europe",
  "United Kingdom": "Europe", "France": "Europe",
  "United Arab Emirates": "Middle East", "Saudi Arabia": "Middle East",
  "Australia": "Oceania",
};

// Zoom thresholds for city visibility
const ZOOM_DETAIL_THRESHOLD = 2.0;
const ZOOM_LABEL_THRESHOLD = 3.0;

// =============================================================
// State
// =============================================================
const state = {
  lang: localStorage.getItem("routemind_lang") || "en",
  theme: localStorage.getItem("routemind_theme") || "dark",
  activeReportTab: localStorage.getItem("routemind_report_tab") || "report",
  sidebarState: localStorage.getItem("routemind_sidebar") || "open",
  mapMode: localStorage.getItem("routemind_map_mode") || "country",
  currentProjectId: null,
  currentTitle: "",
  config: null,
  filters: { date_range_days: 30, carrier: "", priority: "", continent: "",
             country: "", min_delay_days: "", max_delay_days: "" },
  lastData: null,
  mapData: null,
  mapLevel: "world",
  mapSelectedCountry: "",
  mapSelectedContinent: "",
  mapFocusedLocation: null,
  mapCurrentZoom: 1.2,
  mapZoomLevel: "world",
  readonly: false,
  trendType: "line",
  trendMode: "delay_rate",
  carrierMetric: "delay_rate",
  history: [],
  historyError: false,
  worldMapChart: null,
  worldMapReady: false,
  worldMapPromise: null,
  computeSeq: 0,
  _focusSeq: 0,
  _chatHistory: [],
  _lastIntent: null,
  _filterOptions: { carriers: [], countries: [], continents: [], priorities: [],
                     total: 0, last_updated: null,
                     continent_views: {}, country_views: {},
                     country_continents: {}, all_cities: [] },
  _countryToContinent: { ...DEFAULT_COUNTRY_CONTINENTS },
  _appendixOpen: false,
  _isDirty: false,
  _loaderProgress: 0,
  _loaderTarget: 0,
  _loaderTimer: null,
  dbPage: 1,
  dbPerPage: 50,
  dbFilters: { carrier: "", country: "", status: "", search: "" },
  dbData: null,
  editingShipment: null,
  dashboardData: null,
};

let charts = { trend: null, status: null, carrier: null, reasons: null,
               cost: null, scatter: null,
               dashStatus: null, dashCarrier: null, dashContinent: null };

// =============================================================
// Utils
// =============================================================
const $ = (id) => document.getElementById(id);
function t(key) {
  return (I18N[state.lang] && I18N[state.lang][key]) || I18N.en[key] || key;
}
function fmt(str, vars) {
  return str.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "");
}
function tv(type, value) {
  if (state.lang === "en") return value;
  return (VALUE_TRANSLATIONS[type] && VALUE_TRANSLATIONS[type][value]) || value || "";
}
function translateTitle(title) {
  if (state.lang === "zh") return TITLE_TRANSLATIONS[title] || title;
  return title;
}
function translateLane(lane) {
  if (!lane) return "";
  return lane.split(" → ").map((p) => tv("country", p.trim())).join(" → ");
}
function escapeHtml(s) {
  return (s == null ? "" : String(s))
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function fmtCurrency(v) {
  if (v == null) return "—";
  if (typeof Intl !== "undefined" && Intl.NumberFormat) {
    return new Intl.NumberFormat("en-US", {
      style: "currency", currency: "USD",
      notation: "compact", maximumFractionDigits: 1,
    }).format(v);
  }
  return "$" + Math.round(v).toLocaleString();
}
function fmtFullCurrency(v) {
  if (v == null) return "—";
  return "$" + Number(v).toLocaleString(undefined, {
    minimumFractionDigits: 0, maximumFractionDigits: 2,
  });
}
function fmtNum(v) { return v == null ? "—" : Number(v).toLocaleString(); }
function relativeTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  const secs = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000));
  if (secs < 60) return fmt(t("topbar.freshSec"), { n: secs });
  if (secs < 3600) return fmt(t("topbar.freshMin"), { n: Math.floor(secs / 60) });
  return fmt(t("topbar.freshHour"), { n: Math.floor(secs / 3600) });
}

function findWorstCarrier(carriers) {
  const valid = (carriers || []).filter((c) => c.delay_rate != null && c.total_shipments >= 10);
  if (!valid.length) return null;
  return valid.reduce((a, b) => (a.delay_rate > b.delay_rate ? a : b));
}
function findBestCarrier(carriers) {
  const valid = (carriers || []).filter((c) => c.delay_rate != null && c.total_shipments >= 10);
  if (!valid.length) return null;
  return valid.reduce((a, b) => (a.delay_rate < b.delay_rate ? a : b));
}
function findWorstLane(lanes) {
  const valid = (lanes || []).filter((l) => l.delay_rate != null && l.total_shipments >= 10);
  if (!valid.length) return null;
  return valid.reduce((a, b) => (a.delay_rate > b.delay_rate ? a : b));
}

function toast(msg, type = "") {
  const el = $("toast");
  if (!el) return;
  el.textContent = msg;
  el.className = `toast show ${type}`;
  clearTimeout(el._tid);
  el._tid = setTimeout(() => (el.className = "toast"), 2600);
}
function toastT(key, extra = "", type = "") {
  toast(t(key) + (extra || ""), type);
}

function debounce(fn, ms) {
  let tid;
  return (...args) => {
    clearTimeout(tid);
    tid = setTimeout(() => fn(...args), ms);
  };
}
function throttle(fn, ms) {
  let last = 0, timer = null;
  return (...args) => {
    const now = Date.now();
    if (now - last < ms) {
      clearTimeout(timer);
      timer = setTimeout(() => { last = now; fn(...args); }, ms - (now - last));
      return;
    }
    last = now;
    fn(...args);
  };
}

// =============================================================
// Sidebar
// =============================================================
function toggleSidebar() {
  const sb = $("app-sidebar");
  if (!sb) return;
  sb.classList.toggle("collapsed");
  const isCollapsed = sb.classList.contains("collapsed");
  state.sidebarState = isCollapsed ? "collapsed" : "open";
  localStorage.setItem("routemind_sidebar", state.sidebarState);
  if (window.lucide) lucide.createIcons();
  setTimeout(() => {
    if (state.worldMapChart && !state.worldMapChart.isDisposed()) {
      state.worldMapChart.resize();
    }
  }, 300);
}

function newAnalysis() {
  switchView("home");
  setTimeout(() => $("prompt-input")?.focus(), 100);
}

// =============================================================
// User menu
// =============================================================
function toggleUserMenu(e) {
  e?.stopPropagation();
  const menu = $("user-menu");
  if (!menu) return;
  menu.classList.toggle("hidden");
}
function closeUserMenu() {
  $("user-menu")?.classList.add("hidden");
}
function goToSettings() {
  closeUserMenu();
  switchView("settings");
}

// =============================================================
// Loader
// =============================================================
function _renderLoaderUI() {
  const pct = state._loaderProgress;
  const fill = $("loader-road-fill");
  const truck = $("loader-truck");
  const pctEl = $("loader-pct");
  if (fill) fill.style.width = pct + "%";
  if (truck) truck.style.left = (4 + pct * 0.92) + "%";
  if (pctEl) pctEl.textContent = Math.round(pct) + "%";
}
function _loaderTick() {
  const target = state._loaderTarget;
  const current = state._loaderProgress;
  if (current >= target - 0.3) {
    state._loaderProgress = target;
    _renderLoaderUI();
    return;
  }
  const diff = target - current;
  const step = Math.max(0.25, diff * 0.08);
  state._loaderProgress = Math.min(target, current + step);
  _renderLoaderUI();
}
function showLoading() {
  const ov = $("loading-overlay");
  if (!ov) return;
  ov.classList.remove("hidden");
  state._loaderProgress = 0;
  state._loaderTarget = 8;
  _renderLoaderUI();
  const label = $("loader-stage-text");
  if (label) label.textContent = t("loading.prepare");
  if (state._loaderTimer) clearInterval(state._loaderTimer);
  state._loaderTimer = setInterval(_loaderTick, 60);
}
function setLoaderStage(pct, key) {
  state._loaderTarget = Math.max(state._loaderTarget, pct);
  const label = $("loader-stage-text");
  if (label) label.textContent = t(key);
}
function finishLoading() {
  state._loaderTarget = 100;
  setTimeout(() => {
    if (state._loaderTimer) { clearInterval(state._loaderTimer); state._loaderTimer = null; }
    $("loading-overlay")?.classList.add("hidden");
  }, 420);
}
function hideLoading() {
  if (state._loaderTimer) { clearInterval(state._loaderTimer); state._loaderTimer = null; }
  $("loading-overlay")?.classList.add("hidden");
}

// =============================================================
// i18n & theme
// =============================================================
function applyLang(lang) {
  state.lang = lang;
  localStorage.setItem("routemind_lang", lang);
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  $("lang-label").textContent = lang === "zh" ? "中" : "EN";

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });

  if (state.currentTitle) {
    $("rp-title").textContent = translateTitle(state.currentTitle);
  }
  if (state._filterOptions.total != null) {
    $("data-source-label").textContent = state.lang === "zh"
      ? `合成数据 · ${state._filterOptions.total.toLocaleString()} 条记录`
      : `Synthetic Data · ${state._filterOptions.total.toLocaleString()} records`;
  }
  updateFreshness();

  if (state.lastData) {
    renderKPIs(state.lastData.metrics);
    renderRangeBanner(state.lastData.range_stats);
    renderSummaryLine(state.lastData.metrics);
    renderCharts();
    renderLanesTable();
    renderCountriesTable();
    renderAtRiskTable();
    renderExceptions();
    renderAllShipments();
    renderReport(state.lastData);
    renderCostSummary(state.lastData.cost_breakdown, state.lastData.metrics);
    renderDataQuality(state.lastData.data_quality);
    renderDataTables();
    if (state.mapData) renderWorldMap(state.mapData);
    if (state.mapFocusedLocation) {
      const fl = state.mapFocusedLocation;
      fetchAndRenderFocus(fl.type, fl.name, true);
    }
    if ($("chat-log") && $("chat-log").children.length === 0) {
      renderChatOptions(defaultOptions());
    }
  }
  populateFilterSelects();
  populateDbFilterSelects();
  loadHistory();
  updateSettingsLabels();
  updateSettingsStrength();
  updateMapHint();

  if (state.dashboardData) renderDashboard();
  if (state.dbData) renderDatabase();
}

function toggleLang() { applyLang(state.lang === "en" ? "zh" : "en"); }

function applyTheme(theme) {
  state.theme = theme;
  localStorage.setItem("routemind_theme", theme);
  document.documentElement.setAttribute("data-theme", theme);
  const icon = $("theme-icon");
  if (icon) icon.setAttribute("data-lucide", theme === "dark" ? "moon" : "sun");
  if (window.lucide) lucide.createIcons();
  if (state.lastData) {
    renderCharts();
    if (state.mapData && state.worldMapChart) renderWorldMap(state.mapData);
  }
  if (state.dashboardData) renderDashboardCharts();
}
function toggleTheme() { applyTheme(state.theme === "dark" ? "light" : "dark"); }

function updateFreshness() {
  const el = $("freshness-label");
  if (!el) return;
  const iso = state._filterOptions.last_updated;
  if (!iso) { el.textContent = t("topbar.waiting"); return; }
  el.textContent = fmt(t("topbar.freshAt"), { ago: relativeTime(iso) });
}
setInterval(updateFreshness, 30000);

// =============================================================
// Map mode switch
// =============================================================
function updateMapHint() {
  const hint = $("map-hint");
  if (!hint) return;
  hint.textContent = state.mapMode === "city" ? t("map.hintCity") : t("map.hintCountry");
}

function setMapMode(mode) {
  if (mode !== "country" && mode !== "city") return;
  if (state.mapMode === mode) return;
  state.mapMode = mode;
  localStorage.setItem("routemind_map_mode", mode);

  // 更新按钮 UI
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });
  updateMapHint();

  // 清空详情
  state.mapFocusedLocation = null;
  const detail = $("map-detail");
  if (detail) detail.classList.add("hidden");

  // 重绘地图
  if (state.mapData) {
    renderWorldMap(state.mapData);
  }
  console.log("[setMapMode]", mode);
}

// =============================================================
// Navigation
// =============================================================
function switchView(name) {
  document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
  const el = $(`view-${name}`);
  if (el) el.classList.add("active");
  document.querySelectorAll(".nav-item").forEach((n) =>
    n.classList.toggle("active", n.dataset.view === name));
  if (window.lucide) lucide.createIcons();
  closeUserMenu();

  if (name === "home") loadHistory();
  if (name === "settings") loadSettings();
  if (name === "admin") loadAdmin();
  if (name === "dashboard") loadDashboard();
  if (name === "database") loadDatabase(1);
  if (name === "report") {
    setTimeout(() => {
      if (state.worldMapChart && !state.worldMapChart.isDisposed()) {
        state.worldMapChart.resize();
      }
    }, 100);
  }
}
document.querySelectorAll(".nav-item").forEach((item) => {
  item.addEventListener("click", () => switchView(item.dataset.view));
});

// =============================================================
// Report tabs
// =============================================================
function switchReportTab(tab) {
  state.activeReportTab = tab;
  localStorage.setItem("routemind_report_tab", tab);
  $("tab-content-report").classList.toggle("hidden", tab !== "report");
  $("tab-content-data").classList.toggle("hidden", tab !== "data");
  document.querySelectorAll(".rp-tab").forEach((b) =>
    b.classList.toggle("active", b.dataset.tab === tab));
  if (window.lucide) lucide.createIcons();
  syncFiltersToUI(tab === "data" ? "d" : "f");
  if (tab === "data") renderDataTables();
}

function syncFiltersToUI(prefix) {
  const f = state.filters || {};
  const setVal = (id, val) => {
    const el = $(id);
    if (el) el.value = val;
  };
  setVal(`${prefix}-range`, f.date_range_days || 30);
  setVal(`${prefix}-carrier`, f.carrier || "");
  setVal(`${prefix}-priority`, f.priority || "");
  setVal(`${prefix}-continent`, f.continent || "");
  populateCountriesForPrefix(prefix);
  setVal(`${prefix}-country`, f.country || "");
  setVal(`${prefix}-min-delay`, f.min_delay_days ?? "");
  setVal(`${prefix}-max-delay`, f.max_delay_days ?? "");
}

// =============================================================
// API
// =============================================================
async function api(path, options = {}) {
  const controller = new AbortController();
  const tid = setTimeout(() => controller.abort(), 30000);
  try {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...options,
    });
    const data = await res.json().catch(() => ({}));
    if (res.status === 401 && !window.SHARED_TOKEN) {
      window.location.href = "/login";
      throw new Error("auth");
    }
    return data;
  } finally {
    clearTimeout(tid);
  }
}

// =============================================================
// Templates
// =============================================================
const TEMPLATES = {
  delay: {
    en: "Analyze the last 30 days of delays, find carriers and countries with the highest delay rate.",
    zh: "分析过去 30 天的延误订单，找出延误率最高的承运商和国家。",
  },
  carrier: {
    en: "Compare shipment volume, on-time rate, average delay days, and exception ratio across carriers.",
    zh: "比较不同承运商的订单量、准时率、平均延误天数和异常比例。",
  },
  country: {
    en: "Identify countries with the highest delay rate, revenue at risk, and exception counts.",
    zh: "识别延误率最高的国家、风险收入与异常订单。",
  },
  transit: {
    en: "Show in-transit shipments at risk and identify the carriers and lanes that need attention.",
    zh: "展示在途风险订单，找出需要关注的承运商和线路。",
  },
};
function fillPrompt(k) { $("prompt-input").value = TEMPLATES[k][state.lang]; }

// =============================================================
// Generate
// =============================================================
async function generate() {
  const prompt = $("prompt-input").value.trim();
  if (!prompt) { toastT("toast.selectPrompt", "", "error"); return; }

  const status = $("gen-status");
  status.classList.remove("hidden");
  const steps = status.querySelectorAll(".gen-step");
  steps.forEach((s) => s.className = "gen-step");
  steps[0].classList.add("active");

  try {
    const config = await api("/api/analyze", {
      method: "POST", body: JSON.stringify({ prompt })
    });
    steps[0].className = "gen-step done";
    steps[1].className = "gen-step active";
    await new Promise((r) => setTimeout(r, 300));

    const created = await api("/api/projects", {
      method: "POST",
      body: JSON.stringify({ title: config.title, prompt, config,
                              filters: state.filters, summary: "" }),
    });
    state.currentProjectId = created.id;
    state.config = config;
    state.currentTitle = config.title;
    state.readonly = false;
    $("rp-title").textContent = translateTitle(config.title);
    $("rp-subtitle").textContent = prompt.slice(0, 100);

    steps[1].className = "gen-step done";
    steps[2].className = "gen-step active";
    await new Promise((r) => setTimeout(r, 300));

    await loadFilterOptions();
    state.filters.date_range_days = config.date_range_days || 30;
    if (config.min_delay_days) state.filters.min_delay_days = config.min_delay_days;
    syncFiltersToUI("f");
    syncFiltersToUI("d");

    await compute();

    if (!state.lastData) {
      status.classList.add("hidden");
      toastT("toast.computeFailed", "", "error");
      return;
    }

    steps[2].className = "gen-step done";
    steps[3].className = "gen-step active";
    await new Promise((r) => setTimeout(r, 200));
    steps[3].className = "gen-step done";

    setSaved();
    switchView("report");
    resetChat();
    toastT("toast.workspaceReady", "", "success");
    loadHistory();
  } catch (e) {
    console.error(e);
    toastT("toast.genFailed", e.message, "error");
    status.classList.add("hidden");
  }
}

// =============================================================
// Filter options
// =============================================================
async function loadFilterOptions() {
  try {
    const opts = await api("/api/filters");
    state._filterOptions = opts || {};
    if (opts && opts.country_continents) {
      state._countryToContinent = { ...state._countryToContinent, ...opts.country_continents };
    }
    populateFilterSelects();
    populateDbFilterSelects();
    const label = $("data-source-label");
    if (label) {
      const total = (opts && typeof opts.total === "number") ? opts.total : 0;
      label.textContent = state.lang === "zh"
        ? `合成数据 · ${total.toLocaleString()} 条记录`
        : `Synthetic Data · ${total.toLocaleString()} records`;
    }
    updateFreshness();
  } catch (e) {
    console.error("loadFilterOptions failed:", e);
    toast(state.lang === "zh" ? "筛选项加载失败" : "Failed to load filters", "error");
    state._filterOptions = {
      carriers: [], countries: [], continents: [],
      priorities: ["Standard", "Express", "Critical"],
      total: 0, last_updated: null,
      country_continents: {}, continent_views: {}, country_views: {}, all_cities: [],
    };
    populateFilterSelects();
    populateDbFilterSelects();
    const label = $("data-source-label");
    if (label) {
      label.textContent = state.lang === "zh" ? "合成数据 · 0 条记录" : "Synthetic Data · 0 records";
    }
    updateFreshness();
  }
}

function c2cont(countryName) {
  return state._countryToContinent[countryName] || "";
}

function populateFilterSelects() {
  const opts = state._filterOptions;
  if (!opts || !Array.isArray(opts.carriers)) return;

  const carriers = opts.carriers || [];
  const priorities = opts.priorities || ["Standard", "Express", "Critical"];
  const continents = opts.continents || [];

  ["f", "d"].forEach((prefix) => {
    const carrierEl = $(`${prefix}-carrier`);
    if (!carrierEl) return;

    const priorityEl = $(`${prefix}-priority`);
    const continentEl = $(`${prefix}-continent`);
    const countryEl = $(`${prefix}-country`);
    const rangeEl = $(`${prefix}-range`);
    const minDelayEl = $(`${prefix}-min-delay`);
    const maxDelayEl = $(`${prefix}-max-delay`);

    const curCarrier = carrierEl.value;
    carrierEl.innerHTML = `<option value="">${t("filter.all")}</option>` +
      carriers.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(tv("carrier", c))}</option>`).join("");
    carrierEl.value = curCarrier || "";

    if (priorityEl) {
      const curPri = priorityEl.value;
      priorityEl.innerHTML = `<option value="">${t("filter.allPriority")}</option>` +
        priorities.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(tv("priority", c))}</option>`).join("");
      priorityEl.value = curPri || "";
    }

    if (continentEl) {
      const curCont = continentEl.value;
      continentEl.innerHTML = `<option value="">${t("filter.allContinent")}</option>` +
        continents.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(tv("continent", c))}</option>`).join("");
      continentEl.value = curCont || "";
    }

    if (countryEl) populateCountriesForPrefix(prefix);
    if (rangeEl && !rangeEl.value) rangeEl.value = "30";
  });

  const mContEl = $("m-continent");
  if (mContEl) {
    const curMapCont = mContEl.value;
    mContEl.innerHTML = `<option value="">${t("filter.allContinent")}</option>` +
      continents.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(tv("continent", c))}</option>`).join("");
    mContEl.value = curMapCont || "";
  }

  populateMapCountries();
}

function populateCountriesForPrefix(prefix) {
  const opts = state._filterOptions;
  if (!opts || !Array.isArray(opts.countries)) return;
  const countryEl = $(`${prefix}-country`);
  if (!countryEl) return;
  const contEl = $(`${prefix}-continent`);
  const contVal = contEl ? contEl.value : "";
  const countries = (opts.countries || [])
    .map((c) => ({ value: c, continent: c2cont(c) }))
    .filter((x) => !contVal || x.continent === contVal);
  const cur = countryEl.value;
  countryEl.innerHTML = `<option value="">${t("filter.allCountry")}</option>` +
    countries.map((x) => `<option value="${escapeHtml(x.value)}">${escapeHtml(tv("country", x.value))}</option>`).join("");
  countryEl.value = countries.some((x) => x.value === cur) ? cur : "";
}

function populateMapCountries() {
  const opts = state._filterOptions;
  if (!opts || !Array.isArray(opts.countries)) return;
  const mapCountryEl = $("m-country");
  if (!mapCountryEl) return;
  const mapContEl = $("m-continent");
  const contVal = mapContEl ? mapContEl.value : "";
  const countries = (opts.countries || [])
    .map((c) => ({ value: c, continent: c2cont(c) }))
    .filter((x) => !contVal || x.continent === contVal);
  const cur = mapCountryEl.value;
  mapCountryEl.innerHTML = `<option value="">${t("filter.allCountry")}</option>` +
    countries.map((x) => `<option value="${escapeHtml(x.value)}">${escapeHtml(tv("country", x.value))}</option>`).join("");
  mapCountryEl.value = countries.some((x) => x.value === cur) ? cur : "";
}

function populateDbFilterSelects() {
  const opts = state._filterOptions;
  if (!opts || !Array.isArray(opts.carriers)) return;

  const carrierEl = $("db-carrier");
  if (carrierEl) {
    const curCarrier = carrierEl.value;
    carrierEl.innerHTML = `<option value="">${t("filter.all")}</option>` +
      (opts.carriers || []).map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(tv("carrier", c))}</option>`).join("");
    carrierEl.value = curCarrier || "";
  }

  const countryEl = $("db-country");
  if (countryEl) {
    const curCountry = countryEl.value;
    countryEl.innerHTML = `<option value="">${t("filter.allCountry")}</option>` +
      (opts.countries || []).map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(tv("country", c))}</option>`).join("");
    countryEl.value = curCountry || "";
  }
}

function onFilterContinentChange(prefix) {
  populateCountriesForPrefix(prefix);
  applyFilters();
}
function onContinentChange() { onFilterContinentChange("f"); }
function onDataContinentChange() { onFilterContinentChange("d"); }

function onMapContinentChange() {
  populateMapCountries();
  $("m-country").value = "";
  loadMapOnly();
}
function resetMapView() {
  $("m-continent").value = "";
  $("m-country").value = "";
  populateMapCountries();
  state.mapFocusedLocation = null;
  state.mapLevel = "world";
  state.mapSelectedCountry = "";
  state.mapSelectedContinent = "";
  $("map-detail")?.classList.add("hidden");
  loadMapOnly();
}

function syncFilters() {
  const src = state.activeReportTab === "data" ? "d" : "f";
  const getVal = (id) => {
    const el = $(id);
    return el ? el.value : "";
  };
  const rangeVal = parseInt(getVal(`${src}-range`) || "30");
  state.filters = {
    date_range_days: isNaN(rangeVal) || rangeVal <= 0 ? 30 : rangeVal,
    carrier: getVal(`${src}-carrier`),
    priority: getVal(`${src}-priority`),
    continent: getVal(`${src}-continent`),
    country: getVal(`${src}-country`),
    min_delay_days: getVal(`${src}-min-delay`),
    max_delay_days: getVal(`${src}-max-delay`),
  };
}

const debouncedCompute = debounce(() => compute(), 300);
const debouncedRenderDataTables = debounce(() => renderDataTables(), 300);
const debouncedRenderExceptions = debounce(() => renderExceptions(), 300);

function applyFilters() {
  if (state.readonly) { toastT("toast.readonly", "", "error"); return; }
  syncFilters();
  const otherPrefix = state.activeReportTab === "data" ? "f" : "d";
  syncFiltersToUI(otherPrefix);
  markUnsaved();
  debouncedCompute();      // ★ 改为防抖，快速切换下拉不会连点触发多次请求
}

// =============================================================
// Compute
// =============================================================
async function compute() {
  const seq = ++state.computeSeq;
  showLoading();
  setLoaderStage(15, "loading.prepare");

  try {
    const payload = { filters: state.filters };
    console.log("[compute] filters →", payload);

    const data = await api("/api/report", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (seq !== state.computeSeq) return;
    console.log("[compute] /api/report response:", data?.metrics ? "OK" : "EMPTY");

    setLoaderStage(35, "loading.received");
    state.lastData = data;

    (data.map_countries || data.countries || []).forEach((c) => {
      if (c.continent) state._countryToContinent[c.name] = c.continent;
    });

    renderKPIs(data.metrics);
    renderRangeBanner(data.range_stats);
    renderSummaryLine(data.metrics);
    if (seq !== state.computeSeq) return;

    setLoaderStage(50, "loading.kpi");
    renderCharts();
    if (seq !== state.computeSeq) return;

    setLoaderStage(65, "loading.charts");
    renderLanesTable();
    renderCountriesTable();
    renderAtRiskTable();
    renderExceptions();
    renderAllShipments();
    renderReport(data);
    renderCostSummary(data.cost_breakdown, data.metrics);
    renderDataQuality(data.data_quality);
    renderDataTables();
    if (seq !== state.computeSeq) return;

    setLoaderStage(85, "loading.map");

    const mCountry = $("m-country")?.value || "";
    const mContinent = $("m-continent")?.value || "";

    if (mCountry || mContinent) {
      await loadMapOnly();
    } else {
      state.mapData = {
        countries: data.map_countries || data.countries || [],
        cities: data.map_cities || [],
        level: "world",
      };
      state.mapLevel = "world";
      state.mapSelectedCountry = "";
      state.mapSelectedContinent = "";
      renderWorldMap(state.mapData);
      if (!state.mapFocusedLocation) {
        renderCitiesTable([], null, null);
      }
    }
    if (seq !== state.computeSeq) return;

    setLoaderStage(100, "loading.done");
    finishLoading();

    autoSaveProject();
  } catch (e) {
    console.error("[compute] failed:", e);
    if (seq === state.computeSeq) {
      // ★ 不再清空 lastData，保留上一次成功结果，只提示错误
      toastT("toast.computeFailed", " " + (e.message || ""), "error");
      hideLoading();
    }
  }
}

// =============================================================
// Map-only load
// =============================================================
async function loadMapOnly() {
  const mCountry = $("m-country")?.value || "";
  const mContinent = $("m-continent")?.value || "";
  const fCountry = $("f-country")?.value || "";
  const fContinent = $("f-continent")?.value || "";

  let focusCountry = "", focusContinent = "", level = "world";
  if (mCountry) { focusCountry = mCountry; focusContinent = c2cont(mCountry); level = "country"; }
  else if (mContinent) { focusContinent = mContinent; level = "continent"; }
  else if (fCountry) { focusCountry = fCountry; focusContinent = c2cont(fCountry); level = "country"; }
  else if (fContinent) { focusContinent = fContinent; level = "continent"; }

  state.mapLevel = level;
  state.mapSelectedCountry = focusCountry;
  state.mapSelectedContinent = focusContinent;

  // 注意：不传 country / continent → 保持全量数据，所有国家都有颜色
  const filters = {
    date_range_days: parseInt($("f-range")?.value || "30"),
    carrier: $("f-carrier")?.value || "",
    priority: $("f-priority")?.value || "",
  };
  try {
    const data = await api("/api/map", {
      method: "POST",
      body: JSON.stringify({ filters, level }),
    });
    state.mapData = data;
    (data.countries || []).forEach((c) => {
      if (c.continent) state._countryToContinent[c.name] = c.continent;
    });
    renderWorldMap(data);
    if (!state.mapFocusedLocation) {
      renderCitiesTable([], null, null);
    }
  } catch (e) {
    console.error("Map load failed", e);
  }
}

// =============================================================
// KPI
// =============================================================
function renderKPIs(m) {
  if (!m) return;
  $("kpi-total").textContent = fmtNum(m.total_shipments);
  $("kpi-otif").textContent = m.otif_rate == null ? t("common.na") : m.otif_rate + "%";
  $("kpi-delay").textContent = m.delay_rate == null ? t("common.na") : m.delay_rate + "%";
  $("kpi-eta").textContent = m.eta_accuracy_rate == null ? t("common.na") : m.eta_accuracy_rate + "%";
  $("kpi-p90").textContent = m.p90_delay_days == null ? t("common.na")
    : m.p90_delay_days + (state.lang === "zh" ? " 天" : " d");
  const rev = $("kpi-revenue");
  rev.textContent = fmtCurrency(m.revenue);
  rev.dataset.full = fmtFullCurrency(m.revenue);
  rev.title = fmtFullCurrency(m.revenue);
}

function renderSummaryLine(m) {
  if (!m || !m.total_shipments) { $("summary-line").textContent = "—"; return; }
  const p90 = m.p90_delay_days == null ? "—" : m.p90_delay_days;
  const otif = m.otif_rate == null ? "—" : m.otif_rate;
  if (state.lang === "zh") {
    $("summary-line").textContent =
      `${m.total_shipments.toLocaleString()} 个订单中，延误率 ${m.delay_rate}%，` +
      `OTIF ${otif}%，P90 延误 ${p90} 天。`;
  } else {
    $("summary-line").textContent =
      `${m.total_shipments.toLocaleString()} shipments · ` +
      `${m.delay_rate}% delay · OTIF ${otif}% · P90 delay ${p90}d.`;
  }
}

function renderRangeBanner(rs) {
  const active = (state.filters.min_delay_days !== "" && state.filters.min_delay_days != null)
              || (state.filters.max_delay_days !== "" && state.filters.max_delay_days != null);

  [["range-banner"], ["range-banner-data"]].forEach(([id]) => {
    const el = $(id);
    if (!el) return;
    if (!rs || !rs.active || !active || (!rs.total_delayed && !rs.total_shipments)) {
      el.classList.add("hidden");
      return;
    }
    el.classList.remove("hidden");
    const mn = rs.range_min, mx = rs.range_max;
    const rangeTxt = mx == null
      ? (state.lang === "zh" ? `≥ ${mn} 天` : `≥ ${mn} d`)
      : (state.lang === "zh" ? `${mn}–${mx} 天` : `${mn}–${mx} d`);
    const pctD = rs.pct_of_delayed == null ? "—" : rs.pct_of_delayed + "%";
    const pctT = rs.pct_of_total == null ? "—" : rs.pct_of_total + "%";
    el.innerHTML = `
      <div class="range-banner-title">${t("range.title")} [${rangeTxt}]</div>
      <div class="range-banner-stat">${t("range.shipments")}: <strong>${(rs.range_delayed || 0).toLocaleString()}</strong></div>
      <div class="range-banner-stat">${t("range.pctDelayed")}: <strong>${pctD}</strong></div>
      <div class="range-banner-stat">${t("range.pctTotal")}: <strong>${pctT}</strong></div>
    `;
  });
}

// =============================================================
// Charts
// =============================================================
function chartColors() {
  const dark = state.theme === "dark";
  return {
    text: dark ? "#c2cbd9" : "#4a5568",
    grid: dark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)",
    font: { family: "'Inter', sans-serif", size: 10.5 },
    accent: "#60a5fa", warning: "#fbbf24",
    success: "#34d399", danger: "#f87171", purple: "#8b5cf6",
  };
}
function destroyChart(k) { if (charts[k]) { charts[k].destroy(); charts[k] = null; } }

function renderCharts() {
  if (!state.lastData) return;
  const data = state.lastData;
  const c = chartColors();

  destroyChart("trend");
  const trendEl = $("chart-trend");
  if (!trendEl) return;
  const trendCtx = trendEl.getContext("2d");
  const trendGrad = trendCtx.createLinearGradient(0, 0, 0, 220);
  trendGrad.addColorStop(0, "rgba(96,165,250,0.35)");
  trendGrad.addColorStop(1, "rgba(96,165,250,0)");
  const isRate = state.trendMode === "delay_rate";
  charts.trend = new Chart(trendCtx, {
    type: state.trendType,
    data: {
      labels: (data.trend || []).map((p) => p.date.slice(5)),
      datasets: [{
        label: isRate ? t("trend.mode.rate") : t("trend.mode.count"),
        data: (data.trend || []).map((p) => isRate ? p.delay_rate : p.delayed_count),
        borderColor: c.accent,
        backgroundColor: state.trendType === "line" ? trendGrad : "rgba(96,165,250,0.6)",
        fill: state.trendType === "line",
        tension: 0.35, borderWidth: 2,
        pointRadius: 0, pointHoverRadius: 4,
        borderRadius: state.trendType === "bar" ? 4 : 0,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: c.grid }, ticks: { color: c.text, font: c.font, maxTicksLimit: 8 } },
        y: { grid: { color: c.grid }, beginAtZero: true,
             ticks: { color: c.text, font: c.font, callback: (v) => isRate ? v + "%" : v } }
      }
    }
  });

  destroyChart("status");
  const sd = data.status_distribution || {};
  const statusLabels = Object.keys(sd);
  const statusValues = Object.values(sd);
  const totalSD = statusValues.reduce((a, b) => a + b, 0) || 1;
  const statusEl = $("chart-status");
  if (statusEl) {
    const statusColors = [c.success, c.accent, c.danger];
    charts.status = new Chart(statusEl.getContext("2d"), {
      type: "doughnut",
      data: {
        labels: statusLabels.map((k) => tv("status", k)),
        datasets: [{
          data: statusValues,
          backgroundColor: statusColors,
          borderColor: state.theme === "dark" ? "#111827" : "#ffffff",
          borderWidth: 3,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: "58%",
        plugins: {
          legend: {
            position: "right",
            labels: {
              color: c.text, font: c.font, boxWidth: 10, padding: 12,
              generateLabels: () => statusLabels.map((label, i) => ({
                text: `${tv("status", label)}  ${(statusValues[i] || 0).toLocaleString()} (${((statusValues[i] || 0) / totalSD * 100).toFixed(1)}%)`,
                fillStyle: statusColors[i],
                strokeStyle: statusColors[i],
                lineWidth: 0, hidden: false, index: i,
                fontColor: c.text,
              })),
            },
          },
        }
      }
    });
  }

  destroyChart("carrier");
  const carriers = (data.carriers || []).slice(0, 8);
  const metric = state.carrierMetric;
  const isCost = metric === "avg_cost_per_shipment";
  const carrierEl = $("chart-carrier");
  if (carrierEl) {
    charts.carrier = new Chart(carrierEl.getContext("2d"), {
      type: "bar",
      data: {
        labels: carriers.map((x) => tv("carrier", x.name)),
        datasets: [{
          label: metric === "delay_rate" ? t("chart.m.delay")
               : metric === "otif_rate" ? t("chart.m.otif")
               : isCost ? t("chart.m.cost")
               : t("chart.m.volume"),
          data: carriers.map((x) => x[metric] ?? 0),
          backgroundColor: carriers.map((x) => {
            if (metric === "delay_rate" && (x.delay_rate ?? 0) > 15) return "rgba(248,113,113,0.7)";
            if (metric === "otif_rate" && (x.otif_rate ?? 0) < 85) return "rgba(251,191,36,0.7)";
            return "rgba(96,165,250,0.7)";
          }),
          borderWidth: 1, borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, indexAxis: "y",
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const v = ctx.parsed.x;
                if (metric === "total_shipments") return `${t("chart.m.volume")}: ${v}`;
                if (isCost) return `${t("chart.m.cost")}: ${fmtFullCurrency(v)}`;
                return `${ctx.dataset.label}: ${v}%`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: c.grid }, beginAtZero: true,
            ticks: {
              color: c.text, font: c.font,
              callback: (v) => {
                if (metric === "total_shipments") return v;
                if (isCost) return "$" + v;
                return v + "%";
              },
            }
          },
          y: { grid: { display: false }, ticks: { color: c.text, font: c.font } }
        }
      }
    });
  }

  destroyChart("reasons");
  const reasons = (data.delay_reasons || []).slice(0, 8);
  const reasonsEl = $("chart-reasons");
  if (reasonsEl) {
    charts.reasons = new Chart(reasonsEl.getContext("2d"), {
      type: "bar",
      data: {
        labels: reasons.map((r) => tv("reason", r.name)),
        datasets: [{
          data: reasons.map((r) => r.count),
          backgroundColor: [
            "rgba(96,165,250,0.75)", "rgba(139,92,246,0.75)",
            "rgba(251,191,36,0.75)", "rgba(248,113,113,0.75)",
            "rgba(52,211,153,0.75)", "rgba(148,163,184,0.75)",
            "rgba(236,72,153,0.75)", "rgba(14,165,233,0.75)",
          ],
          borderWidth: 0, borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: (ctx) => `${t("table.shipments")}: ${ctx.parsed.y}` } }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: c.text, font: c.font } },
          y: { grid: { color: c.grid }, ticks: { color: c.text, font: c.font }, beginAtZero: true }
        }
      }
    });
  }

  const cb = data.cost_breakdown;
  const costEl = $("chart-cost");
  destroyChart("cost");                     // ← 提到 if 外
  if (cb && costEl) {
    const costLabels = [t("cost.lineHaul"), t("cost.fuel"),
                        t("cost.accessorial"), t("cost.detention")];
    const costValues = [cb.line_haul || 0, cb.fuel || 0, cb.accessorial || 0, cb.detention || 0];
    const costColors = ["#60a5fa", "#8b5cf6", "#fbbf24", "#f87171"];
    charts.cost = new Chart(costEl.getContext("2d"), {
      type: "doughnut",
      data: {
        labels: costLabels,
        datasets: [{
          data: costValues,
          backgroundColor: costColors,
          borderColor: state.theme === "dark" ? "#111827" : "#ffffff",
          borderWidth: 3,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: "55%",
        plugins: {
          legend: {
            position: "right",
            labels: {
              color: c.text, font: c.font, boxWidth: 10, padding: 10,
              generateLabels: () => {
                const total = costValues.reduce((a, b) => a + b, 0) || 1;
                return costLabels.map((label, i) => ({
                  text: `${label}  ${fmtCurrency(costValues[i])} (${(costValues[i] / total * 100).toFixed(0)}%)`,
                  fillStyle: costColors[i],
                  strokeStyle: costColors[i],
                  lineWidth: 0, hidden: false, index: i,
                  fontColor: c.text,
                }));
              },
            },
          },
        }
      }
    });
  }

  const scatterEl = $("chart-scatter");
  destroyChart("scatter");                  // ← 提到 if 外
  if (data.carriers && scatterEl) {
    const points = data.carriers.map((x) => ({
      x: x.avg_cost_per_shipment ?? 0,
      y: x.delay_rate ?? 0,
      name: tv("carrier", x.name),
      volume: x.total_shipments || 0,
    }));
    charts.scatter = new Chart(scatterEl.getContext("2d"), {
      type: "scatter",
      data: {
        datasets: [{
          data: points,
          backgroundColor: points.map((p) => p.y > 15 ? "rgba(248,113,113,0.7)" : "rgba(96,165,250,0.7)"),
          borderColor: points.map((p) => p.y > 15 ? "#f87171" : "#60a5fa"),
          pointRadius: points.map((p) =>
            Math.max(3, Math.min(8, Math.log10((p.volume || 1) + 1) * 2.5 + 3))),
          pointHoverRadius: 10,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const p = ctx.raw;
                return [p.name,
                  `${t("chart.m.cost")}: ${fmtFullCurrency(p.x)}`,
                  `${t("chart.m.delay")}: ${p.y}%`,
                  `${t("chart.m.volume")}: ${p.volume}`];
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: t("chart.costLegend"), color: c.text, font: c.font },
            grid: { color: c.grid }, ticks: { color: c.text, font: c.font, callback: (v) => "$" + v }
          },
          y: {
            title: { display: true, text: t("chart.serviceLegend"), color: c.text, font: c.font },
            grid: { color: c.grid }, ticks: { color: c.text, font: c.font, callback: (v) => v + "%" }, beginAtZero: true
          }
        }
      }
    });
  }
}

function switchTrendType(type, btn) {
  state.trendType = type;
  btn.parentElement.querySelectorAll(".mini-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  if (state.lastData) renderCharts();
}

// =============================================================
// World map — dual coordinate system (map + geo for scatter)
// =============================================================
function getCountryNameMap() {
  return state.lang === "zh" ? VALUE_TRANSLATIONS.country : {};
}

function resolveEntityName(params) {
  let name = params.data?.name || params.name || "";
  if (ZH_TO_EN_COUNTRY[name]) return ZH_TO_EN_COUNTRY[name];
  if (COUNTRY_ALIASES[name]) return COUNTRY_ALIASES[name];
  return name;
}

function loadWorldMap() {
  if (state.worldMapReady) return Promise.resolve();
  if (state.worldMapPromise) return state.worldMapPromise;
  state.worldMapPromise = fetch(
    "https://cdn.jsdelivr.net/gh/apache/echarts@5.5.0/test/data/map/json/world.json"
  ).then((r) => r.json()).then((json) => {
    echarts.registerMap("world", json);
    state.worldMapReady = true;
  }).catch((err) => {
    console.error("Map load failed", err);
    state.worldMapPromise = null;
  });
  return state.worldMapPromise;
}

function getInitialZoom() {
  if (state.mapLevel === "country" && state.mapSelectedCountry) {
    const v = state._filterOptions.country_views?.[state.mapSelectedCountry];
    if (v) return v.zoom || 3.5;
  }
  if (state.mapLevel === "continent" && state.mapSelectedContinent) {
    const v = state._filterOptions.continent_views?.[state.mapSelectedContinent];
    if (v) return v.zoom || 2.4;
  }
  return 1.2;
}

function getInitialCenter() {
  if (state.mapLevel === "country" && state.mapSelectedCountry) {
    const v = state._filterOptions.country_views?.[state.mapSelectedCountry];
    if (v) return v.center;
  }
  if (state.mapLevel === "continent" && state.mapSelectedContinent) {
    const v = state._filterOptions.continent_views?.[state.mapSelectedContinent];
    if (v) return v.center;
  }
  return null;
}

function filterCitiesByZoom(cities, zoom) {
  const arr = cities || [];
  if (zoom >= 4.0) return arr;
  const topCount = zoom < 2.0 ? 10 : 30;
  const sorted = [...arr].sort((a, b) =>
    (b.total_shipments || 0) - (a.total_shipments || 0));
  const topNames = new Set(sorted.slice(0, topCount).map(c => c.name));
  return arr.filter(c => c.in_filter || topNames.has(c.name));
}

function buildCityPoints(data, zoom) {
  const visible = filterCitiesByZoom(data.cities || [], zoom);
  return visible
    .filter(ct => typeof ct.lon === "number" && typeof ct.lat === "number" && ct.lon && ct.lat)
    .map(ct => ({
      name: ct.name,
      country: ct.country,
      value: [ct.lon, ct.lat, ct.delay_rate || 0, ct.total_shipments || 0],
      shipments: ct.total_shipments || 0,
      revenue: ct.revenue || 0,
      otif: ct.otif_rate,
      delay_rate: ct.delay_rate,
      in_filter: !!ct.in_filter,
    }));
}

/* 城市散点层 —— 空心圆 + 亮黄色边框 + 小尺寸*/
function buildCityScatterSeries(cityPoints, zoom) {
  if (!cityPoints.length) return null;
  const showLabels = zoom >= ZOOM_LABEL_THRESHOLD;
  return {
    type: "scatter",
    coordinateSystem: "geo",
    geoIndex: 0,
    zlevel: 2,
    symbol: "circle",
    symbolSize: (val) => {
      const vol = (val && val[3]) || 1;
      // 2 – 4.5 px
      return Math.max(2, Math.min(4.5, Math.log10(vol + 1) * 1.5 + 2));
    },
    itemStyle: {
      // ★ 本体改为青色填充，与国家金色的 highlight 明确区分
      color: "rgba(34,211,238,0.85)",
      borderColor: "#22d3ee",
      borderWidth: 1.5,
      opacity: (params) => params.data?.in_filter ? 1 : 0.55,
      shadowBlur: 4,
      shadowColor: "rgba(34,211,238,0.5)",
    },
    // ★ highlight 改为白色高亮
    emphasis: {
      scale: 1.6,
      itemStyle: {
        color: "rgba(255,255,255,0.92)",
        borderColor: "#ffffff",
        borderWidth: 2.2,
        shadowBlur: 10,
        shadowColor: "rgba(255,255,255,0.9)",
      },
    },
    label: {
      show: showLabels,
      position: "right",
      formatter: (p) => p.data?.in_filter ? tv("city", p.data.name) : "",
      color: state.theme === "dark" ? "#f0f4fa" : "#1e293b",
      fontSize: 9,
      backgroundColor: state.theme === "dark"
        ? "rgba(17,24,39,0.85)" : "rgba(255,255,255,0.9)",
      padding: [2, 5], borderRadius: 3,
    },
    data: cityPoints,
  };
}

let _mapRetryCount = 0;

async function renderWorldMap(data) {
  const mapEl = $("world-map");
  if (!mapEl) return;
  if (mapEl.offsetWidth === 0) {
    if (_mapRetryCount++ > 20) { _mapRetryCount = 0; return; }   // 3s 后放弃
    setTimeout(() => renderWorldMap(data), 150);
    return;
  }
  _mapRetryCount = 0;
  try {
    await loadWorldMap();
  } catch (e) {
    mapEl.innerHTML = `<div style="padding:40px;text-align:center;color:var(--text-3);font-size:12px;">Map unavailable</div>`;
    return;
  }

  const c = chartColors();
  const zoom = getInitialZoom();
  const center = getInitialCenter();
  state.mapCurrentZoom = zoom;
  state.mapZoomLevel = zoom < ZOOM_DETAIL_THRESHOLD ? "world" : "detail";

  const selected = state.mapSelectedCountry || "";

  // 所有有数据的国家都上色；选中国家只加金色边框（无光晕）
  const mapData = (data.countries || []).map((x) => {
    const isSelected = !!selected && x.name === selected;
    const val = x.delay_rate ?? ((x.total_shipments || 0) > 0 ? 0 : null);
    return {
      name: x.name,
      value: val,
      shipments: x.total_shipments || 0,
      revenue: x.revenue || 0,
      delivered: x.delivered_count || 0,
      otif_rate: x.otif_rate,
      // ★ 去掉 shadowBlur / shadowColor，只保留金色边框
      itemStyle: isSelected ? {
        borderColor: "#FFD700",
        borderWidth: 2.5,
      } : undefined,
    };
  });

  // vMax 用 P90 × 1.3，避免 India / Australia 独占红色区间
  const validRates = (data.countries || [])
    .map((x) => x.delay_rate)
    .filter((v) => v != null && isFinite(v) && v >= 0)
    .sort((a, b) => a - b);
  let vMax = 30;
  if (validRates.length) {
    const p90 = validRates[Math.min(
      validRates.length - 1,
      Math.floor(validRates.length * 0.9)
    )];
    vMax = Math.min(100, Math.max(20, Math.ceil(p90 * 1.3 / 5) * 5));
  }

  const cityPoints = buildCityPoints(data, zoom);

  const series = [{
    type: "map",
    map: "world",
    roam: true,
    zoom: zoom,
    center: center || undefined,
    scaleLimit: { min: 1, max: 8 },
    label: { show: false },
    itemStyle: {
      areaColor: state.theme === "dark" ? "#1f2b3e" : "#e5eaf0",
      borderColor: state.theme === "dark" ? "#0d1220" : "#ffffff",
      borderWidth: 0.5,
    },
    emphasis: {
      itemStyle: { areaColor: state.theme === "dark" ? "#2c3e5c" : "#c7d0dd" },
      label: {
        show: true, color: c.text, fontSize: 10,
        formatter: (p) => tv("country", p.name) || p.name,
      },
    },
    data: mapData,
    zlevel: 1,
  }];

  if (state.mapMode === "city") {
    const scatterSeries = buildCityScatterSeries(cityPoints, zoom);
    if (scatterSeries) series.push(scatterSeries);
  }

  if (!state.worldMapChart || state.worldMapChart.isDisposed()) {
    state.worldMapChart = echarts.init(mapEl, null, { renderer: "canvas" });
    state.worldMapChart.on("click", handleMapClick);

    state.worldMapChart.on("georoam", throttle(() => {
      if (!state.worldMapChart || state.worldMapChart.isDisposed()) return;
      try {
        const opt = state.worldMapChart.getOption();
        const s = opt.series && opt.series[0];
        const newZoom = (s && s.zoom) || 1.2;
        const newCenter = s && s.center;
        state.mapCurrentZoom = newZoom;

        state.worldMapChart.setOption({
          geo: [{ zoom: newZoom, center: newCenter || undefined }],
        }, false);

        if (state.mapMode === "city") {
          const newLevel = newZoom < ZOOM_DETAIL_THRESHOLD ? "world" : "detail";
          if (newLevel !== state.mapZoomLevel) {
            state.mapZoomLevel = newLevel;
            const cps = buildCityPoints(state.mapData || {}, newZoom);
            const newScatter = buildCityScatterSeries(cps, newZoom);
            if (newScatter) {
              state.worldMapChart.setOption({ series: [{}, newScatter] }, false);
            }
          }
        }
      } catch (err) { /* ignore */ }
    }, 200));

    if (window.ResizeObserver) {
      new ResizeObserver(() => {
        if (state.worldMapChart && !state.worldMapChart.isDisposed()) {
          state.worldMapChart.resize();
        }
      }).observe(mapEl);
    } else {
      window.addEventListener("resize", () => {
        if (state.worldMapChart && !state.worldMapChart.isDisposed()) {
          state.worldMapChart.resize();
        }
      });
    }
  } else {
    state.worldMapChart.resize();
  }

  state.worldMapChart.setOption({
    backgroundColor: "transparent",
    geo: {
      map: "world",
      roam: false,
      silent: true,
      show: false,
      zoom: zoom,
      center: center || undefined,
    },
    tooltip: {
      trigger: "item",
      backgroundColor: state.theme === "dark" ? "#111827" : "#ffffff",
      borderColor: state.theme === "dark" ? "#1f2b3e" : "#e1e7f0",
      textStyle: { color: state.theme === "dark" ? "#e6ebf5" : "#1e293b", fontSize: 11 },
      padding: [8, 12],
      formatter: (p) => {
        if (!p.data) return tv("country", p.name);
        const d = p.data;
        if (p.seriesType === "scatter") {
          const filterMark = d.in_filter
            ? "" : ` <span style='opacity:0.6'>${t("map.outsideFilter")}</span>`;
          return `<b>${tv("city", d.name)}</b>${filterMark}<br/>` +
            `${t("map.detail.delay")}: ${d.delay_rate ?? "—"}%<br/>` +
            `${t("map.detail.shipments")}: ${(d.shipments || 0).toLocaleString()}<br/>` +
            `${t("map.detail.revenue")}: ${fmtFullCurrency(d.revenue)}`;
        }
        return `<b>${tv("country", p.name)}</b><br/>` +
          `${t("map.detail.delay")}: ${(d.value ?? 0).toFixed(1)}%<br/>` +
          `${t("map.detail.shipments")}: ${(d.shipments || 0).toLocaleString()}<br/>` +
          `${t("map.detail.otif")}: ${d.otif_rate ?? "—"}%<br/>` +
          `${t("map.detail.revenue")}: ${fmtFullCurrency(d.revenue)}`;
      }
    },
    visualMap: {
      min: 0, max: vMax, left: 20, bottom: 20,
      seriesIndex: 0,
      text: [t("map.legend.high"), t("map.legend.low")],
      calculable: true,
      inRange: {
        color: state.theme === "dark"
          ? ["#1e3a5f", "#3b82f6", "#fbbf24", "#f87171"]
          : ["#dbeafe", "#3b82f6", "#fbbf24", "#dc2626"]
      },
      textStyle: { color: c.text, fontSize: 10 },
    },
    series: series,
  }, true);

  setTimeout(() => {
    if (state.worldMapChart && !state.worldMapChart.isDisposed()) state.worldMapChart.resize();
  }, 80);
}

// =============================================================
// Map click handler — mode-aware
// =============================================================
function handleMapClick(params) {
  const rawName = params.name || params.data?.name || "";
  if (!rawName) return;

  const mode = state.mapMode;

  // ===== City 模式 =====
  if (mode === "city") {
    if (params.seriesType !== "scatter") {
      toast(
        state.lang === "zh"
          ? t("toast.cityModeHint")
          : "Switch to Country mode to click countries",
        ""
      );
      return;
    }
    const cityName = params.data?.name || rawName;
    const cityCountry = params.data?.country || "";
    console.log("[map-click city]", cityName, "in", cityCountry);

    renderLocalCityDetail(cityName, cityCountry);

    if (cityCountry) {
      state.mapSelectedCountry = cityCountry;
      state.mapSelectedContinent = c2cont(cityCountry);
      state.mapLevel = "country";
      const mCountryEl = $("m-country");
      if (mCountryEl) {
        const opt = Array.from(mCountryEl.options).find(o => o.value === cityCountry);
        if (opt) mCountryEl.value = cityCountry;
      }
    }
    fetchAndRenderFocus("city", cityName, false);
    return;
  }

  // ===== Country 模式 =====
  if (params.seriesType === "scatter") return;

  let mapped = ZH_TO_EN_COUNTRY[rawName] || COUNTRY_ALIASES[rawName] || rawName;

  const knownCountries = state._filterOptions?.countries || [];
  if (mapped && !knownCountries.includes(mapped)) {
    const all = [
      ...(state.lastData?.countries || []),
      ...(state.lastData?.map_countries || []),
      ...(state.mapData?.countries || []),
    ];
    const hit = all.find(c =>
      c.name === mapped ||
      tv("country", c.name) === rawName ||
      (c.name || "").toLowerCase() === mapped.toLowerCase()
    );
    if (hit) mapped = hit.name;
  }

  console.log("[map-click country] raw=", rawName, "→ mapped=", mapped);

  renderLocalCountryDetail(mapped);

  const mCountryEl = $("m-country");
  if (mCountryEl) {
    const opt = Array.from(mCountryEl.options).find(o => o.value === mapped);
    if (opt) mCountryEl.value = mapped;
  }

  fetchAndRenderFocus("country", mapped, false);
}

// =============================================================
// Local (fallback) detail renderers
// =============================================================
function renderLocalCountryDetail(name) {
  const box = $("map-detail");
  if (!box) return;

  // 多数据源兜底：优先当前地图数据，其次 lastData 的全量 map_countries / countries
  const sources = [
    state.mapData?.countries || [],
    state.lastData?.map_countries || [],
    state.lastData?.countries || [],
  ];
  let data;
  for (const arr of sources) {
    data = arr.find(c => c.name === name);
    if (data) break;
  }

  const translated = tv("country", name) || name;

  // 本地无数据时渲染 skeleton，等待 fetchAndRenderFocus 覆盖
  if (!data) {
    box.innerHTML = `
      <div class="map-focus-label" style="display:flex;">
        <span>${t("map.focus")}:</span>
        <span class="focus-name">${escapeHtml(translated)}</span>
        <span class="focus-hint">${t("map.loading")}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">${t("map.detail.shipments")}</span>
        <span class="detail-value"><span class="skeleton"></span></span>
      </div>
      <div class="detail-item">
        <span class="detail-label">${t("map.detail.delay")}</span>
        <span class="detail-value"><span class="skeleton"></span></span>
      </div>
      <div class="detail-item">
        <span class="detail-label">${t("map.detail.otif")}</span>
        <span class="detail-value"><span class="skeleton"></span></span>
      </div>
      <div class="detail-item">
        <span class="detail-label">${t("map.detail.revenue")}</span>
        <span class="detail-value"><span class="skeleton"></span></span>
      </div>
    `;
    box.classList.remove("hidden");
    return;
  }

  const shipments = data.total_shipments ?? 0;
  const delayRate = data.delay_rate;
  const otif = data.otif_rate;
  const revenue = data.revenue ?? 0;

  box.innerHTML = `
    <div class="map-focus-label" style="display:flex;">
      <span>${t("map.focus")}:</span>
      <span class="focus-name">${escapeHtml(translated)}</span>
      <span class="focus-hint">${t("map.focusHint")}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.shipments")}</span>
      <span class="detail-value">${shipments.toLocaleString()}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.delay")}</span>
      <span class="detail-value warn">${delayRate == null ? "—" : delayRate + "%"}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.otif")}</span>
      <span class="detail-value ok">${otif == null ? "—" : otif + "%"}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.revenue")}</span>
      <span class="detail-value">${fmtFullCurrency(revenue)}</span>
    </div>
  `;
  box.classList.remove("hidden");
}

function renderLocalCityDetail(name, country) {
  const box = $("map-detail");
  if (!box) return;

  const sources = [
    state.mapData?.cities || [],
    state.lastData?.map_cities || [],
  ];
  let data;
  for (const arr of sources) {
    data = arr.find(c => c.name === name);
    if (data) break;
  }

  const translated = tv("city", name) || name;

  if (!data) {
    box.innerHTML = `
      <div class="map-focus-label" style="display:flex;">
        <span>${t("map.focus")}:</span>
        <span class="focus-name">${escapeHtml(translated)}</span>
        <span class="focus-hint">${t("map.loading")}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">${t("map.detail.shipments")}</span>
        <span class="detail-value"><span class="skeleton"></span></span>
      </div>
      <div class="detail-item">
        <span class="detail-label">${t("map.detail.delay")}</span>
        <span class="detail-value"><span class="skeleton"></span></span>
      </div>
      <div class="detail-item">
        <span class="detail-label">${t("map.detail.otif")}</span>
        <span class="detail-value"><span class="skeleton"></span></span>
      </div>
      <div class="detail-item">
        <span class="detail-label">${t("map.detail.revenue")}</span>
        <span class="detail-value"><span class="skeleton"></span></span>
      </div>
    `;
    box.classList.remove("hidden");
    return;
  }

  const shipments = data.total_shipments ?? 0;
  const delayRate = data.delay_rate;
  const otif = data.otif_rate;
  const revenue = data.revenue ?? 0;

  box.innerHTML = `
    <div class="map-focus-label" style="display:flex;">
      <span>${t("map.focus")}:</span>
      <span class="focus-name">${escapeHtml(translated)}</span>
      <span class="focus-hint">${t("map.focusHint")}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.shipments")}</span>
      <span class="detail-value">${shipments.toLocaleString()}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.delay")}</span>
      <span class="detail-value warn">${delayRate == null ? "—" : delayRate + "%"}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.otif")}</span>
      <span class="detail-value ok">${otif == null ? "—" : otif + "%"}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.revenue")}</span>
      <span class="detail-value">${fmtFullCurrency(revenue)}</span>
    </div>
  `;
  box.classList.remove("hidden");
}

// =============================================================
// Focus fetch (backend enrichment)
// =============================================================
async function fetchAndRenderFocus(focusType, focusName, skipMapDrill = false) {
  const seq = ++state._focusSeq;
  try {
    const res = await api("/api/map/focus", {
      method: "POST",
      body: JSON.stringify({
        focus_type: focusType,
        focus_name: focusName,
        date_range_days: parseInt($("f-range")?.value || "30"),
      }),
    });
    if (seq !== state._focusSeq) return;

    state.mapFocusedLocation = {
      type: focusType,
      name: focusName,
      country: res.country || null,
    };

    if (res.error) {
      renderFocusError(focusType, focusName, res.error);
    } else if (!res.focus_metrics || (res.focus_metrics.total_shipments || 0) === 0) {
      renderFocusEmpty(focusType, focusName);
    } else {
      renderFocusDetail(res);
      if (focusType === "country") {
        renderCitiesTable(res.cities || [], null, focusName);
      } else if (res.cities && res.cities.length) {
        renderCitiesTable(res.cities, focusName, res.country || null);
      }
    }

    // 关键：更新高亮 + zoom，但【不重新拉数据】→ 所有国家保持颜色
    if (focusType === "country") {
      state.mapLevel = "country";
      state.mapSelectedCountry = focusName;
      state.mapSelectedContinent = c2cont(focusName);
    } else if (focusType === "city" && res.country) {
      state.mapLevel = "country";
      state.mapSelectedCountry = res.country;
      state.mapSelectedContinent = c2cont(res.country);
    }
    if (state.mapData) {
      renderWorldMap(state.mapData);
    }
  } catch (e) {
    console.error("[focus] failed:", e);
    if (seq === state._focusSeq) {
      renderFocusError(focusType, focusName, e.message || "unknown");
    }
  }
}

function renderFocusEmpty(focusType, focusName) {
  const box = $("map-detail");
  if (!box) return;
  const translated = focusType === "city"
    ? (tv("city", focusName) || focusName)
    : (tv("country", focusName) || focusName);
  const msg = state.lang === "zh"
    ? "当前时间范围内无匹配订单"
    : "No shipments in the selected time range";

  box.innerHTML = `
    <div class="map-focus-label" style="display:flex;">
      <span>${t("map.focus")}:</span>
      <span class="focus-name">${escapeHtml(translated)}</span>
      <span class="focus-hint">${t("map.focusHint")}</span>
    </div>
    <div class="detail-item" style="grid-column: 1 / -1;">
      <span class="detail-value" style="color: var(--text-3); font-size: 13px; font-weight: 500;">
        ${escapeHtml(msg)}
      </span>
    </div>
  `;
  box.classList.remove("hidden");
}

function renderFocusError(focusType, focusName, error) {
  const box = $("map-detail");
  if (!box) return;
  const translated = focusType === "city"
    ? (tv("city", focusName) || focusName)
    : (tv("country", focusName) || focusName);
  const msg = state.lang === "zh"
    ? `加载失败：${error}`
    : `Failed to load: ${error}`;

  box.innerHTML = `
    <div class="map-focus-label" style="display:flex;">
      <span>${t("map.focus")}:</span>
      <span class="focus-name">${escapeHtml(translated)}</span>
      <span class="focus-hint">${t("map.focusHint")}</span>
    </div>
    <div class="detail-item" style="grid-column: 1 / -1;">
      <span class="detail-value" style="color: var(--danger); font-size: 13px; font-weight: 500;">
        ${escapeHtml(msg)}
      </span>
    </div>
  `;
  box.classList.remove("hidden");
}

function renderFocusDetail(res) {
  const box = $("map-detail");
  if (!box) return;
  const m = res.focus_metrics || {};
  const focusName = res.focus_name;
  const focusType = res.focus_type;
  const translated = focusType === "city"
    ? (tv("city", focusName) || focusName)
    : (tv("country", focusName) || focusName);

  box.innerHTML = `
    <div class="map-focus-label" style="display:flex;">
      <span>${t("map.focus")}:</span>
      <span class="focus-name">${escapeHtml(translated)}</span>
      <span class="focus-hint">${t("map.focusHint")}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.shipments")}</span>
      <span class="detail-value">${(m.total_shipments || 0).toLocaleString()}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.delay")}</span>
      <span class="detail-value warn">${m.delay_rate == null ? "—" : m.delay_rate + "%"}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.otif")}</span>
      <span class="detail-value ok">${m.otif_rate == null ? "—" : m.otif_rate + "%"}</span>
    </div>
    <div class="detail-item">
      <span class="detail-label">${t("map.detail.revenue")}</span>
      <span class="detail-value">${fmtFullCurrency(m.revenue)}</span>
    </div>
  `;
  box.classList.remove("hidden");
}

// =============================================================
// Tables
// =============================================================
function renderLanesTable() {
  const rows = state.lastData?.lanes || [];
  $("lane-count").textContent = state.lang === "zh"
    ? `${rows.length} 条线路` : `${rows.length} lanes`;
  const tbody = document.querySelector("#lane-table tbody");
  if (!tbody) return;
  if (!rows.length) { tbody.innerHTML = `<tr class="empty-row"><td colspan="5">—</td></tr>`; return; }
  tbody.innerHTML = rows.map((l) => `
    <tr>
      <td>${escapeHtml(translateLane(l.lane))}</td>
      <td>${(l.total_shipments || 0).toLocaleString()}</td>
      <td>${l.delay_rate == null ? "—" : `<span class="${l.delay_rate > 15 ? "delay-badge" : "ok-badge"}">${l.delay_rate}%</span>`}</td>
      <td>${l.otif_rate == null ? "—" : l.otif_rate + "%"}</td>
      <td>${fmtFullCurrency(l.revenue)}</td>
    </tr>
  `).join("");
}

function renderCountriesTable() {
  const rows = state.lastData?.countries || [];
  $("country-count").textContent = state.lang === "zh"
    ? `${rows.length} 个国家` : `${rows.length} countries`;
  const tbody = document.querySelector("#country-table tbody");
  if (!tbody) return;
  if (!rows.length) { tbody.innerHTML = `<tr class="empty-row"><td colspan="6">—</td></tr>`; return; }
  tbody.innerHTML = rows.map((c, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${escapeHtml(tv("country", c.name))}</td>
      <td>${escapeHtml(tv("continent", c.continent || ""))}</td>
      <td>${(c.total_shipments || 0).toLocaleString()}</td>
      <td>${c.delay_rate == null ? "—" : `<span class="${c.delay_rate > 15 ? "delay-badge" : "ok-badge"}">${c.delay_rate}%</span>`}</td>
      <td>${c.otif_rate == null ? "—" : c.otif_rate + "%"}</td>
    </tr>
  `).join("");
}

function renderCitiesTable(cities, highlightCity, countryName) {
  const rows = cities || [];
  const cnt = $("city-count");
  const title = $("city-table-title");
  const tbody = document.querySelector("#city-table tbody");
  if (!cnt || !title || !tbody) return;
  if (!rows.length) {
    title.textContent = t("table.cityDetail");
    cnt.textContent = t("table.selectCountry");
    tbody.innerHTML = `<tr class="empty-row"><td colspan="5">—</td></tr>`;
    return;
  }
  if (countryName) {
    title.textContent = `${t("table.cityDetail")} — ${tv("country", countryName)}`;
  } else {
    title.textContent = t("table.cityDetail");
  }
  cnt.textContent = state.lang === "zh" ? `${rows.length} 个城市` : `${rows.length} cities`;
  tbody.innerHTML = rows.map((c) => {
    const isHighlight = highlightCity && c.name === highlightCity;
    return `
      <tr class="${isHighlight ? "city-highlight" : ""}">
        <td>${escapeHtml(tv("city", c.name))}</td>
        <td>${(c.total_shipments || 0).toLocaleString()}</td>
        <td>${c.delay_rate == null ? "—" : `<span class="${c.delay_rate > 15 ? "delay-badge" : "ok-badge"}">${c.delay_rate}%</span>`}</td>
        <td>${c.otif_rate == null ? "—" : c.otif_rate + "%"}</td>
        <td>${fmtFullCurrency(c.revenue)}</td>
      </tr>
    `;
  }).join("");
}

function renderAtRiskTable() {
  const rows = state.lastData?.at_risk || [];
  $("atrisk-count").textContent = state.lang === "zh"
    ? `${rows.length} 单` : `${rows.length} shipments`;
  const tbody = document.querySelector("#atrisk-table tbody");
  if (!tbody) return;
  if (!rows.length) { tbody.innerHTML = `<tr class="empty-row"><td colspan="6">—</td></tr>`; return; }
  tbody.innerHTML = rows.map((s) => {
    const days = s.days_left;
    let risk = "";
    if (days < 0) risk = `<span class="overdue-badge">+${Math.abs(days)}${state.lang === "zh" ? "天" : "d"}</span>`;
    else if (days <= 1) risk = `<span class="delay-badge">${days}${state.lang === "zh" ? "天" : "d"}</span>`;
    else risk = `<span class="ok-badge">${days}${state.lang === "zh" ? "天" : "d"}</span>`;
    return `
      <tr>
        <td>${s.shipment_id}</td>
        <td>${escapeHtml(tv("carrier", s.carrier))}</td>
        <td>${escapeHtml(tv("country", s.destination_country || ""))}</td>
        <td>${s.expected_delivery_date || "—"}</td>
        <td>${days} ${state.lang === "zh" ? "天" : "d"}</td>
        <td>${risk}</td>
      </tr>
    `;
  }).join("");
}

function renderExceptions() {
  const rows = (state.lastData?.exceptions || []).filter((s) => {
    const q = ($("search-input")?.value || "").toLowerCase();
    if (!q) return true;
    return s.shipment_id.toLowerCase().includes(q)
      || (s.carrier || "").toLowerCase().includes(q)
      || (s.destination_country || "").toLowerCase().includes(q);
  });
  const tbody = document.querySelector("#exception-table tbody");
  if (!tbody) return;
  if (!rows.length) { tbody.innerHTML = `<tr class="empty-row"><td colspan="7">—</td></tr>`; return; }
  tbody.innerHTML = rows.map((s) => `
    <tr>
      <td>${s.shipment_id}</td>
      <td>${escapeHtml(tv("carrier", s.carrier))}</td>
      <td>${escapeHtml(tv("country", s.destination_country || ""))}</td>
      <td>${s.expected_delivery_date || "—"}</td>
      <td>${s.actual_delivery_date || "—"}</td>
      <td><span class="delay-badge">+${s.delay_days}${state.lang === "zh" ? "天" : "d"}</span></td>
      <td>${escapeHtml(tv("reason", s.delay_reason || "Unknown"))}</td>
    </tr>
  `).join("");
}

function renderAllShipments() {
  const rows = state.lastData?.all_shipments || [];
  $("all-count").textContent = state.lang === "zh" ? `${rows.length} 行` : `${rows.length} rows`;
  const tbody = document.querySelector("#all-table tbody");
  if (!tbody) return;
  if (!rows.length) { tbody.innerHTML = `<tr class="empty-row"><td colspan="7">—</td></tr>`; return; }
  tbody.innerHTML = rows.map((s) => {
    let delay = null;
    if (s.actual_delivery_date && s.expected_delivery_date) {
      delay = Math.round(
        (new Date(s.actual_delivery_date) - new Date(s.expected_delivery_date)) / 86400000
      );
    }
    const stCls = s.status === "Delivered" ? "status-delivered"
                : s.status === "In Transit" ? "status-in-transit" : "status-exception";
    const onTime = delay != null && delay <= 0;
    const onTimeTxt = delay == null ? "—"
      : onTime ? `<span class="ok-badge">${state.lang === "zh" ? "是" : "Yes"}</span>`
               : `<span class="overdue-badge">${state.lang === "zh" ? "否" : "No"}</span>`;
    const delayTxt = delay == null ? "—"
      : delay > 0 ? `<span class="delay-badge">+${delay}${state.lang === "zh" ? "天" : "d"}</span>`
                  : `<span class="ok-badge">${delay}${state.lang === "zh" ? "天" : "d"}</span>`;
    return `
      <tr>
        <td>${s.shipment_id}</td>
        <td>${escapeHtml(tv("carrier", s.carrier))}</td>
        <td>${escapeHtml(tv("country", s.destination_country || ""))}</td>
        <td>${s.ship_date || "—"}</td>
        <td><span class="${stCls}">${tv("status", s.status)}</span></td>
        <td>${onTimeTxt}</td>
        <td>${delayTxt}</td>
      </tr>
    `;
  }).join("");
}

function renderDataTables() {
  if (!state.lastData) return;
  const d = state.lastData;

  $("dstat-total").textContent = fmtNum(d.metrics.total_shipments);
  $("dstat-delivered").textContent = fmtNum(d.metrics.delivered_count);
  $("dstat-delayed").textContent = fmtNum(d.metrics.delayed_count);
  $("dstat-transit").textContent = fmtNum(d.metrics.in_transit_count);
  $("dstat-exception").textContent = fmtNum(d.metrics.exception_count);

  const excQuery = ($("d-search-exc")?.value || "").toLowerCase();
  const excRows = (d.exceptions || []).filter((s) =>
    !excQuery || s.shipment_id.toLowerCase().includes(excQuery)
      || (s.carrier || "").toLowerCase().includes(excQuery)
      || (s.destination_country || "").toLowerCase().includes(excQuery)
  );
  $("d-exc-count").textContent = state.lang === "zh" ? `${excRows.length} 行` : `${excRows.length} rows`;
  const excTbody = document.querySelector("#data-exception-table tbody");
  if (!excTbody) return;
  if (!excRows.length) {
    excTbody.innerHTML = `<tr class="empty-row"><td colspan="8">—</td></tr>`;
  } else {
    excTbody.innerHTML = excRows.map((s) => `
      <tr>
        <td>${s.shipment_id}</td>
        <td>${escapeHtml(tv("carrier", s.carrier))}</td>
        <td>${escapeHtml(tv("country", s.destination_country || ""))}</td>
        <td>${escapeHtml(tv("city", s.destination || ""))}</td>
        <td>${s.expected_delivery_date || "—"}</td>
        <td>${s.actual_delivery_date || "—"}</td>
        <td><span class="delay-badge">+${s.delay_days}${state.lang === "zh" ? "天" : "d"}</span></td>
        <td>${escapeHtml(tv("reason", s.delay_reason || "Unknown"))}</td>
      </tr>
    `).join("");
  }

  const allQuery = ($("d-search-all")?.value || "").toLowerCase();
  const allRows = (d.all_shipments || []).filter((s) =>
    !allQuery || s.shipment_id.toLowerCase().includes(allQuery)
      || (s.carrier || "").toLowerCase().includes(allQuery)
      || (s.destination_country || "").toLowerCase().includes(allQuery)
      || (s.destination || "").toLowerCase().includes(allQuery)
  );
  $("d-all-count").textContent = state.lang === "zh" ? `${allRows.length} 行` : `${allRows.length} rows`;
  const allTbody = document.querySelector("#data-all-table tbody");
  if (!allTbody) return;
  if (!allRows.length) {
    allTbody.innerHTML = `<tr class="empty-row"><td colspan="10">—</td></tr>`;
  } else {
    allTbody.innerHTML = allRows.map((s) => {
      let delay = null;
      if (s.actual_delivery_date && s.expected_delivery_date) {
        delay = Math.round(
          (new Date(s.actual_delivery_date) - new Date(s.expected_delivery_date)) / 86400000
        );
      }
      const stCls = s.status === "Delivered" ? "status-delivered"
                  : s.status === "In Transit" ? "status-in-transit" : "status-exception";
      const onTime = delay != null && delay <= 0;
      const onTimeTxt = delay == null ? "—"
        : onTime ? `<span class="ok-badge">${state.lang === "zh" ? "是" : "Yes"}</span>`
                 : `<span class="overdue-badge">${state.lang === "zh" ? "否" : "No"}</span>`;
      const delayTxt = delay == null ? "—"
        : delay > 0 ? `<span class="delay-badge">+${delay}${state.lang === "zh" ? "天" : "d"}</span>`
                    : `<span class="ok-badge">${delay}${state.lang === "zh" ? "天" : "d"}</span>`;
      return `
        <tr>
          <td>${s.shipment_id}</td>
          <td>${escapeHtml(tv("carrier", s.carrier))}</td>
          <td>${escapeHtml(tv("country", s.destination_country || ""))}</td>
          <td>${escapeHtml(tv("city", s.destination || ""))}</td>
          <td>${escapeHtml(tv("priority", s.priority || "Standard"))}</td>
          <td>${s.ship_date || "—"}</td>
          <td><span class="${stCls}">${tv("status", s.status)}</span></td>
          <td>${onTimeTxt}</td>
          <td>${delayTxt}</td>
          <td>${fmtFullCurrency(s.shipping_cost)}</td>
        </tr>
      `;
    }).join("");
  }
}

function renderCostSummary(cb, m) {
  if (!cb) return;
  $("cost-line").textContent = fmtCurrency(cb.line_haul);
  $("cost-fuel").textContent = fmtCurrency(cb.fuel);
  $("cost-acc").textContent = fmtCurrency(cb.accessorial);
  $("cost-det").textContent = fmtCurrency(cb.detention);
  $("cost-avg").textContent = m && m.avg_cost_per_shipment != null
    ? fmtCurrency(m.avg_cost_per_shipment) : "—";
}

function renderDataQuality(dq) {
  if (!dq) return;
  const items = [
    [t("dq.total"), dq.total.toLocaleString()],
    [t("dq.missingExpected"), dq.missing_expected_date.toLocaleString()],
    [t("dq.missingActual"), dq.missing_actual_date.toLocaleString()],
    [t("dq.quality"), (dq.quality_pct ?? "—") + "%"],
  ];
  $("data-quality").innerHTML = items.map(([k, v]) => `
    <div class="dq-item">
      <div class="dq-label">${k}</div>
      <div class="dq-value">${v}</div>
    </div>
  `).join("");
}

function toggleAppendix() {
  state._appendixOpen = !state._appendixOpen;
  $("appendix-body").classList.toggle("hidden", !state._appendixOpen);
  $("appendix-icon").classList.toggle("open", state._appendixOpen);
}

// =============================================================
// Report
// =============================================================
function renderReport(data) {
  const m = data.metrics;
  if (!m || !m.total_shipments) { $("report-body").textContent = t("report.empty"); return; }
  const carriers = data.carriers || [];
  const countries = data.countries || [];
  const reasons = data.delay_reasons || [];
  const lanes = data.lanes || [];
  const L = state.lang;
  const lines = [];
  const worstCarrier = findWorstCarrier(carriers);
  const worstCountry = countries[0];
  const worstLane = findWorstLane(lanes);

  if (L === "zh") {
    lines.push(`**${t("report.volume")}**：共 ${m.total_shipments.toLocaleString()} 个包裹，已送达 ${m.delivered_count.toLocaleString()} 个，在途 ${m.in_transit_count.toLocaleString()} 个，异常 ${m.exception_count.toLocaleString()} 个。`);
  } else {
    lines.push(`**${t("report.volume")}**: ${m.total_shipments.toLocaleString()} shipments · ${m.delivered_count.toLocaleString()} delivered · ${m.in_transit_count.toLocaleString()} in transit · ${m.exception_count.toLocaleString()} exception.`);
  }
  if (m.delivered_count) {
    if (L === "zh") {
      lines.push(`**${t("report.quality")}**：延误率 ${m.delay_rate}%，准时率 ${m.on_time_rate}%，OTIF ${m.otif_rate}%，平均延误 ${m.avg_delay_days} 天。`);
    } else {
      lines.push(`**${t("report.quality")}**: delay ${m.delay_rate}% · on-time ${m.on_time_rate}% · OTIF ${m.otif_rate}% · avg delay ${m.avg_delay_days}d.`);
    }
  }
  if (m.p90_delay_days != null) {
    if (L === "zh") lines.push(`**${t("report.p90")}**：P90 延误 ${m.p90_delay_days} 天，即最差 10% 的用户至少等了这么长时间。`);
    else lines.push(`**${t("report.p90")}**: P90 delay ${m.p90_delay_days}d — worst 10% waited at least this long.`);
  }
  if (m.eta_accuracy_rate != null) {
    if (L === "zh") lines.push(`**${t("report.eta")}**：±1 天内的 ETA 准确率 ${m.eta_accuracy_rate}%。`);
    else lines.push(`**${t("report.eta")}**: ${m.eta_accuracy_rate}% within ±1 day.`);
  }
  if (worstCarrier) {
    if (L === "zh") lines.push(`**${t("report.worstCarrier")}**：${tv("carrier", worstCarrier.name)}，延误率 ${worstCarrier.delay_rate}%，样本 ${worstCarrier.total_shipments.toLocaleString()} 个。`);
    else lines.push(`**${t("report.worstCarrier")}**: ${tv("carrier", worstCarrier.name)} — ${worstCarrier.delay_rate}% delay over ${worstCarrier.total_shipments.toLocaleString()} shipments.`);
  }
  if (worstCountry && worstCountry.delay_rate != null) {
    if (L === "zh") lines.push(`**${t("report.worstCountry")}**：${tv("country", worstCountry.name)}，延误率 ${worstCountry.delay_rate}%，收入 ${fmtFullCurrency(worstCountry.revenue)}。`);
    else lines.push(`**${t("report.worstCountry")}**: ${tv("country", worstCountry.name)} — ${worstCountry.delay_rate}% delay · revenue ${fmtFullCurrency(worstCountry.revenue)}.`);
  }
  if (reasons.length) {
    if (L === "zh") lines.push(`**${t("report.topReason")}**：${tv("reason", reasons[0].name)}（${reasons[0].count.toLocaleString()} 单）。`);
    else lines.push(`**${t("report.topReason")}**: ${tv("reason", reasons[0].name)} (${reasons[0].count.toLocaleString()} cases).`);
  }
  const rs = data.range_stats;
  if (rs && rs.active && rs.total_delayed) {
    const mn = rs.range_min, mx = rs.range_max;
    const rangeTxt = mx ? `${mn}–${mx}${L === "zh" ? " 天" : "d"}` : `≥${mn}${L === "zh" ? " 天" : "d"}`;
    if (L === "zh") lines.push(`**${t("report.range")} [${rangeTxt}]**：${rs.range_delayed.toLocaleString()} 个包裹（占所有延误 ${rs.pct_of_delayed}%，占总订单 ${rs.pct_of_total}%）。`);
    else lines.push(`**${t("report.range")} [${rangeTxt}]**: ${rs.range_delayed.toLocaleString()} shipments (${rs.pct_of_delayed}% of delayed · ${rs.pct_of_total}% of total).`);
  }
  if (worstLane) {
    if (L === "zh") lines.push(`**${t("report.worstLane")}**：${translateLane(worstLane.lane)}，延误率 ${worstLane.delay_rate}%。`);
    else lines.push(`**${t("report.worstLane")}**: ${worstLane.lane} — ${worstLane.delay_rate}% delay.`);
  }
  if (m.at_risk_count) {
    if (L === "zh") lines.push(`**${t("report.atRisk")}**：当前有 ${m.at_risk_count} 个在途订单存在 SLA 违约风险。`);
    else lines.push(`**${t("report.atRisk")}**: ${m.at_risk_count} in-transit shipments at risk of missing their SLA.`);
  }
  const steps = [];
  if (worstCarrier) {
    steps.push(fmt(t("report.step1"), {
      carrier: tv("carrier", worstCarrier.name),
      rate: worstCarrier.delay_rate,
      count: worstCarrier.total_shipments.toLocaleString(),
    }));
  }
  if (worstCountry && worstCountry.delay_rate != null) {
    steps.push(fmt(t("report.step2"), {
      country: tv("country", worstCountry.name),
      rate: worstCountry.delay_rate,
    }));
  }
  steps.push(t("report.step3"));
  if (m.at_risk_count) steps.push(fmt(t("report.step4"), { count: m.at_risk_count }));
  if (worstLane) {
    steps.push(fmt(t("report.step5"), {
      lane: L === "zh" ? translateLane(worstLane.lane) : worstLane.lane,
      rate: worstLane.delay_rate,
    }));
  }
  lines.push(`**${t("report.nextSteps")}**：\n` + steps.map((s, i) => `${i + 1}. ${s}`).join("\n"));
  lines.push(t("report.disclaimer"));

  const html = escapeHtml(lines.join("\n\n"))
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^&gt;\s?(.+)$/gm, "<blockquote>$1</blockquote>")
    .replace(/\n/g, "<br>");
  $("report-body").innerHTML = html;
}

// =============================================================
// AI Assistant
// =============================================================
function toggleAIPanel() {
  if (state.readonly) { toastT("toast.readonly", "", "error"); return; }
  const panel = $("ai-panel");
  if (!panel) return;
  const isOpen = !panel.classList.contains("hidden");
  if (isOpen) {
    panel.classList.add("hidden");
    $("main-content").classList.remove("with-ai");
  } else {
    panel.classList.remove("hidden");
    $("main-content").classList.add("with-ai");
    if (!$("chat-log").innerHTML.trim()) resetChat();
  }
}
function resetChat() {
  const log = $("chat-log");
  if (!log) return;
  log.innerHTML = "";
  state._chatHistory = [];
  state._lastIntent = null;
  addChat("assistant", t("chat.welcome"));
  renderChatOptions(defaultOptions());
}
function addChat(role, text) {
  const log = $("chat-log");
  if (!log) return;
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.innerHTML = escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  state._chatHistory.push({ role, text });
  if (state._chatHistory.length > 6) state._chatHistory = state._chatHistory.slice(-6);
}
function defaultOptions() {
  return ["delay", "carrier", "country", "otif", "atrisk", "revenue", "cost", "optimize"];
}
function renderChatOptions(options) {
  const box = $("chat-options");
  if (!box) return;
  if (!options || !options.length) { box.innerHTML = ""; return; }
  box.innerHTML = options.map((k) =>
    `<button class="opt-btn" data-opt="${k}">${t("qa.opt." + k)}</button>`
  ).join("");
  box.querySelectorAll(".opt-btn").forEach((btn) => {
    btn.addEventListener("click", () => handleQuestion(btn.dataset.opt, true));
  });
}
function sendAssistant() {
  const input = $("chat-input");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  handleQuestion(text, false);
}
function matchIntent(text) {
  const s = text.toLowerCase();
  if (/(延误|延迟|delay|late|slip)/.test(s)) return "delay";
  if (/(承运商|物流商|carrier|shipping company|快递)/.test(s)) return "carrier";
  if (/(国家|地区|country|destination|map|地图)/.test(s)) return "country";
  if (/(收入|revenue|金额|money|sales)/.test(s)) return "revenue";
  if (/(成本|cost)/.test(s)) return "cost";
  if (/(otif|准时且完整|on.time.*in.full)/.test(s)) return "otif";
  if (/(在途|风险|at.risk|at-risk|overdue)/.test(s)) return "atrisk";
  if (/(优化|改善|improve|optimize|suggest|建议|recommend|怎么)/.test(s)) return "optimize";
  return null;
}
async function handleQuestion(textOrKey, isKey) {
  if (!state.lastData) { addChat("assistant", t("chat.noData")); return; }

  // 快捷按钮：走本地规则，零延迟
  if (isKey) {
    addChat("user", t("qa.opt." + textOrKey));
    state._lastIntent = textOrKey;
    answerIntent(textOrKey, state.lastData);
    return;
  }

  // 自由文本：调 LLM
  addChat("user", textOrKey);

  const loadingEl = document.createElement("div");
  loadingEl.className = "chat-msg assistant";
  loadingEl.innerHTML = '<span style="opacity:0.6;">思考中…</span>';
  $("chat-log").appendChild(loadingEl);
  $("chat-log").scrollTop = $("chat-log").scrollHeight;

  const fallback = () => {
    const intent = matchIntent(textOrKey) || state._lastIntent;
    if (intent) {
      state._lastIntent = intent;
      answerIntent(intent, state.lastData);
    } else {
      addChat("assistant", t("chat.fallback"));
      renderChatOptions(defaultOptions());
    }
  };

  try {
    const d = state.lastData;
    const res = await api("/api/assistant", {
      method: "POST",
      body: JSON.stringify({
        question: textOrKey,
        report: {
          metrics: d.metrics,
          carriers: (d.carriers || []).slice(0, 5),
          countries: (d.countries || []).slice(0, 5),
          delay_reasons: (d.delay_reasons || []).slice(0, 5),
          cost_breakdown: d.cost_breakdown,
          range_stats: d.range_stats,
        },
      }),
    });

    loadingEl.remove();

    if (res.answer) {
      addChat("assistant", res.answer);
      renderChatOptions(defaultOptions());
    } else {
      fallback();
    }
  } catch (e) {
    loadingEl.remove();
    fallback();
  }
}

function answerIntent(intent, data) {
  const m = data.metrics;
  const carriers = data.carriers || [];
  const countries = data.countries || [];
  const reasons = data.delay_reasons || [];
  const cb = data.cost_breakdown || {};
  let msg = "";
  const worst = findWorstCarrier(carriers);
  const best = findBestCarrier(carriers);
  const worstCountry = countries[0];

  if (intent === "delay") {
    msg = fmt(t("qa.delay"), {
      delay_rate: m.delay_rate ?? 0, delayed: m.delayed_count ?? 0,
      total: m.total_shipments ?? 0, avg: m.avg_delay_days ?? 0,
      p90: m.p90_delay_days ?? 0,
      reason: reasons[0] ? tv("reason", reasons[0].name) : "—",
    });
  } else if (intent === "carrier") {
    msg = fmt(t("qa.carrier"), {
      worst: worst ? tv("carrier", worst.name) : "—",
      worstRate: worst?.delay_rate ?? 0,
      best: best ? tv("carrier", best.name) : "—",
      bestRate: best?.delay_rate ?? 0,
    });
  } else if (intent === "country") {
    msg = fmt(t("qa.country"), {
      name: worstCountry ? tv("country", worstCountry.name) : "—",
      rate: worstCountry?.delay_rate ?? 0,
      count: worstCountry?.total_shipments ?? 0,
    });
  } else if (intent === "revenue") {
    msg = fmt(t("qa.revenue"), {
      revenue: (m.revenue || 0).toLocaleString(),
      avgCost: (m.avg_cost_per_shipment || 0).toLocaleString(),
    });
  } else if (intent === "cost") {
    msg = fmt(t("qa.cost"), {
      lineHaul: (cb.line_haul || 0).toLocaleString(),
      fuel: (cb.fuel || 0).toLocaleString(),
      accessorial: (cb.accessorial || 0).toLocaleString(),
      detention: (cb.detention || 0).toLocaleString(),
    });
  } else if (intent === "otif") {
    msg = fmt(t("qa.otif"), {
      rate: m.otif_rate ?? 0, count: m.otif_count ?? 0,
      delivered: m.delivered_count ?? 0,
    });
  } else if (intent === "atrisk") {
    msg = fmt(t("qa.atrisk"), { count: m.at_risk_count ?? 0 });
  } else if (intent === "optimize") {
    msg = fmt(t("qa.optimize"), {
      worstCarrier: worst ? tv("carrier", worst.name) : "—",
      worstCarrierRate: worst?.delay_rate ?? 0,
      worstCountry: worstCountry ? tv("country", worstCountry.name) : "—",
      worstCountryRate: worstCountry?.delay_rate ?? 0,
      topReason: reasons[0] ? tv("reason", reasons[0].name) : "—",
    });
  }
  addChat("assistant", msg || t("chat.fallback"));
  renderChatOptions(defaultOptions());
}

// =============================================================
// Save / auto-save / Share / Export / Versions
// =============================================================
function markUnsaved() {
  state._isDirty = true;
  const el = $("save-status");
  if (el) {
    el.textContent = t("ws.unsaved");
    el.classList.remove("saved");
  }
}
function setSaved() {
  state._isDirty = false;
  const el = $("save-status");
  if (el) {
    el.textContent = t("ws.saved");
    el.classList.add("saved");
  }
}

async function autoSaveProject() {
  if (state.readonly) return;
  if (!state.currentProjectId) return;
  if (!state.lastData) return;

  const statusEl = $("save-status");
  if (statusEl) {
    statusEl.textContent = state.lang === "zh" ? "保存中…" : "Saving…";
    statusEl.classList.remove("saved");
  }

  try {
    await api(`/api/projects/${state.currentProjectId}`, {
      method: "PUT",
      body: JSON.stringify({
        title: state.currentTitle || $("rp-title")?.textContent || "Untitled",
        config: state.config,
        filters: state.filters,
        summary: summaryToJSON(),
      }),
    });
    setSaved();
    loadHistory();
  } catch (e) {
    console.error("[autoSave] failed:", e);
    if (statusEl) {
      statusEl.textContent = state.lang === "zh" ? "保存失败" : "Save failed";
      statusEl.classList.remove("saved");
    }
  }
}

// 兼容保留（旧按钮可能引用）
async function saveProject() {
  await autoSaveProject();
}

function summaryToJSON() {
  if (!state.lastData?.metrics) return "";
  const m = state.lastData.metrics;
  return JSON.stringify({
    delay_rate: m.delay_rate, otif_rate: m.otif_rate, shipments: m.total_shipments,
  });
}
function formatSummaryJSON(raw) {
  if (!raw) return "—";
  let d;
  try { d = typeof raw === "string" ? JSON.parse(raw) : raw; }
  catch { return raw; }
  if (!d.shipments) return "—";
  if (state.lang === "zh") {
    return `${d.delay_rate}% 延误 · ${d.shipments.toLocaleString()} 单 · OTIF ${d.otif_rate}%`;
  }
  return `${d.delay_rate}% delay · ${d.shipments.toLocaleString()} shipments · OTIF ${d.otif_rate}%`;
}
async function exportCSV() {
  const res = await fetch("/api/export", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filters: state.filters }),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "routemind_exceptions.csv"; a.click();
  URL.revokeObjectURL(url);
  toastT("toast.saved", "", "success");
}
function printReport() { window.print(); }
async function shareProject() {
  if (!state.currentProjectId) { toastT("toast.saveFirst", "", "error"); return; }
  const res = await api(`/api/projects/${state.currentProjectId}/share`, { method: "POST" });
  const fullUrl = `${location.origin}${res.url}`;
  await navigator.clipboard.writeText(fullUrl).catch(() => {});
  toastT("toast.copied", fullUrl, "success");
}
async function showVersions() {
  if (!state.currentProjectId) { toastT("toast.noProject", "", "error"); return; }
  if (state.readonly) { toastT("toast.readonly", "", "error"); return; }
  const versions = await api(`/api/projects/${state.currentProjectId}/versions`);
  if (!versions.length) { toastT("toast.noVersions"); return; }
  const list = versions.slice(0, 10).map((v, i) =>
    `${i + 1}. ${new Date(v.created_at).toLocaleString()}`
  ).join("\n");
  const promptMsg = state.lang === "zh"
    ? `历史版本：\n${list}\n\n输入序号恢复（1-${Math.min(10, versions.length)}）：`
    : `Version history:\n${list}\n\nEnter number to restore (1-${Math.min(10, versions.length)}):`;
  const pick = prompt(promptMsg, "1");
  if (!pick) return;
  const idx = parseInt(pick) - 1;
  if (idx < 0 || idx >= versions.length) return;
  try {
    const res = await api(
      `/api/projects/${state.currentProjectId}/versions/${versions[idx].version_id}/restore`,
      { method: "POST" }
    );
    if (res.ok) {
      state.filters = res.filters;
      if (res.config) state.config = res.config;
      syncFiltersToUI("f"); syncFiltersToUI("d");
      await compute();
      toastT("toast.versionRestored", "", "success");
    }
  } catch (e) { console.error(e); }
}

// =============================================================
// History
// =============================================================
async function loadHistory() {
  try {
    const res = await fetch("/api/projects", {
      headers: { "Content-Type": "application/json" },
    });
    if (res.status === 401) {
      state.history = []; state.historyError = false; renderHistory(); return;
    }
    if (!res.ok) {
      state.history = []; state.historyError = true; renderHistory(); return;
    }
    const data = await res.json().catch(() => null);
    if (Array.isArray(data)) {
      state.history = data; state.historyError = false;
    } else {
      state.history = []; state.historyError = true;
    }
    renderHistory();
  } catch (e) {
    console.error(e);
    state.history = []; state.historyError = true;
    renderHistory();
  }
}

function groupByTime(items) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1);
  const weekAgo = new Date(today); weekAgo.setDate(today.getDate() - 7);
  const groups = { today: [], yesterday: [], week: [], older: [] };
  items.forEach(p => {
    const d = new Date(p.updated_at);
    if (d >= today) groups.today.push(p);
    else if (d >= yesterday) groups.yesterday.push(p);
    else if (d >= weekAgo) groups.week.push(p);
    else groups.older.push(p);
  });
  return Object.fromEntries(Object.entries(groups).filter(([_, v]) => v.length));
}

function renderHistory() {
  const list = $("history-list");
  if (!list) return;

  const arr = Array.isArray(state.history) ? state.history : [];

  if (!arr.length) {
    list.innerHTML = `<div class="history-empty">${t("history.empty")}</div>`;
    return;
  }

  const groups = groupByTime(arr);
  const groupLabels = {
    today: t("history.today"),
    yesterday: t("history.yesterday"),
    week: t("history.week"),
    older: t("history.older"),
  };

  list.innerHTML = Object.entries(groups).map(([key, items]) => `
    <div class="history-group-label">${groupLabels[key]}</div>
    ${items.map(p => {
      const active = p.id === state.currentProjectId ? "active" : "";
      return `
        <div class="history-item ${active}" onclick="openProject('${p.id}')"
             title="${escapeHtml(formatSummaryJSON(p.summary))}">
          <span class="hi-title">${escapeHtml(translateTitle(p.title))}</span>
          <span class="hi-actions">
            <button class="icon-btn tiny"
                    onclick="event.stopPropagation(); deleteProject('${p.id}')">✕</button>
          </span>
        </div>
      `;
    }).join("")}
  `).join("");
}

async function openProject(id) {
  console.log("[openProject] start:", id);
  try {
    const p = await api(`/api/projects/${id}`);
    if (!p || !p.id) {
      toastT("toast.notFound", "", "error");
      return;
    }
    state.currentProjectId = p.id;
    state.config = p.config || {};
    state.currentTitle = p.title || "Untitled";
    state.filters = p.filters || {};
    state.readonly = false;

    if ($("rp-title")) $("rp-title").textContent = translateTitle(state.currentTitle);
    if ($("rp-subtitle")) $("rp-subtitle").textContent = (p.prompt || "").slice(0, 100);

    await loadFilterOptions();
    syncFiltersToUI("f");
    syncFiltersToUI("d");
    switchView("report");
    await compute();

    if (!state.lastData) {
      toastT("toast.computeFailed", "", "error");
      return;
    }

    setSaved();

    switchReportTab("report");
    resetChat();
    renderHistory();
    console.log("[openProject] DONE");
  } catch (e) {
    console.error("[openProject] failed:", e);
    hideLoading();
    toast(t("history.openFailed") + (e.message || "unknown"), "error");
  }
}

async function deleteProject(id) {
  if (!confirm(t("toast.deleteProject"))) return;
  await api(`/api/projects/${id}`, { method: "DELETE" });
  if (state.currentProjectId === id) {
    state.currentProjectId = null;
    state.lastData = null;
    state.currentTitle = "";
    switchView("home");
  }
  toastT("toast.deleted");
  loadHistory();
}

// =============================================================
// Shared view
// =============================================================
async function loadShared(token) {
  const p = await api(`/api/share/${token}`);
  if (!p.id) { toastT("toast.invalidShare", "", "error"); return; }
  state.currentProjectId = p.id;
  state.config = p.config || {};
  state.currentTitle = p.title;
  state.filters = p.filters || {};
  state.readonly = true;
  $("rp-title").textContent = translateTitle(p.title);
  $("rp-actions").style.display = "none";

  const aiBtn = $("ai-toggle-top");
  if (aiBtn) aiBtn.style.display = "none";
  $("ai-panel")?.classList.add("hidden");

  document.querySelectorAll(".filter select, .map-filters select, .map-filters button, .map-mode-switch button")
    .forEach((s) => s.disabled = true);
  document.querySelectorAll(".sidebar-new").forEach((e) => e.style.display = "none");

  await loadFilterOptions();
  syncFiltersToUI("f"); syncFiltersToUI("d");
  await compute();
  switchView("report");
  switchReportTab("report");

  $("chat-input").disabled = true;
  $("chat-input").placeholder = t("toast.readonly");
}

// =============================================================
// Settings
// =============================================================
function updateSettingsLabels() {
  if (!window.CURRENT_USER) return;
  $("set-role").textContent = window.CURRENT_USER.is_admin
    ? t("settings.admin") : t("settings.user");
}
function loadSettings() {
  if (!window.CURRENT_USER) return;
  $("set-username").textContent = window.CURRENT_USER.username;
  $("set-email").textContent = window.CURRENT_USER.email;
  updateSettingsLabels();
}
function evaluatePw(pw) {
  return {
    len: pw.length >= 8, upper: /[A-Z]/.test(pw),
    digit: /\d/.test(pw),
    symbol: /[!@#$%^&*()_\-+=\[\]{};:'",.<>/?\\|`~]/.test(pw),
  };
}
function updateSettingsStrength() {
  const el = $("set-new-pw");
  if (!el) return;
  const pw = el.value;
  const checks = evaluatePw(pw);
  const score = Object.values(checks).filter(Boolean).length;
  const map = [
    { w: "0%", color: "var(--border)", text: "—" },
    { w: "25%", color: "var(--danger)", text: t("settings.weak") },
    { w: "50%", color: "var(--warning)", text: t("settings.fair") },
    { w: "75%", color: "#eab308", text: t("settings.good") },
    { w: "100%", color: "var(--success)", text: t("settings.strong") },
  ];
  const s = map[Math.min(score, 4)];
  const fill = $("set-pw-fill"), label = $("set-pw-label");
  if (fill) { fill.style.width = s.w; fill.style.background = s.color; }
  if (label) label.textContent = `${t("settings.strength")}: ${s.text}`;
}
async function changePassword() {
  const oldPw = $("set-old-pw").value;
  const newPw = $("set-new-pw").value;
  const confirmPw = $("set-confirm-pw").value;
  if (!oldPw || !newPw) { toastT("toast.missingFields", "", "error"); return; }
  if (newPw !== confirmPw) { toastT("toast.passwordMismatch", "", "error"); return; }
  const checks = evaluatePw(newPw);
  if (!checks.len || !checks.upper || !checks.digit) {
    toastT("toast.passwordWeak", "", "error"); return;
  }
  const res = await api("/api/auth/change-password", {
    method: "POST",
    body: JSON.stringify({ old_password: oldPw, new_password: newPw, confirm: confirmPw }),
  });
  if (res.error) { toast(res.error, "error"); return; }
  toastT("toast.passwordUpdated", "", "success");
  $("set-old-pw").value = ""; $("set-new-pw").value = ""; $("set-confirm-pw").value = "";
  updateSettingsStrength();
}

// =============================================================
// Admin
// =============================================================
async function loadAdmin() {
  if (!window.CURRENT_USER?.is_admin) return;
  try {
    const stats = await api("/api/admin/stats");
    $("admin-stats").innerHTML = `
      <div class="stat-card"><div class="stat-label">${t("admin.users")}</div><div class="stat-value">${stats.users}</div></div>
      <div class="stat-card"><div class="stat-label">${t("admin.projects")}</div><div class="stat-value">${stats.projects}</div></div>
      <div class="stat-card"><div class="stat-label">${t("kpi.total")}</div><div class="stat-value">${stats.shipments.toLocaleString()}</div></div>`;
    await loadAdminUsers(1);
    await loadAudit();
  } catch (e) { toastT("toast.adminFailed", "", "error"); }
}
async function loadAdminUsers(page = 1) {
  const res = await api(`/api/admin/users?page=${page}`);
  const tbody = document.querySelector("#admin-users-table tbody");
  if (!tbody) return;
  tbody.innerHTML = res.users.map((u) => `
    <tr>
      <td>${u.id}</td>
      <td>${escapeHtml(u.username)}</td>
      <td>${escapeHtml(u.email)}</td>
      <td><span class="role-badge ${u.is_admin ? "role-admin" : "role-user"}">${u.is_admin ? t("admin.roleAdmin") : t("admin.roleUser")}</span></td>
      <td><span class="status-dot-sm ${u.is_active ? "status-active" : "status-inactive"}"></span>${u.is_active ? t("admin.active") : t("admin.disabled")}</td>
      <td>
        <button class="btn tiny" onclick="adminToggleActive(${u.id})">${u.is_active ? t("admin.disable") : t("admin.enable")}</button>
        <button class="btn tiny" onclick="adminToggleAdmin(${u.id})">${u.is_admin ? t("admin.revokeAdmin") : t("admin.makeAdmin")}</button>
        <button class="btn tiny danger" onclick="adminDeleteUser(${u.id})">${t("admin.delete")}</button>
      </td>
    </tr>`).join("") || `<tr class="empty-row"><td colspan="6">—</td></tr>`;
  $("admin-user-pagination").innerHTML = `
    <button ${res.page <= 1 ? "disabled" : ""} onclick="loadAdminUsers(${res.page - 1})">${t("admin.prev")}</button>
    <span>${res.page} / ${res.pages}</span>
    <button ${res.page >= res.pages ? "disabled" : ""} onclick="loadAdminUsers(${res.page + 1})">${t("admin.next")}</button>`;
  if (window.lucide) lucide.createIcons();
}
async function adminToggleActive(id) {
  const res = await api(`/api/admin/users/${id}/toggle-active`, { method: "POST" });
  if (res.error) { toast(res.error, "error"); return; }
  loadAdminUsers(1);
}
async function adminToggleAdmin(id) {
  const res = await api(`/api/admin/users/${id}/toggle-admin`, { method: "POST" });
  if (res.error) { toast(res.error, "error"); return; }
  loadAdminUsers(1);
}
async function adminDeleteUser(id) {
  if (!confirm(t("toast.deleteUser"))) return;
  const res = await api(`/api/admin/users/${id}`, { method: "DELETE" });
  if (res.error) { toast(res.error, "error"); return; }
  loadAdminUsers(1);
}
async function uploadCSV() {
  const file = $("csv-file").files[0];
  if (!file) { toastT("toast.selectCsv", "", "error"); return; }
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch("/api/admin/upload-csv", { method: "POST", body: fd }).then((r) => r.json());
  const box = $("csv-result");
  box.classList.remove("hidden");
  if (res.error) {
    box.className = "admin-result err";
    box.textContent = t("toast.csvUploadFailed") + res.error +
      (res.details ? "\n" + res.details.join("\n") : "");
    return;
  }
  box.className = "admin-result ok";
  box.textContent = state.lang === "zh"
    ? `成功导入 ${res.imported} 行${res.error_count ? `，跳过 ${res.error_count} 行` : ""}。`
    : `${res.imported} rows imported${res.error_count ? `, ${res.error_count} skipped` : ""}.`;
  toastT("toast.csvImported", "", "success");
  await loadFilterOptions();
  await loadAdmin();
}
async function simulateTick() {
  const res = await api("/api/admin/simulate-tick", { method: "POST" });
  if (res.error) { toast(res.error, "error"); return; }
  toast(state.lang === "zh"
    ? `新增 ${res.added} 条，总计 ${res.total.toLocaleString()} 条`
    : `+${res.added} rows. Total ${res.total.toLocaleString()}.`, "success");
  await loadFilterOptions();
  await loadAdmin();
}
async function loadAudit() {
  const rows = await api("/api/admin/audit");
  const tbody = document.querySelector("#audit-table tbody");
  if (!tbody) return;
  tbody.innerHTML = rows.map((r) => `
    <tr>
      <td>${new Date(r.created_at).toLocaleString()}</td>
      <td>${r.username || "—"}</td>
      <td>${r.action}</td>
      <td>${escapeHtml(r.detail || "")}</td>
    </tr>`).join("") || `<tr class="empty-row"><td colspan="4">—</td></tr>`;
}

// =============================================================
// Dashboard
// =============================================================
async function loadDashboard() {
  try {
    const data = await api("/api/dashboard");
    state.dashboardData = data;
    renderDashboard();
    if (window.CURRENT_USER?.is_admin) {
      $("dash-admin-card").style.display = "block";
    } else {
      $("dash-admin-card").style.display = "none";
    }
  } catch (e) {
    console.error(e);
    toast(state.lang === "zh" ? "加载失败" : "Failed to load dashboard", "error");
  }
}

function renderDashboard() {
  const d = state.dashboardData;
  if (!d) return;
  $("dash-total").textContent = (d.total || 0).toLocaleString();
  $("dash-last-updated").textContent = d.last_updated
    ? relativeTime(d.last_updated)
    : t("topbar.waiting");
  $("dash-quality").textContent = (d.data_quality?.quality_pct ?? "—") + "%";
  const missing = (d.data_quality?.missing_expected || 0)
    + (d.data_quality?.missing_actual || 0);
  $("dash-missing").textContent = missing.toLocaleString();

  const dq = d.data_quality || {};
  const dqItems = [
    [t("dashboard.missingExpected"), (dq.missing_expected || 0).toLocaleString()],
    [t("dashboard.missingActual"), (dq.missing_actual || 0).toLocaleString()],
    [t("dashboard.invalidStatus"), (dq.invalid_status || 0).toLocaleString()],
    [t("dashboard.validRatio"), (dq.quality_pct ?? "—") + "%"],
  ];
  $("dash-quality-detail").innerHTML = dqItems.map(([k, v]) => `
    <div class="dq-list-item">
      <span class="dq-list-label">${k}</span>
      <span class="dq-list-value">${v}</span>
    </div>
  `).join("");

  renderDashboardCharts();
}

function renderDashboardCharts() {
  const d = state.dashboardData;
  if (!d) return;
  const c = chartColors();

  if (charts.dashStatus) { charts.dashStatus.destroy(); charts.dashStatus = null; }
  const statusEl = $("dash-chart-status");
  if (statusEl) {
    const sd = d.status_distribution || {};
    const labels = Object.keys(sd);
    const values = Object.values(sd);
    const total = values.reduce((a, b) => a + b, 0) || 1;
    const colors = ["#34d399", "#60a5fa", "#f87171"];
    charts.dashStatus = new Chart(statusEl.getContext("2d"), {
      type: "doughnut",
      data: {
        labels: labels.map(k => tv("status", k)),
        datasets: [{ data: values, backgroundColor: colors, borderWidth: 3,
                     borderColor: state.theme === "dark" ? "#111827" : "#ffffff" }],
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: "58%",
        plugins: {
          legend: {
            position: "right",
            labels: {
              color: c.text, font: c.font, boxWidth: 10, padding: 12,
              generateLabels: () => labels.map((label, i) => ({
                text: `${tv("status", label)}  ${(values[i] || 0).toLocaleString()} (${((values[i] || 0) / total * 100).toFixed(1)}%)`,
                fillStyle: colors[i], strokeStyle: colors[i],
                lineWidth: 0, hidden: false, index: i, fontColor: c.text,
              })),
            },
          },
        }
      }
    });
  }

  if (charts.dashCarrier) { charts.dashCarrier.destroy(); charts.dashCarrier = null; }
  const carrierEl = $("dash-chart-carrier");
  if (carrierEl) {
    const carriers = d.carriers || [];
    charts.dashCarrier = new Chart(carrierEl.getContext("2d"), {
      type: "bar",
      data: {
        labels: carriers.map(x => tv("carrier", x.name)),
        datasets: [{
          data: carriers.map(x => x.count || 0),
          backgroundColor: "rgba(96,165,250,0.75)",
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, indexAxis: "y",
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: c.grid }, ticks: { color: c.text, font: c.font }, beginAtZero: true },
          y: { grid: { display: false }, ticks: { color: c.text, font: c.font } }
        }
      }
    });
  }

  if (charts.dashContinent) { charts.dashContinent.destroy(); charts.dashContinent = null; }
  const contEl = $("dash-chart-continent");
  if (contEl) {
    const conts = d.continents || [];
    charts.dashContinent = new Chart(contEl.getContext("2d"), {
      type: "bar",
      data: {
        labels: conts.map(x => tv("continent", x.name)),
        datasets: [{
          data: conts.map(x => x.count || 0),
          backgroundColor: "rgba(139,92,246,0.75)",
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, indexAxis: "y",
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: c.grid }, ticks: { color: c.text, font: c.font }, beginAtZero: true },
          y: { grid: { display: false }, ticks: { color: c.text, font: c.font } }
        }
      }
    });
  }
}

// =============================================================
// Database
// =============================================================
async function loadDatabase(page = 1) {
  state.dbPage = page;
  state.dbPerPage = parseInt($("db-per-page").value) || 50;
  state.dbFilters = {
    carrier: $("db-carrier").value,
    country: $("db-country").value,
    status: $("db-status").value,
    search: ($("db-search").value || "").trim(),
  };
  const params = new URLSearchParams({
    page: state.dbPage,
    per_page: state.dbPerPage,
  });
  if (state.dbFilters.carrier) params.append("carrier", state.dbFilters.carrier);
  if (state.dbFilters.country) params.append("country", state.dbFilters.country);
  if (state.dbFilters.status) params.append("status", state.dbFilters.status);
  if (state.dbFilters.search && state.dbFilters.search.length >= 2) {
    params.append("search", state.dbFilters.search);
  }

  try {
    const data = await api(`/api/db/shipments?${params.toString()}`);
    state.dbData = data;
    renderDatabase();
  } catch (e) {
    console.error(e);
    toast(t("database.failedLoad"), "error");
  }
}

function applyDbFilters() {
  loadDatabase(1);
}
const debouncedDbSearch = debounce(() => loadDatabase(1), 400);

function renderDatabase() {
  const d = state.dbData;
  if (!d) return;
  const rows = d.rows || [];
  const isAdmin = !!d.is_admin;

  $("db-count-label").textContent = fmt(t("database.total"), { n: (d.total || 0).toLocaleString() });

  const thead = document.querySelector("#db-table thead tr");
  const actionsTh = thead.querySelector(".db-actions-col");
  if (actionsTh) actionsTh.style.display = isAdmin ? "" : "none";

  const tbody = $("db-table-body");
  if (!rows.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="${isAdmin ? 10 : 9}">—</td></tr>`;
  } else {
    tbody.innerHTML = rows.map((s) => {
      let delay = null;
      if (s.actual_delivery_date && s.expected_delivery_date) {
        delay = Math.round(
          (new Date(s.actual_delivery_date) - new Date(s.expected_delivery_date)) / 86400000
        );
      }
      const delayTxt = delay == null ? "—"
        : delay > 0 ? `<span class="delay-badge">+${delay}${state.lang === "zh" ? "天" : "d"}</span>`
                    : `<span class="ok-badge">${delay}${state.lang === "zh" ? "天" : "d"}</span>`;
      const statusTxt = s.status === "Delivered" ? `<span class="status-delivered">${tv("status", s.status)}</span>`
        : s.status === "In Transit" ? `<span class="status-in-transit">${tv("status", s.status)}</span>`
        : `<span class="status-exception">${tv("status", s.status)}</span>`;
      const actions = isAdmin
        ? `<td class="db-row-actions">
             <button class="btn" onclick="openEditModal('${escapeHtml(s.shipment_id)}')">${t("database.edit")}</button>
             <button class="btn tiny danger" onclick="deleteShipment('${escapeHtml(s.shipment_id)}')">${t("database.delete")}</button>
           </td>`
        : `<td class="db-row-actions" style="display:none;"></td>`;
      return `
        <tr>
          <td>${escapeHtml(s.shipment_id)}</td>
          <td>${escapeHtml(tv("carrier", s.carrier))}</td>
          <td>${escapeHtml(tv("country", s.destination_country || ""))}</td>
          <td>${escapeHtml(tv("city", s.destination || ""))}</td>
          <td>${statusTxt}</td>
          <td>${s.expected_delivery_date || "—"}</td>
          <td>${s.actual_delivery_date || "—"}</td>
          <td>${delayTxt}</td>
          <td>${fmtFullCurrency(s.shipping_cost)}</td>
          ${actions}
        </tr>
      `;
    }).join("");
  }

  renderDbPagination(d);
}

function renderDbPagination(d) {
  const el = $("db-pagination");
  if (!el) return;
  const page = d.page || 1;
  const pages = d.pages || 1;
  const maxBtn = 7;
  let start = Math.max(1, page - 3);
  let end = Math.min(pages, start + maxBtn - 1);
  if (end - start < maxBtn - 1) start = Math.max(1, end - maxBtn + 1);

  let html = `<button ${page <= 1 ? "disabled" : ""} onclick="loadDatabase(${page - 1})">‹</button>`;
  if (start > 1) {
    html += `<button onclick="loadDatabase(1)">1</button>`;
    if (start > 2) html += `<span>…</span>`;
  }
  for (let i = start; i <= end; i++) {
    html += `<button class="${i === page ? "active" : ""}" onclick="loadDatabase(${i})">${i}</button>`;
  }
  if (end < pages) {
    if (end < pages - 1) html += `<span>…</span>`;
    html += `<button onclick="loadDatabase(${pages})">${pages}</button>`;
  }
  html += `<button ${page >= pages ? "disabled" : ""} onclick="loadDatabase(${page + 1})">›</button>`;
  el.innerHTML = html;
}

// =============================================================
// Database edit / delete
// =============================================================
function openEditModal(sid) {
  const d = state.dbData;
  if (!d) return;
  const row = (d.rows || []).find(r => r.shipment_id === sid);
  if (!row) return;
  state.editingShipment = row;

  const fields = [
    { key: "shipment_id", label: "ID", readonly: true },
    { key: "carrier", label: t("table.carrier") },
    { key: "destination", label: t("table.city") },
    { key: "destination_country", label: t("table.country") },
    { key: "destination_continent", label: t("table.continent") },
    { key: "status", label: t("table.status"), type: "select",
      options: ["Delivered", "In Transit", "Exception"] },
    { key: "priority", label: t("table.priority"), type: "select",
      options: ["Standard", "Express", "Critical"] },
    { key: "expected_delivery_date", label: t("table.expected"), type: "date" },
    { key: "actual_delivery_date", label: t("table.actual"), type: "date" },
    { key: "delay_reason", label: t("table.reason") },
    { key: "shipping_cost", label: t("table.revenue"), type: "number" },
    { key: "order_quantity", label: "Order Qty", type: "number" },
    { key: "delivered_quantity", label: "Delivered Qty", type: "number" },
  ];

  const body = $("db-edit-body");
  body.innerHTML = fields.map(f => {
    const val = row[f.key] ?? "";
    if (f.type === "select") {
      return `<div class="field">
        <label>${f.label}</label>
        <select data-key="${f.key}">
          ${f.options.map(o => `<option value="${o}" ${val === o ? "selected" : ""}>${tv(f.key === "status" ? "status" : "priority", o)}</option>`).join("")}
        </select>
      </div>`;
    }
    return `<div class="field">
      <label>${f.label}</label>
      <input type="${f.type || "text"}" data-key="${f.key}" value="${escapeHtml(val)}" ${f.readonly ? "readonly" : ""}>
    </div>`;
  }).join("");

  $("db-edit-modal").classList.remove("hidden");
}

function closeEditModal() {
  $("db-edit-modal").classList.add("hidden");
  state.editingShipment = null;
}

async function saveEditShipment() {
  if (!state.editingShipment) return;
  const sid = state.editingShipment.shipment_id;
  const body = $("db-edit-body");
  const updates = {};
  body.querySelectorAll("[data-key]").forEach(el => {
    const k = el.dataset.key;
    if (k === "shipment_id") return;
    const v = el.value;
    if (v === "" || v == null) return;
    if (el.type === "number") updates[k] = parseFloat(v);
    else if (el.tagName === "SELECT") updates[k] = v;
    else updates[k] = v;
  });

  try {
    const res = await api(`/api/db/shipments/${encodeURIComponent(sid)}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    });
    if (res.error) { toast(res.error, "error"); return; }
    toastT("database.saveSuccess", "", "success");
    closeEditModal();
    await loadDatabase(state.dbPage);
    await loadFilterOptions();
  } catch (e) {
    console.error(e);
    toast(t("database.saveFailed") + (e.message || "unknown"), "error");
  }
}

async function deleteShipment(sid) {
  if (!confirm(t("database.deleteConfirm"))) return;
  try {
    const res = await api(`/api/db/shipments/${encodeURIComponent(sid)}`, { method: "DELETE" });
    if (res.error) { toast(res.error, "error"); return; }
    toastT("database.deleteSuccess", "", "success");
    await loadDatabase(state.dbPage);
    await loadFilterOptions();
  } catch (e) {
    console.error(e);
    toast(t("database.deleteFailed") + (e.message || "unknown"), "error");
  }
}

// =============================================================
// Logout
// =============================================================
async function logout() {
  if (state._isDirty && !confirm(t("toast.unsavedWarning"))) return;
  await api("/api/auth/logout", { method: "POST" });
  window.location.href = "/login";
}

// =============================================================
// Init
// =============================================================
window.addEventListener("DOMContentLoaded", async () => {
  applyTheme(state.theme);
  applyLang(state.lang);
  if (window.lucide) lucide.createIcons();

  if (state.sidebarState === "collapsed") {
    $("app-sidebar")?.classList.add("collapsed");
  }

  // 恢复地图模式 UI
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === state.mapMode);
  });
  updateMapHint();

  $("set-new-pw")?.addEventListener("input", updateSettingsStrength);
  $("d-search-exc")?.addEventListener("input", debouncedRenderDataTables);
  $("d-search-all")?.addEventListener("input", debouncedRenderDataTables);
  $("trend-mode")?.addEventListener("change", () => {
    state.trendMode = $("trend-mode").value;
    renderCharts();
  });
  $("carrier-metric")?.addEventListener("change", () => {
    state.carrierMetric = $("carrier-metric").value;
    renderCharts();
  });
  ["d-range", "d-carrier", "d-priority", "d-country", "d-min-delay", "d-max-delay"]
    .forEach((id) => $(id)?.addEventListener("change", applyFilters));

  ["db-carrier", "db-country", "db-status", "db-per-page"]
    .forEach((id) => $(id)?.addEventListener("change", applyDbFilters));
  $("db-search")?.addEventListener("input", debouncedDbSearch);

  window.addEventListener("beforeunload", (e) => {
    if (!state.readonly && state._isDirty) {
      e.preventDefault();
      e.returnValue = "";
    }
  });

  document.addEventListener("click", (e) => {
    const menu = $("user-menu");
    const wrap = $("user-menu-wrap");
    if (!menu || !wrap) return;
    if (!wrap.contains(e.target)) closeUserMenu();
  });

  window.addEventListener("focus", () => {
    if (state.history.length === 0) loadHistory();
  });

  // 兜底：清空可能被浏览器自动填充到搜索框的值
  setTimeout(() => {
    document.querySelectorAll('input.search[type="search"]').forEach(el => {
      if (el.value && (el.value.includes("@") || el.value.length > 50)) {
        el.value = "";
      }
    });
  }, 200);

  switchReportTab(state.activeReportTab);

  if (window.SHARED_TOKEN) {
    await loadShared(window.SHARED_TOKEN);
    return;
  }
  if (!window.CURRENT_USER) {
    document.querySelector(".main").innerHTML =
      '<div style="padding:60px;text-align:center;color:#8892a6;font-size:13px;">Session missing. <a href="/login" style="color:#60a5fa;">Sign in again</a></div>';
    return;
  }

  await loadHistory();
  await loadFilterOptions();
});