/* vXv Barber's — interactions & motion (GSAP + ScrollTrigger + Lenis) */
(function () {
  "use strict";
  var d = document, html = d.documentElement, body = d.body;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var shot = /[?&]shot\b/.test(location.search);
  var reduce = shot || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var G = window.gsap, ST = window.ScrollTrigger;
  var motion = !!(G && ST) && !reduce;
  var store = {
    get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  };
  if (motion) G.registerPlugin(ST);

  /* ---------- smooth scroll (desktop pointers only) ---------- */
  var lenis = null;
  if (motion && fine && window.Lenis) {
    lenis = new window.Lenis({ duration: 1.15, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); } });
    lenis.on("scroll", ST.update);
    G.ticker.add(function (t) { lenis.raf(t * 1000); });
    G.ticker.lagSmoothing(0);
  }

  /* ---------- header ---------- */
  var hdr = $(".hdr"), lastY = 0;
  var onScrollHdr = function () {
    var y = window.scrollY || html.scrollTop;
    hdr.classList.toggle("solid", y > 30);
    if (!body.classList.contains("menu-open")) {
      if (y > 500 && y > lastY + 4) hdr.classList.add("hide");
      else if (y < lastY - 4 || y < 500) hdr.classList.remove("hide");
    }
    lastY = y;
  };
  window.addEventListener("scroll", onScrollHdr, { passive: true });
  onScrollHdr();

  /* ---------- mobile menu ---------- */
  var burger = $(".burger");
  var setMenu = function (open) {
    body.classList.toggle("menu-open", open);
    burger.setAttribute("aria-expanded", open);
    burger.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
    hdr.classList.remove("hide");
    if (lenis) open ? lenis.stop() : lenis.start();
  };
  if (burger) burger.addEventListener("click", function () { setMenu(!body.classList.contains("menu-open")); });
  d.addEventListener("keydown", function (e) { if (e.key === "Escape" && body.classList.contains("menu-open")) setMenu(false); });

  /* ---------- page transitions ---------- */
  var curtain = $(".curtain");
  if (motion && curtain) {
    if (store.get("vxv-nav")) {
      G.set(curtain, { yPercent: 0 });
      G.to(curtain, { yPercent: -101, duration: .9, ease: "power4.inOut", delay: .05 });
      store.set("vxv-nav", "");
    }
    d.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a");
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === "_blank" || a.hasAttribute("download")) return;
      var url = new URL(a.href, location.href);
      if (url.origin !== location.origin || url.protocol.indexOf("http") !== 0) return;
      if (url.pathname === location.pathname) return;
      e.preventDefault();
      store.set("vxv-nav", "1");
      G.fromTo(curtain, { yPercent: 101 }, { yPercent: 0, duration: .6, ease: "power4.inOut", onComplete: function () { location.href = url.href; } });
    });
    window.addEventListener("pageshow", function (e) { if (e.persisted) G.set(curtain, { yPercent: 101 }); });
  }

  /* ---------- hero intro (+ loader on first visit) ---------- */
  var hero = $(".hero");
  var heroIntro = function () {
    if (!motion || !hero) return;
    var tl = G.timeline({ defaults: { ease: "power4.out" } });
    tl.from($$(".hero h1 .line>span"), { yPercent: 112, duration: 1.3, stagger: .1 })
      .from($$(".hero [data-in]"), { y: 24, autoAlpha: 0, duration: 1, stagger: .07 }, "-=1")
      .from($$(".trip .panel"), { yPercent: 18, autoAlpha: 0, duration: 1.4, stagger: .12 }, "-=1.05")
      .from($$(".trip .panel .media"), { scale: 1.25, duration: 1.8, stagger: .12, ease: "power3.out" }, "<");
  };
  var loader = $(".loader");
  if (loader) {
    if (!motion || store.get("vxv-intro")) { loader.remove(); heroIntro(); }
    else {
      store.set("vxv-intro", "1");
      if (lenis) lenis.stop();
      var cnt = $(".loader-count", loader), o = { v: 0 };
      var tl0 = G.timeline();
      tl0.from($$("polygon", loader), { scaleY: 0, transformOrigin: "50% 100%", duration: .8, stagger: .09, ease: "power4.out" })
        .to(o, { v: 100, duration: 1.2, ease: "power2.inOut", onUpdate: function () { cnt.textContent = Math.round(o.v); } }, 0)
        .to(loader, { yPercent: -100, duration: 1, ease: "power4.inOut" }, "+=.15")
        .add(function () { heroIntro(); }, "-=.55")
        .add(function () { loader.remove(); if (lenis) lenis.start(); });
    }
  } else heroIntro();

  /* ---------- scroll motion ---------- */
  if (motion) {
    // generic fade-up, batched so siblings stagger
    ST.batch("[data-rv]", {
      start: "top 90%", once: true,
      onEnter: function (els) { G.to(els, { y: 0, autoAlpha: 1, duration: 1.1, stagger: .08, ease: "power3.out", overwrite: true }); }
    });
    G.set("[data-rv]", { y: 36, autoAlpha: 0 });

    // headings: masked line reveals
    $$("[data-lines]").forEach(function (h) {
      if (h.closest(".hero")) return;
      G.from($$(".line>span", h), { yPercent: 112, duration: 1.2, stagger: .09, ease: "power4.out", scrollTrigger: { trigger: h, start: "top 88%", once: true } });
    });

    // images: a veil lifts off the frame (the image itself is never clipped, so lazy-loading still fires)
    $$(".ph[data-reveal]").forEach(function (ph) {
      var veil = d.createElement("i");
      veil.style.cssText = "position:absolute;inset:0;z-index:3;background:#e9e6df;transform-origin:50% 0;pointer-events:none";
      ph.appendChild(veil);
      var media = $("img,video", ph);
      var tl = G.timeline({ scrollTrigger: { trigger: ph, start: "top 88%", once: true } });
      tl.to(veil, { scaleY: 0, duration: 1.2, ease: "power4.inOut" });
      if (media) tl.from(media, { scale: 1.22, duration: 1.8, ease: "power3.out" }, 0);
    });

    // parallax inside frames
    $$("[data-par]").forEach(function (el) {
      var amt = parseFloat(el.getAttribute("data-par")) || 8;
      G.fromTo(el, { yPercent: -amt, scale: 1.18 }, { yPercent: amt, scale: 1.18, ease: "none", scrollTrigger: { trigger: el.parentNode, start: "top bottom", end: "bottom top", scrub: true } });
    });

    // hero panels drift as the hero leaves
    if ($(".trip")) {
      $$(".trip .panel .media").forEach(function (m, i) {
        G.to(m, { yPercent: 10 + i * 3, ease: "none", scrollTrigger: { trigger: ".trip", start: "top 60%", end: "bottom top", scrub: true } });
      });
    }

    // counters
    $$("[data-count]").forEach(function (el) {
      var to = parseFloat(el.getAttribute("data-count")), dec = (el.getAttribute("data-count").split(".")[1] || "").length, o = { v: 0 };
      G.to(o, { v: to, duration: 2, ease: "power3.out", scrollTrigger: { trigger: el, start: "top 92%", once: true },
        onUpdate: function () { el.textContent = o.v.toFixed(dec).replace(".", ","); } });
    });

    // big footer word
    var fw = $$(".ftr-word span");
    if (fw.length) G.from(fw, { yPercent: 100, duration: 1.2, stagger: .06, ease: "power4.out", scrollTrigger: { trigger: ".ftr-word", start: "top 95%", once: true } });

    // horizontal gallery — pinned on desktop only
    var mm = G.matchMedia();
    mm.add("(min-width: 961px)", function () {
      var hg = $(".hg"), track = hg && $(".hg-track", hg), bar = hg && $(".hg-bar i", hg);
      if (!hg) return;
      var dist = function () { return Math.max(0, track.scrollWidth - window.innerWidth); };
      G.to(track, {
        x: function () { return -dist(); }, ease: "none",
        scrollTrigger: { trigger: hg, start: "top top", end: function () { return "+=" + dist(); }, pin: true, scrub: .8, invalidateOnRefresh: true,
          onUpdate: function (s) { if (bar) bar.style.transform = "scaleX(" + s.progress + ")"; } }
      });
    });

    window.addEventListener("load", function () { ST.refresh(); });
    // safety net: anything an animation left hidden becomes visible if its trigger is already above the viewport
    setTimeout(function () {
      $$("[data-rv]").forEach(function (el) { if (el.getBoundingClientRect().top < window.innerHeight && getComputedStyle(el).opacity === "0") G.to(el, { autoAlpha: 1, y: 0, duration: .6 }); });
    }, 3500);
  }

  /* ---------- videos: play only when on screen ---------- */
  var vids = $$("video[data-auto]");
  if (vids.length) {
    var vio = "IntersectionObserver" in window ? new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) {
          if (v.dataset.src && !v.getAttribute("src")) v.src = v.dataset.src;
          var p = v.play(); if (p && p.catch) p.catch(function () {});
        } else if (!v.paused) v.pause();
      });
    }, { rootMargin: "300px 0px" }) : null;
    vids.forEach(function (v) {
      v.muted = true;
      if (vio) vio.observe(v); else { if (v.dataset.src) v.src = v.dataset.src; }
    });
  }

  /* ---------- price hover image ---------- */
  var pf = $(".pfloat");
  if (pf && fine) {
    var tx = 0, ty = 0, cx = 0, cy = 0, run = false;
    var loop = function () { cx += (tx - cx) * .15; cy += (ty - cy) * .15; pf.style.left = cx + "px"; pf.style.top = cy + "px"; if (run) requestAnimationFrame(loop); };
    $$(".price[data-img]").forEach(function (row) {
      row.addEventListener("mouseenter", function (e) {
        cx = tx = e.clientX + 170; cy = ty = e.clientY;
        var k = row.getAttribute("data-img");
        $$("img", pf).forEach(function (im) { im.classList.toggle("on", im.getAttribute("data-k") === k); });
        pf.classList.add("on"); if (!run) { run = true; loop(); }
      });
      row.addEventListener("mousemove", function (e) { tx = e.clientX + 170; ty = e.clientY; });
      row.addEventListener("mouseleave", function () { pf.classList.remove("on"); run = false; });
    });
  }

  /* ---------- reviews carousel: tap to pause on touch ---------- */
  $$(".rev-row").forEach(function (r) {
    r.addEventListener("touchstart", function () { r.classList.add("paused"); }, { passive: true });
    r.addEventListener("touchend", function () { setTimeout(function () { r.classList.remove("paused"); }, 2500); });
  });

  /* ---------- opening hours ---------- */
  var zNow = function () {
    try {
      var parts = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Zurich", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date());
      var o = {}; parts.forEach(function (p) { o[p.type] = p.value; });
      return { day: { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 }[o.weekday], min: +o.hour * 60 + +o.minute };
    } catch (e) { var n = new Date(); return { day: n.getDay(), min: n.getHours() * 60 + n.getMinutes() }; }
  };
  var now = zNow();
  var toM = function (s) { var a = s.split(":"); return +a[0] * 60 + +a[1]; };
  var names = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
  $$("[data-hours]").forEach(function (el) {
    var h = JSON.parse(el.getAttribute("data-hours")), t = h[now.day];
    var open = !!(t && now.min >= toM(t[0]) && now.min < toM(t[1])), txt;
    if (open) txt = "Ouvert · jusqu’à " + t[1];
    else if (t && now.min < toM(t[0])) txt = "Fermé · ouvre à " + t[0];
    else { var k = 1, nx; while (k < 8 && !(nx = h[(now.day + k) % 7])) k++; txt = "Fermé · ouvre " + (k === 1 ? "demain" : names[(now.day + k) % 7]) + " à " + nx[0]; }
    $$("[data-status]", el).forEach(function (s) { s.textContent = txt; s.classList.toggle("on", open); });
    var row = $('tr[data-day="' + now.day + '"]', el); if (row) row.classList.add("today");
  });

  /* ---------- filters ---------- */
  $$("[data-filter]").forEach(function (grp) {
    var items = $$(grp.getAttribute("data-filter"));
    $$("button", grp).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("button", grp).forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        var f = b.getAttribute("data-f");
        items.forEach(function (it) { it.hidden = !(f === "all" || (" " + it.getAttribute("data-tags") + " ").indexOf(" " + f + " ") > -1); });
        if (motion) ST.refresh();
      });
    });
  });

  /* ---------- lightbox ---------- */
  var lb = $(".lb");
  if (lb) {
    var lbImg = $(".lb-stage img", lb), lbCap = $(".lb-cap", lb), lbN = $(".lb-count", lb), list = [], li = 0, last;
    var vis = function () { return $$(".gi[data-full]").filter(function (x) { return !x.hidden; }); };
    var render = function () {
      var it = list[li], src = it.getAttribute("data-full"), im = new Image();
      lbImg.classList.remove("ready");
      im.onload = function () { lbImg.src = src; lbImg.alt = it.getAttribute("data-cap") || ""; requestAnimationFrame(function () { lbImg.classList.add("ready"); }); };
      im.src = src;
      lbCap.textContent = it.getAttribute("data-cap") || "";
      lbN.textContent = (li + 1) + " / " + list.length;
    };
    var open = function (it) { list = vis(); li = list.indexOf(it); render(); lb.classList.add("on"); lb.setAttribute("aria-hidden", "false"); last = d.activeElement; $(".lb-x", lb).focus(); if (lenis) lenis.stop(); body.style.overflow = "hidden"; };
    var close = function () { lb.classList.remove("on"); lb.setAttribute("aria-hidden", "true"); body.style.overflow = ""; if (lenis) lenis.start(); if (last) last.focus(); };
    var go = function (k) { li = (li + k + list.length) % list.length; render(); };
    $$(".gi[data-full]").forEach(function (it) {
      it.tabIndex = 0; it.setAttribute("role", "button");
      it.addEventListener("click", function () { open(it); });
      it.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(it); } });
    });
    $(".lb-x", lb).addEventListener("click", close);
    $(".lb-prev", lb).addEventListener("click", function () { go(-1); });
    $(".lb-next", lb).addEventListener("click", function () { go(1); });
    d.addEventListener("keydown", function (e) { if (!lb.classList.contains("on")) return; if (e.key === "Escape") close(); if (e.key === "ArrowLeft") go(-1); if (e.key === "ArrowRight") go(1); });
    var sx = null;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) { if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1); sx = null; });
  }

  /* ---------- lazy maps ---------- */
  $$(".map[data-map]").forEach(function (m) {
    var b = $("button", m);
    if (b) b.addEventListener("click", function () {
      var f = d.createElement("iframe");
      f.src = m.getAttribute("data-map"); f.title = m.getAttribute("data-title") || "Carte"; f.loading = "lazy";
      m.innerHTML = ""; m.appendChild(f);
    });
  });

  /* ---------- WhatsApp widget ---------- */
  var wa = $(".waw");
  if (wa) {
    var wb = $(".waw-btn", wa);
    var setWa = function (o) { wa.classList.toggle("open", o); wa.classList.remove("tease"); wb.setAttribute("aria-expanded", String(o)); };
    wb.addEventListener("click", function (e) { e.stopPropagation(); setWa(!wa.classList.contains("open")); });
    d.addEventListener("click", function (e) { if (wa.classList.contains("open") && !wa.contains(e.target)) setWa(false); });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape") setWa(false); });
    var tm = $(".waw-msg time", wa), nd = new Date();
    if (tm) tm.textContent = String(nd.getHours()).padStart(2, "0") + ":" + String(nd.getMinutes()).padStart(2, "0");
    if (!store.get("vxv-wa")) setTimeout(function () {
      if (wa.classList.contains("open")) return;
      wa.classList.add("tease"); store.set("vxv-wa", "1");
      setTimeout(function () { wa.classList.remove("tease"); }, 6000);
    }, 8000);
  }

  /* ---------- cursor + magnetic buttons ---------- */
  if (fine && motion) {
    var cur = d.createElement("div"); cur.className = "cur"; cur.innerHTML = "<span></span>"; body.appendChild(cur);
    var qx = G.quickTo(cur, "x", { duration: .45, ease: "power3" }), qy = G.quickTo(cur, "y", { duration: .45, ease: "power3" });
    window.addEventListener("mousemove", function (e) { qx(e.clientX); qy(e.clientY); cur.classList.add("on"); }, { passive: true });
    d.addEventListener("mouseleave", function () { cur.classList.remove("on"); });
    d.addEventListener("mouseover", function (e) {
      var t = e.target.closest ? e.target.closest("[data-cursor]") : null;
      cur.classList.toggle("big", !!t);
      if (t) cur.firstChild.textContent = t.getAttribute("data-cursor");
      var hot = e.target.closest && e.target.closest("a,button,input,textarea");
      cur.style.opacity = hot && !t ? ".25" : "";
    });
    $$(".btn,.soc,.burger,.waw-btn").forEach(function (b) {
      var bx = G.quickTo(b, "x", { duration: .5, ease: "power3" }), by = G.quickTo(b, "y", { duration: .5, ease: "power3" });
      b.addEventListener("mousemove", function (e) { var r = b.getBoundingClientRect(); bx((e.clientX - r.left - r.width / 2) * .22); by((e.clientY - r.top - r.height / 2) * .3); });
      b.addEventListener("mouseleave", function () { bx(0); by(0); });
    });
  }

  var y = $("[data-year]"); if (y) y.textContent = new Date().getFullYear();
})();
