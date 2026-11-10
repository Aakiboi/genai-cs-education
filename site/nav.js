// Shared header + helpers for all pages.
(function () {
  const pages = [["index.html", "Findings"], ["validation.html", "Validation"],
                 ["timeline.html", "Timeline"], ["tokens.html", "Token usage"]];
  const here = location.pathname.split("/").pop() || "index.html";
  const h = document.createElement("header");
  h.className = "top";
  h.innerHTML = `<div class="wrap"><b>GenAI in CS Education</b><nav>${pages.map(([f, t]) =>
    `<a href="${f}" class="${f === here ? "on" : ""}">${t}</a>`).join("")}</nav></div>`;
  document.body.prepend(h);
})();

const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = n => n == null ? "—" : Number(n).toLocaleString();
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmtTime = s => new Date(s).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });

// Sortable table: cols = [{key, label, render?}]
function renderTable(el, rows, cols) {
  let sortKey = null, dir = 1;
  function draw() {
    const r = sortKey ? [...rows].sort((a, b) => {
      const x = a[sortKey], y = b[sortKey];
      return (x == null) - (y == null) || (x > y ? 1 : x < y ? -1 : 0) * dir;
    }) : rows;
    el.innerHTML = `<table><thead><tr>${cols.map(c => `<th data-k="${c.key}">${c.label}${sortKey === c.key ? (dir > 0 ? " ▲" : " ▼") : ""}</th>`).join("")}</tr></thead>
      <tbody>${r.map(row => `<tr>${cols.map(c => `<td>${c.render ? c.render(row) : esc(row[c.key])}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    el.querySelectorAll("th").forEach(th => th.onclick = () => {
      dir = sortKey === th.dataset.k ? -dir : 1; sortKey = th.dataset.k; draw();
    });
  }
  draw();
}

function chartDefaults() {
  if (!window.Chart) return;
  Chart.defaults.color = css("--muted");
  Chart.defaults.borderColor = css("--line");
  Chart.defaults.font.family = "system-ui, -apple-system, Segoe UI, sans-serif";
  Chart.defaults.maintainAspectRatio = false;
}
