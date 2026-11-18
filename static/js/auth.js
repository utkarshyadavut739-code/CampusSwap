// Runs on every page: logout button, plus login/register forms when present.
(function () {
  async function postJSON(url, data) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data || {}),
    });
    let body = {};
    try { body = await res.json(); } catch (_) {}
    return { ok: res.ok, status: res.status, body };
  }

  function safeNext(value) {
    // only allow same-site relative paths
    return value && value.startsWith("/") && !value.startsWith("//") ? value : "/";
  }

  const logout = document.getElementById("logout-btn");
  if (logout) {
    logout.addEventListener("click", async () => {
      await postJSON("/api/logout");
      window.location.href = "/";
    });
  }

  function wireForm(formId, url, redirectTo) {
    const form = document.getElementById(formId);
    if (!form) return;
    const errorBox = document.getElementById("auth-error");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      errorBox.hidden = true;
      const btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      const data = Object.fromEntries(new FormData(form).entries());
      const { ok, body } = await postJSON(url, data);
      if (ok) {
        window.location.href = redirectTo(form);
      } else {
        errorBox.textContent = body.error || "Something went wrong. Try again.";
        errorBox.hidden = false;
        btn.disabled = false;
      }
    });
  }

  wireForm("login-form", "/api/login", (f) => safeNext(f.dataset.next));
  wireForm("register-form", "/api/register", () => "/");
})();
