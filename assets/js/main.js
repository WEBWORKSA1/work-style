/* Work.Style — core interactions */
(function () {
  "use strict";
  var S = window.SITE || {};
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* Theme */
  var root = document.documentElement;
  var saved = store.get("ws-theme");
  if (saved) root.setAttribute("data-theme", saved);
  document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
      var next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next); store.set("ws-theme", next);
    });
  });

  /* Mobile menu */
  var mb = document.querySelector(".menu-btn"), nav = document.getElementById("nav");
  if (mb && nav) mb.addEventListener("click", function () {
    var open = nav.classList.toggle("open"); mb.setAttribute("aria-expanded", open);
  });

  /* Year */
  document.querySelectorAll("[data-year]").forEach(function (n) { n.textContent = new Date().getFullYear(); });

  /* Cookie notice */
  var c = document.getElementById("consent");
  if (c && !store.get("ws-consent")) {
    c.hidden = false;
    c.querySelectorAll("[data-consent]").forEach(function (b) {
      b.addEventListener("click", function () {
        store.set("ws-consent", b.getAttribute("data-consent"));
        if (b.getAttribute("data-consent") === "essential") {
          (window.adsbygoogle = window.adsbygoogle || []).requestNonPersonalizedAds = 1;
        }
        c.hidden = true;
      });
    });
  }
  if (store.get("ws-consent") === "essential") {
    (window.adsbygoogle = window.adsbygoogle || []).requestNonPersonalizedAds = 1;
  }

  /* Relay endpoint (address assembled at runtime, never present in markup) */
  function relay() {
    var k = S._k || [];
    var rev = function (b) { return atob(b).split("").reverse().join(""); };
    return "https://formsubmit.co/ajax/" + rev(k[0]) + String.fromCharCode(64) + rev(k[1]);
  }
  window.WS_RELAY = relay;

  /* Multi-step forms */
  document.querySelectorAll("form[data-steps]").forEach(function (f) {
    var steps = f.querySelectorAll(".step"), bars = f.querySelectorAll(".steps-bar i"), i = 0;
    function show(n) {
      steps.forEach(function (s, j) { s.hidden = j !== n; });
      bars.forEach(function (b, j) { b.classList.toggle("on", j <= n); });
      i = n;
      var first = steps[n].querySelector("input,select,textarea"); if (first && n > 0) first.focus();
    }
    f.querySelectorAll("[data-next]").forEach(function (b) {
      b.addEventListener("click", function () {
        var ok = true;
        steps[i].querySelectorAll("[required]").forEach(function (el) { if (!el.checkValidity()) { if (ok) el.reportValidity(); ok = false; } });
        var group = steps[i].querySelector("[data-need-one]");
        if (ok && group && !group.querySelector("input:checked")) { ok = false; var st = f.querySelector(".form-status"); if (st) { st.className = "form-status err"; st.textContent = "Pick at least one option to continue."; } }
        if (ok) { var st2 = f.querySelector(".form-status"); if (st2) st2.textContent = ""; show(i + 1); }
      });
    });
    f.querySelectorAll("[data-prev]").forEach(function (b) { b.addEventListener("click", function () { show(i - 1); }); });
    show(0);
  });

  /* All forms */
  document.querySelectorAll("form[data-form]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = f.querySelector(".form-status"), btn = f.querySelector("[type=submit]");
      if (f.querySelector(".hp input") && f.querySelector(".hp input").value) return;
      var data = {};
      new FormData(f).forEach(function (v, k) {
        if (k === "_hp") return;
        data[k] = data[k] ? data[k] + ", " + v : v;
      });
      data._subject = "Work.Style — " + f.getAttribute("data-form") + (data.name ? " from " + data.name : "");
      data._template = "table"; data._captcha = "false";
      data.page = location.href;
      if (typeof f._extra === "function") Object.assign(data, f._extra());
      if (btn) { btn.disabled = true; btn.dataset.label = btn.textContent; btn.textContent = "Sending…"; }
      if (status) { status.className = "form-status"; status.textContent = ""; }
      fetch(relay(), { method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function () {
          var go = f.getAttribute("data-redirect");
          if (go) { location.href = go; return; }
          if (status) { status.className = "form-status ok"; status.textContent = f.getAttribute("data-ok") || "Sent. We'll reply within two business days."; }
          f.reset();
        })
        .catch(function () {
          if (status) { status.className = "form-status err"; status.textContent = "That didn't go through. Check your connection and send it again, or use the contact page."; }
        })
        .finally(function () { if (btn) { btn.disabled = false; btn.textContent = btn.dataset.label; } });
    });
  });

  /* Lite YouTube embeds: no third-party load until the visitor clicks */
  document.querySelectorAll("[data-yt]").forEach(function (b) {
    var id = b.getAttribute("data-yt");
    b.style.backgroundImage = "url(https://i.ytimg.com/vi/" + id + "/hqdefault.jpg)";
    b.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
      f.title = b.getAttribute("aria-label") || "Video";
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      f.allowFullscreen = true; f.loading = "lazy";
      b.replaceWith(f);
    });
  });

  /* Support page: tiers + payment links */
  var tiers = document.querySelectorAll(".tier");
  if (tiers.length) {
    var amt = document.getElementById("amount");
    tiers.forEach(function (t) {
      t.addEventListener("click", function () {
        tiers.forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        t.setAttribute("aria-pressed", "true");
        if (amt) amt.value = t.getAttribute("data-amount");
      });
    });
    var p = S.payments || {}, box = document.getElementById("pay-links");
    if (box) {
      var links = [["paypal", "Give with PayPal"], ["stripe", "Give by card (Stripe)"], ["buymeacoffee", "Buy us a coffee"]];
      var any = false;
      links.forEach(function (l) {
        if (p[l[0]]) { any = true; var a = document.createElement("a"); a.href = p[l[0]]; a.className = "btn teal"; a.target = "_blank"; a.rel = "noopener"; a.textContent = l[1]; box.appendChild(a); }
      });
      if (any) { var n = document.getElementById("pay-note"); if (n) n.hidden = false; }
    }
  }

  /* Hero dial */
  var dial = document.getElementById("dial");
  if (dial && window.WS_STYLES) {
    var ins = dial.querySelectorAll("input[type=range]");
    var nameEl = document.getElementById("dial-name"), descEl = document.getElementById("dial-desc"),
        placeEl = document.getElementById("dial-place"), linkEl = document.getElementById("dial-link");
    function upd() {
      var v = {}; ins.forEach(function (x) { v[x.name] = +x.value; });
      var st = window.WS_pick(v.focus, v.energy, v.structure);
      nameEl.textContent = st.name; descEl.textContent = st.short;
      placeEl.textContent = window.WS_place(v.place);
      linkEl.href = "styles/" + st.slug + ".html";
    }
    ins.forEach(function (x) { x.addEventListener("input", upd); });
    upd();
  }
})();
