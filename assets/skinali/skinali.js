(function () {
  var BASE = "/assets/skinali/";
  var N = 20;
  var main = document.querySelector(".main-image");
  var list = document.getElementById("list");
  var head = document.getElementById("list-head");

  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function esc(s) {
    return (s || "").replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function setSrc(sel, src, alt) {
    var img = main.querySelector(sel + " img");
    if (img) { img.src = src; if (alt != null) img.alt = alt; }
  }
  function clearSel() {
    list.querySelectorAll(".it.sel").forEach(function (x) { x.classList.remove("sel"); });
  }

  function buildSwatches(el, group, init) {
    var h = "";
    for (var i = 1; i <= N; i++) {
      var ij = pad(i);
      h += '<label><input type="radio" name="' + group + '" value="' + ij + '"' +
           (ij === init ? " checked" : "") +
           '><img src="' + BASE + "img/thumbs/thumb" + ij + '.png" alt=""></label>';
    }
    el.innerHTML = h;
    el.addEventListener("change", function (e) {
      var v = e.target.value;
      if (group === "top") setSrc(".top", BASE + "img/parts/top" + v + ".png");
      if (group === "compt") setSrc(".compt", BASE + "img/parts/compt" + v + ".png");
      if (group === "bottom") setSrc(".bottom", BASE + "img/parts/bottom" + v + ".png");
      if (group === "solid") { setSrc(".fartuk", BASE + "img/fart/solid" + v + ".png"); clearSel(); }
    });
  }

  buildSwatches(document.getElementById("sw-top"), "top", "01");
  buildSwatches(document.getElementById("sw-compt"), "compt", "01");
  buildSwatches(document.getElementById("sw-bottom"), "bottom", "01");
  buildSwatches(document.getElementById("sw-solid"), "solid", "04");
  setSrc(".fartuk", BASE + "img/fart/solid04.png");

  var light = document.getElementById("light");
  light.addEventListener("change", function () {
    main.querySelector(".light").style.visibility = light.checked ? "visible" : "hidden";
  });

  document.querySelectorAll(".sk-tabs__cap button").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll(".sk-tabs__cap button").forEach(function (x) { x.classList.remove("active"); });
      document.querySelectorAll(".sk-tab").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      document.querySelector(b.dataset.tab).classList.add("active");
    });
  });

  function render(items) {
    if (!items.length) { list.innerHTML = '<div class="empty">Нет изображений</div>'; return; }
    list.innerHTML = items.map(function (it) {
      return '<div class="it" data-src="' + it.t + '" title="' + esc(it.c) + '">' +
             '<img loading="lazy" src="' + it.t + '" alt="' + esc(it.c) + '">' +
             '<div class="c">' + esc(it.c) + "</div></div>";
    }).join("");
  }

  list.addEventListener("click", function (e) {
    var it = e.target.closest(".it");
    if (!it) return;
    clearSel();
    it.classList.add("sel");
    setSrc(".fartuk", it.dataset.src, it.title);
  });

  var chips = document.getElementById("chips");
  function loadCat(id, title) {
    head.textContent = title || "";
    list.innerHTML = '<div class="loading">Загрузка…</div>';
    fetch(BASE + "data/cat_" + id + ".json").then(function (r) { return r.json(); }).then(render);
  }
  fetch(BASE + "data/categories.json").then(function (r) { return r.json(); }).then(function (cats) {
    chips.innerHTML = cats.map(function (c) {
      return '<button data-id="' + c.id + '">' + esc(c.title) + "</button>";
    }).join("");
    chips.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      chips.querySelectorAll("button").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      loadCat(b.dataset.id, b.textContent);
    });
    if (cats.length) { chips.querySelector("button").classList.add("active"); loadCat(cats[0].id, cats[0].title); }
  });

  var qimg = new URLSearchParams(location.search).get("img");
  if (qimg) {
    setSrc(".fartuk", qimg, new URLSearchParams(location.search).get("code") || "");
    document.querySelectorAll(".sk-tabs__cap button").forEach(function (b) { b.classList.toggle("active", b.dataset.tab === "#tab-photo"); });
    document.querySelectorAll(".sk-tab").forEach(function (x) { x.classList.toggle("active", x.id === "tab-photo"); });
  }

  var PRICE_M2 = 3180, BACKLIGHT = 3000, INSTALL = 1950;
  function money(n) { return new Intl.NumberFormat("ru-RU").format(Math.round(n)) + " ₽"; }
  function calcPrice() {
    var w = parseFloat(document.getElementById("pw").value) || 0;
    var h = parseFloat(document.getElementById("ph").value) || 0;
    var area = (w / 1000) * (h / 1000);
    var total = area * PRICE_M2;
    if (document.getElementById("pback").checked) total += BACKLIGHT;
    if (document.getElementById("pinst").checked) total += INSTALL;
    document.getElementById("price").textContent = area > 0 ? "от " + money(total) : "—";
  }
  ["pw", "ph", "pback", "pinst"].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener("input", calcPrice);
  });
  if (document.getElementById("price")) calcPrice();

  var fitWrap = document.querySelector(".preview-fit");
  var mainImg = document.querySelector(".main-image");
  function fit() {
    if (!fitWrap || !mainImg) return;
    var s = Math.min(1, fitWrap.clientWidth / 700);
    mainImg.style.transform = "scale(" + s + ")";
    fitWrap.style.height = (466 * s) + "px";
  }
  window.addEventListener("resize", fit);
  window.addEventListener("load", fit);
  fit();
})();
