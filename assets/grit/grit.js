(function () {
  var BASE = "/assets/grit/";
  var facade = document.getElementById("facade");
  var facadeWrap = document.getElementById("facade-wrap");
  var wardrobe = document.getElementById("wardrobe");
  var imglist = document.getElementById("imglist");
  var count = 2;
  var mode = "facade";
  var current = null;
  var qimg = new URLSearchParams(location.search).get("img");

  function esc(s) {
    return (s || "").replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function paint() {
    if (mode === "facade") {
      var mull = "";
      for (var i = 1; i < count; i++) {
        mull += '<div class="mullion" style="left:' + (i * 100 / count) + '%"></div>';
      }
      facade.innerHTML = '<div class="inner"><div class="glass"' +
        (current ? ' style="background-image:url(\'' + current + '\')"' : "") + "></div>" + mull + "</div>";
    } else {
      document.querySelectorAll("#wardrobe .style_doors").forEach(function (s) {
        s.classList.toggle("active", parseInt(s.dataset.n, 10) === count);
      });
    }
  }

  function applyPattern() {
    document.querySelectorAll("#wardrobe .img_doors_style").forEach(function (el) {
      el.innerHTML = current ? '<img src="' + current + '" alt="">' : "";
    });
  }

  var firstCount = document.querySelector('#count button[data-n="1"]');
  function syncCount() {
    if (firstCount) firstCount.hidden = mode === "closet";
    if (mode === "closet" && count === 1) {
      count = 2;
      document.querySelectorAll("#count button").forEach(function (x) { x.classList.toggle("active", x.dataset.n === "2"); });
    }
  }

  document.querySelectorAll("#mode button").forEach(function (b) {
    b.addEventListener("click", function () {
      mode = b.dataset.mode || "facade";
      document.querySelectorAll("#mode button").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      facadeWrap.hidden = mode !== "facade";
      wardrobe.hidden = mode !== "closet";
      syncCount();
      paint();
    });
  });

  document.querySelectorAll("#count button").forEach(function (b) {
    b.addEventListener("click", function () {
      count = parseInt(b.dataset.n, 10) || 1;
      document.querySelectorAll("#count button").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      paint();
    });
  });

  function selectImg(img) {
    imglist.querySelectorAll(".this_closet_active").forEach(function (x) { x.classList.remove("this_closet_active"); });
    img.classList.add("this_closet_active");
    current = img.getAttribute("src");
    paint();
    applyPattern();
  }

  function clearActive() { imglist.querySelectorAll(".this_closet_active").forEach(function (x) { x.classList.remove("this_closet_active"); }); }

  function renderList(items) {
    if (!items.length) { imglist.innerHTML = '<li class="empty">Нет изображений</li>'; return; }
    imglist.innerHTML = items.map(function (it) {
      return '<li><img class="big_i" src="' + it.t + '" alt="' + esc(it.c) + '"><span class="id_closet">' + esc(it.c) + "</span></li>";
    }).join("");
    if (qimg) {
      var match = null;
      imglist.querySelectorAll("img.big_i").forEach(function (x) { if (x.getAttribute("src") === qimg) match = x; });
      if (match) selectImg(match); else { clearActive(); current = qimg; paint(); applyPattern(); }
    } else {
      var f = imglist.querySelector("img.big_i");
      if (f) selectImg(f);
    }
  }

  imglist.addEventListener("click", function (e) {
    var img = e.target.closest("img.big_i");
    if (img) selectImg(img);
  });

  var chips = document.getElementById("chips");
  var head = document.getElementById("list-head");
  function loadCat(id, title) {
    head.textContent = title || "";
    imglist.innerHTML = '<li class="empty">Загрузка…</li>';
    fetch(BASE + "data/cat_" + id + ".json").then(function (r) { return r.json(); }).then(renderList);
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
    if (cats.length) {
      chips.querySelector("button").classList.add("active");
      loadCat(cats[0].id, cats[0].title);
    }
  });

  paint();
  applyPattern();
  if (qimg) { current = qimg; paint(); applyPattern(); }
})();
