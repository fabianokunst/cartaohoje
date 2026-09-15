/* Cartão Hoje — interações mínimas (~1,5 KB). Sem dependências. */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  /* Header: sombra ao rolar */
  var hdr = document.querySelector(".hdr");
  if (hdr) {
    var onScroll = function () {
      if (window.scrollY > 8) hdr.setAttribute("data-stuck", "");
      else hdr.removeAttribute("data-stuck");
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* Menu mobile */
  var burger = document.querySelector(".burger");
  var mnav = document.getElementById("menu-mobile");
  if (burger && mnav) {
    burger.addEventListener("click", function () {
      var open = burger.getAttribute("aria-expanded") === "true";
      burger.setAttribute("aria-expanded", String(!open));
      if (open) mnav.removeAttribute("data-open");
      else mnav.setAttribute("data-open", "");
    });
    mnav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        burger.setAttribute("aria-expanded", "false");
        mnav.removeAttribute("data-open");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && burger.getAttribute("aria-expanded") === "true") {
        burger.setAttribute("aria-expanded", "false");
        mnav.removeAttribute("data-open");
        burger.focus();
      }
    });
  }

  /* Reveal on scroll — desligado se o usuário pedir menos movimento */
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var items = document.querySelectorAll(".rv");
  if (reduce || !("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(items, function (el) { el.setAttribute("data-in", ""); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.setAttribute("data-in", "");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });

    /* O que já está na primeira tela aparece de imediato: nada legível
       depende de rolagem, e não há flash de conteúdo em telas altas. */
    Array.prototype.forEach.call(items, function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) el.setAttribute("data-in", "");
      else io.observe(el);
    });

    /* Rede de segurança: nada pode ficar invisível para sempre
       (viewports muito altos, impressão, IO que não dispara). */
    window.addEventListener("load", function () {
      setTimeout(function () {
        Array.prototype.forEach.call(items, function (el) {
          if (el.hasAttribute("data-in")) return;
          var r = el.getBoundingClientRect();
          if (r.top < window.innerHeight) el.setAttribute("data-in", "");
        });
      }, 900);
    });
  }

  /* Acordeão do FAQ: abre só um por vez dentro do mesmo grupo */
  document.querySelectorAll("[data-accordion]").forEach(function (group) {
    var all = group.querySelectorAll("details");
    all.forEach(function (d) {
      d.addEventListener("toggle", function () {
        if (!d.open) return;
        all.forEach(function (o) { if (o !== d) o.open = false; });
      });
    });
  });
})();
