/* vXv Barber's — v3 interactions (GSAP + ScrollTrigger + Lenis) */
(function () {
  "use strict";
  var d = document, html = d.documentElement, body = d.body;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var G = window.gsap, ST = window.ScrollTrigger;
  var motion = !!(G && ST) && !reduce;
  var store = {
    get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  };
  if (motion) G.registerPlugin(ST);

  /* ---------- smooth scroll (mouse/trackpad only) ---------- */
  var lenis = null;
  if (motion && fine && window.Lenis) {
    lenis = new window.Lenis({ duration: 1.1, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      virtualScroll: function (v) { var t = v.event && v.event.target; return !(Math.abs(v.deltaX) > Math.abs(v.deltaY) && t && t.closest && t.closest(".reels")); } });
    lenis.on("scroll", ST.update);
    G.ticker.add(function (t) { lenis.raf(t * 1000); });
    G.ticker.lagSmoothing(0);
    $$('a[href^="#"]').forEach(function (a) {
      a.addEventListener("click", function (e) { var t = $(a.getAttribute("href")); if (t) { e.preventDefault(); lenis.scrollTo(t, { offset: -(($(".hdr") || {}).offsetHeight || 90) + 1 }); } });
    });
  }
  var lockScroll = function (on) { if (lenis) on ? lenis.stop() : lenis.start(); body.style.overflow = on ? "hidden" : ""; body.classList.toggle("modal-open", on); };
  var setInert = function (ov, on) { $$("body > *").forEach(function (el) { if (el !== ov && el.tagName !== "SCRIPT") el.inert = on; }); };

  /* ---------- header tools: scissors snip + clipper shaves as you scroll ---------- */
  var scA = $(".scis #sc-a"), scB = $(".scis #sc-b");
  var shave = $(".shave"), clip = $(".clipper"), hair = $(".hair"), stub = $(".stubble");
  var lastY = window.scrollY, ang = 4, angT = 4, buzzT = 0, crumbT = 0, idleT;
  var setScis = function (a) {
    if (!scA) return;
    scA.style.transform = "rotate(" + (-a).toFixed(2) + "deg)";
    scB.style.transform = "rotate(" + a.toFixed(2) + "deg)";
  };
  var edgeFrac = 0.93; // teeth sit near the right end of the clipper box
  var layoutTools = function () {
    var y = window.scrollY || html.scrollTop;
    var max = Math.max(1, html.scrollHeight - window.innerHeight);
    var p = Math.min(1, Math.max(0, y / max));
    if (clip && hair) {
      var L = hair.offsetLeft, W = hair.offsetWidth, cw = clip.offsetWidth;
      var x = L + p * (W - cw);
      clip.style.transform = "translate3d(" + x.toFixed(1) + "px,0,0)";
      var cut = Math.max(0, Math.min(W, x + cw * edgeFrac - L));
      hair.style.clipPath = "inset(0 0 0 " + cut.toFixed(1) + "px)";
      if (stub) stub.style.clipPath = "inset(0 " + (W - cut).toFixed(1) + "px 0 0)";
      return { x: x, cw: cw, cut: cut + L };
    }
    return null;
  };
  var spawnCrumb = function (geo) {
    if (!shave || !geo) return;
    var r = clip.parentNode.getBoundingClientRect();
    for (var i = 0; i < 2; i++) {
      var c = d.createElement("i");
      c.className = "crumb-hair";
      c.style.left = (r.left + geo.cut - 2 + Math.random() * 6) + "px";
      c.style.top = (r.bottom - 8) + "px";
      c.style.setProperty("--dx", (Math.random() * 18 - 9).toFixed(1) + "px");
      c.style.setProperty("--r", (Math.random() * 260 - 130).toFixed(0) + "deg");
      body.appendChild(c);
      setTimeout(function (n) { n.remove(); }.bind(null, c), 820);
    }
  };
  var lastGeo = null, needLayout = true;
  window.addEventListener("resize", function () { needLayout = true; });
  var toolsFrame = function () {
    var y = window.scrollY || html.scrollTop, dy = y - lastY;
    lastY = y;
    if (!dy && !needLayout && Math.abs(angT - ang) < 0.05) return;
    var geo = (dy || needLayout) ? (lastGeo = layoutTools()) : lastGeo;
    needLayout = false;
    if (Math.abs(dy) > 0.4) {
      angT = 3 + 21 * Math.abs(Math.sin(y / 55));
      if (clip) clip.classList.add("buzz");
      clearTimeout(idleT);
      idleT = setTimeout(function () { angT = 4; if (clip) clip.classList.remove("buzz"); }, 160);
      var now = performance.now();
      if (dy > 0 && now - crumbT > 55 && !reduce) { crumbT = now; spawnCrumb(geo); }
    }
    ang += (angT - ang) * 0.25;
    setScis(ang);
  };
  if (scA || clip) {
    if (G) G.ticker.add(toolsFrame); else (function loop() { toolsFrame(); requestAnimationFrame(loop); })();
    window.addEventListener("resize", layoutTools);
    var sc = $(".scis");
    if (sc) sc.addEventListener("mouseenter", function () {
      if (!G) return;
      var o = { a: ang };
      G.timeline().to(o, { a: 26, duration: .16, ease: "power2.out", onUpdate: function () { ang = angT = o.a; } })
        .to(o, { a: 2, duration: .14, ease: "power3.in", onUpdate: function () { ang = angT = o.a; } })
        .to(o, { a: 24, duration: .16, ease: "power2.out", onUpdate: function () { ang = angT = o.a; } })
        .to(o, { a: 4, duration: .2, ease: "power3.in", onUpdate: function () { ang = angT = o.a; } });
    });
  }

  /* ---------- mobile menu ---------- */
  var burger = $(".burger");
  var setMenu = function (open) {
    body.classList.toggle("menu-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
    if (lenis) open ? lenis.stop() : lenis.start();
  };
  if (burger) burger.addEventListener("click", function () { setMenu(!body.classList.contains("menu-open")); });
  d.addEventListener("keydown", function (e) { if (e.key === "Escape" && body.classList.contains("menu-open")) setMenu(false); });
  window.addEventListener("pageshow", function (e) {
    if (!e.persisted || !body.classList.contains("menu-open")) return;
    var mn = $(".mnav"); if (mn) mn.style.transition = "none";
    setMenu(false);
    if (mn) { void mn.offsetWidth; mn.style.transition = ""; }
  });

  /* ---------- split headings into words for the reveal ---------- */
  var splitWords = function (el) {
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var parts = n.textContent.split(/([ \t\n\r\f]+)/), frag = d.createDocumentFragment();
          parts.forEach(function (t) {
            if (!t) return;
            if (/^[ \t\n\r\f]+$/.test(t)) { frag.appendChild(d.createTextNode(t)); return; }
            var w = d.createElement("span"); w.className = "w";
            var i = d.createElement("span"); i.textContent = t; w.appendChild(i); frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1 && !n.classList.contains("w")) walk(n);
      });
    };
    walk(el);
    return $$(".w>span", el);
  };

  /* a script that arrives after the CSS failsafe (2.5 s) has already shown the page must not hide what is on screen again */
  var late = performance.now() > 2300;
  var onScreen = function (el) { var r = el.getBoundingClientRect(); return r.bottom > 0 && r.top < window.innerHeight; };
  var fresh = function (el) { return !(late && onScreen(el)); };

  /* ---------- hero intro ---------- */
  if (motion && !late) {
    var hero = $(".hero, .phead");
    if (hero) {
      var h1 = $("h1", hero), words = h1 ? splitWords(h1) : [];
      var tl = G.timeline({ defaults: { ease: "power4.out" }, delay: .1 });
      tl.from(words, { yPercent: 110, duration: 1.1, stagger: .05 })
        .from($$("[data-in]", hero), { y: 22, autoAlpha: 0, duration: .9, stagger: .07 }, "-=.8");
      var cols = $$(".wall .wcol");
      if (cols.length) tl.from(cols, { yPercent: 14, autoAlpha: 0, duration: 1.3, stagger: .12, ease: "power3.out" }, .15);
    }
  }

  /* ---------- scroll motion ---------- */
  if (motion) {
    var rvs = $$("[data-rv]").filter(fresh);
    G.set(rvs, { y: 34, autoAlpha: 0 });
    if (rvs.length) ST.batch(rvs, {
      start: "top 92%", once: true,
      onEnter: function (els) { G.to(els, { y: 0, autoAlpha: 1, duration: 1, stagger: .07, ease: "power3.out", overwrite: true }); }
    });
    $$("[data-split]").filter(fresh).forEach(function (h) {
      var ws = splitWords(h);
      G.from(ws, { yPercent: 110, duration: 1, stagger: .04, ease: "power4.out", scrollTrigger: { trigger: h, start: "top 90%", once: true } });
    });
    $$(".ph[data-reveal]").filter(fresh).forEach(function (ph) {
      var veil = d.createElement("i");
      veil.style.cssText = "position:absolute;inset:0;z-index:3;background:#ebe8e1;transform-origin:50% 0;pointer-events:none";
      ph.appendChild(veil);
      var media = $("img,video", ph);
      var t = G.timeline({ scrollTrigger: { trigger: ph, start: "top 90%", once: true } });
      t.to(veil, { scaleY: 0, duration: 1.1, ease: "power4.inOut" });
      if (media) { media.style.transition = "none"; t.fromTo(media, { scale: 1.2 }, { scale: 1, duration: 1.7, ease: "power3.out", clearProps: "transform", onComplete: function () { media.style.transition = ""; } }, 0); }
    });
    $$("[data-par]").forEach(function (el) {
      var amt = parseFloat(el.getAttribute("data-par")) || 8;
      G.fromTo(el, { yPercent: -amt, scale: 1.16 }, { yPercent: amt, scale: 1.16, ease: "none", scrollTrigger: { trigger: el.parentNode, start: "top bottom", end: "bottom top", scrub: true } });
    });
    $$("[data-count]").filter(fresh).forEach(function (el) {
      var raw = el.getAttribute("data-count"), to = parseFloat(raw), dec = (raw.split(".")[1] || "").length,
          suf = el.getAttribute("data-suffix") || "", o = { v: 0 };
      G.to(o, { v: to, duration: 2, ease: "power3.out", scrollTrigger: { trigger: el, start: "top 94%", once: true },
        onStart: function () { el.style.width = el.getBoundingClientRect().width + "px"; el.style.whiteSpace = "nowrap"; },
        onUpdate: function () { el.textContent = o.v.toFixed(dec).replace(".", ",") + suf; },
        onComplete: function () { el.style.width = ""; el.style.whiteSpace = ""; } });
    });
    var fw = $$(".ftr-word span");
    if (fw.length && fresh(fw[0])) G.from(fw, { yPercent: 105, duration: 1.1, stagger: .05, ease: "power4.out", scrollTrigger: { trigger: ".ftr-word", start: "top 96%", once: true } });
    var trip = $(".trip");
    if (trip && window.innerWidth > 980 && fresh(trip)) G.from($$(".panel", trip), { y: 60, autoAlpha: 0, duration: 1.2, stagger: .12, ease: "power3.out", scrollTrigger: { trigger: trip, start: "top 85%", once: true } });
    window.addEventListener("load", function () { ST.refresh(); });
    setTimeout(function () {
      $$("[data-rv]").forEach(function (el) { var r = el.getBoundingClientRect(); if (r.top < window.innerHeight && r.bottom > 0 && getComputedStyle(el).opacity === "0") G.to(el, { autoAlpha: 1, y: 0, duration: .6 }); });
    }, 3000);
  }

  html.classList.remove("pre-intro");

  /* ---------- videos: lazy-load and play only on screen ---------- */
  var vids = $$("video[data-auto]");
  if (vids.length) {
    var vio = "IntersectionObserver" in window ? new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting && !reduce) {
          if (v.dataset.src && !v.getAttribute("src")) { v.src = v.dataset.src; }
          var p = v.play(); if (p && p.catch) p.catch(function () {});
        } else if (!v.paused) v.pause();
      });
    }, { rootMargin: "120px 120px" }) : null;
    vids.forEach(function (v) {
      v.muted = true; v.setAttribute("muted", "");
      if (vio) vio.observe(v); else if (v.dataset.src && !reduce) { v.src = v.dataset.src; }
    });
  }

  var lp = $$("video[data-psrc]");
  if (lp.length) {
    var pio = "IntersectionObserver" in window ? new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.poster = en.target.dataset.psrc; en.target.removeAttribute("data-psrc"); pio.unobserve(en.target); } });
    }, { rootMargin: "600px 0px" }) : null;
    lp.forEach(function (v) { if (pio) pio.observe(v); else v.poster = v.dataset.psrc; });
  }

  /* ---------- video modal (full versions with sound) ---------- */
  var vm = $(".vmodal");
  if (vm) {
    var vEl = $("video", vm), vT = $(".vm-top .t", vm), vMeta = $(".vm-meta", vm), vN = $(".vm-count", vm);
    var seen = {}, list = [];
    $$(".reels [data-video], .masonry [data-video]").concat($$("[data-video]")).forEach(function (b) { var s = b.getAttribute("data-video"); if (!seen[s]) { seen[s] = 1; list.push({ src: s, t: b.getAttribute("data-title"), m: b.getAttribute("data-meta"), p: b.getAttribute("data-poster") }); } });
    var vi = 0, lastF;
    var show = function () {
      var it = list[vi];
      vEl.src = it.src; vEl.poster = it.p || ""; vT.textContent = it.t || ""; vMeta.textContent = it.m || "";
      vN.textContent = (vi + 1) + " / " + list.length;
      var p = vEl.play(); if (p && p.catch) p.catch(function () {});
    };
    var openV = function (src) {
      vi = Math.max(0, list.findIndex(function (x) { return x.src === src; }));
      lastF = d.activeElement; vm.classList.add("on"); vm.setAttribute("aria-hidden", "false"); lockScroll(true); show();
      setInert(vm, true); $(".vm-x", vm).focus();
    };
    var closeV = function () { vm.classList.remove("on"); vm.setAttribute("aria-hidden", "true"); vEl.pause(); vEl.removeAttribute("src"); vEl.load(); lockScroll(false); setInert(vm, false); if (lastF) lastF.focus(); };
    $$("[data-video]").forEach(function (b) { b.addEventListener("click", function (e) { e.preventDefault(); openV(b.getAttribute("data-video")); }); });
    $(".vm-x", vm).addEventListener("click", closeV);
    $(".vm-prev", vm).addEventListener("click", function () { vi = (vi - 1 + list.length) % list.length; show(); });
    $(".vm-next", vm).addEventListener("click", function () { vi = (vi + 1) % list.length; show(); });
    vm.addEventListener("click", function (e) { if (e.target === vm || e.target.classList.contains("vm-stage")) closeV(); });
    /* Tab cycles close → video → prev → next: once focus enters the browser's own video controls the page stops getting keys, Escape included */
    var stops = [$(".vm-x", vm), vEl, $(".vm-prev", vm), $(".vm-next", vm)];
    vm.addEventListener("keydown", function (e) {
      if (e.key !== "Tab") return;
      e.preventDefault();
      var i = stops.indexOf(d.activeElement);
      stops[i < 0 ? 0 : (i + (e.shiftKey ? -1 : 1) + stops.length) % stops.length].focus();
    });
    /* a mouse click on those controls parks focus inside them too: hand it back to the video as soon as the pointer moves on (controls send the page no events of their own) */
    vm.addEventListener("pointermove", function () { if (vm.classList.contains("on") && d.activeElement === vEl) vEl.focus({ preventScroll: true }); });
    d.addEventListener("keydown", function (e) {
      if (!vm.classList.contains("on")) return;
      if (e.key === "Escape") closeV();
      if (e.key === "ArrowRight") $(".vm-next", vm).click();
      if (e.key === "ArrowLeft") $(".vm-prev", vm).click();
    });
  }

  /* ---------- reels carousel: arrows + drag ---------- */
  $$(".reels").forEach(function (rl) {
    var wrap = rl.closest("section");
    var step = function () { var c = $(".reel", rl); return c ? c.getBoundingClientRect().width + 14 : 300; };
    var navs = $$("[data-reels]", wrap);
    navs.forEach(function (b) { b.addEventListener("click", function () { rl.scrollBy({ left: (b.getAttribute("data-reels") === "next" ? 1 : -1) * step() * 2, behavior: "smooth" }); }); });
    var upd = function () {
      var mx = rl.scrollWidth - rl.clientWidth - 2;
      navs.forEach(function (b) { b.setAttribute("aria-disabled", String(b.getAttribute("data-reels") === "next" ? rl.scrollLeft >= mx : rl.scrollLeft <= 2)); });
    };
    rl.addEventListener("scroll", upd, { passive: true }); window.addEventListener("resize", upd); upd();
    if (!fine) return;
    var down = false, sx = 0, sl = 0, moved = false;
    rl.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") return; down = true; moved = false; sx = e.clientX; sl = rl.scrollLeft; });
    window.addEventListener("pointermove", function (e) { if (!down) return; var dx = e.clientX - sx; if (Math.abs(dx) > 5) { moved = true; rl.classList.add("drag"); } rl.scrollLeft = sl - dx; });
    window.addEventListener("pointerup", function () { if (!down) return; down = false; setTimeout(function () { rl.classList.remove("drag"); }, 0); });
    rl.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  });

  /* ---------- marquees: tap to pause on touch ---------- */
  $$(".mrow,.rev-row").forEach(function (r) {
    var tm;
    r.addEventListener("touchstart", function () { clearTimeout(tm); r.classList.add("paused"); }, { passive: true });
    var go = function () { clearTimeout(tm); tm = setTimeout(function () { r.classList.remove("paused"); }, 2200); };
    r.addEventListener("touchend", go); r.addEventListener("touchcancel", go);
  });

  /* ---------- price hover image ---------- */
  var pf = $(".pfloat");
  if (pf && fine) {
    var pfLoad = function () { $$("img[data-src]", pf).forEach(function (i) { i.src = i.dataset.src; i.removeAttribute("data-src"); }); };
    var plist = $(".prices");
    if (plist && "IntersectionObserver" in window) { var pfo = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { pfLoad(); pfo.disconnect(); } }, { rootMargin: "0px 0px 600px 0px" }); pfo.observe(plist); } else pfLoad();
    var tx = 0, ty = 0, cx = 0, cy = 0, run = false;
    var px = function (x) { return x > window.innerWidth * .55 ? x - 190 : x + 160; };
    var loop = function () { cx += (tx - cx) * .15; cy += (ty - cy) * .15; pf.style.left = cx + "px"; pf.style.top = cy + "px"; if (run) requestAnimationFrame(loop); };
    $$(".price[data-img]").forEach(function (row) {
      row.addEventListener("mouseenter", function (e) {
        cx = tx = px(e.clientX); cy = ty = e.clientY;
        var k = row.getAttribute("data-img");
        $$("img", pf).forEach(function (im) { im.classList.toggle("on", im.getAttribute("data-k") === k); });
        pf.classList.add("on"); if (!run) { run = true; loop(); }
      });
      row.addEventListener("mousemove", function (e) { tx = px(e.clientX); ty = e.clientY; });
      row.addEventListener("mouseleave", function () { pf.classList.remove("on"); run = false; });
    });
  }

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
  var fh = function (s) { var a = s.split(":"); return (+a[0]) + "h" + (a[1] === "00" ? "" : a[1]); };
  $$("[data-hours]").forEach(function (el) {
    var h = JSON.parse(el.getAttribute("data-hours")), t = h[now.day];
    var open = !!(t && now.min >= toM(t[0]) && now.min < toM(t[1])), txt;
    if (open) txt = "Ouvert · jusqu’à " + fh(t[1]);
    else if (t && now.min < toM(t[0])) txt = "Fermé · ouvre\u00a0à\u00a0" + fh(t[0]);
    else { var k = 1, nx; while (k < 8 && !(nx = h[(now.day + k) % 7])) k++; txt = "Fermé · ouvre " + (k === 1 ? "demain" : names[(now.day + k) % 7]) + "\u00a0à\u00a0" + fh(nx[0]); }
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
        var grid = items[0] && items[0].parentNode;
        if (grid) grid.setAttribute("data-show", f);
        items.forEach(function (it) { if (!it.hidden && G && getComputedStyle(it).opacity === "0") G.to(it, { autoAlpha: 1, y: 0, duration: .5 }); });
        if (motion) ST.refresh();
        if (grid) {
          var bar = grp.closest(".gbar");
          var off = $(".hdr").offsetHeight + (bar ? bar.offsetHeight : 0) + 12;
          var top = Math.max(0, Math.round(grid.getBoundingClientRect().top + window.scrollY - off));
          if (window.scrollY > top + 4) {
            if (lenis) { lenis.resize(); lenis.scrollTo(window.scrollY, { immediate: true, force: true }); lenis.scrollTo(top, { duration: .8, force: true }); }
            else window.scrollTo({ top: top, behavior: reduce ? "auto" : "smooth" });
          }
        }
      });
    });
  });

  /* ---------- photo lightbox ---------- */
  var lb = $(".lb");
  if (lb) {
    body.appendChild(lb);
    var lbImg = $(".lb-stage img", lb), lbCap = $(".lb-cap", lb), lbN = $(".lb-count", lb), pl = [], li = 0, lastL, lbTok = 0;
    var vis = function () { return $$(".gi[data-full]").filter(function (x) { return !x.hidden; }); };
    var render = function () {
      var it = pl[li], src = it.getAttribute("data-full"), cap = it.getAttribute("data-cap") || "", im = new Image(), my = ++lbTok;
      lbImg.classList.remove("ready");
      im.onload = function () {
        if (my !== lbTok) return;
        lbImg.src = src; lbImg.alt = cap;
        requestAnimationFrame(function () { if (my === lbTok) lbImg.classList.add("ready"); });
      };
      im.src = src;
      lbCap.textContent = cap;
      lbN.textContent = (li + 1) + " / " + pl.length;
      if (pl.length > 1) [1, -1].forEach(function (k) { new Image().src = pl[(li + k + pl.length) % pl.length].getAttribute("data-full"); });
    };
    var openL = function (it) { pl = vis(); li = pl.indexOf(it); render(); lb.classList.add("on"); lb.setAttribute("aria-hidden", "false"); lastL = d.activeElement; lockScroll(true); setInert(lb, true); $(".lb-x", lb).focus(); };
    var closeL = function () { lb.classList.remove("on"); lb.setAttribute("aria-hidden", "true"); lockScroll(false); setInert(lb, false); if (lastL) lastL.focus(); };
    var go = function (k) { li = (li + k + pl.length) % pl.length; render(); };
    $$(".gi[data-full]").forEach(function (it) { it.addEventListener("click", function () { openL(it); }); });
    $(".lb-x", lb).addEventListener("click", closeL);
    $(".lb-prev", lb).addEventListener("click", function () { go(-1); });
    $(".lb-next", lb).addEventListener("click", function () { go(1); });
    d.addEventListener("keydown", function (e) { if (!lb.classList.contains("on")) return; if (e.key === "Escape") closeL(); if (e.key === "ArrowLeft") go(-1); if (e.key === "ArrowRight") go(1); });
    var sx2 = null;
    lb.addEventListener("touchstart", function (e) { sx2 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) { if (sx2 === null) return; var dx = e.changedTouches[0].clientX - sx2; if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1); sx2 = null; });
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
    window.addEventListener("pageshow", function (e) { if (e.persisted) setWa(false); });
    wb.addEventListener("click", function (e) { e.stopPropagation(); setWa(!wa.classList.contains("open")); });
    d.addEventListener("click", function (e) { if (wa.classList.contains("open") && !wa.contains(e.target)) setWa(false); });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape") setWa(false); });
    var tm = $(".waw-msg time", wa), nd = new Date();
    if (tm) tm.textContent = String(nd.getHours()).padStart(2, "0") + ":" + String(nd.getMinutes()).padStart(2, "0");
    if (!store.get("vxv-wa")) setTimeout(function () {
      if (wa.classList.contains("open") || body.classList.contains("modal-open")) return;
      wa.classList.add("tease"); store.set("vxv-wa", "1");
      setTimeout(function () { wa.classList.remove("tease"); }, 6000);
    }, 9000);
  }

  /* ---------- magnetic buttons ---------- */
  if (fine && motion) {
    $$(".btn,.soc,.waw-btn,.reel-nav button").forEach(function (b) {
      var bx = G.quickTo(b, "x", { duration: .5, ease: "power3" }), by = G.quickTo(b, "y", { duration: .5, ease: "power3" });
      b.addEventListener("mousemove", function (e) { if (b.getAttribute("aria-disabled") === "true") return; var r = b.getBoundingClientRect(); bx((e.clientX - r.left - r.width / 2) * .2); by((e.clientY - r.top - r.height / 2) * .28); });
      b.addEventListener("mouseleave", function () { bx(0); by(0); });
      if (b.classList.contains("waw-btn")) {
        b.addEventListener("mouseenter", function () { G.to(b, { scale: 1.07, duration: .4, ease: "power3", overwrite: "auto" }); });
        b.addEventListener("mouseleave", function () { G.to(b, { scale: 1, duration: .4, ease: "power3", overwrite: "auto" }); });
      }
    });
  }

  var yr = $("[data-year]"); if (yr) yr.textContent = new Date().getFullYear();
})();
