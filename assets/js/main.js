/* OpenLongTail project page — interactions */
(function () {
  "use strict";

  /* ---------- Lazy load + play videos only when in view ---------- */
  const allVideos = Array.from(document.querySelectorAll("video[data-src]"));
  let speed = 1;

  function ensureLoaded(v) {
    if (!v.src) {
      v.src = v.dataset.src;
      v.load();
    }
  }

  const playObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      const v = e.target;
      if (e.isIntersecting) {
        ensureLoaded(v);
        v.playbackRate = speed;
        const p = v.play();
        if (p && p.catch) p.catch(() => {});
      } else {
        v.pause();
      }
    });
  }, { rootMargin: "200px 0px", threshold: 0.1 });

  allVideos.forEach((v) => playObs.observe(v));

  /* ---------- Per-card Generated / Ground-Truth toggle ---------- */
  document.querySelectorAll(".toggle").forEach((tg) => {
    const card = tg.closest(".scene-card");
    tg.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.dataset.mode; // pred | gt
        tg.querySelectorAll("button").forEach((b) => b.classList.toggle("active", b === btn));
        const role = card.querySelector(".scene-foot .role b");
        if (role) role.textContent = mode === "gt" ? "Ground Truth" : "OpenLongTail";
        card.querySelectorAll("video.switch").forEach((v) => {
          const next = mode === "gt" ? v.dataset.gt : v.dataset.pred;
          v.dataset.src = next;
          // reload if already showing
          v.pause();
          v.src = next;
          v.load();
          v.playbackRate = speed;
          const p = v.play();
          if (p && p.catch) p.catch(() => {});
        });
      });
    });
  });

  /* ---------- Playback speed ---------- */
  document.querySelectorAll(".speed-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      speed = parseFloat(btn.dataset.speed);
      document.querySelectorAll(".speed-btn").forEach((b) => b.classList.toggle("active", b === btn));
      allVideos.forEach((v) => { if (v.src) v.playbackRate = speed; });
    });
  });

  /* ---------- Mosaic show-more ---------- */
  const moreBtn = document.getElementById("mosaicMore");
  if (moreBtn) {
    moreBtn.addEventListener("click", () => {
      const hidden = document.querySelectorAll(".mosaic .mosaic-hidden");
      const expanded = moreBtn.classList.toggle("expanded");
      hidden.forEach((t) => t.classList.toggle("show", expanded));
      moreBtn.childNodes[0].nodeValue = expanded ? "Show fewer views " : "Show all 65 views ";
      // re-observe newly visible tiles
      hidden.forEach((t) => { const v = t.querySelector("video"); if (v) playObs.observe(v); });
    });
  }

  /* ---------- Copy BibTeX ---------- */
  const copyBtn = document.getElementById("copyBib");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const txt = document.getElementById("bibtex").innerText;
      try { await navigator.clipboard.writeText(txt); } catch (e) {}
      const orig = copyBtn.innerHTML;
      copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied';
      copyBtn.disabled = true;
      setTimeout(() => { copyBtn.innerHTML = orig; copyBtn.disabled = false; }, 1600);
    });
  }

  /* ---------- Nav + back-to-top visibility ---------- */
  const onScroll = () => {
    const y = window.scrollY;
    document.body.classList.toggle("nav-visible", y > window.innerHeight * 0.6);
    document.body.classList.toggle("back-to-top-visible", y > window.innerHeight * 0.9);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  const backTop = document.getElementById("backTop");
  if (backTop) backTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  /* ---------- Active nav link via section observer ---------- */
  const links = Array.from(document.querySelectorAll(".section-nav-link"));
  const byId = {};
  links.forEach((l) => { byId[l.getAttribute("href").slice(1)] = l; });
  const secObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        links.forEach((l) => l.classList.remove("active"));
        const l = byId[e.target.id];
        if (l) l.classList.add("active");
      }
    });
  }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
  ["abstract", "gallery", "eval", "external", "method", "citation"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) secObs.observe(el);
  });
})();
