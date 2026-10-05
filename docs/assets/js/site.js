/* vXv Barber's — interactions */
(function () {
  "use strict";
  var d = document, html = d.documentElement, body = d.body;
  var shot = /[?&]shot\b/.test(location.search);
  if (shot) {
    html.classList.add("shot");
    var sy = (location.search.match(/[?&]y=(\d+)/) || [])[1];
    if (sy) d.addEventListener("DOMContentLoaded", function () { d.querySelector("main").style.transform = "translateY(-" + sy + "px)"; });
  }
  var reduce = shot || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var desk = function () { return window.innerWidth > 900; };
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- loader (home, once per session) ---------- */
  var loader = $(".loader");
  var heroGo = function () { $$(".hero [data-rv], .hero [data-lines], .hero .mask").forEach(function (el) { el.classList.add("is-in"); }); };
  if (loader) {
    if (reduce || store.get("vxv-intro")) {
      loader.remove(); loader = null;
    } else {
      store.set("vxv-intro", "1");
      var bar = $(".loader-bar", loader), pct = $(".loader-pct", loader), p = 0;
      var tick = setInterval(function () {
        p = Math.min(100, p + Math.random() * 18 + 6);
        bar.style.transform = "scaleX(" + p / 100 + ")";
        pct.textContent = String(Math.round(p)).padStart(3, "0");
        if (p >= 100) {
          clearInterval(tick);
          setTimeout(function () {
            loader.classList.add("done");
            setTimeout(heroGo, 380);
            setTimeout(function () { loader && loader.remove(); }, 1300);
          }, 260);
        }
      }, 110);
    }
  }

  /* ---------- page curtain ---------- */
  if (!reduce) {
    if (store.get("vxv-nav")) {
      body.classList.add("entering");
      requestAnimationFrame(function () { requestAnimationFrame(function () {
        body.classList.remove("entering"); body.classList.add("entered");
      }); });
    }
    d.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a");
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === "_blank" || a.hasAttribute("download")) return;
      var url = new URL(a.href, location.href);
      if (url.origin !== location.origin || url.protocol.indexOf("http") !== 0) return;
      if (url.pathname === location.pathname && url.hash) return;
      e.preventDefault();
      store.set("vxv-nav", "1");
      body.classList.remove("entered", "menu-open");
      body.classList.add("leaving");
      setTimeout(function () { location.href = url.href; }, 520);
    });
    window.addEventListener("pageshow", function (e) { if (e.persisted) body.classList.remove("leaving"); });
  }

  /* ---------- header ---------- */
  var hdr = $(".hdr"), lastY = window.scrollY;
  var onHdr = function () {
    var y = window.scrollY;
    hdr.classList.toggle("is-solid", y > 40);
    if (!body.classList.contains("menu-open")) hdr.classList.toggle("is-hidden", y > 400 && y > lastY + 2);
    if (y < lastY - 2) hdr.classList.remove("is-hidden");
    lastY = y;
  };

  /* ---------- mobile menu ---------- */
  var burger = $(".burger");
  if (burger) burger.addEventListener("click", function () {
    var open = body.classList.toggle("menu-open");
    burger.setAttribute("aria-expanded", open);
    burger.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
    hdr.classList.remove("is-hidden");
  });
  d.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && body.classList.contains("menu-open")) burger.click();
  });

  /* ---------- reveal on scroll ---------- */
  var fired = false;
  var revealAll = function () { $$("[data-rv],[data-lines],.mask,.rule").forEach(function (el) { el.classList.add("is-in"); }); };
  var heroHeld = !!loader;
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      fired = true;
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        if (heroHeld && en.target.closest(".hero")) return;
        en.target.classList.add("is-in");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    $$("[data-rv],[data-lines],.mask,.rule").forEach(function (el) { io.observe(el); });
    if (heroHeld) setTimeout(function () { heroHeld = false; }, 2400);
    // hidden tabs / headless renders never fire IO — don't leave the page blank
    setTimeout(function () { if (!fired) revealAll(); }, 2600);
  } else {
    revealAll();
  }

  /* ---------- manifesto words ---------- */
  var mani = $(".manifesto-text");
  var words = [];
  if (mani) {
    var wrapWords = function (node) {
      $$("*", node).length;
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (t) {
            if (!t) return;
            if (/^\s+$/.test(t)) { frag.appendChild(d.createTextNode(t)); return; }
            var s = d.createElement("span"); s.className = "w"; s.textContent = t; frag.appendChild(s);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) wrapWords(n);
      });
    };
    wrapWords(mani);
    words = $$(".w", mani);
    if (reduce) words.forEach(function (w) { w.classList.add("on"); });
  }
  var onMani = function () {
    if (!words.length || reduce) return;
    var r = mani.getBoundingClientRect(), vh = window.innerHeight;
    var p = (vh * 0.85 - r.top) / (r.height + vh * 0.35);
    var n = Math.round(Math.max(0, Math.min(1, p)) * words.length);
    for (var i = 0; i < words.length; i++) words[i].classList.toggle("on", i < n);
  };

  /* ---------- counters ---------- */
  var counters = $$("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, to = parseFloat(el.getAttribute("data-count")), dec = (el.getAttribute("data-count").split(".")[1] || "").length;
        var t0 = performance.now(), dur = reduce ? 1 : 1800;
        var step = function (t) {
          var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 4);
          el.textContent = (to * e).toFixed(dec).replace(".", ",");
          if (k < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        cio.unobserve(el);
      });
    }, { threshold: 0.4 });
    counters.forEach(function (c) { cio.observe(c); });
  }

  /* ---------- horizontal gallery ---------- */
  var hg = $(".hgal"), track = hg && $(".hgal-track", hg), prog = hg && $(".hgal-progress i", hg);
  var hgDist = 0;
  var sizeHg = function () {
    if (!hg) return;
    hg.classList.toggle("hg-static", reduce && desk());
    if (!desk() || reduce) { hg.style.height = ""; track.style.transform = ""; return; }
    hgDist = Math.max(0, track.scrollWidth - window.innerWidth);
    hg.style.height = (window.innerHeight + hgDist) + "px";
  };
  var onHg = function () {
    if (!hg || !desk() || reduce) return;
    var r = hg.getBoundingClientRect();
    var p = Math.max(0, Math.min(1, -r.top / (hg.offsetHeight - window.innerHeight || 1)));
    track.style.transform = "translate3d(" + (-p * hgDist) + "px,0,0)";
    if (prog) prog.style.transform = "scaleX(" + p + ")";
  };

  /* ---------- parallax ---------- */
  var pars = $$("[data-par]");
  var onPar = function () {
    if (reduce) return;
    var vh = window.innerHeight;
    pars.forEach(function (el) {
      var r = el.parentNode.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) return;
      var k = parseFloat(el.getAttribute("data-par")) || 0.12;
      var c = (r.top + r.height / 2 - vh / 2);
      el.style.transform = "translate3d(0," + (c * -k).toFixed(1) + "px,0) scale(1.12)";
    });
  };

  /* ---------- scroll loop ---------- */
  var ticking = false;
  var onScroll = function () {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () { ticking = false; onHdr(); onMani(); onHg(); onPar(); });
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", function () { sizeHg(); onScroll(); });
  window.addEventListener("load", function () { sizeHg(); onScroll(); });
  sizeHg(); onScroll();

  /* ---------- videos: lazy + play only in view ---------- */
  var vids = $$("video[data-auto]");
  if (vids.length) {
    var vio = "IntersectionObserver" in window ? new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) {
          if (v.dataset.src && !v.src) { v.src = v.dataset.src; }
          var pr = v.play(); if (pr && pr.catch) pr.catch(function () {});
        } else if (!v.paused) v.pause();
      });
    }, { rootMargin: "200px 0px" }) : null;
    vids.forEach(function (v) {
      v.muted = true;
      if (vio) vio.observe(v); else { if (v.dataset.src) v.src = v.dataset.src; v.play && v.play(); }
    });
  }

  /* ---------- price hover image ---------- */
  var hov = $(".hover-img");
  if (hov && fine) {
    var hx = 0, hy = 0, cx = 0, cy = 0, hRun = false;
    var hLoop = function () {
      cx += (hx - cx) * 0.14; cy += (hy - cy) * 0.14;
      hov.style.left = cx + "px"; hov.style.top = cy + "px";
      if (hRun) requestAnimationFrame(hLoop);
    };
    $$(".price[data-img]").forEach(function (row) {
      row.addEventListener("mouseenter", function (e) {
        cx = hx = e.clientX; cy = hy = e.clientY;
        var key = row.getAttribute("data-img");
        $$("img", hov).forEach(function (im) { im.classList.toggle("on", im.getAttribute("data-k") === key); });
        hov.classList.add("on"); if (!hRun) { hRun = true; hLoop(); }
      });
      row.addEventListener("mousemove", function (e) { hx = e.clientX + 150; hy = e.clientY; });
      row.addEventListener("mouseleave", function () { hov.classList.remove("on"); hRun = false; });
    });
  }

  /* ---------- quotes carousel ---------- */
  var qs = $$(".quote"), dots = $$(".qdot"), qi = 0, qt;
  if (qs.length) {
    qs.forEach(function (q) {
      var bq = $("blockquote", q), i = 0;
      bq.innerHTML = bq.textContent.split(" ").map(function (w) { return '<span class="w2" style="--i:' + (i++) + '">' + w + "</span>"; }).join(" ");
    });
    var show = function (n) {
      qs[qi].classList.remove("on"); dots[qi] && dots[qi].classList.remove("on");
      qi = (n + qs.length) % qs.length;
      qs[qi].classList.add("on");
      if (dots[qi]) { dots[qi].classList.remove("on"); void dots[qi].offsetWidth; dots[qi].classList.add("on"); }
      clearTimeout(qt); qt = setTimeout(function () { show(qi + 1); }, 6500);
    };
    dots.forEach(function (b, i) { b.addEventListener("click", function () { show(i); }); });
    var stage = $(".quote-stage");
    var fit = function () { var h = 0; qs.forEach(function (q) { h = Math.max(h, q.scrollHeight); }); stage.style.minHeight = h + "px"; };
    fit(); window.addEventListener("resize", fit);
    show(0);
  }

  /* ---------- opening hours ---------- */
  var zNow = function () {
    try {
      var parts = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Zurich", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date());
      var o = {}; parts.forEach(function (p) { o[p.type] = p.value; });
      var days = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 0 };
      return { day: days[o.weekday], min: parseInt(o.hour, 10) * 60 + parseInt(o.minute, 10) };
    } catch (e) { var n = new Date(); return { day: n.getDay(), min: n.getHours() * 60 + n.getMinutes() }; }
  };
  var now = zNow();
  $$("[data-hours]").forEach(function (el) {
    var h = JSON.parse(el.getAttribute("data-hours")); // index 0 = Sunday
    var t = h[now.day], label = $(".ostat", el) || el;
    var fmt = function (m) { return Math.floor(m / 60) + ":" + String(m % 60).padStart(2, "0"); };
    var toM = function (s) { var a = s.split(":"); return +a[0] * 60 + +a[1]; };
    var open = t && now.min >= toM(t[0]) && now.min < toM(t[1]);
    var txt;
    if (open) txt = "Ouvert · ferme à " + t[1];
    else if (t && now.min < toM(t[0])) txt = "Fermé · ouvre à " + t[0];
    else {
      var k = 1, nx; while (k < 8 && !(nx = h[(now.day + k) % 7])) k++;
      var names = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
      txt = "Fermé · ouvre " + (k === 1 ? "demain" : names[(now.day + k) % 7]) + " à " + nx[0];
    }
    void fmt;
    label.textContent = txt;
    label.classList.toggle("is-open", !!open);
    var row = $('tr[data-day="' + now.day + '"]', el.closest(".sdetail") || d);
    if (row) row.classList.add("today");
  });

  /* ---------- filters (reviews + gallery) ---------- */
  $$("[data-filter-group]").forEach(function (grp) {
    var items = $$(grp.getAttribute("data-filter-group"));
    $$("button", grp).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("button", grp).forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
        var f = b.getAttribute("data-f");
        items.forEach(function (it) {
          var show = f === "all" || (" " + it.getAttribute("data-tags") + " ").indexOf(" " + f + " ") > -1;
          it.hidden = !show;
        });
      });
    });
  });

  /* ---------- lightbox ---------- */
  var lb = $(".lb");
  if (lb) {
    var lbImg = $(".lb-stage img", lb), lbCap = $(".lb-cap", lb), lbCount = $(".lb-count", lb), list = [], li = 0, lastFocus;
    var open = function (i) {
      list = $$(".gitem[data-full]").filter(function (x) { return !x.hidden; });
      li = i; render(); lb.classList.add("on"); lb.setAttribute("aria-hidden", "false");
      body.style.overflow = "hidden"; lastFocus = d.activeElement; $(".lb-x", lb).focus();
    };
    var render = function () {
      var it = list[li]; lbImg.classList.remove("ready");
      var src = it.getAttribute("data-full");
      var im = new Image(); im.onload = function () { lbImg.src = src; lbImg.alt = it.getAttribute("data-cap") || ""; requestAnimationFrame(function () { lbImg.classList.add("ready"); }); };
      im.src = src;
      lbCap.textContent = it.getAttribute("data-cap") || "";
      lbCount.textContent = String(li + 1).padStart(2, "0") + " / " + String(list.length).padStart(2, "0");
    };
    var close = function () { lb.classList.remove("on"); lb.setAttribute("aria-hidden", "true"); body.style.overflow = ""; lastFocus && lastFocus.focus(); };
    var go = function (k) { li = (li + k + list.length) % list.length; render(); };
    $$(".gitem[data-full]").forEach(function (it) {
      it.setAttribute("tabindex", "0"); it.setAttribute("role", "button");
      var h = function () { open($$(".gitem[data-full]").filter(function (x) { return !x.hidden; }).indexOf(it)); };
      it.addEventListener("click", h);
      it.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); h(); } });
    });
    $(".lb-x", lb).addEventListener("click", close);
    $(".lb-prev", lb).addEventListener("click", function () { go(-1); });
    $(".lb-next", lb).addEventListener("click", function () { go(1); });
    d.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("on")) return;
      if (e.key === "Escape") close(); if (e.key === "ArrowLeft") go(-1); if (e.key === "ArrowRight") go(1);
    });
    var sx = null;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) { if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1); sx = null; });
  }

  /* ---------- lazy maps ---------- */
  $$(".map[data-map]").forEach(function (m) {
    var load = function () {
      if (m.querySelector("iframe")) return;
      var f = d.createElement("iframe");
      f.src = m.getAttribute("data-map"); f.loading = "lazy"; f.title = m.getAttribute("data-title") || "Carte";
      f.referrerPolicy = "no-referrer-when-downgrade";
      m.innerHTML = ""; m.appendChild(f);
    };
    var b = $("button", m); if (b) b.addEventListener("click", load);
  });

  /* ---------- WhatsApp widget ---------- */
  var wa = $(".wa");
  if (wa) {
    var waBtn = $(".wa-btn", wa);
    var setWa = function (o) { wa.classList.toggle("open", o); waBtn.setAttribute("aria-expanded", o); wa.classList.remove("tease"); };
    waBtn.addEventListener("click", function () { setWa(!wa.classList.contains("open")); });
    d.addEventListener("click", function (e) { if (wa.classList.contains("open") && !wa.contains(e.target)) setWa(false); });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape") setWa(false); });
    var hh = new Date(); var tm = $(".wa-msg time", wa);
    if (tm) tm.textContent = String(hh.getHours()).padStart(2, "0") + ":" + String(hh.getMinutes()).padStart(2, "0");
    if (!store.get("vxv-wa")) {
      setTimeout(function () { if (!wa.classList.contains("open")) { wa.classList.add("tease"); store.set("vxv-wa", "1"); setTimeout(function () { wa.classList.remove("tease"); }, 6000); } }, 7000);
    }
  }

  /* ---------- cursor + magnetic ---------- */
  if (fine && !reduce) {
    var cur = d.createElement("div"); cur.className = "cur"; cur.innerHTML = "<span></span>"; body.appendChild(cur);
    var mx = -100, my = -100, kx = -100, ky = -100;
    window.addEventListener("mousemove", function (e) { mx = e.clientX; my = e.clientY; cur.classList.add("on"); }, { passive: true });
    d.addEventListener("mouseleave", function () { cur.classList.remove("on"); });
    (function loop() { kx += (mx - kx) * 0.2; ky += (my - ky) * 0.2; cur.style.transform = "translate3d(" + kx + "px," + ky + "px,0)"; requestAnimationFrame(loop); })();
    d.addEventListener("mouseover", function (e) {
      var t = e.target.closest ? e.target.closest("[data-cursor],a,button") : null;
      cur.classList.remove("big", "link");
      if (!t) return;
      var lab = t.getAttribute && t.getAttribute("data-cursor");
      if (lab) { cur.classList.add("big"); cur.firstChild.textContent = lab; }
      else cur.classList.add("link");
    });
    $$(".btn,.soc .go,.burger").forEach(function (b) {
      b.addEventListener("mousemove", function (e) {
        var r = b.getBoundingClientRect();
        b.style.transform = "translate(" + ((e.clientX - r.left - r.width / 2) * 0.18).toFixed(1) + "px," + ((e.clientY - r.top - r.height / 2) * 0.28).toFixed(1) + "px)";
      });
      b.addEventListener("mouseleave", function () { b.style.transform = ""; });
    });
  }

  /* hero lines run right away when there is no intro */
  if (!loader) setTimeout(heroGo, body.classList.contains("entered") ? 350 : 80);
  var y = $("[data-year]"); if (y) y.textContent = new Date().getFullYear();
})();
