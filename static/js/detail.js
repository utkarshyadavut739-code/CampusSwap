// Listing detail page: reveal seller's number and send a message
(function () {
  const box = document.getElementById("contact-box");
  if (!box) return;

  const id = box.dataset.id;
  const showBtn = document.getElementById("show-contact");
  const info = document.getElementById("contact-info");
  const phoneEl = document.getElementById("contact-phone");
  const copyBtn = document.getElementById("copy-phone");
  const form = document.getElementById("msg-form");
  const feedback = document.getElementById("msg-feedback");

  showBtn.addEventListener("click", async () => {
    const res = await fetch(`/api/listings/${id}/contact`);
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      alert(body.error || "Could not load contact details.");
      return;
    }
    phoneEl.textContent = body.phone;
    info.hidden = false;
    showBtn.hidden = true;
  });

  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(phoneEl.textContent);
      copyBtn.textContent = "Copied!";
    } catch (_) {
      copyBtn.textContent = "Copy failed";
    }
    setTimeout(() => (copyBtn.textContent = "Copy number"), 1500);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    feedback.hidden = true;
    const body = form.body.value.trim();
    const res = await fetch(`/api/listings/${id}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body }),
    });
    const data = await res.json().catch(() => ({}));
    feedback.hidden = false;
    if (res.ok) {
      feedback.className = "success";
      feedback.textContent = "Message sent! The seller will see it in their inbox.";
      form.reset();
    } else {
      feedback.className = "error";
      feedback.textContent = data.error || "Could not send message.";
    }
  });
})();
