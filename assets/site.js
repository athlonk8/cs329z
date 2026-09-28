/* CS 329Z 中文学习站 — 客户端搜索 */
(function () {
  var input = document.getElementById("search-input");
  var box = document.getElementById("search-results");
  if (!input || !box) return;
  var data = null;
  var inReading = /\/reading\//.test(location.pathname);
  var prefix = inReading ? "" : "reading/";

  fetch((inReading ? "../" : "") + "assets/search.json")
    .then(function (r) { return r.json(); })
    .then(function (d) { data = d; })
    .catch(function () { data = []; });

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function render(q) {
    if (!data) return;
    q = q.trim().toLowerCase();
    if (!q) { box.hidden = true; return; }
    var hits = data.filter(function (it) {
      return (it.title_zh + " " + it.title + " " + it.summary + " " + it.tags + " " + it.week)
        .toLowerCase().indexOf(q) !== -1;
    }).slice(0, 12);
    if (!hits.length) {
      box.innerHTML = '<div class="sr-empty">没有匹配的材料</div>';
    } else {
      box.innerHTML = hits.map(function (it) {
        return '<a href="' + prefix + it.slug + '.html">' + esc(it.title_zh) +
          ' <span class="sr-week">· ' + esc(it.week) + " · " + esc(it.kind) + "</span></a>";
      }).join("");
    }
    box.hidden = false;
  }

  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { render(input.value); }, 120);
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { box.hidden = true; input.blur(); }
  });
  document.addEventListener("click", function (e) {
    if (!box.contains(e.target) && e.target !== input) box.hidden = true;
  });
})();

/* 中英对照切换 */
(function () {
  var btn = document.getElementById("lang-toggle");
  if (!btn) return;
  var mode = localStorage.getItem("cs329z-lang") || "both";
  function apply() {
    document.body.classList.toggle("zh-only", mode === "zh");
    btn.textContent = mode === "zh" ? "显示英文" : "仅看中文";
  }
  btn.addEventListener("click", function () {
    mode = mode === "zh" ? "both" : "zh";
    localStorage.setItem("cs329z-lang", mode);
    apply();
  });
  apply();
})();
