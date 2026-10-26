(function () {
  const $ = (id) => document.getElementById(id);

  // ============================================================
  // i18n
  // ============================================================
  const I18N = {
    en: {
      "builder.back": "← Back to RouteMind",
      "builder.title": "App Builder",
      "builder.subtitle": "Describe your idea, get a working app",
      "builder.newApp": "+ New App",
      "builder.untitled": "Untitled App",
      "builder.settingsBtn": "⚙ Settings",
      "builder.shareBtn": "Share",

      "builder.modelNotConfigured": "API Key not configured",
      "builder.modelConfigured": "Configured · {model}",
      "builder.configure": "Configure",

      "builder.welcomeTitle": "Turn ideas into running apps",
      "builder.welcomeDesc": "Describe in one sentence — AI generates complete runnable HTML in real time. Chat is the iteration.",
      "builder.fallbackHint": "Without an API key: 2048 · Todo · Calculator · Ledger · Pomodoro · Snake · Weather · Logistics",

      "builder.instructionPlaceholder": "Describe what you need… Enter to send, Shift+Enter for newline",
      "builder.generateBtn": "Generate",
      "builder.stopBtn": "Stop",
      "builder.generating": "Generating…",
      "builder.generatingProgress": "Generating… ({n} chars)",
      "builder.done": "✅ Generated ({n} chars)",
      "builder.stopped": "⏹ Stopped (incomplete, {n} chars received)",
      "builder.stoppedPlain": "⏹ Stopped (incomplete)",
      "builder.errorPrefix": "❌ {msg}",
      "builder.networkError": "❌ Network error: {msg}",
      "builder.needInstruction": "Please enter a requirement first",
      "builder.invalidResult": "❌ Invalid result (no HTML), please retry or change model",

      "builder.tabPreview": "Preview",
      "builder.tabCode": "Code",
      "builder.tabVersions": "Versions",
      "builder.reload": "↻ Reload",
      "builder.copy": "Copy",
      "builder.download": "Download",
      "builder.loading": "Loading…",

      "builder.settingsTitle": "Configure Model Service",
      "builder.settingsHint": "Use your own API key. Configuration syncs to your account.",
      "builder.provider": "Provider",
      "builder.apiKey": "API Key",
      "builder.baseUrl": "Base URL",
      "builder.model": "Model",
      "builder.testConnection": "Test Connection",
      "builder.testing": "Testing…",
      "builder.saveSettings": "Save",
      "builder.clearSettings": "Clear",
      "builder.needApiKey": "Please fill in API Key, Base URL and Model",
      "builder.keyPlaceholderKeep": "Configured ({preview}) — leave empty to keep",
      "builder.keyPlaceholderNew": "sk-...",
      "builder.connectionSuccess": "Connection OK",
      "builder.connectionFailed": "Connection failed",
      "builder.settingsSaved": "Settings saved",
      "builder.settingsCleared": "Configuration cleared",
      "builder.networkErrorShort": "Network error",

      "builder.chatInitialTitle": "Turn ideas into running apps",
      "builder.chatInitialDesc": "Describe in one sentence — AI generates complete runnable HTML in real time.",

      "builder.projectEmpty": "No projects yet",
      "builder.versionEmpty": "No versions yet",
      "builder.versionInitial": "Initial version",
      "builder.versionCurrent": "Current",
      "builder.projectNoContentTitle": "This project has no content yet",
      "builder.projectNoContentDesc": "Enter a requirement below and AI will generate the first version.",

      "builder.copied": "Copied",
      "builder.copyFailed": "Copy failed",
      "builder.noCode": "No code yet",
      "builder.shareCopied": "Share link copied: {url}",
      "builder.shareFailed": "Share failed",
      "builder.deleteConfirm": "Delete this app? This cannot be undone.",
      "builder.deleted": "Deleted",
      "builder.deleteFailed": "Delete failed: {msg}",

      "builder.example2048": "2048 Game",
      "builder.exampleTodo": "Todo List",
      "builder.examplePomodoro": "Pomodoro",
      "builder.exampleLedger": "Ledger",
      "builder.exampleLogistics": "Logistics Dashboard",
      "builder.exampleOrderTracker": "Order Tracker",

      "builder.prompt2048": "Build a playable 2048 game with keyboard and touch, saving the high score locally",
      "builder.promptTodo": "Build a todo list with add/complete/delete and persistence",
      "builder.promptPomodoro": "Build a pomodoro timer: 25 min work + 5 min break loop",
      "builder.promptLedger": "Build a ledger with category stats and monthly pie chart",
      "builder.promptLogistics": "Build a logistics dashboard showing total orders, status distribution, carrier ranking and continent breakdown, with charts",
      "builder.promptOrderTracker": "Build a logistics order tracking page with paginated list, filter by carrier / country / status",
    },
    zh: {
      "builder.back": "← 返回 RouteMind",
      "builder.title": "App Builder",
      "builder.subtitle": "描述一句话，生成可运行的应用",
      "builder.newApp": "+ 新建应用",
      "builder.untitled": "未命名应用",
      "builder.settingsBtn": "⚙ 设置",
      "builder.shareBtn": "分享",

      "builder.modelNotConfigured": "未配置 API Key",
      "builder.modelConfigured": "已配置 · {model}",
      "builder.configure": "配置",

      "builder.welcomeTitle": "把想法变成可运行的应用",
      "builder.welcomeDesc": "用一句话描述需求，AI 实时生成完整可运行的 HTML。对话即迭代。",
      "builder.fallbackHint": "未配置 Key 时支持：2048 · 待办 · 计算器 · 记账 · 番茄钟 · 贪吃蛇 · 天气 · 物流面板",

      "builder.instructionPlaceholder": "描述你的需求… Enter 发送，Shift+Enter 换行",
      "builder.generateBtn": "生成",
      "builder.stopBtn": "停止",
      "builder.generating": "生成中…",
      "builder.generatingProgress": "生成中… ({n} 字符)",
      "builder.done": "✅ 已生成（{n} 字符）",
      "builder.stopped": "⏹ 已停止（未完成，已收到 {n} 字符）",
      "builder.stoppedPlain": "⏹ 已停止（未完成）",
      "builder.errorPrefix": "❌ {msg}",
      "builder.networkError": "❌ 网络错误: {msg}",
      "builder.needInstruction": "请先输入需求",
      "builder.invalidResult": "❌ 生成结果无效（未拿到 HTML），请重试或换个模型",

      "builder.tabPreview": "预览",
      "builder.tabCode": "代码",
      "builder.tabVersions": "版本历史",
      "builder.reload": "↻ 刷新",
      "builder.copy": "复制",
      "builder.download": "下载",
      "builder.loading": "加载中…",

      "builder.settingsTitle": "配置模型服务",
      "builder.settingsHint": "使用你自己的 API Key，配置会同步到你的账号。",
      "builder.provider": "平台",
      "builder.apiKey": "API Key",
      "builder.baseUrl": "接口地址",
      "builder.model": "模型",
      "builder.testConnection": "测试连接",
      "builder.testing": "测试中…",
      "builder.saveSettings": "保存",
      "builder.clearSettings": "清除配置",
      "builder.needApiKey": "请填写 API Key、接口地址和模型",
      "builder.keyPlaceholderKeep": "已配置 ({preview}) — 留空则不修改",
      "builder.keyPlaceholderNew": "sk-...",
      "builder.connectionSuccess": "连接成功",
      "builder.connectionFailed": "连接失败",
      "builder.settingsSaved": "设置已保存",
      "builder.settingsCleared": "已清除配置",
      "builder.networkErrorShort": "网络错误",

      "builder.chatInitialTitle": "把想法变成可运行的应用",
      "builder.chatInitialDesc": "用一句话描述需求，AI 实时生成完整可运行的 HTML。",

      "builder.projectEmpty": "暂无项目",
      "builder.versionEmpty": "暂无版本",
      "builder.versionInitial": "初始版本",
      "builder.versionCurrent": "当前",
      "builder.projectNoContentTitle": "这个项目还没有内容",
      "builder.projectNoContentDesc": "在下方输入需求，AI 会为你生成第一个版本。",

      "builder.copied": "已复制",
      "builder.copyFailed": "复制失败",
      "builder.noCode": "暂无代码",
      "builder.shareCopied": "分享链接已复制：{url}",
      "builder.shareFailed": "分享失败",
      "builder.deleteConfirm": "确定删除这个应用？删除后不可恢复。",
      "builder.deleted": "已删除",
      "builder.deleteFailed": "删除失败: {msg}",

      "builder.example2048": "2048 游戏",
      "builder.exampleTodo": "待办清单",
      "builder.examplePomodoro": "番茄钟",
      "builder.exampleLedger": "记账本",
      "builder.exampleLogistics": "物流面板",
      "builder.exampleOrderTracker": "订单追踪",

      "builder.prompt2048": "做一个可玩的 2048 游戏，支持键盘和触屏，最高分本地保存",
      "builder.promptTodo": "做一个待办清单，支持添加/完成/删除，数据持久化",
      "builder.promptPomodoro": "做一个番茄钟，25 分钟工作 + 5 分钟休息循环",
      "builder.promptLedger": "做一个记账本，支持分类统计和月度饼图",
      "builder.promptLogistics": "做一个物流数据面板，展示订单总量、状态分布、承运商排行和洲际分布，用图表呈现",
      "builder.promptOrderTracker": "做一个物流订单追踪页，分页展示订单列表，可按承运商、国家、状态筛选",
    },
  };

  let lang = localStorage.getItem("builder_lang") || "zh";
  let clientSessionId = Date.now().toString(36);

  function t(key, vars) {
    let s = (I18N[lang] && I18N[lang][key]) || I18N.en[key] || key;
    if (vars) {
      s = s.replace(/\{(\w+)\}/g, (_, k) => (vars[k] != null ? vars[k] : ""));
    }
    return s;
  }

  function applyLang(newLang) {
    if (newLang && (newLang === "en" || newLang === "zh")) {
      lang = newLang;
      localStorage.setItem("builder_lang", lang);
    }
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      el.placeholder = t(el.dataset.i18nPlaceholder);
    });

    document.querySelectorAll("#lang-switch button").forEach((b) => {
      b.classList.toggle("active", b.dataset.lang === lang);
    });

    updateModelStatus();
    if (settings.configured) fillSettingsForm();
    renderWelcomeIfEmpty();
    if (currentProjectId) {
      renderVersions();
      const log = $("chat-log");
      if (log && !log.querySelector(".chat-msg")) {
        restoreChatHistory();
      }
    }
    loadProjects();
    renderGenButtonIdle();
  }

  document.querySelectorAll("#lang-switch button").forEach((btn) => {
    btn.addEventListener("click", () => applyLang(btn.dataset.lang));
  });

  // ============================================================
  // State
  // ============================================================
  let currentProjectId = null;
  let currentCode = "";
  let versions = [];
  let generating = false;
  let settings = {
    configured: false,
    provider: "openai",
    baseUrl: "",
    model: "",
    apiKeyPreview: "",
  };
  let abortController = null;

  const PROVIDERS = [
    { id: "groq", name: "Groq", baseUrl: "https://api.groq.com/openai/v1",
      models: ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-120b"] },
    { id: "openai", name: "OpenAI", baseUrl: "https://api.openai.com/v1",
      models: ["gpt-4o-mini", "gpt-4o", "gpt-4.1"] },
    { id: "deepseek", name: "DeepSeek", baseUrl: "https://api.deepseek.com/v1",
      models: ["deepseek-chat", "deepseek-reasoner"] },
    { id: "gemini", name: "Google Gemini", baseUrl: "https://generativelanguage.googleapis.com/v1beta/openai",
      models: ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash"] },
    { id: "moonshot", name: "Kimi", baseUrl: "https://api.moonshot.cn/v1",
      models: ["moonshot-v1-32k", "kimi-k2-0905-preview"] },
    { id: "dashscope", name: "通义千问", baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
      models: ["qwen-plus", "qwen-max", "qwen3-coder-plus"] },
    { id: "zhipu", name: "智谱 GLM", baseUrl: "https://open.bigmodel.cn/api/paas/v4",
      models: ["glm-4.6", "glm-4-plus", "glm-4-flash"] },
    { id: "openrouter", name: "OpenRouter", baseUrl: "https://openrouter.ai/api/v1",
      models: ["anthropic/claude-sonnet-4.5", "openai/gpt-4o-mini"] },
    { id: "custom", name: "自定义", baseUrl: "", models: [] },
  ];

  function escapeHtml(s) {
    return (s == null ? "" : String(s))
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function toast(msg, type) {
    const el = document.createElement("div");
    el.textContent = msg;
    el.style.cssText = `position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(100px);
      background:#162033;border:1px solid ${type === "error" ? "#f87171" : type === "success" ? "#34d399" : "#1f2b3e"};
      color:${type === "error" ? "#f87171" : type === "success" ? "#34d399" : "#e6ebf5"};
      padding:10px 18px;border-radius:8px;font-size:13px;z-index:9999;transition:all .3s;opacity:0;max-width:80vw`;
    document.body.appendChild(el);
    requestAnimationFrame(() => { el.style.transform = "translateX(-50%) translateY(0)"; el.style.opacity = "1"; });
    setTimeout(() => { el.style.opacity = "0"; el.style.transform = "translateX(-50%) translateY(100px)"; setTimeout(() => el.remove(), 300); }, 2400);
  }

  // ============================================================
  // 持久化桥：iframe → 父页面 localStorage
  // ============================================================
  function getPreviewNs() {
    return "appbuilder:preview:" + (currentProjectId || ("new-" + clientSessionId));
  }

  function getPreviewData(ns) {
    try {
      return JSON.parse(localStorage.getItem(ns) || "{}");
    } catch (e) {
      return {};
    }
  }

  function wrapSrcdoc(html) {
    if (!html) return html;

    const ns = getPreviewNs();
    const initialData = getPreviewData(ns);
    // 防止 </script> 提前闭合
    const dataJSON = JSON.stringify(initialData)
      .replace(/</g, "\\u003c")
      .replace(/>/g, "\\u003e")
      .replace(/&/g, "\\u0026");
    const nsJSON = JSON.stringify(ns);

    const injector = `<script>
(function(){
  var NS = ${nsJSON};
  var store = {};
  try { store = (${dataJSON}) || {}; } catch (e) { store = {}; }

  function notify(key, value) {
    try {
      window.parent.postMessage(
        { __appbuilder: true, ns: NS, key: key, value: value }, "*"
      );
    } catch (e) {}
  }

  var fakeStorage = {
    getItem: function(k) {
      return Object.prototype.hasOwnProperty.call(store, k) ? String(store[k]) : null;
    },
    setItem: function(k, v) {
      var sv = String(v);
      store[k] = sv;
      notify(k, sv);
    },
    removeItem: function(k) {
      delete store[k];
      notify(k, null);
    },
    clear: function() {
      store = {};
      notify("__clear__", null);
    },
    key: function(i) {
      var ks = Object.keys(store);
      return i < ks.length ? ks[i] : null;
    }
  };
  try {
    Object.defineProperty(fakeStorage, "length", {
      get: function() { return Object.keys(store).length; }
    });
  } catch (e) {}

  try {
    Object.defineProperty(window, "localStorage", { configurable: true, value: fakeStorage });
  } catch (e) { try { window.localStorage = fakeStorage; } catch (e2) {} }
  try {
    Object.defineProperty(window, "sessionStorage", { configurable: true, value: fakeStorage });
  } catch (e) { try { window.sessionStorage = fakeStorage; } catch (e2) {} }

  window.__APP_INIT_DATA__ = store;
})();
<\/script>`;

    if (/<head[^>]*>/i.test(html)) {
      return html.replace(/<head[^>]*>/i, (m) => m + injector);
    }
    if (/<html[^>]*>/i.test(html)) {
      return html.replace(/<html[^>]*>/i, (m) => m + injector);
    }
    return injector + html;
  }

  // 父页面接收 iframe 消息，持久化到父页面 localStorage
  window.addEventListener("message", function (e) {
    const d = e.data;
    if (!d || d.__appbuilder !== true) return;

    const iframe = $("app-frame");
    if (!iframe || e.source !== iframe.contentWindow) return;

    if (typeof d.ns !== "string" || d.ns.indexOf("appbuilder:preview:") !== 0) return;

    try {
      if (d.key === "__clear__") {
        localStorage.removeItem(d.ns);
        return;
      }
      const all = getPreviewData(d.ns);
      if (d.value === null || d.value === undefined) {
        delete all[d.key];
      } else {
        all[d.key] = d.value;
      }
      localStorage.setItem(d.ns, JSON.stringify(all));
    } catch (err) {
      // 忽略 localStorage 满 / 隐私模式等异常
    }
  });

  // ============================================================
  // Welcome / 聊天区
  // ============================================================
  function welcomeHTML() {
    return `
      <div class="chat-welcome">
        <h2>${escapeHtml(t("builder.welcomeTitle"))}</h2>
        <p>${escapeHtml(t("builder.welcomeDesc"))}</p>
        <div class="example-chips">
          <button onclick="fillPrompt('2048')">${escapeHtml(t("builder.example2048"))}</button>
          <button onclick="fillPrompt('todo')">${escapeHtml(t("builder.exampleTodo"))}</button>
          <button onclick="fillPrompt('pomodoro')">${escapeHtml(t("builder.examplePomodoro"))}</button>
          <button onclick="fillPrompt('ledger')">${escapeHtml(t("builder.exampleLedger"))}</button>
          <button onclick="fillPrompt('logistics')">${escapeHtml(t("builder.exampleLogistics"))}</button>
          <button onclick="fillPrompt('tracker')">${escapeHtml(t("builder.exampleOrderTracker"))}</button>
        </div>
        <p class="fallback-hint">${escapeHtml(t("builder.fallbackHint"))}</p>
      </div>`;
  }

  function renderWelcomeIfEmpty() {
    const log = $("chat-log");
    if (!log) return;
    if (!log.innerHTML.trim() || log.querySelector(".chat-welcome")) {
      log.innerHTML = welcomeHTML();
    }
  }

  const PROMPT_KEYS = {
    2048: "builder.prompt2048",
    todo: "builder.promptTodo",
    pomodoro: "builder.promptPomodoro",
    ledger: "builder.promptLedger",
    logistics: "builder.promptLogistics",
    tracker: "builder.promptOrderTracker",
  };

  window.fillPrompt = function (key) {
    const el = $("instruction");
    if (!el) return;
    const text = PROMPT_KEYS[key] ? t(PROMPT_KEYS[key]) : String(key || "");
    el.value = text;
    el.focus();
  };

  // ============================================================
  // 项目列表
  // ============================================================
  async function loadProjects() {
    try {
      const res = await fetch("/api/builder/projects");
      if (!res.ok) return;
      const projects = await res.json();
      renderProjectList(projects);
    } catch (e) { /* ignore */ }
  }

  function renderProjectList(projects) {
    const box = $("project-list");
    if (!box) return;
    if (!projects.length) {
      box.innerHTML = `<div style="color:var(--text-3);font-size:12px;padding:8px;">${escapeHtml(t("builder.projectEmpty"))}</div>`;
      return;
    }
    box.innerHTML = projects.map(p => {
      const active = p.id === currentProjectId ? "active" : "";
      const titleSafe = escapeHtml(p.title || "").replace(/'/g, "&#39;");
      return `
        <div class="project-item ${active}">
          <span class="project-name" onclick="openProject('${p.id}', '${titleSafe}')" title="${escapeHtml(p.title)}">
            ${escapeHtml(p.title)}
          </span>
          <button class="project-delete" title="✕"
                  onclick="event.stopPropagation(); deleteProject('${p.id}')">✕</button>
        </div>`;
    }).join("");
  }

  window.newProject = function () {
    clientSessionId = Date.now().toString(36);
    currentProjectId = null;
    currentCode = "";
    versions = [];

    $("app-frame").srcdoc = "";
    const codeEl = $("code-view").querySelector("code");
    if (codeEl) {
      codeEl.textContent = "";
      codeEl.className = "language-html";
      delete codeEl.dataset.highlighted;
    }
    $("version-list").innerHTML = "";

    $("chat-log").innerHTML = welcomeHTML();
    $("project-title").textContent = t("builder.untitled");
    $("instruction").value = "";
    $("instruction").focus();

    switchTab("preview");
    loadProjects();
  };

  window.openProject = async function (pid, title) {
    currentProjectId = pid;
    $("project-title").textContent = title;

    const log = $("chat-log");
    if (log) log.innerHTML = "";

    await loadVersions();

    if (versions.length) {
      await restoreVersion(versions[0].id, true);
      restoreChatHistory();
    } else {
      $("chat-log").innerHTML = `
        <div class="chat-welcome">
          <h2>${escapeHtml(t("builder.projectNoContentTitle"))}</h2>
          <p>${escapeHtml(t("builder.projectNoContentDesc"))}</p>
        </div>`;
      $("app-frame").srcdoc = "";
      const codeEl = $("code-view").querySelector("code");
      if (codeEl) {
        codeEl.textContent = "";
        delete codeEl.dataset.highlighted;
      }
    }

    loadProjects();
  };

  window.deleteProject = async function (pid) {
    if (!confirm(t("builder.deleteConfirm"))) return;
    try {
      const res = await fetch(`/api/builder/projects/${pid}`, { method: "DELETE" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        toast(data.error || t("builder.shareFailed"), "error");
        return;
      }
      try { localStorage.removeItem("appbuilder:preview:" + pid); } catch (e) {}
      if (currentProjectId === pid) {
        window.newProject();
      }
      await loadProjects();
      toast(t("builder.deleted"), "success");
    } catch (e) {
      toast(t("builder.deleteFailed", { msg: e.message }), "error");
    }
  };

  // ============================================================
  // 版本
  // ============================================================
  async function loadVersions() {
    if (!currentProjectId) {
      versions = [];
      $("version-list").innerHTML = "";
      return;
    }
    try {
      const res = await fetch(`/api/builder/projects/${currentProjectId}/versions`);
      if (!res.ok) { versions = []; return; }
      versions = await res.json();
      renderVersions();
    } catch (e) { /* ignore */ }
  }

  function renderVersions(activeId) {
    const box = $("version-list");
    if (!box) return;
    if (!versions.length) {
      box.innerHTML = `<div style="color:var(--text-3);font-size:12px;padding:8px;">${escapeHtml(t("builder.versionEmpty"))}</div>`;
      return;
    }
    box.innerHTML = versions.map((v, i) => {
      const isActive = activeId ? v.id === activeId : i === 0;
      const label = v.instruction || t("builder.versionInitial");
      return `
        <div class="version-item ${isActive ? "active" : ""}" onclick="restoreVersion('${v.id}')">
          <div class="vi-title">v${versions.length - i} · ${escapeHtml(label)}</div>
          <div class="vi-time">${new Date(v.created_at).toLocaleString()}</div>
          ${isActive ? `<span class="vi-current">${escapeHtml(t("builder.versionCurrent"))}</span>` : ""}
        </div>`;
    }).join("");
  }

  window.restoreVersion = async function (vid, keepTab) {
    const v = versions.find(x => x.id === vid);
    if (!v) return;

    let code = v.code;
    if (typeof code !== "string") {
      try {
        const r = await fetch(`/api/builder/versions/${vid}/code`);
        if (r.ok) {
          const data = await r.json();
          code = data.code || "";
        }
      } catch (e) {
        toast(t("builder.networkError", { msg: e.message }), "error");
        return;
      }
    }
    if (typeof code !== "string") code = "";

    currentCode = code;
    renderCode(code);
    renderVersions(vid);

    if (!keepTab) {
      switchTab("preview");
    }
    const iframe = $("app-frame");
    iframe.srcdoc = "";
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        iframe.srcdoc = wrapSrcdoc(code);
      });
    });
  };

  function restoreChatHistory() {
    const log = $("chat-log");
    if (!log || !versions.length) return;

    const sorted = [...versions].sort((a, b) => {
      const ta = new Date(a.created_at).getTime() || 0;
      const tb = new Date(b.created_at).getTime() || 0;
      return ta - tb;
    });

    log.innerHTML = "";
    sorted.forEach((v, i) => {
      const isLatest = i === sorted.length - 1;
      const versionNo = sorted.length - i;

      const userMsg = document.createElement("div");
      userMsg.className = "chat-msg user";
      userMsg.textContent = v.instruction || t("builder.versionInitial");
      log.appendChild(userMsg);

      const aiMsg = document.createElement("div");
      aiMsg.className = "chat-msg assistant";
      aiMsg.textContent = isLatest
        ? `v${versionNo} · ${t("builder.versionCurrent")}`
        : `v${versionNo}`;
      log.appendChild(aiMsg);
    });

    requestAnimationFrame(() => { log.scrollTop = log.scrollHeight; });
  }

  // ============================================================
  // Tab
  // ============================================================
  window.switchTab = function (name) {
    document.querySelectorAll(".tab").forEach(t =>
      t.classList.toggle("active", t.dataset.tab === name));
    ["preview", "code", "versions"].forEach(n => {
      $("tab-" + n).classList.toggle("hidden", n !== name);
    });
  };

  // ============================================================
  // 代码区
  // ============================================================
  function renderCode(code) {
    const el = $("code-view").querySelector("code");
    if (!el) return;
    delete el.dataset.highlighted;
    el.textContent = code || "";
    el.className = "language-html";
    if (window.hljs) {
      try { hljs.highlightElement(el); } catch (e) {}
    }
  }

  window.reloadPreview = function () {
    if (currentCode) $("app-frame").srcdoc = wrapSrcdoc(currentCode);
  };

  window.copyCode = function () {
    if (!currentCode) return toast(t("builder.noCode"), "error");
    navigator.clipboard.writeText(currentCode)
      .then(() => toast(t("builder.copied"), "success"))
      .catch(() => toast(t("builder.copyFailed"), "error"));
  };

  window.downloadCode = function () {
    if (!currentCode) return toast(t("builder.noCode"), "error");
    const blob = new Blob([currentCode], { type: "text/html" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = ($("project-title").textContent || "app") + ".html";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  // ============================================================
  // 设置
  // ============================================================
  window.openSettings = async function () {
    await loadSettings();
    renderProviderGrid();
    fillSettingsForm();
    $("s-error").textContent = "";
    $("settings-modal").classList.remove("hidden");
  };

  window.closeSettings = function () {
    $("settings-modal").classList.add("hidden");
  };

  async function loadSettings() {
    try {
      const r = await fetch("/api/builder/settings").then(x => x.json());
      if (r && r.configured) {
        settings = {
          configured: true,
          provider: r.provider || "custom",
          baseUrl: r.base_url || "",
          model: r.model || "",
          apiKeyPreview: r.api_key_preview || "",
        };
      } else {
        settings = {
          configured: false,
          provider: "groq",
          baseUrl: "",
          model: "",
          apiKeyPreview: "",
        };
      }
    } catch (e) {
      settings = {
        configured: false,
        provider: "groq",
        baseUrl: "",
        model: "",
        apiKeyPreview: "",
      };
    }
  }

  function renderProviderGrid() {
    const grid = $("provider-grid");
    if (!grid) return;
    grid.innerHTML = PROVIDERS.map(p =>
      `<button type="button" class="provider-btn ${p.id === settings.provider ? "active" : ""}" onclick="selectProvider('${p.id}')">${p.name}</button>`
    ).join("");
  }

  window.selectProvider = function (id) {
    const p = PROVIDERS.find(x => x.id === id);
    if (!p) return;
    settings.provider = id;
    settings.baseUrl = p.baseUrl;
    settings.model = p.models[0] || "";
    renderProviderGrid();
    fillSettingsForm();
  };

  function fillSettingsForm() {
    const keyInput = $("s-api-key");
    keyInput.value = "";
    keyInput.type = "password";
    keyInput.placeholder = settings.apiKeyPreview
      ? t("builder.keyPlaceholderKeep", { preview: settings.apiKeyPreview })
      : t("builder.keyPlaceholderNew");

    $("s-base-url").value = settings.baseUrl || "";
    $("s-model").value = settings.model || "";
    const p = PROVIDERS.find(x => x.id === settings.provider);
    $("model-options").innerHTML = (p?.models || []).map(m => `<option value="${m}">`).join("");
  }

  window.toggleKeyVis = function () {
    const el = $("s-api-key");
    el.type = el.type === "password" ? "text" : "password";
  };

  window.saveSettings = async function () {
    const body = {
      provider: settings.provider,
      base_url: $("s-base-url").value.trim(),
      model: $("s-model").value.trim(),
    };
    const keyValue = $("s-api-key").value.trim();
    if (keyValue) {
      body.api_key = keyValue;
    } else if (!settings.configured) {
      $("s-error").textContent = t("builder.needApiKey");
      return;
    }

    if (!body.base_url || !body.model) {
      $("s-error").textContent = t("builder.needApiKey");
      return;
    }

    const r = await fetch("/api/builder/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(x => x.json()).catch(() => ({ error: t("builder.networkErrorShort") }));

    if (r.error) {
      $("s-error").textContent = r.error;
      return;
    }
    await loadSettings();
    updateModelStatus();
    closeSettings();
    toast(t("builder.settingsSaved"), "success");
  };

  window.testConnection = async function () {
    const keyValue = $("s-api-key").value.trim();
    const body = {
      provider: settings.provider,
      api_key: keyValue,
      base_url: $("s-base-url").value.trim(),
      model: $("s-model").value.trim(),
    };
    if (!keyValue && settings.configured) {
      delete body.api_key;
      body.use_saved_key = true;
    } else if (!keyValue) {
      $("s-error").textContent = t("builder.needApiKey");
      return;
    }
    if (!body.base_url || !body.model) {
      $("s-error").textContent = t("builder.needApiKey");
      return;
    }

    $("test-btn").disabled = true;
    $("test-btn").textContent = t("builder.testing");
    $("s-error").textContent = "";

    const r = await fetch("/api/builder/settings/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(x => x.json()).catch(() => ({ ok: false, error: t("builder.networkErrorShort") }));

    $("test-btn").disabled = false;
    $("test-btn").textContent = t("builder.testConnection");

    if (r.ok) toast(t("builder.connectionSuccess"), "success");
    else $("s-error").textContent = r.error || t("builder.connectionFailed");
  };

  window.clearSettings = async function () {
    await fetch("/api/builder/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: "groq",
        api_key: "",
        base_url: "",
        model: "",
        clear: true,
      }),
    });
    settings = {
      configured: false,
      provider: "groq",
      baseUrl: "",
      model: "",
      apiKeyPreview: "",
    };
    updateModelStatus();
    closeSettings();
    toast(t("builder.settingsCleared"));
  };

  function updateModelStatus() {
    const hasKey = !!settings.configured;
    const statusEl = $("model-status");
    const labelEl = $("model-label");
    if (!statusEl || !labelEl) return;
    statusEl.classList.toggle("ok", hasKey);
    labelEl.textContent = hasKey
      ? t("builder.modelConfigured", { model: settings.model })
      : t("builder.modelNotConfigured");
  }

  // ============================================================
  // 生成（支持停止）
  // ============================================================
  function setGenButtonBusy(busy) {
    const btn = $("gen-btn");
    const text = $("gen-btn-text");
    if (!btn || !text) return;
    if (busy) {
      btn.disabled = false;
      btn.classList.add("loading");
      text.textContent = t("builder.stopBtn");
    } else {
      btn.disabled = false;
      btn.classList.remove("loading");
      text.textContent = t("builder.generateBtn");
    }
  }

  function renderGenButtonIdle() {
    const btn = $("gen-btn");
    const text = $("gen-btn-text");
    if (!btn || !text) return;
    if (generating) {
      text.textContent = t("builder.stopBtn");
    } else {
      btn.classList.remove("loading");
      text.textContent = t("builder.generateBtn");
    }
  }

  window.generate = async function () {
    if (generating) {
      if (abortController) {
        try { abortController.abort(); } catch (e) {}
      }
      return;
    }

    const instruction = $("instruction").value.trim();
    if (!instruction) {
      toast(t("builder.needInstruction"), "error");
      return;
    }

    const log = $("chat-log");
    const welcome = log.querySelector(".chat-welcome");
    if (welcome) welcome.remove();

    log.insertAdjacentHTML("beforeend",
      `<div class="chat-msg user">${escapeHtml(instruction)}</div>`);
    $("instruction").value = "";

    const msgEl = document.createElement("div");
    msgEl.className = "chat-msg assistant streaming";
    msgEl.textContent = t("builder.generating");
    log.appendChild(msgEl);
    log.scrollTop = log.scrollHeight;

    generating = true;
    abortController = new AbortController();
    setGenButtonBusy(true);

    const hardTimeout = setTimeout(() => {
      if (abortController) { try { abortController.abort(); } catch (e) {} }
    }, 5 * 60 * 1000);

    let reader = null;
    let aborted = false;

    const fetchWithTimeout = async (url, opts, ms) => {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), ms);
      try {
        return await fetch(url, { ...opts, signal: ctrl.signal });
      } finally {
        clearTimeout(timer);
      }
    };

    try {
      const res = await fetch("/api/builder/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          instruction,
          project_id: currentProjectId,
          current_code: currentCode,
        }),
        signal: abortController.signal,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        msgEl.className = "chat-msg error";
        msgEl.textContent = t("builder.errorPrefix", { msg: err.error || `HTTP ${res.status}` });
        return;
      }

      reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let eventData = [];
      let codeBuffer = "";
      let lastRefresh = 0;
      let fatalError = null;
      let gotDone = false;

      const closeReader = () => {
        if (reader) { try { reader.cancel(); } catch (e) {} reader = null; }
      };

      const dispatch = () => {
        if (!eventData.length) return;
        const payload = eventData.join("\n");
        eventData = [];
        if (payload === "[DONE]") { gotDone = true; closeReader(); return; }
        try {
          const j = JSON.parse(payload);

          // 兼容旧格式
          if (j.retrying) { msgEl.textContent = `⏳ ${j.retrying}`; return; }

          // 新事件
          if (j.stage === "attempt") {
            msgEl.textContent = j.attempt === 1
              ? t("builder.generating")
              : `🔄 第 ${j.attempt} 次尝试…`;
            return;
          }
          if (j.stage === "retry") {
            msgEl.textContent = `⏳ 修改未达标（${j.reason}），重试中…`;
            return;
          }
          if (j.stage === "fallback") {
            msgEl.textContent = `⚡ ${j.reason || "使用快速生成"}`;
            return;
          }

          if (j.error) { fatalError = j.error; closeReader(); return; }
          const delta = j.choices?.[0]?.delta?.content || "";
          if (delta) {
            codeBuffer += delta;
            msgEl.textContent = t("builder.generatingProgress", { n: codeBuffer.length });
            const now = Date.now();
            if (now - lastRefresh > 300) {
              lastRefresh = now;
              const partial = extractHtml(codeBuffer);
              if (partial) $("app-frame").srcdoc = wrapSrcdoc(partial);
            }
          }
        } catch (e) {}
      };

      while (!fatalError && !gotDone && !aborted) {
        let result;
        try {
          result = await reader.read();
        } catch (readErr) {
          if (readErr.name === "AbortError") { aborted = true; break; }
          break;
        }
        if (result.done) {
          if (buffer) {
            buffer.split(/\r?\n/).forEach(line => {
              if (line.startsWith("data:")) {
                const d = line.slice(5).trimStart();
                if (d) eventData.push(d);
              }
            });
            dispatch();
          }
          break;
        }
        buffer += decoder.decode(result.value, { stream: true });
        let nl;
        while ((nl = buffer.indexOf("\n")) !== -1) {
          let line = buffer.slice(0, nl);
          if (line.endsWith("\r")) line = line.slice(0, -1);
          buffer = buffer.slice(nl + 1);
          if (line === "") {
            dispatch();
            if (gotDone || fatalError) break;
          } else if (line.startsWith("data:")) {
            eventData.push(line.slice(5).trimStart());
          }
        }
      }

      closeReader();

      if (aborted) {
        msgEl.className = "chat-msg error";
        msgEl.textContent = t("builder.stopped", { n: codeBuffer.length });
        if (codeBuffer.trim()) {
          const partial = extractHtml(codeBuffer) || codeBuffer.trim();
          if (partial && partial.includes("<")) {
            renderCode(partial);
          }
        }
        return;
      }

      if (fatalError) {
        msgEl.className = "chat-msg error";
        msgEl.textContent = t("builder.errorPrefix", { msg: fatalError });
        return;
      }

      const html = extractHtml(codeBuffer) || codeBuffer.trim();
      if (!html || !html.includes("<")) {
        msgEl.className = "chat-msg error";
        msgEl.textContent = t("builder.invalidResult");
        return;
      }

      currentCode = html;
      $("app-frame").srcdoc = wrapSrcdoc(html);
      renderCode(html);
      msgEl.className = "chat-msg assistant";
      msgEl.textContent = t("builder.done", { n: html.length });

      generating = false;
      abortController = null;
      clearTimeout(hardTimeout);
      setGenButtonBusy(false);
      switchTab("preview");

      try {
        const save = await fetchWithTimeout("/api/builder/versions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_id: currentProjectId,
            instruction,
            code: html,
            title: currentProjectId ? undefined : instruction.slice(0, 30),
          }),
        }, 8000).then(r => r.json());

        if (save && save.project_id) {
          const wasNew = !currentProjectId;
          if (wasNew) {
            const oldNs = "appbuilder:preview:new-" + clientSessionId;
            const newNs = "appbuilder:preview:" + save.project_id;
            try {
              const temp = localStorage.getItem(oldNs);
              if (temp) {
                localStorage.setItem(newNs, temp);
                localStorage.removeItem(oldNs);
              }
            } catch (e) {}
          }
          currentProjectId = save.project_id;
          $("project-title").textContent = instruction.slice(0, 30);

          if (wasNew) {
            const iframe = $("app-frame");
            iframe.srcdoc = "";
            requestAnimationFrame(() => {
              requestAnimationFrame(() => {
                iframe.srcdoc = wrapSrcdoc(html);
              });
            });
          }
        }
      } catch (e) {
        console.warn("[save version] failed or timeout:", e);
      }

      try {
        await fetchWithTimeout(`/api/builder/projects/${currentProjectId}/versions`, {}, 8000)
          .then(r => r.json()).then(data => { versions = data || []; renderVersions(); });
      } catch (e) {}

      try {
        await fetchWithTimeout("/api/builder/projects", {}, 8000)
          .then(r => r.json()).then(data => renderProjectList(data || []));
      } catch (e) {}

    } catch (e) {
      if (e.name === "AbortError") {
        aborted = true;
        msgEl.className = "chat-msg error";
        msgEl.textContent = t("builder.stoppedPlain");
      } else {
        msgEl.className = "chat-msg error";
        msgEl.textContent = t("builder.networkError", { msg: e.message || e });
      }
    } finally {
      clearTimeout(hardTimeout);
      if (reader) { try { reader.cancel(); } catch (e) {} reader = null; }
      if (generating) {
        generating = false;
        abortController = null;
        setGenButtonBusy(false);
      }
      const logEl = $("chat-log");
      if (logEl) logEl.scrollTop = logEl.scrollHeight;
    }
  };

  function extractHtml(raw) {
    if (!raw) return null;
    const m = raw.match(/```html\s*([\s\S]*?)(```|$)/i);
    if (m) return m[1].trim();
    if (raw.trim().startsWith("<!DOCTYPE") || raw.includes("<html")) return raw.trim();
    return null;
  }

  // ============================================================
  // 分享
  // ============================================================
  window.saveShare = async function () {
    if (!currentCode) return toast(t("builder.noCode"), "error");
    const title = $("project-title").textContent || "shared";
    const res = await fetch("/api/builder/share", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: currentProjectId, title, code: currentCode }),
    }).then(r => r.json()).catch(() => ({}));
    if (res.url) {
      const full = location.origin + res.url;
      await navigator.clipboard.writeText(full).catch(() => {});
      toast(t("builder.shareCopied", { url: full }), "success");
    } else {
      toast(t("builder.shareFailed"), "error");
    }
  };

  // ============================================================
  // 初始化
  // ============================================================
  document.addEventListener("DOMContentLoaded", async () => {
    applyLang(lang);
    await loadSettings();
    updateModelStatus();
    renderWelcomeIfEmpty();
    await loadProjects();

    const instr = $("instruction");
    if (instr) {
      instr.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          window.generate();
        }
      });
    }
  });
})();