// Browse page: filters, search, and rendering listings from /api/listings
(function () {
  const grid = document.getElementById("grid");
  if (!grid) return;

  const emptyBox = document.getElementById("empty");
  const countEl = document.getElementById("count");
  const qEl = document.getElementById("f-q");
  const condEl = document.getElementById("f-condition");
  const hostelEl = document.getElementById("f-hostel");
  const sortEl = document.getElementById("f-sort");
  const priceEl = document.getElementById("f-price");
  const priceLabel = document.getElementById("f-price-label");
  const chips = document.getElementById("chips");
  const MAX_PRICE = Number(priceEl.max);

  const state = { category: "All" };
  const EMOJI = {
    "Books & Notes": "📚",
    "Electronics": "💻",
    "Furniture": "🛋",
    "Bikes & Cycles": "🚲",
    "Hostel Essentials": "🪣",
    "Tickets & Passes": "🎟",
  };

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function formatPrice(n) {
    return n === 0 ? "Free" : "₹" + Number(n).toLocaleString("en-IN");
  }

  function timeAgo(iso) {
    const secs = Math.max(1, (Date.now() - new Date(iso).getTime()) / 1000);
    const units = [["day", 86400], ["hour", 3600], ["minute", 60]];
    for (const [name, size] of units) {
      if (secs >= size) {
        const n = Math.floor(secs / size);
        return `${n} ${name}${n > 1 ? "s" : ""} ago`;
      }
    }
    return "just now";
  }

  function card(l) {
    const img = l.image
      ? `<img src="${esc(l.image)}" alt="" loading="lazy">`
      : esc(EMOJI[l.category] || "📦");
    return `
      <a class="card" href="/listing/${l.id}">
        <div class="card-img">${img}</div>
        <div class="card-body">
          <p class="price">${formatPrice(l.price)}</p>
          <h3>${esc(l.title)}</h3>
          <span class="badge">${esc(l.condition_label)}</span>
          <p class="meta">${esc(l.hostel)} · ${timeAgo(l.created_at)}</p>
        </div>
      </a>`;
  }

  async function load() {
    const p = new URLSearchParams();
    if (qEl.value.trim()) p.set("q", qEl.value.trim());
    if (state.category !== "All") p.set("category", state.category);
    if (Number(priceEl.value) < MAX_PRICE) p.set("max_price", priceEl.value);
    if (condEl.value) p.set("condition", condEl.value);
    if (hostelEl.value) p.set("hostel", hostelEl.value);
    p.set("sort", sortEl.value);

    try {
      const res = await fetch("/api/listings?" + p.toString());
      const data = await res.json();
      const list = data.listings || [];
      grid.innerHTML = list.map(card).join("");
      countEl.textContent = `${list.length} listing${list.length === 1 ? "" : "s"}`;
      emptyBox.hidden = list.length > 0;
    } catch (_) {
      grid.innerHTML = "";
      countEl.textContent = "";
      emptyBox.textContent = "Could not load listings. Is the server running?";
      emptyBox.hidden = false;
    }
  }

  function updatePriceLabel() {
    const v = Number(priceEl.value);
    priceLabel.textContent = v >= MAX_PRICE ? "Any price" : "Up to ₹" + v.toLocaleString("en-IN");
  }

  let timer;
  qEl.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(load, 300);
  });
  [condEl, hostelEl, sortEl].forEach((el) => el.addEventListener("change", load));
  priceEl.addEventListener("input", () => {
    updatePriceLabel();
    clearTimeout(timer);
    timer = setTimeout(load, 200);
  });

  chips.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    chips.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    state.category = chip.dataset.cat;
    load();
  });

  document.getElementById("f-reset").addEventListener("click", () => {
    qEl.value = "";
    condEl.value = "";
    hostelEl.value = "";
    sortEl.value = "newest";
    priceEl.value = MAX_PRICE;
    state.category = "All";
    chips.querySelectorAll(".chip").forEach((c) => c.classList.toggle("active", c.dataset.cat === "All"));
    updatePriceLabel();
    load();
  });

  updatePriceLabel();
  load();
})();
