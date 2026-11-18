// "Tack it up" form: validation, photo preview, and POST /api/listings
(function () {
  const form = document.getElementById("sell-form");
  if (!form) return;

  const errorBox = document.getElementById("sell-error");
  const photo = document.getElementById("photo");
  const preview = document.getElementById("photo-preview");
  const MAX_BYTES = 5 * 1024 * 1024;

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.hidden = false;
  }

  photo.addEventListener("change", () => {
    const file = photo.files[0];
    if (!file) {
      preview.hidden = true;
      return;
    }
    if (file.size > MAX_BYTES) {
      showError("Photo is too large (max 5 MB).");
      photo.value = "";
      preview.hidden = true;
      return;
    }
    errorBox.hidden = true;
    preview.src = URL.createObjectURL(file);
    preview.hidden = false;
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.hidden = true;

    const title = form.title.value.trim();
    const price = form.price.value.trim();
    const phone = form.phone.value.trim();

    if (title.length < 3) return showError("Give your item a title (at least 3 characters).");
    if (price === "" || Number(price) < 0) return showError("Enter 0 or a positive price.");
    if (!/^\d{10}$/.test(phone)) return showError("Enter a valid 10-digit phone number.");

    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    try {
      const res = await fetch("/api/listings", { method: "POST", body: new FormData(form) });
      const body = await res.json().catch(() => ({}));
      if (res.status === 401) {
        window.location.href = "/login?next=/%23sell";
        return;
      }
      if (!res.ok) {
        showError(body.error || "Could not post your ad. Try again.");
        btn.disabled = false;
        return;
      }
      window.location.href = "/listing/" + body.id;
    } catch (_) {
      showError("Network error. Is the server running?");
      btn.disabled = false;
    }
  });
})();
