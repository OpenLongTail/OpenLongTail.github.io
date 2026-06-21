#!/usr/bin/env python3
import html

VIEW_LABEL = {"cl": "Cross-Left", "cr": "Cross-Right", "rl": "Rear-Left", "rr": "Rear-Right", "rt": "Rear-Tele"}

# id, name, badge_text, badge_class, has_gt
SCENES = [
    ("s01", "Busy Urban Street",        "Urban",        "",     True),
    ("s02", "Work Zone",                "Work Zone",    "work", True),
    ("s03", "Work Zone",                "Work Zone",    "work", True),
    ("s04", "Urban Corridor",           "Urban",        "",     True),
    ("s05", "Suburban Through-Road",    "Suburban",     "",     True),
    ("s06", "Residential Street",       "Residential",  "",     True),
    ("s07", "Snow Driving",             "Snow",         "",     True),
    ("s08", "Work Zone",                "Work Zone",    "work", True),
    ("s09", "Boulevard",                "Boulevard",    "",     True),
    ("s10", "Low-Sun Glare Drive",      "In-the-Wild",  "wild", False),
    ("s11", "Overcast Residential",     "In-the-Wild",  "wild", False),
    ("s12", "Sunny Tree-Lined Street",  "In-the-Wild",  "wild", False),
    ("s13", "Urban Crossing",           "In-the-Wild",  "wild", False),
]

VID = "assets/videos"
POS = "assets/posters"

def v_attrs(src, poster):
    return (f'preload="none" muted loop playsinline poster="{poster}" '
            f'data-src="{src}"')

def view_cell(sid, view, has_gt, is_input=False):
    """One cell in the surround grid."""
    if is_input:
        src = f"{VID}/{sid}_front.mp4"
        pos = f"{POS}/{sid}_front.jpg"
        return (f'<div class="view-cell is-input">'
                f'<span class="view-tag">Input · Front</span>'
                f'<video {v_attrs(src, pos)}></video></div>')
    pred = f"{VID}/{sid}_pred_{view}.mp4"
    pos = f"{POS}/{sid}_pred_{view}.jpg"
    extra = ""
    vid_class = ""
    if has_gt:
        gt = f"{VID}/{sid}_gt_{view}.mp4"
        extra = f' data-pred="{pred}" data-gt="{gt}"'
        vid_class = ' class="switch"'
    return (f'<div class="view-cell">'
            f'<span class="view-tag">{VIEW_LABEL[view]}</span>'
            f'<video{vid_class} {v_attrs(pred, pos)}{extra}></video></div>')

def scene_card(sid, name, badge, badge_cls, has_gt):
    bc = f"badge {badge_cls}".strip()
    # 3x2 surround: cl, front, cr / rl, rt, rr
    cells = [
        view_cell(sid, "cl", has_gt), view_cell(sid, "", has_gt, is_input=True), view_cell(sid, "cr", has_gt),
        view_cell(sid, "rl", has_gt), view_cell(sid, "rt", has_gt), view_cell(sid, "rr", has_gt),
    ]
    if has_gt:
        foot = (f'<div class="scene-foot">'
                f'<span class="role">Surround views: <b>OpenLongTail</b></span>'
                f'<span class="toggle" data-card="{sid}">'
                f'<button class="active" data-mode="pred">Generated</button>'
                f'<button data-mode="gt">Ground&nbsp;Truth</button></span></div>')
    else:
        foot = ''
    return (f'<div class="scene-card" data-scene="{sid}">'
            f'<div class="scene-head"><span class="scene-name">{html.escape(name)}</span>'
            f'<span class="{bc}">{html.escape(badge)}</span></div>'
            f'<div class="surround">{"".join(cells)}</div>'
            f'{foot}</div>')

def mosaic_tiles():
    tiles = []
    order = ["cl", "cr", "rt", "rl", "rr"]
    idx = 0
    for sid, name, *_ in SCENES:
        for view in order:
            src = f"{VID}/{sid}_pred_{view}.mp4"
            pos = f"{POS}/{sid}_pred_{view}.jpg"
            hidden = "" if idx < 20 else " mosaic-hidden"
            tiles.append(
                f'<div class="tile{hidden}">'
                f'<span class="view-tag">{html.escape(name)} · {VIEW_LABEL[view]}</span>'
                f'<video {v_attrs(src, pos)}></video></div>')
            idx += 1
    return "".join(tiles)

AFFIL = [
    "Texas A&amp;M University", "NVIDIA", "University of Wisconsin&ndash;Madison",
    "The University of Texas at Austin", "Yale University",
    "Adobe", "Meta", "University of Delaware", "Stanford University",
]
# (name, [affiliation indices 1-based], url, mark)
AUTHORS = [
    ("Lulin Liu",      [1],     "https://lulinliu.github.io/", "*"),
    ("Nuo Chen",       [1],    "https://nuochen1203.github.io/", "*"),
    ("Yan Wang",       [2],    "https://yanwang.org/", ""),
    ("Bangya Liu",     [3],    "https://phddirectory.ece.wisc.edu/staff/liu-bangya/", ""),
    ("Wenyan Cong",    [4],    "https://www.wenyancong.com/", ""),
    ("Hezhen Hu",      [4],    "https://alexhu.top/", ""),
    ("Boris Ivanovic", [2],    "https://research.nvidia.com/labs/avg/author/boris-ivanovic/", ""),
    ("Hao Wang",       [1],    "http://www.wanghao.in/", ""),
    ("Ziyao Zeng",     [5],    "https://vision.cs.yale.edu/members/ziyao-zeng.html", ""),
    ("Xinyu Gong",     [6],    "", ""),
    ("Yang Zhou",      [1],    "https://yangzhou.engr.tamu.edu/", ""),
    ("Zixiang Xiong",  [1],    "https://engineering.tamu.edu/electrical/profiles/zxiong.html", ""),
    ("Dilin Wang",     [7],    "https://wdilin.github.io/", ""),
    ("Zhangyang Wang", [4],    "https://vita-group.github.io/", ""),
    ("Weisong Shi",    [8],    "https://www.cis.udel.edu/people/faculty/weisong-shi/", ""),
    ("Ruohan Zhang",   [9],    "https://ai.stanford.edu/~zharu/", ""),
    ("Marco Pavone",   [2, 9], "https://research.nvidia.com/person/marco-pavone", ""),
    ("Zhiwen Fan",     [1],    "https://zhiwenfan.github.io/", "†"),
]

def render_authors():
    out = []
    for name, aff, url, mark in AUTHORS:
        sup = ",".join(str(a) for a in aff) + mark
        inner = f'{html.escape(name)}<sup>{sup}</sup>'
        if url:
            out.append(f'<a class="author-link" href="{url}" target="_blank" rel="noopener">{inner}</a>')
        else:
            out.append(f'<span class="author-link">{inner}</span>')
    return ", ".join(out)

def render_affils():
    return " &nbsp; ".join(f'<sup>{i+1}</sup>{a}' for i, a in enumerate(AFFIL))

def build_eval_table():
    # (method label, ours?, [ (AS, CR) x 4 categories + Avg ])
    rows = [
        ("Alpamayo R1", False,            ["0.457","71.4","0.534","50.0","0.575","50.0","0.683","50.0","0.534","58.8"]),
        ("Alpamayo 1.5", False,           ["0.469","75.0","0.347","100.0","0.517","33.3","0.731","50.0","0.501","61.1"]),
        ("+ SFT (10K Rand)", False,       ["0.659","25.0","0.670","0.0","0.733","0.0","0.936","0.0","0.716","11.1"]),
        ("+ SFT (10K + NV-OOD GT)", False,["0.743","0.0","0.688","0.0","0.758","0.0","0.938","0.0","0.764","0.0"]),
        ("+ SFT (10K + NV-OOD Syn)", True,["0.747","0.0","0.662","0.0","0.717","0.0","0.935","0.0","0.748","0.0"]),
        ("+ SFT (10K + NV GT + Waymo GT)", False, ["0.691","12.5","0.691","0.0","0.735","0.0","0.958","0.0","0.736","5.6"]),
        ("+ SFT (10K + NV Syn + Waymo Syn)", True, ["0.699","12.5","0.689","0.0","0.765","0.0","0.950","0.0","0.748","5.6"]),
    ]
    # mark Avg AS (index 8) and Avg CR (index 9): best=bold, 2nd=underline
    def cell(val, col, is_cr):
        # only decorate the Avg columns (8,9)
        if col == 8:  # Avg AS, higher better -> best 0.764, 2nd 0.748
            if val == "0.764": return f"<b>{val}</b>"
            if val == "0.748": return f'<span class="u">{val}</span>'
        if col == 9:  # Avg CR, lower better -> best 0.0, 2nd 5.6
            if val == "0.0": return f"<b>{val}%</b>"
            if val == "5.6": return f'<span class="u">{val}%</span>'
        return val + ("%" if is_cr else "")
    body = ""
    for label, ours, vals in rows:
        cls = ' class="ours"' if ours else ""
        tag = ' <span class="tag-ours">Ours</span>' if ours else ""
        tds = ""
        for i, v in enumerate(vals):
            is_cr = (i % 2 == 1)
            grp = ' class="grp"' if i % 2 == 0 else ""
            tds += f"<td{grp}>{cell(v, i, is_cr)}</td>"
        body += f'<tr{cls}><td class="method">{label}{tag}</td>{tds}</tr>'
    return f'''<div class="eval-table-wrap"><table class="eval-table">
      <thead>
        <tr><th class="method" rowspan="2">Model / Training data</th>
            <th class="grp" colspan="2">Complex Int.</th><th colspan="2">Cyclists</th>
            <th class="grp" colspan="2">Uncommon Veh.</th><th colspan="2">Work Zone</th>
            <th class="grp" colspan="2">Average</th></tr>
        <tr>
            <th class="grp metric-sub">AS&uarr;</th><th class="metric-sub">CR&darr;</th>
            <th class="metric-sub">AS&uarr;</th><th class="metric-sub">CR&darr;</th>
            <th class="grp metric-sub">AS&uarr;</th><th class="metric-sub">CR&darr;</th>
            <th class="metric-sub">AS&uarr;</th><th class="metric-sub">CR&darr;</th>
            <th class="grp metric-sub">AS&uarr;</th><th class="metric-sub">CR&darr;</th></tr>
      </thead>
      <tbody>{body}</tbody>
    </table></div>'''

gallery_cards = "".join(scene_card(*s) for s in SCENES if s[4])
wild_cards = "".join(scene_card(*s) for s in SCENES if not s[4])

BIBTEX = """@inproceedings{openlongtail2026,
  title     = {OpenLongTail: Generative Scaling of Long-Tail Driving Data},
  author    = {Liu, Lulin and Chen, Nuo and Wang, Yan and Liu, Bangya and Cong, Wenyan and Hu, Hezhen and Ivanovic, Boris and Wang, Hao and Zeng, Ziyao and Gong, Xinyu and Zhou, Yang and Xiong, Zixiang and Wang, Dilin and Wang, Zhangyang and Shi, Weisong and Zhang, Ruohan and Pavone, Marco and Fan, Zhiwen},
  year      = {2026}
}"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OpenLongTail: Generative Scaling of Long-Tail Driving Data</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<link rel="stylesheet" href="assets/css/index.css">
</head>
<body>

<nav class="section-nav"><div class="section-nav-inner">
  <a class="section-nav-link" href="#abstract">Abstract</a>
  <a class="section-nav-link" href="#gallery">Multi-View Gallery</a>
  <a class="section-nav-link" href="#eval">Evaluation</a>
  <a class="section-nav-link" href="#external">External Helps NV</a>
  <a class="section-nav-link" href="#method">Method</a>
  <a class="section-nav-link" href="#citation">BibTeX</a>
</div></nav>

<!-- HERO -->
<header class="hero-section" id="top">
  <video class="hero-video" autoplay muted loop playsinline poster="{POS}/hero_bg.jpg">
    <source src="{VID}/hero_bg.mp4" type="video/mp4"></video>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-title">
      <h1 class="logo-title" aria-label="OpenLongTail">
        <svg viewBox="0 46 1200 168" role="img" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="ltg" gradientUnits="userSpaceOnUse" x1="150" y1="0" x2="1200" y2="0">
              <stop offset="0" stop-color="#5aa8ff"/>
              <stop offset="0.40" stop-color="#b9a3ff"/>
              <stop offset="0.72" stop-color="#f3a3c8"/>
              <stop offset="1" stop-color="#ffce9e"/>
              <animate attributeName="x1" values="150;30;150" dur="9s" repeatCount="indefinite"/>
              <animate attributeName="x2" values="1200;1080;1200" dur="9s" repeatCount="indefinite"/>
            </linearGradient>
          </defs>
          <!-- long-tail distribution curve running under the word -->
          <path d="M 190,182 C 330,182 372,156 500,153 C 642,150 800,172 1002,166"
                fill="none" stroke="url(#ltg)" stroke-width="4" stroke-linecap="round" opacity="0.85"/>
          <!-- the real tail: sweeps off the end of the word and flicks up -->
          <path d="M 1000,158 C 1062,158 1112,150 1142,132 C 1166,116 1181,104 1198,85
                   C 1177,112 1151,129 1120,143 C 1074,167 1040,179 1000,180 Z"
                fill="url(#ltg)"/>
          <!-- rare long-tail events dissolving off the tip -->
          <circle cx="1182" cy="78" r="3.1" fill="url(#ltg)"/>
          <circle cx="1199" cy="65" r="2.3" fill="url(#ltg)" opacity="0.85"/>
          <circle cx="1213" cy="55" r="1.6" fill="url(#ltg)" opacity="0.65"/>
          <!-- wordmark: "Open" hollow/open, "LongTail" solid -->
          <text x="600" y="176" text-anchor="middle" letter-spacing="1.5"
                font-family="'Orbitron', sans-serif" font-weight="800" font-size="86">
            <tspan fill="none" stroke="url(#ltg)" stroke-width="2.2" paint-order="stroke">Open</tspan><tspan fill="url(#ltg)">LongTail</tspan>
          </text>
        </svg>
      </h1>
      <p class="subtitle">Generative Scaling of Long-Tail Driving Data</p>
    </div>
    <div class="authors">{render_authors()}</div>
    <div class="affiliations">{render_affils()}</div>
    <div class="author-notes"><sup>*</sup>Equal contribution &nbsp;&nbsp; <sup>&dagger;</sup>Corresponding author</div>
    <div class="links">
      <a class="link-button" href="#" onclick="return false;"><i class="fas fa-file-pdf"></i> Paper</a>
      <a class="link-button" href="#" onclick="return false;"><i class="ai ai-arxiv"></i> arXiv</a>
      <a class="link-button" href="#" onclick="return false;"><i class="fab fa-github"></i> Code</a>
    </div>
  </div>
  <a class="scroll-hint" href="#abstract"><i class="fas fa-chevron-down"></i></a>
</header>

<!-- ABSTRACT -->
<section class="content-section" id="abstract">
  <div class="container">
    <h2 class="section-title">Abstract</h2>
    <div class="tldr-card">
      <p class="tldr-text"><span class="tldr-label">TL;DR</span>
        OpenLongTail turns <span class="tldr-emphasis">monocular dash-cam long-tail videos</span> into
        synchronized, pose-grounded <span class="tldr-emphasis">multi-view training assets</span>, improving
        closed-loop driving robustness to a level comparable with real multi-camera capture.</p>
    </div>
    <div class="abstract-centered-text">
      <p class="content-text">Scaling robust driving policies is fundamentally bottlenecked by the scarcity of edge cases
        in curated datasets. While the real world continuously captures these critical events, such long-tail events remain
        underutilized when collected from heterogeneous sources, which often lack the full view coverage required for training
        policy models. We introduce <b>OpenLongTail</b>, an open-source generative data engine for scaling autonomous driving
        policies under long-tail events. We develop a pose-informed extrapolative view synthesis pipeline that generates the
        missing context, and enhance cross-view consistency and temporal alignment by injecting Pl&uuml;cker ray geometry into a
        scalable generation engine. Synthesizing heterogeneous long-tail data yields significant improvements in closed-loop
        driving robustness, validated through extrapolative view synthesis and ego-trajectory recovery metrics.</p>
    </div>
  </div>
</section>

<!-- GALLERY -->
<section class="content-section alt" id="gallery">
  <div class="container wide">
    <h2 class="section-title">Multi-View Generation Gallery</h2>
    <p class="section-sub">From a single front-view input, OpenLongTail synthesizes five surround views under the target rig.
      Toggle each card between <b>Generated</b> and <b>Ground&nbsp;Truth</b>. The input (front) is always real.</p>
    <div class="speed-control"><span class="lbl">Playback speed</span>
      <button class="speed-btn" data-speed="0.5">0.5&times;</button>
      <button class="speed-btn active" data-speed="1">1&times;</button>
      <button class="speed-btn" data-speed="2">2&times;</button></div>
    <div class="gallery-grid">{gallery_cards}</div>
  </div>
</section>

<!-- EVALUATION -->
<section class="content-section" id="eval">
  <div class="container wide">
    <h2 class="section-title">Closed-Loop Evaluation in AlpaSim</h2>
    <p class="section-sub">Fine-tuning Alpamayo-R1 with OpenLongTail-synthesized multi-view data improves closed-loop
      driving robustness on 53 long-tail events, on par with training on real multi-camera capture.
      AS = AlpaSim Score (higher is better); CR = Collision Rate (lower is better).</p>
    {build_eval_table()}
    <p class="fig-caption">OpenLongTail-synthesized data (<b>Ours</b>) lifts average AS to 0.748 and drives collision rate
      to 0.0%, comparable to training on ground-truth multi-view data (0.764 AS).</p>
  </div>
</section>

<!-- EXTERNAL HELPS NV -->
<section class="content-section alt" id="external">
  <div class="container wide">
    <h2 class="section-title">External Sources Like Waymo Can Help NV</h2>
    <p class="section-sub">OpenLongTail converts external monocular videos (e.g. Waymo E2E) into target-rig
      multi-view assets, expanding the long-tail training pool. Adding both NV and external synthesized data
      produces more scene-consistent closed-loop rollouts across uncommon vehicles, cyclists, and complex intersections.</p>
    <img class="method-image" src="assets/img/external_waymo.png" alt="Closed-loop benefits of generative scaling with external sources">
    <p class="fig-caption">Closed-loop BEV rollouts of Alpamayo&nbsp;R1 versus variants augmented with OpenLongTail
      assets from NV data and from NV + external (Waymo) sources. Generated data expands useful long-tail coverage
      rather than merely increasing sample count.</p>
  </div>
</section>

<!-- METHOD -->
<section class="content-section" id="method">
  <div class="container">
    <h2 class="section-title">How It Works</h2>
    <img class="method-image" src="assets/img/pipeline.png?v=6" alt="OpenLongTail pipeline overview">
    <p class="fig-caption">Given a long-tail front-view video, OpenLongTail recovers a metric ego-trajectory, builds pose-aware
      geometric conditions, and synthesizes synchronized non-front views within a Wan&nbsp;2.1-VACE backbone.</p>
    <div class="feature-grid">
      <div class="feature"><span class="fi"><i class="fas fa-route"></i></span><h3>Metric Pose Recovery</h3>
        <p>MapAnything recovers a metric-scale ego-trajectory, stabilized by Kalman + RTS smoothing for jitter-free pose conditioning.</p></div>
      <div class="feature"><span class="fi"><i class="fas fa-cube"></i></span><h3>Pl&uuml;cker Ray Geometry</h3>
        <p>Per-token camera rays encode target-camera geometry so every branch operates in one consistent 3D ray frame.</p></div>
      <div class="feature"><span class="fi"><i class="fas fa-layer-group"></i></span><h3>Temporal Depth Warp</h3>
        <p>Depth-based reprojection propagates visible front-view evidence into side and rear targets, even with zero overlap.</p></div>
      <div class="feature"><span class="fi"><i class="fas fa-diagram-project"></i></span><h3>Cross-View Memory</h3>
        <p>A directed memory graph lets each target view condition on generated neighbors for seam-level consistency.</p></div>
    </div>
  </div>
</section>

<!-- CITATION -->
<section class="citation-section" id="citation">
  <div class="container">
    <div class="citation-header">
      <h2 class="section-title citation-title">BibTeX</h2>
      <button class="citation-copy-btn" id="copyBib"><i class="far fa-copy"></i> Copy</button>
    </div>
    <pre class="citation-code" id="bibtex">{html.escape(BIBTEX)}</pre>
  </div>
</section>

<footer class="footer">
  <div class="container">
    <p>OpenLongTail: Generative Scaling of Long-Tail Driving Data. Project page styled after
      <a href="https://mosaicmem.github.io/mosaicmem/" target="_blank">MosaicMem</a>.</p>
  </div>
</footer>

<div class="back-to-top-wrap"><button class="back-to-top" id="backTop">
  <i class="fas fa-arrow-up"></i><span class="back-to-top-label">Back to top</span></button></div>

<script src="assets/js/main.js"></script>
</body>
</html>"""

with open("index.html", "w") as f:
    f.write(HTML)
print("index.html written:", len(HTML), "bytes")
print("gallery cards:", sum(1 for s in SCENES if s[4]), "wild cards:", sum(1 for s in SCENES if not s[4]))
print("mosaic tiles:", len(SCENES) * 5)
