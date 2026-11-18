// My listings page: mark sold, edit, delete, plus buyer messages
(function () {
  const mine = document.getElementById("mine");
  if (!mine) return;

  const mineEmpty = document.getElementById("mine-empty");
  const inbox = document.getElementById("inbox");
  const inboxEmpty = document.getElementById("inbox-empty");

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const price = (n) => (n === 0 ? "Free" : "₹" + Number(n).toLocaleString("en-IN"));

  async function api(url, method, data) {
    const res = await fetch(url, {
      method,
      headers: data ? { "Content-Type": "application/json" } : {},
      body: data ? JSON.stringify(data) : undefined,
    });
    if (res.status === 401) {
      window.location.href = "/login?next=/my-listings";
      return null;
    }
    const body = await res.json().catch(() => ({}));
    return { ok: res.ok, body };
  }

  async function loadMine() {
    const r = await api("/api/my-listings", "GET");
    if (!r) return;
    const list = r.body.listings || [];
    mineEmpty.hidden = list.length > 0;
    mine.innerHTML = list
      .map(
        (l) => `
      <div class="mine-row">
        <div class="mine-info">
          <h3><a href="/listing/${l.id}">${esc(l.title)}</a>
            ${l.status === "sold" ? '<span class="badge badge-sold">Sold</span>' : ""}</h3>
          <p class="meta">${price(l.price)} · ${esc(l.category)} · ${esc(l.hostel)}</p>
        </div>
        <div class="actions">
          <button class="btn btn-ghost btn-small" data-action="sold" data-id="${l.id}">
            ${l.status === "sold" ? "Mark available" : "Mark sold"}
          </button>
          <button class="btn btn-ghost btn-small" data-action="edit" data-id="${l.id}"
            data-title="${esc(l.title)}" data-price="${l.price}">Edit</button>
          <button class="btn btn-danger btn-small" data-action="delete" data-id="${l.id}">Delete</button>
        </div>
      </div>`
      )
      .join("");
  }

  async function loadInbox() {
    const r = await api("/api/inbox", "GET");
    if (!r) return;
    const msgs = r.body.messages || [];
    inboxEmpty.hidden = msgs.length > 0;
    inbox.innerHTML = msgs
      .map(
        (m) => `
      <div class="inbox-item">
        <strong>${esc(m.sender_name)} <span class="muted">about</span>
          <a href="/listing/${m.listing_id}">${esc(m.title)}</a></strong>
        <p style="margin:0">${esc(m.body)}</p>
        <span class="meta">Reply: ${esc(m.sender_phone)} · ${esc(m.sender_email)} ·
          ${new Date(m.created_at).toLocaleString()}</span>
      </div>`
      )
      .join("");
  }

  mine.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;

    if (btn.dataset.action === "sold") {
      await api(`/api/listings/${id}/sold`, "POST", {});
    } else if (btn.dataset.action === "delete") {
      if (!confirm("Delete this listing permanently?")) return;
      await api(`/api/listings/${id}`, "DELETE");
    } else if (btn.dataset.action === "edit") {
      const title = prompt("New title:", btn.dataset.title);
      if (title === null) return;
      const newPrice = prompt("New price (₹):", btn.dataset.price);
      if (newPrice === null) return;
      const r = await api(`/api/listings/${id}`, "PUT", { title, price: newPrice });
      if (r && !r.ok) alert(r.body.error || "Could not update listing.");
    }
    loadMine();
  });

  loadMine();
  loadInbox();
})();
