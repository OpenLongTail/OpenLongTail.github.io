/* OpenLongTail project page — interactions */
(function () {
  "use strict";

  /* ---------- Synchronized multi-view playback ----------
   * A group (scene card / stage / mosaic tile) shows the views of one rig, all
   * clips of equal length. Each group runs on its own clock and every view is
   * slaved to it (phase = clock mod period):
   *  - groups are fetched a couple at a time, on-screen ones first, and a
   *    group starts only once every view is buffered enough to play through;
   *  - views are primed at playbackRate 0 and released together, because the
   *    start-up latency of play() differs per video;
   *  - if a view stalls, the others wait at rate 0 and the group resumes from
   *    wherever the slowest view got to;
   *  - small drift is absorbed by nudging playbackRate, large drift by
   *    waiting (view ahead) or seeking (view behind). */
  let speed = 1;
  let lastTick = performance.now();
  let rateZeroOK = true;      // falls back to pause() where playbackRate 0 is refused
  const MAX_LOADING = 2;      // groups fetched in parallel
  const LOAD_TIMEOUT = 20000; // stop waiting on a group's fetch after this (ms)
  const WAIT_MS = 10000;      // start on partial data only after waiting this long
  const NO_PRELOAD_MS = 1500; // browsers that ignore preload (iOS) fetch only once playing
  const PRIME_MS = 2000;      // release a primed group even if a view never reports playing
  const STALL_MS = 150;       // once buffered, ignore stalls shorter than this (loop wrap)
  const PROGRESS_MS = 250;    // window over which a playing view must advance at >= half rate
  const SEEK_DRIFT = 0.3;     // s behind — jump to the clock
  const WAIT_DRIFT = 0.08;    // s ahead — hold at rate 0 until the clock catches up
  const NUDGE_DRIFT = 0.02;   // s — below this, play at nominal speed

  const groups = Array.from(document.querySelectorAll(".scene-card, .stage, .mosaic .tile"))
    .map((el) => ({ el, videos: Array.from(el.querySelectorAll("video[data-src]")),
                    visible: false, running: false, priming: false, holding: false,
                    clock: 0, since: 0, primeAt: 0, load: "", loadStart: 0 }))
    .filter((g) => g.videos.length);
  const groupOf = new Map(groups.map((g) => [g.el, g]));

  function ensureLoaded(v) {
    if (!v.getAttribute("src")) {
      v.preload = "auto";      // buffer the whole clip, not just what play() asks for
      v.src = v.dataset.src;
      v.load();
    }
  }

  function isBuffered(v, t) {
    const b = v.buffered;
    for (let i = 0; i < b.length; i++) if (b.start(i) <= t && t <= b.end(i)) return true;
    return false;
  }

  function fullyBuffered(v) {
    if (v.readyState < 3 || !isFinite(v.duration)) return false;
    const b = v.buffered;
    return b.length === 1 && b.start(0) <= 0.1 && b.end(0) >= v.duration - 0.15;
  }

  const live = (g) => g.videos.filter((v) => !v.error);   // a broken clip must not block its group

  function queueLoad(g) { if (!g.load) g.load = "queued"; }

  function pumpLoads(now) {
    let active = 0;
    groups.forEach((g) => {
      if (g.load !== "loading") return;
      if (live(g).every(fullyBuffered) || now - g.loadStart > LOAD_TIMEOUT) g.load = "done";
      else active++;
    });
    if (active >= MAX_LOADING) return;
    const next = groups.filter((g) => g.load === "queued").sort((a, b) => b.visible - a.visible);
    next.slice(0, MAX_LOADING - active).forEach((g) => {
      g.load = "loading";
      g.loadStart = now;
      g.videos.forEach(ensureLoaded);
    });
  }

  function canStart(g, now) {
    if (g.load !== "loading" && g.load !== "done") return false;
    const vs = live(g);
    if (vs.every(fullyBuffered)) return true;
    // browsers suspend preloading once they expect to play through; trust that
    if (vs.every((v) => v.readyState >= 4)) return true;
    const wait = now - Math.max(g.since, g.loadStart);
    if (wait > NO_PRELOAD_MS && vs.every((v) => v.buffered.length === 0)) return true;
    return wait > WAIT_MS;
  }

  function period(g) {
    let p = 0;
    g.videos.forEach((v) => { if (isFinite(v.duration) && v.duration > p) p = v.duration; });
    return p;
  }

  // signed distance a - b on a circle of length p, in [-p/2, p/2)
  function wrapDiff(a, b, p) { return (((a - b) % p) + p * 1.5) % p - p / 2; }

  function phase(g, p) { return ((g.clock % p) + p) % p; }

  function tryPlay(v, now) {
    if (v._playPending || now < (v._blockedUntil || 0)) return;
    const p = v.play();
    if (p && p.then) {
      v._playPending = true;
      p.then(() => { v._playPending = false; }, (err) => {
        v._playPending = false;
        // back off only when autoplay is refused, not when our own pause() aborted it
        if (err && err.name === "NotAllowedError") v._blockedUntil = performance.now() + 1000;
      });
    }
  }

  function setRate(v, r) {
    if (r === 0 && !rateZeroOK) { if (!v.paused) v.pause(); return; }
    if (Math.abs(v.playbackRate - r) <= 0.005) return;
    try {
      v.playbackRate = r;
      v._winAt = 0;            // restart the progress window at the new rate
    } catch (e) {
      if (r !== 0) throw e;
      rateZeroOK = false;
      v.pause();
    }
  }

  function seekTo(v, t, p) {
    if (v.readyState >= 1 && Math.abs(wrapDiff(v.currentTime, t, p)) > NUDGE_DRIFT) v.currentTime = t;
  }

  // put every view at the group's phase and start it at rate 0 (see priming in tick)
  function start(g, now) {
    const p = period(g);
    g.videos.forEach((v) => {
      if (p) seekTo(v, phase(g, p), p);
      setRate(v, rateZeroOK ? 0 : speed);
      tryPlay(v, now);
    });
    g.running = true;
    g.priming = rateZeroOK;
    g.holding = false;
    g.primeAt = now;
  }

  function stop(g) {
    g.videos.forEach((v) => v.pause());
    g.running = false;
    g.priming = false;
    g.holding = false;
  }

  function syncVideo(v, target, p, now) {
    if (!v.getAttribute("src") || v.readyState < 1 || v.seeking) return;
    if (v.paused) {            // autoplay refused earlier, or the rate-0 fallback paused it
      seekTo(v, target, p);
      setRate(v, speed);
      tryPlay(v, now);
      return;
    }
    if (v.readyState < 3) return;
    const drift = wrapDiff(v.currentTime, target, p);
    let rate = speed;
    if (drift > WAIT_DRIFT && rateZeroOK) {
      rate = 0;
    } else if (Math.abs(drift) > SEEK_DRIFT && isBuffered(v, target)) {
      v.currentTime = target;
    } else if (Math.abs(drift) > NUDGE_DRIFT) {
      rate = speed * (1 - Math.max(-0.25, Math.min(0.25, drift * 2.5)));
    }
    setRate(v, rate);
  }

  // views that are starved of data, seeking, or advancing at under half their rate
  function stalledViews(g, p, now, grace) {
    return live(g).filter((v) => {
      let s = v.seeking || v.readyState < 3;
      if (v.paused || v.playbackRate === 0) {
        v._winAt = 0;
        v._slow = false;
      } else if (!v._winAt) {
        v._winAt = now;
        v._winT = v.currentTime;
      } else if (now - v._winAt >= PROGRESS_MS) {
        const moved = (((v.currentTime - v._winT) % p) + p) % p;
        v._slow = moved < 0.5 * v.playbackRate * (now - v._winAt) / 1000;
        v._winAt = now;
        v._winT = v.currentTime;
      }
      if (v._slow) s = true;
      if (!s) v._stallSince = 0;
      else if (!v._stallSince) v._stallSince = now;
      return s && now - v._stallSince >= grace;
    });
  }

  function tick(now) {
    const dt = Math.min(now - lastTick, 1000) / 1000 * speed;
    lastTick = now;
    pumpLoads(now);
    groups.forEach((g) => {
      if (!g.visible) return;
      if (!g.running) {
        if (canStart(g, now)) start(g, now);
        return;
      }
      const p = period(g);
      if (!p) return;
      const vs = live(g);
      if (g.priming) {
        // release all views in the same frame once every pipeline is actually running
        if (vs.every((v) => !v.paused && !v._playPending && v.readyState >= 3) || now - g.primeAt > PRIME_MS) {
          g.priming = false;
          vs.forEach((v) => setRate(v, speed));
        }
        return;
      }
      // while clips are still arriving, hold on any stall; once buffered, debounce
      const grace = vs.every(fullyBuffered) ? STALL_MS : 0;
      const stalled = stalledViews(g, p, now, grace);
      if (stalled.length) {
        vs.forEach((v) => { if (!stalled.includes(v)) setRate(v, 0); });
        g.holding = true;
        return;
      }
      if (g.holding) {
        // resume from the slowest view; views ahead of it wait at rate 0 in syncVideo
        let lag = 0;
        vs.forEach((v) => { if (v.readyState >= 1) lag = Math.min(lag, wrapDiff(v.currentTime, phase(g, p), p)); });
        g.clock += lag;
        g.holding = false;
      }
      g.clock += dt;
      const target = phase(g, p);
      g.videos.forEach((v) => syncVideo(v, target, p, now));
    });
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  // queue a group's clips for fetching shortly before it scrolls in ...
  const loadObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      const g = groupOf.get(e.target);
      if (g && e.isIntersecting) {
        queueLoad(g);
        loadObs.unobserve(e.target);
      }
    });
  }, { rootMargin: "500px 0px" });

  // ... and play it only while it is (nearly) on screen
  const playObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      const g = groupOf.get(e.target);
      if (!g) return;
      g.visible = e.isIntersecting;
      if (g.visible) {
        queueLoad(g);
        g.since = performance.now();
      } else {
        stop(g);
      }
    });
  }, { rootMargin: "200px 0px", threshold: 0.05 });

  groups.forEach((g) => { loadObs.observe(g.el); playObs.observe(g.el); });

  /* ---------- Per-card Generated / Ground-Truth toggle ---------- */
  document.querySelectorAll(".toggle").forEach((tg) => {
    const card = tg.closest(".scene-card");
    tg.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.dataset.mode; // pred | gt
        tg.querySelectorAll("button").forEach((b) => b.classList.toggle("active", b === btn));
        const role = card.querySelector(".scene-foot .role b");
        if (role) role.textContent = mode === "gt" ? "Ground Truth" : "OpenLongTail";
        // freeze the card, swap sources, and resume all views together once buffered
        const g = groupOf.get(card);
        if (g) { stop(g); g.since = performance.now(); }
        card.querySelectorAll("video.switch").forEach((v) => {
          const next = mode === "gt" ? v.dataset.gt : v.dataset.pred;
          v.dataset.src = next;
          if (!v.getAttribute("src")) return;
          v.src = next;
          v.load();
          // show the frozen frame of the new clip, not its first frame, while it buffers
          if (g) v.addEventListener("loadedmetadata", () => {
            const p = period(g);
            if (p && !g.running) v.currentTime = phase(g, p);
          }, { once: true });
        });
      });
    });
  });

  /* ---------- Playback speed ---------- */
  document.querySelectorAll(".speed-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      speed = parseFloat(btn.dataset.speed);
      document.querySelectorAll(".speed-btn").forEach((b) => b.classList.toggle("active", b === btn));
      // the sync loop applies the new rate on its next frame
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
      // tiles are already observed as sync groups; they start once shown
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

  /* ---------- Single -> Multi stage: replay fan-out on scroll ---------- */
  const stage = document.querySelector(".stage");
  if (stage) {
    const stageObs = new IntersectionObserver((entries) => {
      entries.forEach((e) => stage.classList.toggle("playing", e.isIntersecting));
    }, { threshold: 0.35 });
    stageObs.observe(stage);
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
  ["abstract", "expand", "gallery", "eval", "external", "method", "citation"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) secObs.observe(el);
  });
})();
