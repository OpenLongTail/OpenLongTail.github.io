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
    ("Hao Wang",       [1],    "https://haohww.github.io/", ""),
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
        ("+ SFT (10K + NV-OOD GT + Waymo-E2E GT)", False, ["0.691","12.5","0.691","0.0","0.735","0.0","0.958","0.0","0.736","5.6"]),
        ("+ SFT (10K + NV-OOD Syn + Waymo-E2E Syn)", True, ["0.699","12.5","0.689","0.0","0.765","0.0","0.950","0.0","0.748","5.6"]),
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

def build_transform(sid="s07"):
    # key, label, role, left%, top%, tx, ty, delay, ray-x2, ray-y2
    P = [
        ("front", "Front · Input", "input", "39.13%", "2.14%", "0px", "120px", ".15s", 460, 78),
        ("cl", "Cross-Left",  "gen", "4.35%",  "20.9%", "188px",  "58px",  ".70s", 150, 178),
        ("cr", "Cross-Right", "gen", "73.9%",  "20.9%", "-188px", "58px",  ".85s", 770, 178),
        ("rl", "Rear-Left",   "gen", "4.35%",  "73.6%", "188px",  "-112px", "1.00s", 150, 462),
        ("rr", "Rear-Right",  "gen", "73.9%",  "73.6%", "-188px", "-112px", "1.15s", 770, 462),
        ("rt", "Rear-Tele",   "gen", "39.13%", "78.9%", "0px",    "-130px", ".90s", 460, 492),
    ]
    # input ray: front view feeds into the core
    rays = '<line class="ray ray-in" x1="460" y1="116" x2="460" y2="234" pathLength="1" style="--d:.35s"/>'
    views = ""
    for key, label, role, left, top, tx, ty, d, cx, cy in P:
        if role == "gen":
            rays += f'<line class="ray" x1="460" y1="280" x2="{cx}" y2="{cy}" pathLength="1" style="--d:{d}"/>'
            src, pos = f"{VID}/{sid}_pred_{key}.mp4", f"{POS}/{sid}_pred_{key}.jpg"
            cls = "stage-view"
        else:
            src, pos = f"{VID}/{sid}_front.mp4", f"{POS}/{sid}_front.jpg"
            cls = "stage-view input"
        views += (f'<div class="{cls}" style="left:{left};top:{top};--tx:{tx};--ty:{ty};--d:{d}">'
                  f'<span class="vtag">{label}</span>'
                  f'<video {v_attrs(src, pos)}></video></div>')
    return f'''<!-- SINGLE -> MULTI STAGE -->
<section class="content-section stage-section" id="expand">
  <div class="container wide">
    <h2 class="section-title">From a Single View to a Full Surround Rig</h2>
    <p class="section-sub">OpenLongTail extrapolates one observed monocular front view into five synchronized
      non-front views under the target camera rig.</p>
    <div class="stage">
      <svg class="stage-rays" viewBox="0 0 920 560" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
        <defs><linearGradient id="rayg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#5aa8ff"/><stop offset="1" stop-color="#f3a3c8"/></linearGradient></defs>
        {rays}
      </svg>
      <div class="stage-core" aria-hidden="true">
        <svg class="car" viewBox="0 0 80 124" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="carbody" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="#1c2738"/><stop offset="1" stop-color="#0b0f17"/></linearGradient>
            <linearGradient id="caredge" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#5aa8ff"/><stop offset="1" stop-color="#f3a3c8"/></linearGradient>
          </defs>
          <rect x="16" y="6" width="48" height="112" rx="20" fill="url(#carbody)" stroke="url(#caredge)" stroke-width="2.2"/>
          <rect x="8" y="40" width="9" height="8" rx="3" fill="url(#carbody)" stroke="url(#caredge)" stroke-width="1.4"/>
          <rect x="63" y="40" width="9" height="8" rx="3" fill="url(#carbody)" stroke="url(#caredge)" stroke-width="1.4"/>
          <path d="M24,41 Q40,31 56,41 L52,53 Q40,48 28,53 Z" fill="rgba(143,196,255,.55)"/>
          <rect x="27" y="55" width="26" height="28" rx="8" fill="rgba(160,200,255,.16)"/>
          <path d="M28,85 Q40,81 52,85 L56,97 Q40,91 24,97 Z" fill="rgba(243,163,200,.5)"/>
          <rect x="22" y="9" width="9" height="5" rx="2.5" fill="#d6ecff"/>
          <rect x="49" y="9" width="9" height="5" rx="2.5" fill="#d6ecff"/>
          <rect x="22" y="110" width="9" height="4" rx="2" fill="#ff9bb0"/>
          <rect x="49" y="110" width="9" height="4" rx="2" fill="#ff9bb0"/>
        </svg>
      </div>
      {views}
    </div>
  </div>
</section>'''

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
<link rel="stylesheet" href="assets/css/index.css?v=12">
</head>
<body>

<nav class="section-nav"><div class="section-nav-inner">
  <a class="section-nav-link" href="#abstract">Abstract</a>
  <a class="section-nav-link" href="#expand">Single &rarr; Multi</a>
  <a class="section-nav-link" href="#gallery">Multi-View Gallery</a>
  <a class="section-nav-link" href="#eval">Evaluation</a>
  <a class="section-nav-link" href="#external">Cross-Source Scaling</a>
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
        OpenLongTail is an <span class="tldr-emphasis">open-scaling generative data engine</span> that converts heterogeneous
        long-tail driving videos into <span class="tldr-emphasis">pose-grounded, multi-view data</span>, enabling scalable
        VLA policy learning from heterogeneous sources.</p>
    </div>
    <div class="abstract-centered-text">
      <p class="content-text">Scaling robust driving policies is fundamentally bottlenecked by the scarcity of edge cases
        in curated datasets. While the real world continuously captures these critical events, such long-tail events remain
        underutilized when collected from heterogeneous sources. Specifically, diverse but valuable in-the-wild long-tail
        videos lack the full view coverage required for training policy models, often missing multi-view poses or originating
        solely from monocular dash cameras. This modality gap prevents these observations from being converted into scalable
        training data for long-tail generalization. We introduce <b>OpenLongTail</b>, an open-source generative data engine for
        scaling autonomous driving policies under long-tail events. To transform heterogeneous data sources into view-aligned
        and temporally coherent multi-view assets that are useful for policy learning, we develop a pose-informed extrapolative
        view synthesis pipeline that generates the missing context. We further enhance cross-view consistency and the temporal
        alignment for the newly generated views by injecting Pl&uuml;cker ray geometry into the scalable generation engine. By
        synthesizing heterogeneous long-tail data, we observe a significant improvement in closed-loop driving robustness in
        handling long-tail events. By measuring the extrapolative view synthesis and pose metrics, we validate the effectiveness
        of OpenLongTail in visual fidelity, cross-view consistency, and ego-trajectory recovery.</p>
    </div>
  </div>
</section>

{build_transform()}

<!-- GALLERY -->
<section class="content-section alt" id="gallery">
  <div class="container wide">
    <h2 class="section-title">Multi-View Generation Gallery</h2>
    <p class="section-sub">From an observed front-view video, OpenLongTail synthesizes five non-front views under a target camera rig.
      Toggle each card between <b>Generated</b> and <b>Ground&nbsp;Truth</b>. The front input view is always the original observation.</p>
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
    <h2 class="section-title">OpenLongTail Improves VLA Driving Policies</h2>
    <p class="section-subtitle">Closed-Loop Evaluation in AlpaSim</p>
    <p class="section-sub">Fine-tuning Alpamayo-R1 with OpenLongTail-synthesized multi-view data improves closed-loop
      driving robustness on 53 long-tail events, on par with training on ground-truth multi-camera capture.
      AS = AlpaSim Score (higher is better); CR = Collision Rate (lower is better).</p>
    {build_eval_table()}
    <p class="fig-caption">OpenLongTail-synthesized data (<b>Ours</b>) lifts average AS to 0.748 and reduces the collision rate
      to 0.0%, comparable to training on ground-truth multi-view data (0.764 AS).
      <br><span style="opacity:.8">SFT: supervised fine-tuning &nbsp;&middot;&nbsp; 10K Rand: 10K randomly sampled trajectories &nbsp;&middot;&nbsp;
      NV-OOD: NVIDIA PAV out-of-distribution subset &nbsp;&middot;&nbsp; GT: ground-truth multi-view &nbsp;&middot;&nbsp;
      Syn: OpenLongTail-synthesized multi-view.</span></p>
  </div>
</section>

<!-- CROSS-SOURCE SCALING -->
<section class="content-section alt" id="external">
  <div class="container wide">
    <h2 class="section-title">Generative Scaling Across Diverse Sources</h2>
    <p class="section-sub">OpenLongTail converts external monocular videos (e.g., Waymo E2E) into target-rig
      multi-view assets, expanding the long-tail training pool. Combining in-house (NVIDIA PAV) and external
      synthesized data yields more scene-consistent closed-loop rollouts across uncommon vehicles, cyclists,
      and complex intersections.</p>
    <img class="method-image" src="assets/img/external_waymo.png" alt="Closed-loop benefits of generative scaling across sources">
    <p class="fig-caption">Closed-loop bird's-eye-view rollouts of Alpamayo-R1 versus variants fine-tuned with
      OpenLongTail-synthesized assets from NVIDIA PAV data and from PAV combined with an external source (Waymo E2E).
      Generative scaling expands useful long-tail coverage rather than merely increasing the number of training samples.</p>
  </div>
</section>

<!-- METHOD -->
<section class="content-section" id="method">
  <div class="container">
    <h2 class="section-title">Method Overview</h2>
    <img class="method-image" src="assets/img/pipeline.png?v=6" alt="OpenLongTail pipeline overview">
    <p class="fig-caption">Given a long-tail front-view driving video, OpenLongTail first recovers a motion-consistent metric
      ego-trajectory and uses it to construct pose-aware geometric conditions. The generation model combines Pl&uuml;cker-ray
      geometry, temporal depth warping, and a cross-view memory bank within a Wan&nbsp;2.1-VACE backbone to synthesize
      synchronized non-front views under the target camera rig.</p>
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

<script src="assets/js/main.js?v=12"></script>
</body>
</html>"""

with open("index.html", "w") as f:
    f.write(HTML)
print("index.html written:", len(HTML), "bytes")
print("gallery cards:", sum(1 for s in SCENES if s[4]), "wild cards:", sum(1 for s in SCENES if not s[4]))
print("mosaic tiles:", len(SCENES) * 5)
