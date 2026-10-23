(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);

  const AUTH_LANG = {
    // 语言切换时更新 data-* 属性
    "history": {
      strengthWeak: { en: "Weak", zh: "弱" },
      strengthFair: { en: "Fair", zh: "一般" },
      strengthGood: { en: "Good", zh: "良好" },
      strengthStrong: { en: "Strong", zh: "强" },
      strengthLabel: { en: "Strength", zh: "强度" },
      networkError: { en: "Network error. Please try again.", zh: "网络错误，请重试。" },
      pwMismatch: { en: "Passwords do not match.", zh: "两次密码不一致。" },
      pwWeak: { en: "Password does not meet requirements.", zh: "密码不符合要求。" },
      accountCreated: { en: "Account created.", zh: "账号已创建。" },
      passwordUpdated: { en: "Password updated.", zh: "密码已更新。" },
      resetGenerated: { en: "If this email exists, a reset link has been generated.", zh: "如果该邮箱存在，已生成重置链接。" },
      resetDemoLink: { en: "Demo reset link:", zh: "演示重置链接：" },
    }
  };

  function getLang() {
    return localStorage.getItem("routemind_lang") || "en";
  }

  function setLang(lang) {
    localStorage.setItem("routemind_lang", lang);
    applyLang(lang);
  }

  function applyLang(lang) {
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    document.querySelectorAll("[data-en]").forEach((el) => {
      const val = el.dataset[lang];
      if (val != null) el.textContent = val;
    });
    document.querySelectorAll("[data-en-placeholder]").forEach((el) => {
      const val = el.dataset[lang + "Placeholder"];
      if (val != null) el.placeholder = val;
    });
    // Update language switch buttons
    document.querySelectorAll("#lang-switch button").forEach((b) => {
      b.classList.toggle("active", b.dataset.lang === lang);
    });
    // Update password strength label
    updateStrength();
  }

  function toast(msg, type = "") {
    const el = $("toast");
    if (!el) return;
    el.textContent = msg;
    el.className = `toast show ${type}`;
    clearTimeout(el._tid);
    el._tid = setTimeout(() => (el.className = "toast"), 3000);
  }

  function label(key) {
    const lang = getLang();
    return AUTH_LANG.history[key][lang] || AUTH_LANG.history[key].en;
  }

  async function postJSON(url, body) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
      });
      return res.json().catch(() => ({}));
    } catch (e) {
      return { error: label("networkError") };
    }
  }

  function showForm(formId) {
    ["form-login", "form-register", "form-forgot", "form-reset"].forEach((id) => {
      const el = $(id);
      if (el) el.classList.toggle("hidden", id !== formId);
    });
    const mode = formId.replace("form-", "");
    document.querySelectorAll(".auth-tab").forEach((t) =>
      t.classList.toggle("active", t.dataset.mode === mode)
    );
    const firstInput = $(formId)?.querySelector("input:not([type=hidden]):not([type=checkbox])");
    if (firstInput) setTimeout(() => firstInput.focus(), 50);
  }

  // Language switch
  document.querySelectorAll("#lang-switch button").forEach((btn) => {
    btn.addEventListener("click", () => setLang(btn.dataset.lang));
  });

  document.querySelectorAll(".auth-tab").forEach((tab) => {
    tab.addEventListener("click", () => showForm(`form-${tab.dataset.mode}`));
  });
  $("link-forgot")?.addEventListener("click", (e) => {
    e.preventDefault(); showForm("form-forgot");
  });
  document.querySelectorAll("[data-back]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault(); showForm(`form-${el.dataset.back}`);
    });
  });

  function evaluateStrength(pw) {
    return {
      len: pw.length >= 8,
      upper: /[A-Z]/.test(pw),
      digit: /\d/.test(pw),
      symbol: /[!@#$%^&*()_\-+=\[\]{};:'",.<>/?\\|`~]/.test(pw),
    };
  }
  function updateStrength() {
    const pw = $("reg-password")?.value || "";
    const checks = evaluateStrength(pw);
    document.querySelectorAll(".pw-req").forEach((el) => {
      const k = el.dataset.req;
      el.classList.toggle("met", !!checks[k]);
    });
    const score = Object.values(checks).filter(Boolean).length;
    const fill = $("pw-fill");
    const labelEl = $("pw-label");
    if (!fill || !labelEl) return;
    const lang = getLang();
    const map = [
      { w: "0%", color: "var(--border)", text: "—" },
      { w: "25%", color: "var(--danger)", text: label("strengthWeak") },
      { w: "50%", color: "var(--warning)", text: label("strengthFair") },
      { w: "75%", color: "#eab308", text: label("strengthGood") },
      { w: "100%", color: "var(--success)", text: label("strengthStrong") },
    ];
    const s = map[Math.min(score, 4)];
    fill.style.width = s.w;
    fill.style.background = s.color;
    labelEl.textContent = `${label("strengthLabel")}: ${s.text}`;
  }
  $("reg-password")?.addEventListener("input", updateStrength);

  const formLogin = $("form-login");
  if (formLogin) {
    formLogin.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = formLogin.querySelector("button[type=submit]");
      btn.disabled = true;
      btn.textContent = getLang() === "zh" ? "登录中…" : "Signing in…";
      try {
        const res = await postJSON("/api/auth/login", {
          identifier: $("login-identifier").value.trim(),
          password: $("login-password").value,
          remember: $("login-remember").checked,
        });
        if (res.error) { toast(res.error, "error"); return; }
        window.location.href = "/";
      } catch (err) {
        toast(label("networkError"), "error");
      } finally {
        btn.disabled = false;
        btn.textContent = getLang() === "zh" ? "登录" : "Sign In";
      }
    });
  }

  const formRegister = $("form-register");
  if (formRegister) {
    formRegister.addEventListener("submit", async (e) => {
      e.preventDefault();
      const pw = $("reg-password").value;
      const cf = $("reg-confirm").value;
      if (pw !== cf) { toast(label("pwMismatch"), "error"); return; }
      const checks = evaluateStrength(pw);
      if (!checks.len || !checks.upper || !checks.digit) {
        toast(label("pwWeak"), "error"); return;
      }
      const btn = formRegister.querySelector("button[type=submit]");
      btn.disabled = true;
      btn.textContent = getLang() === "zh" ? "创建中…" : "Creating…";
      try {
        const res = await postJSON("/api/auth/register", {
          username: $("reg-username").value.trim(),
          email: $("reg-email").value.trim(),
          password: pw,
          confirm: cf,
        });
        if (res.error) { toast(res.error, "error"); return; }
        toast(label("accountCreated"), "success");
        setTimeout(() => {
          $("login-identifier").value = $("reg-email").value.trim();
          $("reg-password").value = "";
          $("reg-confirm").value = "";
          $("reg-username").value = "";
          $("reg-email").value = "";
          showForm("form-login");
        }, 800);
      } catch (err) {
        toast(label("networkError"), "error");
      } finally {
        btn.disabled = false;
        btn.textContent = getLang() === "zh" ? "创建账号" : "Create Account";
      }
    });
  }

  const formForgot = $("form-forgot");
  if (formForgot) {
    formForgot.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = formForgot.querySelector("button[type=submit]");
      btn.disabled = true;
      btn.textContent = getLang() === "zh" ? "生成中…" : "Generating…";
      try {
        const res = await postJSON("/api/auth/forgot", {
          email: $("forgot-email").value.trim(),
        });
        const box = $("forgot-result");
        box.classList.remove("hidden");
        if (res.demo_reset_url) {
          box.innerHTML = `${label("resetDemoLink")} <a href="${res.demo_reset_url}">${res.demo_reset_url}</a>`;
        } else {
          box.textContent = res.message || label("resetGenerated");
        }
      } catch (err) {
        toast(label("networkError"), "error");
      } finally {
        btn.disabled = false;
        btn.textContent = getLang() === "zh" ? "生成重置链接" : "Generate Reset Link";
      }
    });
  }

  const formReset = $("form-reset");
  if (formReset) {
    formReset.addEventListener("submit", async (e) => {
      e.preventDefault();
      const pw = $("reset-password").value;
      const cf = $("reset-confirm").value;
      if (pw !== cf) { toast(label("pwMismatch"), "error"); return; }
      const btn = formReset.querySelector("button[type=submit]");
      btn.disabled = true;
      btn.textContent = getLang() === "zh" ? "更新中…" : "Updating…";
      try {
        const res = await postJSON("/api/auth/reset", {
          token: $("reset-token").value,
          password: pw,
        });
        if (res.error) { toast(res.error, "error"); return; }
        toast(label("passwordUpdated"), "success");
        setTimeout(() => (window.location.href = "/login"), 1000);
      } catch (err) {
        toast(label("networkError"), "error");
      } finally {
        btn.disabled = false;
        btn.textContent = getLang() === "zh" ? "更新密码" : "Update Password";
      }
    });
  }

  // Init
  applyLang(getLang());
})();