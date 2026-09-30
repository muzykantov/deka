(function () {
  var BASE = "/assets/closet/";
  var imglist = document.getElementById("imglist");

  function esc(s) {
    return (s || "").replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  document.querySelectorAll("#tabs_closet > ul a").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      document.querySelectorAll("#tabs_closet > ul a").forEach(function (x) { x.classList.remove("active"); });
      a.classList.add("active");
      document.querySelectorAll(".choose_closet").forEach(function (x) { x.classList.remove("active"); });
      document.querySelector(a.getAttribute("href")).classList.add("active");
    });
  });

  document.querySelectorAll(".img_doors_style").forEach(function (el) {
    el.innerHTML = '<img src="" class="closet_show" alt="">';
  });

  function apply(src) {
    document.querySelectorAll(".img_doors_style").forEach(function (el) {
      el.innerHTML = '<img src="' + src + '" class="closet_show" alt="Вы выбрали этот рисунок.">';
    });
  }

  function select(img, scroll) {
    imglist.querySelectorAll(".this_closet_active").forEach(function (x) { x.classList.remove("this_closet_active"); });
    img.classList.add("this_closet_active");
    apply(img.getAttribute("src"));
    if (scroll) img.scrollIntoView({ block: "nearest", inline: "nearest" });
  }

  var qimg = new URLSearchParams(location.search).get("img");
  function clearActive() { imglist.querySelectorAll(".this_closet_active").forEach(function (x) { x.classList.remove("this_closet_active"); }); }

  function render(items) {
    if (!items.length) { imglist.innerHTML = '<li class="empty">Нет изображений</li>'; return; }
    imglist.innerHTML = items.map(function (it) {
      return '<li><img class="big_i" src="' + it.t + '" data-c="' + esc(it.c) + '" alt="' + esc(it.c) + '">' +
             '<span class="id_closet">' + esc(it.c) + "</span></li>";
    }).join("");
    if (qimg) {
      var match = null;
      imglist.querySelectorAll("img.big_i").forEach(function (x) { if (x.getAttribute("src") === qimg) match = x; });
      if (match) select(match, false); else { clearActive(); apply(qimg); }
    } else {
      var f = imglist.querySelector("img.big_i");
      if (f) select(f);
    }
  }

  imglist.addEventListener("click", function (e) {
    var img = e.target.closest("img.big_i");
    if (img) select(img, true);
  });

  var chips = document.getElementById("chips");
  function loadCat(id) {
    imglist.innerHTML = '<li class="empty">Загрузка…</li>';
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
      loadCat(b.dataset.id);
    });
    if (cats.length) { chips.querySelector("button").classList.add("active"); loadCat(cats[0].id); }
  });

  if (qimg) apply(qimg);
})();
