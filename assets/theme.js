(function () {
  var root = document.documentElement;
  var SUN = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';

  function current() {
    var saved = localStorage.getItem("deka-theme");
    return saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  var theme = current();
  root.setAttribute("data-theme", theme);

  function paint() {
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.innerHTML = theme === "dark" ? SUN : MOON;
      b.setAttribute("aria-label", theme === "dark" ? "Светлая тема" : "Тёмная тема");
    });
  }
  function toggle() {
    theme = theme === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", theme);
    localStorage.setItem("deka-theme", theme);
    paint();
  }
  document.addEventListener("DOMContentLoaded", function () {
    paint();
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) { b.addEventListener("click", toggle); });
    document.querySelectorAll(".qsearch").forEach(function (f) {
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        var q = f.querySelector("input").value.trim();
        location.href = "/search.html?q=" + encodeURIComponent(q);
      });
    });
    var burger = document.querySelector(".burger");
    var nav = document.querySelector(".nav");
    if (burger && nav) burger.addEventListener("click", function () { nav.classList.toggle("open"); });
  });
  window.DEKA = { toggleTheme: toggle, getTheme: function () { return theme; } };
})();
