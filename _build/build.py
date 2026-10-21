#!/usr/bin/env python3
"""Work.Style static site generator. Run: python3 _build/build.py  (from repo root)
Outputs plain HTML files to the repo root so GitHub Pages (free plan) can serve them as-is."""
import json, os, re, html, datetime
import markdown
from styles_data import STYLES, PLACES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://work.style"
TODAY = datetime.date.today().isoformat()
ADS = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6620975821265271" crossorigin="anonymous"></script>'
OWNER = "https://web.works/contact"
PAGES = []  # for sitemap

LOGO = ('<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="2" y="2" width="36" height="36" rx="10" fill="#172033"/>'
        '<path d="M9 13l4.5 14L18 16l4.5 11L27 13" fill="none" stroke="#F6F7F4" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="31.5" cy="27" r="3" fill="#E8B531"/></svg>')

NAV = [("quiz.html", "Assessment"), ("styles/", "Work styles"), ("tools/", "Tools"), ("guides/", "Guides"),
       ("videos.html", "Videos"), ("teams.html", "For teams"), ("contests.html", "Contests"), ("support.html", "Support")]


def esc(s):
    return html.escape(s, quote=True)


LAYOUT_WRITTEN = [False]


def nav_html():
    out = []
    for href, label in NAV:
        out.append('<a href="{{ page.pre }}%s"{%% if page.nav_key == "%s" %%} aria-current="page"{%% endif %%}>%s</a>' % (href, href, label))
    return "".join(out)


def write_layout():
    pre = "{{ page.pre }}"
    lay = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{{{{ page.basetag }}}}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{{{ page.full_title | escape }}}}</title>
<meta name="description" content="{{{{ page.description | escape }}}}">
<link rel="canonical" href="{{{{ page.canon }}}}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Work.Style">
<meta property="og:title" content="{{{{ page.full_title | escape }}}}">
<meta property="og:description" content="{{{{ page.description | escape }}}}">
<meta property="og:url" content="{{{{ page.canon }}}}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#172033">
<meta name="google-adsense-account" content="ca-pub-6620975821265271">
<link rel="icon" href="{pre}assets/img/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{pre}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Public+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}assets/css/style.css">
{ADS}
{{{{ page.jsonld }}}}
{{{{ page.extra_head }}}}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="owner-strip">Contact, if you are interested in this website / domain name / Sponsorship / Advertisement / Partnership — <a href="{OWNER}" target="_blank" rel="noopener">contact here</a></div>
<header class="site-head">
 <div class="wrap head-row">
  <a class="brand" href="{pre}index.html" aria-label="Work.Style home">{LOGO}<span>Work<span class="dot">.</span>Style</span></a>
  <button class="icon-btn menu-btn" aria-expanded="false" aria-controls="nav" aria-label="Open menu"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>
  <nav class="nav" id="nav" aria-label="Main">{nav_html()}<a class="btn small pencil" href="{pre}quiz.html">Find my style</a>
   <button class="icon-btn" data-theme-toggle aria-label="Switch light or dark theme"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
  </nav>
 </div>
</header>
<main id="main">
{{{{ content }}}}
</main>
{footer(pre)}
<div class="consent" id="consent" hidden role="dialog" aria-label="Cookie notice">
 <p>We use cookies to run this site and, with Google AdSense, to show ads. You can accept personalized ads or limit cookies to essential ones and see non-personalized ads. Read our <a href="{pre}privacy.html">privacy policy</a>.</p>
 <div class="acts"><button class="btn small" data-consent="all">Accept all</button><button class="btn small alt" data-consent="essential">Essential only</button></div>
</div>
<script src="{pre}assets/js/config.js"></script>
<script src="{pre}assets/js/styles-data.js"></script>
<script src="{pre}assets/js/main.js"></script>
{{{{ page.scripts }}}}
</body>
</html>
"""
    os.makedirs(os.path.join(ROOT, "_layouts"), exist_ok=True)
    open(os.path.join(ROOT, "_layouts/default.html"), "w").write(lay)


def page(path, title, desc, body, extra_head="", scripts="", jsonld=None, nav_key=None, dynbase=False):
    depth = path.count("/")
    pre = "../" * depth
    canon = BASE_URL + "/" + (path[:-10] if path.endswith("index.html") else path)
    full_title = title if "Work.Style" in title else f"{title} | Work.Style"
    basetag = ("<script>document.write('<base href=\"'+(location.pathname.indexOf('/work-style/')===0?'/work-style/':'/')+'\">')</script>") if dynbase else ""
    ld = ('<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>") if jsonld else ""
    fm = {"layout": "default", "full_title": full_title, "description": desc, "canon": canon, "pre": pre,
          "nav_key": nav_key or "", "jsonld": ld, "extra_head": extra_head, "scripts": scripts, "basetag": basetag}
    head = "---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fm.items()) + "---\n"
    if "{{" in body or "{%" in body:
        raise SystemExit("Liquid-like syntax in body of " + path)
    dest = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(head + body.strip() + "\n")
    if path not in ("404.html", "thank-you.html"):
        PAGES.append(canon)


def footer(pre):
    return f"""<footer class="site-foot">
 <div class="wrap">
  <div class="foot-grid">
   <div>
    <a class="brand" href="{pre}index.html" style="color:#fff">{LOGO}<span>Work<span class="dot">.</span>Style</span></a>
    <p style="margin-top:14px">Find how you work best — then build the days, desk and team around it.</p>
    <form class="form" data-form="Newsletter signup" data-ok="You're on the list. The next issue lands Thursday." style="margin-top:14px">
     <label for="nl-email" style="color:#fff">The Thursday note: one work-style idea a week</label>
     <div class="hp"><label>Leave empty<input name="_hp" tabindex="-1" autocomplete="off"></label></div>
     <input id="nl-email" type="email" name="email" placeholder="you@company.com" required autocomplete="email">
     <select name="work_model" aria-label="How do you work now?"><option value="">How do you work now? (optional)</option><option>Remote</option><option>Hybrid</option><option>Office</option><option>Freelance / self-employed</option></select>
     <button class="btn pencil" type="submit">Subscribe</button>
     <p class="form-status" aria-live="polite"></p>
    </form>
   </div>
   <div><h4>Explore</h4><ul>
    <li><a href="{pre}quiz.html">Work Style Assessment</a></li><li><a href="{pre}styles/">The 8 work styles</a></li>
    <li><a href="{pre}tools/">Free tools</a></li><li><a href="{pre}guides/">Guides</a></li><li><a href="{pre}videos.html">Videos</a></li></ul></div>
   <div><h4>Get involved</h4><ul>
    <li><a href="{pre}teams.html">Team assessments</a></li><li><a href="{pre}contests.html">Contests &amp; prizes</a></li>
    <li><a href="{pre}support.html">Support Work.Style</a></li><li><a href="{pre}careers.html">Write or work with us</a></li>
    <li><a href="{pre}advertise.html">Advertise &amp; sponsor</a></li></ul></div>
   <div><h4>About</h4><ul>
    <li><a href="{pre}about.html">About &amp; methodology</a></li><li><a href="{pre}contact.html">Contact</a></li>
    <li><a href="{pre}privacy.html">Privacy &amp; cookies</a></li><li><a href="{pre}terms.html">Terms of use</a></li>
    <li><a href="{pre}disclaimer.html">Disclaimer</a></li><li><a href="{pre}trademark.html">Trademark &amp; copyright</a></li>
    <li><a href="{pre}sitemap.html">Site map</a></li></ul></div>
  </div>
  <div class="foot-legal">
   <p>© <span data-year>{datetime.date.today().year}</span> Work.Style. All original content, assessment items, tools and archetype descriptions on this site are protected by copyright.</p>
   <p>Trademark notice: "Work.Style" is the name of this independent website. It is not affiliated with, endorsed by or connected to any company, product or service that uses "Workstyle", "Work Style" or similar names or marks. All third-party names and marks belong to their respective owners. <a href="{pre}trademark.html">Full disclosure</a>.</p>
   <p>The Work Style Assessment is for self-reflection and education. It is not a psychological, medical or hiring instrument. Ads on this site are served by Google AdSense.</p>
  </div>
 </div>
</footer>"""


def form_status():
    return '<p class="form-status" aria-live="polite"></p>'


def hp():
    return '<div class="hp"><label>Leave empty<input name="_hp" tabindex="-1" autocomplete="off"></label></div>'


# ---------------------------------------------------------------- data JS
QUESTIONS = [
 # axis, text, dir  (+1 = agreeing pushes toward sprint / social / flexible / office)
 ("focus", "I do my best work in long, uninterrupted blocks of two hours or more.", -1),
 ("focus", "I like switching between several small tasks during the day.", 1),
 ("focus", "Being interrupted while I'm concentrating really throws me off.", -1),
 ("focus", "I get more done in short, intense bursts than in long sessions.", 1),
 ("focus", "A day with lots of variety energizes me more than a day on one problem.", 1),
 ("energy", "I prefer to think through a problem on my own before discussing it.", -1),
 ("energy", "Talking ideas out loud with others helps me think more clearly.", 1),
 ("energy", "After a day full of meetings, I need quiet time to recharge.", -1),
 ("energy", "I'd rather work on a shared project than own a project by myself.", 1),
 ("energy", "I feel more motivated when I can see and hear my teammates working.", 1),
 ("structure", "I like to have a clear plan before I start a project.", -1),
 ("structure", "I'm comfortable starting before I know exactly how I'll finish.", 1),
 ("structure", "Last-minute changes to my schedule stress me out.", -1),
 ("structure", "I'd rather have goals and freedom than step-by-step instructions.", 1),
 ("structure", "I keep a detailed to-do list or calendar and follow it closely.", -1),
 ("place", "I'm more productive at home than in an office.", -1),
 ("place", "I miss the casual conversations of a shared workplace when I'm away from it.", 1),
 ("place", "A commute is a price I'm willing to pay to see colleagues in person.", 1),
 ("place", "I can easily create a distraction-free space where I live.", -1),
 ("place", "Being physically with my team helps me feel I belong.", 1),
]


def write_data_js():
    data = {s["slug"]: {k: s[k] for k in ("slug", "code", "name", "short", "focus", "energy", "structure", "strengths", "watch", "env", "methods", "best_with", "place")} for s in STYLES}
    js = "window.WS_STYLES=" + json.dumps(data, ensure_ascii=False) + ";\n"
    js += "window.WS_Q=" + json.dumps([{"a": a, "t": t, "d": d} for a, t, d in QUESTIONS]) + ";\n"
    js += """window.WS_pick=function(f,e,s){var F=f>=50?"sprint":"deep",E=e>=50?"social":"solo",S=s>=50?"improviser":"planner";
for(var k in window.WS_STYLES){var x=window.WS_STYLES[k];if(x.focus===F&&x.energy===E&&x.structure===S)return x;}};
window.WS_place=function(p){return p<34?"Best fit: remote-first":p<67?"Best fit: hybrid":"Best fit: office-first";};
"""
    with open(os.path.join(ROOT, "assets/js/styles-data.js"), "w") as f:
        f.write(js)


# ---------------------------------------------------------------- guides
def load_guides():
    gdir = os.path.join(ROOT, "_build/guides")
    out = []
    for fn in sorted(os.listdir(gdir)):
        raw = open(os.path.join(gdir, fn), encoding="utf-8").read()
        head, body = raw.split("\n---\n", 1)
        meta = dict(l.split(": ", 1) for l in head.strip().splitlines())
        meta["slug"] = fn[:-3]
        meta["md"] = body
        out.append(meta)
    order = ["remote-work-guide", "productivity-methods", "hybrid-work-schedule", "home-office-setup", "team-work-styles",
             "async-communication", "four-day-work-week", "work-life-boundaries", "meeting-hygiene", "digital-nomad-basics"]
    out.sort(key=lambda g: order.index(g["slug"]) if g["slug"] in order else 99)
    return out


GUIDES = []


def md(text):
    # simple task-list checkboxes
    text = text.replace("- [ ] ", "- ☐ ")
    h = markdown.markdown(text, extensions=["tables", "toc", "sane_lists"])
    return h


def aside(pre, slug=None):
    rel = [g for g in GUIDES if g["slug"] != slug][:4]
    items = "".join(f'<li><a href="{pre}guides/{g["slug"]}.html">{esc(g["title"])}</a></li>' for g in rel)
    return f"""<aside class="article-aside">
 <div class="panel pencil"><h3>What's your work style?</h3><p>Twenty questions, about five minutes, and you'll know which setup, schedule and methods fit you.</p><a class="btn" href="{pre}quiz.html">Take the assessment</a></div>
 <div class="panel"><h3>Bring it to your team</h3><p>Map every person's style on one page and fix the friction before it starts.</p><a href="{pre}teams.html">Get a team report</a></div>
 <div class="panel"><h3>Keep reading</h3><ul style="padding-left:1.1em;margin:0">{items}</ul></div>
</aside>"""


def build_guides():
    for g in GUIDES:
        body_html = md(g["md"])
        heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body_html)
        toc = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in heads)
        body = f"""<div class="wrap page-head">
 <p class="crumbs"><a href="../index.html">Home</a> / <a href="index.html">Guides</a> / {esc(g['category'])}</p>
 <h1 style="max-width:20ch">{esc(g['title'])}</h1>
 <p class="lede">{esc(g['desc'])}</p>
 <p class="byline">By the Work.Style editorial team · {g['read']} min read · Updated {datetime.date.today().strftime('%B %Y')}</p>
</div>
<div class="wrap article-layout" style="padding-bottom:40px">
 <article class="article">
  <details class="toc panel" style="padding:14px 18px;margin-bottom:24px"><summary>In this guide</summary><ol>{toc}</ol></details>
  {body_html}
  <div class="panel teal" style="margin-top:36px"><h3>Was this useful?</h3><p>Work.Style is independent and free. If this guide saved you time, you can <a href="../support.html">support the site</a> or <a href="../contests.html">enter this month's contest</a>.</p></div>
 </article>
 {aside('../', g['slug'])}
</div>"""
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
              "dateModified": TODAY, "author": {"@type": "Organization", "name": "Work.Style"},
              "publisher": {"@type": "Organization", "name": "Work.Style"}, "mainEntityOfPage": f"{BASE_URL}/guides/{g['slug']}.html"}
        page(f"guides/{g['slug']}.html", g["title"], g["desc"], body, jsonld=ld, nav_key="guides/")
    items = "".join(f"""<li><a href="{g['slug']}.html"><div><h3>{esc(g['title'])}</h3><p>{esc(g['desc'])}</p></div><span class="meta">{esc(g['category'])}, {g['read']} min</span></a></li>""" for g in GUIDES)
    body = f"""<div class="wrap page-head"><h1>Guides</h1><p class="lede">Practical, plain-language playbooks for remote, hybrid and office work — setups, schedules, methods and team habits.</p></div>
<div class="wrap" style="padding-bottom:40px"><ul class="guide-list">{items}</ul></div>"""
    page("guides/index.html", "Work Guides: Remote, Hybrid, Productivity and Teams", "Practical guides to remote work, hybrid schedules, home-office setup, productivity methods and managing teams with different work styles.", body, nav_key="guides/")


# ---------------------------------------------------------------- styles pages
def style_axes(s):
    f = "Deep focus" if s["focus"] == "deep" else "Quick sprints"
    e = "Independent" if s["energy"] == "solo" else "Collaborative"
    st = "Planned" if s["structure"] == "planner" else "Flexible"
    return f, e, st


def build_styles():
    for s in STYLES:
        f, e, st = style_axes(s)
        li = lambda xs: "".join(f"<li>{esc(x)}</li>" for x in xs)
        others = "".join(f'<a href="{o["slug"]}.html"><span class="style-code">{o["code"]}</span><strong>{o["name"]}</strong><span>{esc(o["short"])}</span></a>' for o in STYLES)
        body = f"""<div class="wrap page-head">
 <p class="crumbs"><a href="../index.html">Home</a> / <a href="index.html">Work styles</a> / {s['name']}</p>
 <h1>{s['name']}</h1>
 <p class="lede">{esc(s['short'])}</p>
 <p><span class="pill">{f}</span><span class="pill">{e}</span><span class="pill">{st}</span><span class="place-tag">{PLACES[s['place']]}</span></p>
</div>
<div class="wrap article-layout" style="padding-bottom:30px">
 <article class="article">
  <p>{esc(s['summary'])}</p>
  <h2>Strengths</h2><ul>{li(s['strengths'])}</ul>
  <h2>Watch-outs</h2><ul>{li(s['watch'])}</ul>
  <h2>Where you work best</h2><p>{esc(s['env'])}</p>
  <h2>A day that fits {s['name'].replace('The ', 'the ')}</h2><ol>{li(s['day'])}</ol>
  <h2>Tools and habits that help</h2><ul>{li(s['tools'])}</ul>
  <h2>Productivity methods to try</h2><p>{', '.join(s['methods'])}. Read how each works in <a href="../guides/productivity-methods.html">9 productivity methods</a>.</p>
  <h2>Works well with</h2><p>{esc(s['best_with'])}</p>
  <p class="form-note">Work styles describe preferences, not abilities. Most people use more than one style depending on the task.</p>
 </article>
 {aside('../')}
</div>
<section class="band"><div class="wrap"><div class="section-head"><h2>All eight work styles</h2></div><div class="style-grid">{others}</div></div></section>"""
        page(f"styles/{s['slug']}.html", f"{s['name']} Work Style: Strengths, Ideal Setup and Daily Routine",
             f"{s['short']} Strengths, watch-outs, ideal environment, daily routine and productivity methods for {s['name']}.", body, nav_key="styles/")
    grid = "".join(f'<a href="{o["slug"]}.html"><span class="style-code">{o["code"]}</span><strong>{o["name"]}</strong><span>{esc(o["short"])}</span></a>' for o in STYLES)
    body = f"""<div class="wrap page-head"><h1>The eight work styles</h1><p class="lede">Three questions decide most of how you work: do you go deep or move fast, work alone or together, plan first or start first? Every combination is a style.</p></div>
<div class="wrap"><div class="style-grid">{grid}</div>
<div class="grid-3" style="margin:34px 0 50px">
 <div class="panel"><h3>Deep ↔ Sprint</h3><p>Long uninterrupted focus, or short intense bursts with variety.</p></div>
 <div class="panel"><h3>Independent ↔ Collaborative</h3><p>Thinking alone first, or thinking out loud with others.</p></div>
 <div class="panel"><h3>Planned ↔ Flexible</h3><p>A clear plan before starting, or finding the path as you go.</p></div>
</div>
<p class="center" style="margin-bottom:50px"><a class="btn pencil" href="../quiz.html">Find out which one you are</a></p></div>"""
    page("styles/index.html", "The 8 Work Styles", "The eight Work.Style archetypes — Cartographer, Tinkerer, Mentor, Collaborator, Sprinter, Scout, Coordinator and Catalyst — explained.", body, nav_key="styles/")


# ---------------------------------------------------------------- videos
VIDEOS = [
 ("5XD2kNopsUs", "Why work doesn't happen at work", "Jason Fried, TED", "Remote & focus"),
 ("arj7oStGLkU", "Inside the mind of a master procrastinator", "Tim Urban, TED", "Productivity"),
 ("rrkrvAUbU9Y", "The puzzle of motivation", "Dan Pink, TED", "Motivation"),
 ("c0KYU2j0TM4", "The power of introverts", "Susan Cain, TED", "Work styles"),
 ("fLJsdqxnZb0", "The happy secret to better work", "Shawn Achor, TED", "Wellbeing"),
 ("Vyn_xLrtZaY", "Forget the pecking order at work", "Margaret Heffernan, TED", "Teams"),
 ("R1vskiVDwl4", "10 ways to have a better conversation", "Celeste Headlee, TED", "Communication"),
 ("fxbCHn6gE3U", "The surprising habits of original thinkers", "Adam Grant, TED", "Creativity"),
 ("3E7hkPZ-HTk", "Quit social media", "Cal Newport, TEDxTysons", "Deep work"),
 ("5MuIMqhT8DM", "Sleep is your superpower", "Matt Walker, TED", "Wellbeing"),
 ("H14bBuluwB8", "Grit: the power of passion and perseverance", "Angela Lee Duckworth, TED", "Motivation"),
 ("qp0HIF3SfI4", "How great leaders inspire action", "Simon Sinek, TED", "Leadership"),
]


def video_cards(vs, pre=""):
    return "".join(f"""<div class="video"><div class="frame"><button data-yt="{v}" aria-label="Play: {esc(t)}"><span>Play video</span></button></div>
<div class="cap"><strong>{esc(t)}</strong><small>{esc(a)} · {esc(c)}</small></div></div>""" for v, t, a, c in vs)


def build_videos():
    body = f"""<div class="wrap page-head"><h1>Videos on how we work</h1><p class="lede">Twelve talks worth your time on focus, motivation, teams and wellbeing. Videos are embedded from YouTube and only load when you press play.</p></div>
<div class="wrap" style="padding-bottom:30px"><div class="video-grid">{video_cards(VIDEOS)}</div>
<div class="panel pencil" style="margin-top:34px"><h3>Make a video with us</h3><p>Creators who make videos about remote work, productivity or workplace culture can apply to be featured or join paid collaborations. <a href="careers.html">Apply as a creator</a>.</p></div></div>"""
    page("videos.html", "Videos on Focus, Productivity and Teams", "A curated library of talks on deep work, motivation, procrastination, introverts at work, team culture and wellbeing.", body, nav_key="videos.html")


# ---------------------------------------------------------------- home
def build_home():
    grid = "".join(f'<a href="styles/{o["slug"]}.html"><span class="style-code">{o["code"]}</span><strong>{o["name"]}</strong><span>{esc(o["short"])}</span></a>' for o in STYLES)
    g = GUIDES[:6]
    guides = "".join(f"""<li><a href="guides/{x['slug']}.html"><div><h3>{esc(x['title'])}</h3><p>{esc(x['desc'])}</p></div><span class="meta">{x['read']} min</span></a></li>""" for x in g)
    body = f"""<section class="hero"><div class="wrap hero-grid">
 <div>
  <h1>Work the way you actually work best.</h1>
  <p class="lede">Some people need four quiet hours. Some need a whiteboard and three colleagues. Find your work style, then build your schedule, desk and team habits around it.</p>
  <div class="hero-actions"><a class="btn pencil" href="quiz.html">Take the free assessment</a><a class="btn alt" href="teams.html">Assess my team</a></div>
  <p class="hero-proof">20 questions, about 5 minutes, no sign-up needed.</p>
 </div>
 <div class="dial" id="dial">
  <h2>Quick read: slide to where you sit</h2>
  <p class="hint">A rough preview. The full assessment is more accurate.</p>
  <div class="axis"><div class="axis-labels"><span>Long deep focus</span><span>Quick bursts</span></div><input type="range" name="focus" min="0" max="100" value="30" aria-label="Deep focus to quick bursts"></div>
  <div class="axis"><div class="axis-labels"><span>Work alone</span><span>Work together</span></div><input type="range" name="energy" min="0" max="100" value="35" aria-label="Alone to together"></div>
  <div class="axis"><div class="axis-labels"><span>Plan first</span><span>Start first</span></div><input type="range" name="structure" min="0" max="100" value="40" aria-label="Plan first to start first"></div>
  <div class="axis"><div class="axis-labels"><span>Home</span><span>Office</span></div><input type="range" name="place" min="0" max="100" value="45" aria-label="Home to office"></div>
  <div class="dial-out" aria-live="polite"><p class="name" id="dial-name">The Cartographer</p><p id="dial-desc"></p><span class="place-tag" id="dial-place"></span> <a id="dial-link" href="styles/cartographer.html" style="margin-left:8px">Read this profile</a></div>
 </div>
</div></section>

<section class="band"><div class="wrap">
 <div class="section-head"><div><h2>Eight ways people work</h2><p>Three trade-offs — deep or fast, alone or together, planned or flexible — combine into eight styles. Each has its own best setup.</p></div><a class="btn alt small" href="styles/">Compare all styles</a></div>
 <div class="style-grid">{grid}</div>
</div></section>

<section><div class="wrap">
 <div class="section-head"><div><h2>Free tools for better workdays</h2><p>No sign-up, nothing stored. Run them in your browser.</p></div></div>
 <div class="tool-row">
  <a class="tile feature" href="tools/meeting-cost.html"><h3>Meeting cost calculator</h3><p>Put a price on that weekly status meeting. Most teams cut one recurring meeting after running it.</p><span class="go">Calculate a meeting</span></a>
  <a class="tile" href="tools/focus-timer.html"><h3>Focus timer</h3><p>Pomodoro, 50/10 or a custom deep-work block.</p><span class="go">Start a session</span></a>
  <a class="tile yellow" href="tools/commute-savings.html"><h3>Commute savings</h3><p>Hours and money a remote day gives back.</p><span class="go">Run the numbers</span></a>
 </div>
 <div class="tool-row b">
  <a class="tile" href="tools/desk-setup.html"><h3>Desk height</h3><p>Chair, desk and screen heights for your height.</p><span class="go">Set up my desk</span></a>
  <a class="tile" href="tools/freelance-rate.html"><h3>Freelance rate</h3><p>The hourly rate that covers your costs and time off.</p><span class="go">Find my rate</span></a>
  <a class="tile yellow" href="tools/hybrid-planner.html"><h3>Hybrid week planner</h3><p>Tap each weekday to mark it home or office. See your commute load and the balance between collaboration and focus days.</p><span class="go">Plan my week</span></a>
 </div>
</div></section>

<section class="band"><div class="wrap">
 <div class="section-head"><div><h2>Guides</h2><p>Plain-language playbooks you can use today.</p></div><a class="btn alt small" href="guides/">All guides</a></div>
 <ul class="guide-list">{guides}</ul>
</div></section>

<section class="band-ink"><div class="wrap grid-2" style="align-items:center">
 <div>
  <h2>Your team has four work styles and one calendar.</h2>
  <p>That's where most friction comes from. A Work.Style team report maps every person on one page and gives you a meeting rhythm, hybrid schedule and pairing plan that fits all of them.</p>
  <div class="stat-row"><div><strong>1 page</strong><span>whole-team map</span></div><div><strong>90 min</strong><span>optional workshop</span></div><div><strong>48 h</strong><span>reply time</span></div></div>
 </div>
 <div class="panel" style="color:var(--ink)">
  <h3 class="mt0">Get a team report</h3>
  <form class="form" data-form="Team report request (home)" data-redirect="thank-you.html">
   {hp()}
   <div><label for="h-name">Your name</label><input id="h-name" name="name" type="text" required autocomplete="name"></div>
   <div><label for="h-email">Work email</label><input id="h-email" name="email" type="email" required autocomplete="email"></div>
   <div><label for="h-size">Team size</label><select id="h-size" name="team_size" required><option value="">Choose one</option><option>2–5</option><option>6–15</option><option>16–50</option><option>51–200</option><option>200+</option></select></div>
   <button class="btn teal" type="submit">Request my team report</button>{form_status()}
   <p class="form-note">We reply within two business days. No spam, ever.</p>
  </form>
 </div>
</div></section>

<section><div class="wrap">
 <div class="section-head"><div><h2>Watch</h2><p>Short talks on focus, motivation and teams.</p></div><a class="btn alt small" href="videos.html">All videos</a></div>
 <div class="video-grid">{video_cards(VIDEOS[:3])}</div>
</div></section>

<section class="band"><div class="wrap grid-3">
 <div class="panel pencil"><h3>Show Your Setup contest</h3><p>Send a photo of your workspace and the story behind it. Monthly winners get a featured profile and a prize.</p><a href="contests.html">Enter the contest</a></div>
 <div class="panel"><h3>Keep Work.Style free</h3><p>No paywalls, no account required. Reader support pays for new tools and guides.</p><a href="support.html">Support the site</a></div>
 <div class="panel teal"><h3>Write, film or coach with us</h3><p>We're looking for writers, video creators, workplace coaches and community ambassadors.</p><a href="careers.html">See open roles</a></div>
</div></section>"""
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Work.Style", "url": BASE_URL + "/",
          "description": "Find your work style and build better workdays: free assessment, tools and guides for remote, hybrid and office work."}
    page("index.html", "Work.Style — Find Your Work Style and Build Better Workdays",
         "Take the free Work Style Assessment, discover which of eight work styles fits you, and use free tools and guides for remote, hybrid and office work.", body, jsonld=ld)


# ---------------------------------------------------------------- quiz
QUIZ_JS = r"""<script>
(function(){
 var Q=window.WS_Q, box=document.getElementById("qs"), bar=document.getElementById("qbar"), cnt=document.getElementById("qcount");
 var labels=["Strongly disagree","Disagree","Neutral","Agree","Strongly agree"];
 Q.forEach(function(q,i){
  var d=document.createElement("fieldset");d.className="q";d.style.border="1px solid var(--line)";
  var h='<legend class="visually-hidden">Question '+(i+1)+'</legend><p>'+(i+1)+'. '+q.t+'</p><div class="scale">';
  labels.forEach(function(l,j){h+='<label><input type="radio" name="q'+i+'" value="'+(j-2)+'" required> '+l+'</label>';});
  d.innerHTML=h+'</div>';box.appendChild(d);
 });
 function prog(){var n=box.querySelectorAll("input:checked").length;bar.style.width=(n/Q.length*100)+"%";cnt.textContent=n+" of "+Q.length+" answered";}
 box.addEventListener("change",prog);prog();
 function score(vals){var t={focus:0,energy:0,structure:0,place:0},m={focus:0,energy:0,structure:0,place:0};
  Q.forEach(function(q,i){t[q.a]+=vals[i]*q.d;m[q.a]+=2;});
  var o={};for(var k in t)o[k]=Math.round((t[k]+m[k])/(2*m[k])*100);return o;}
 function show(o){
  var st=window.WS_pick(o.focus,o.energy,o.structure), r=document.getElementById("result");
  document.getElementById("r-name").textContent=st.name;
  document.getElementById("r-short").textContent=st.short;
  document.getElementById("r-place").textContent=window.WS_place(o.place);
  document.getElementById("r-link").href="styles/"+st.slug+".html";
  var axes=[["focus","Deep focus","Quick sprints"],["energy","Independent","Collaborative"],["structure","Planned","Flexible"],["place","Home","Office"]];
  document.getElementById("r-bars").innerHTML=axes.map(function(a){return '<div class="rb"><div class="ends"><span>'+a[1]+'</span><span>'+a[2]+'</span></div><div class="track" role="img" aria-label="'+a[1]+' to '+a[2]+': '+o[a[0]]+' of 100"><i style="left:'+o[a[0]]+'%"></i></div></div>';}).join("");
  document.getElementById("r-str").innerHTML=st.strengths.map(function(x){return "<li>"+x+"</li>"}).join("");
  document.getElementById("r-watch").innerHTML=st.watch.map(function(x){return "<li>"+x+"</li>"}).join("");
  document.getElementById("r-env").textContent=st.env;
  document.getElementById("r-methods").textContent=st.methods.join(", ");
  var code=[o.focus,o.energy,o.structure,o.place].join("-");
  var url=location.origin+location.pathname+"#r="+code;
  document.getElementById("r-share").value=url;
  var rf=document.getElementById("report-form");rf._extra=function(){return {result:st.name+" ("+code+")",place:window.WS_place(o.place)};};
  r.hidden=false;document.getElementById("quiz-form").hidden=true;r.scrollIntoView({behavior:"smooth"});
  history.replaceState(null,"","#r="+code);
 }
 document.getElementById("quiz-form").addEventListener("submit",function(e){
  e.preventDefault();var vals=[],miss=-1;
  Q.forEach(function(q,i){var c=box.querySelector('input[name=q'+i+']:checked');if(!c&&miss<0)miss=i;vals.push(c?+c.value:0);});
  if(miss>=0){var el=box.querySelectorAll(".q")[miss];el.scrollIntoView({behavior:"smooth",block:"center"});el.querySelector("input").focus();document.getElementById("qmiss").textContent="Question "+(miss+1)+" still needs an answer.";return;}
  show(score(vals));
 });
 document.getElementById("r-copy").addEventListener("click",function(){var i=document.getElementById("r-share");i.select();try{navigator.clipboard.writeText(i.value);}catch(e){document.execCommand("copy");}this.textContent="Link copied";});
 document.getElementById("r-again").addEventListener("click",function(){history.replaceState(null,"",location.pathname);location.reload();});
 var m=location.hash.match(/r=(\d+)-(\d+)-(\d+)-(\d+)/);
 if(m)show({focus:+m[1],energy:+m[2],structure:+m[3],place:+m[4]});
})();
</script>"""


def build_quiz():
    body = f"""<div class="wrap page-head"><h1>The Work Style Assessment</h1>
<p class="lede">Twenty statements. For each one, choose how much it sounds like you at work. There are no right answers — and no sign-up.</p></div>
<div class="wrap" style="padding-bottom:40px">
 <form id="quiz-form" class="quiz" novalidate>
  <div class="progress"><div class="bar"><i id="qbar"></i></div><p class="form-note" id="qcount" style="margin:6px 0 0"></p></div>
  <div id="qs"></div>
  <p class="form-status err" id="qmiss" aria-live="polite"></p>
  <button class="btn pencil" type="submit">See my work style</button>
 </form>
 <div id="result" hidden class="quiz">
  <p class="form-note">Your result</p>
  <h2 id="r-name" style="font-size:clamp(2.2rem,5vw,3.4rem)"></h2>
  <p class="lede" id="r-short" style="font-size:1.15rem"></p>
  <span class="place-tag" id="r-place"></span>
  <div class="result-bars" id="r-bars"></div>
  <div class="grid-2"><div class="panel"><h3>Strengths</h3><ul id="r-str"></ul></div><div class="panel"><h3>Watch-outs</h3><ul id="r-watch"></ul></div></div>
  <div class="panel" style="margin-top:20px"><h3>Where you work best</h3><p id="r-env"></p><p><strong>Methods to try:</strong> <span id="r-methods"></span></p><a class="btn" id="r-link" href="#">Read your full profile</a></div>
  <div class="panel pencil" style="margin-top:20px">
   <h3>Email me my full report and a team guide</h3>
   <p>Get a printable summary of your result, a weekly schedule template for your style and a guide to working with the other seven styles.</p>
   <form class="form" id="report-form" data-form="Assessment report request" data-ok="Done. Your report is on its way — check your inbox within two business days.">
    {hp()}
    <div class="row"><div><label for="rf-name">First name</label><input id="rf-name" name="name" type="text" required autocomplete="given-name"></div>
    <div><label for="rf-email">Email</label><input id="rf-email" name="email" type="email" required autocomplete="email"></div></div>
    <div><label for="rf-role">Which best describes you?</label><select id="rf-role" name="role"><option>Individual contributor</option><option>Manager or team lead</option><option>Founder or executive</option><option>HR or people team</option><option>Freelancer</option><option>Student</option></select></div>
    <label class="check"><input type="checkbox" name="newsletter" value="yes" checked> Also send me the Thursday note (one email a week, unsubscribe any time)</label>
    <button class="btn" type="submit">Email my report</button>{form_status()}
   </form>
  </div>
  <div class="panel" style="margin-top:20px"><h3>Share your result</h3><div class="row form"><input id="r-share" type="text" readonly aria-label="Shareable result link"><button class="btn alt small" id="r-copy" type="button">Copy link</button></div>
  <p style="margin-top:14px">Managing a team? <a href="teams.html">Map everyone's style on one page</a>. <button class="btn small alt" id="r-again" type="button" style="margin-left:8px">Retake</button></p></div>
  <p class="form-note" style="margin-top:20px">This assessment is for self-reflection and is not a psychological, clinical or hiring instrument. See <a href="about.html#method">our methodology</a>.</p>
 </div>
</div>"""
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Work Style Assessment", "applicationCategory": "EducationalApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    page("quiz.html", "Free Work Style Assessment (5 Minutes)", "A free 20-question work style test. Find out if you're a Cartographer, Tinkerer, Mentor, Collaborator, Sprinter, Scout, Coordinator or Catalyst — and where you work best.", body, scripts=QUIZ_JS, jsonld=ld, nav_key="quiz.html")


# ---------------------------------------------------------------- tools
TOOLS = [
 ("meeting-cost", "Meeting Cost Calculator", "Calculate what a meeting really costs in salary time — one-off or recurring — and see the yearly total."),
 ("commute-savings", "Commute Savings Calculator", "See how many hours and how much money working from home saves each week and year."),
 ("focus-timer", "Focus Timer (Pomodoro and Deep Work)", "A free online focus timer with Pomodoro 25/5, 50/10 and 90-minute deep-work presets."),
 ("desk-setup", "Desk and Monitor Height Calculator", "Get suggested chair, desk and monitor heights for your height, in centimetres or inches."),
 ("hybrid-planner", "Hybrid Week Planner", "Plan your home and office days and see your weekly commute time and collaboration balance."),
 ("freelance-rate", "Freelance Hourly Rate Calculator", "Work out the hourly rate you need to cover income goals, costs, taxes and time off."),
]

TOOL_BODIES = {
"meeting-cost": ("""<div class="calc"><form class="panel form" id="mc" onsubmit="return false">
 <div class="row"><div><label for="mc-n">People attending</label><input id="mc-n" type="number" min="1" value="6"></div>
 <div><label for="mc-m">Length (minutes)</label><input id="mc-m" type="number" min="5" step="5" value="60"></div></div>
 <div class="row"><div><label for="mc-s">Average annual salary</label><input id="mc-s" type="number" min="0" step="1000" value="75000"></div>
 <div><label for="mc-o">Overhead multiplier</label><input id="mc-o" type="number" min="1" step="0.05" value="1.3"></div></div>
 <div><label for="mc-f">How often</label><select id="mc-f"><option value="1">Once</option><option value="52" selected>Weekly</option><option value="26">Every two weeks</option><option value="12">Monthly</option><option value="260">Daily (weekdays)</option></select></div>
 <p class="form-note">Hourly cost = salary × overhead ÷ 2,080 working hours. Overhead covers benefits, payroll taxes and equipment; 1.25–1.4 is a common range.</p>
</form>
<div class="panel pencil" aria-live="polite"><p class="mt0">This meeting costs</p><p class="big-num" id="mc-one">$0</p><p>each time, and <strong id="mc-yr">$0</strong> a year at this frequency — <strong id="mc-hr">0</strong> person-hours.</p><p class="form-note">Cut it to 25 minutes and save <strong id="mc-save">$0</strong> a year.</p></div></div>""",
r"""<script>(function(){var g=function(i){return +document.getElementById(i).value||0},f=function(n){return "$"+Math.round(n).toLocaleString()};
function c(){var h=g("mc-s")*g("mc-o")/2080,one=h*g("mc-n")*g("mc-m")/60,fr=g("mc-f");
document.getElementById("mc-one").textContent=f(one);document.getElementById("mc-yr").textContent=f(one*fr);
document.getElementById("mc-hr").textContent=Math.round(g("mc-n")*g("mc-m")/60*fr).toLocaleString();
var m=g("mc-m");document.getElementById("mc-save").textContent=f(m>25?h*g("mc-n")*(m-25)/60*fr:0);}
document.getElementById("mc").addEventListener("input",c);c();})();</script>"""),
"commute-savings": ("""<div class="calc"><form class="panel form" id="cs" onsubmit="return false">
 <div class="row"><div><label for="cs-t">One-way commute (minutes)</label><input id="cs-t" type="number" min="0" value="40"></div>
 <div><label for="cs-d">Remote days per week</label><input id="cs-d" type="number" min="0" max="7" value="3"></div></div>
 <div class="row"><div><label for="cs-c">Travel cost per round trip</label><input id="cs-c" type="number" min="0" step="0.5" value="12"></div>
 <div><label for="cs-l">Lunch and coffee per office day</label><input id="cs-l" type="number" min="0" step="0.5" value="14"></div></div>
 <div class="row"><div><label for="cs-h">Extra home costs per remote day</label><input id="cs-h" type="number" min="0" step="0.5" value="3"></div>
 <div><label for="cs-w">Working weeks per year</label><input id="cs-w" type="number" min="1" max="52" value="46"></div></div>
 <p class="form-note">Travel cost: fuel, parking, transit fare or a per-km rate. Home costs: heating, power and snacks.</p>
</form>
<div class="panel teal" aria-live="polite"><p class="mt0">Working remotely saves you</p><p class="big-num" id="cs-hrs">0 h</p><p>of commuting a year — about <strong id="cs-days">0</strong> full eight-hour days — and <strong id="cs-money">$0</strong> a year after extra home costs.</p></div></div>""",
r"""<script>(function(){var g=function(i){return +document.getElementById(i).value||0};
function c(){var d=g("cs-d")*g("cs-w"),hrs=d*g("cs-t")*2/60,money=d*(g("cs-c")+g("cs-l")-g("cs-h"));
document.getElementById("cs-hrs").textContent=Math.round(hrs).toLocaleString()+" h";document.getElementById("cs-days").textContent=Math.round(hrs/8);
document.getElementById("cs-money").textContent="$"+Math.round(money).toLocaleString();}
document.getElementById("cs").addEventListener("input",c);c();})();</script>"""),
"focus-timer": ("""<div class="panel" style="max-width:720px;margin:0 auto">
 <div class="chips" role="group" aria-label="Timer preset" id="ft-presets">
  <label><input type="radio" name="p" value="25,5" checked><span>Pomodoro 25 / 5</span></label>
  <label><input type="radio" name="p" value="50,10"><span>Focus 50 / 10</span></label>
  <label><input type="radio" name="p" value="90,20"><span>Deep work 90 / 20</span></label>
  <label><input type="radio" name="p" value="15,3"><span>Quick sprint 15 / 3</span></label>
 </div>
 <p class="center" id="ft-mode" style="margin:22px 0 0;font-weight:600">Focus</p>
 <p class="timer-face" id="ft-face" aria-live="off">25:00</p>
 <p class="center form-note" id="ft-count">Completed sessions today: 0</p>
 <div class="center" style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap"><button class="btn pencil" id="ft-go">Start</button><button class="btn alt" id="ft-reset">Reset</button><button class="btn alt" id="ft-skip">Skip to break</button></div>
 <p class="form-note center" style="margin-top:16px">Tip: every break is a cue to stand up and look at something far away for 20 seconds.</p>
</div>""",
r"""<script>(function(){var f=25,b=5,left=f*60,run=null,mode="focus",done=0,face=document.getElementById("ft-face"),go=document.getElementById("ft-go");
function draw(){var m=Math.floor(left/60),s=left%60;face.textContent=(m<10?"0":"")+m+":"+(s<10?"0":"")+s;document.title=face.textContent+" "+(mode==="focus"?"Focus":"Break")+" | Work.Style";document.getElementById("ft-mode").textContent=mode==="focus"?"Focus":"Break";}
function beep(){try{var a=new (window.AudioContext||window.webkitAudioContext)(),o=a.createOscillator();o.frequency.value=660;o.connect(a.destination);o.start();setTimeout(function(){o.stop();a.close();},400);}catch(e){}}
function sw(){if(mode==="focus"){done++;document.getElementById("ft-count").textContent="Completed sessions today: "+done;mode="break";left=b*60;}else{mode="focus";left=f*60;}beep();draw();}
function tick(){left--;if(left<=0)sw();draw();}
go.onclick=function(){if(run){clearInterval(run);run=null;go.textContent="Resume";}else{run=setInterval(tick,1000);go.textContent="Pause";}};
document.getElementById("ft-reset").onclick=function(){clearInterval(run);run=null;mode="focus";left=f*60;go.textContent="Start";draw();};
document.getElementById("ft-skip").onclick=function(){sw();};
document.getElementById("ft-presets").addEventListener("change",function(e){var v=e.target.value.split(",");f=+v[0];b=+v[1];document.getElementById("ft-reset").click();});
draw();})();</script>"""),
"desk-setup": ("""<div class="calc"><form class="panel form" id="ds" onsubmit="return false">
 <div class="chips" role="group" aria-label="Units"><label><input type="radio" name="u" value="cm" checked><span>Centimetres</span></label><label><input type="radio" name="u" value="in"><span>Inches</span></label></div>
 <div><label for="ds-h">Your height</label><input id="ds-h" type="number" min="100" max="230" value="175"></div>
 <p class="form-note">Estimates from standard body proportions, assuming typical shoes. Fine-tune by checking that your elbows sit at about 90° and your feet rest flat.</p>
</form>
<div class="panel pencil" aria-live="polite">
 <p class="mt0"><strong>Seat height:</strong> <span id="ds-seat"></span></p>
 <p><strong>Sitting desk height (keyboard surface):</strong> <span id="ds-desk"></span></p>
 <p><strong>Standing desk height:</strong> <span id="ds-stand"></span></p>
 <p><strong>Top of monitor, sitting (from floor):</strong> <span id="ds-mon"></span></p>
 <p><strong>Screen distance:</strong> <span id="ds-dist"></span></p>
 <p class="form-note">See the full <a href="../guides/home-office-setup.html">ergonomic checklist</a>.</p>
</div></div>""",
r"""<script>(function(){var f=document.getElementById("ds"),h=document.getElementById("ds-h");
function c(){var u=f.querySelector("input[name=u]:checked").value,H=+h.value||0,cm=u==="in"?H*2.54:H;
var r=function(x){return u==="in"?(x/2.54).toFixed(1)+" in":Math.round(x)+" cm";};
document.getElementById("ds-seat").textContent=r(cm*0.25);document.getElementById("ds-desk").textContent=r(cm*0.41);
document.getElementById("ds-stand").textContent=r(cm*0.63);document.getElementById("ds-mon").textContent=r(cm*0.70);
document.getElementById("ds-dist").textContent=u==="in"?"20–30 in (about an arm's length)":"50–75 cm (about an arm's length)";}
f.addEventListener("change",function(e){if(e.target.name==="u"){h.value=e.target.value==="in"?Math.round(h.value/2.54):Math.round(h.value*2.54);h.min=e.target.value==="in"?40:100;h.max=e.target.value==="in"?90:230;}c();});
h.addEventListener("input",c);c();})();</script>"""),
"hybrid-planner": ("""<div class="calc"><div class="panel">
 <p class="mt0">Tap a day to switch it between home and office.</p>
 <div class="week" id="hp-week"><button data-mode="home">Mon<br>Home</button><button data-mode="office">Tue<br>Office</button><button data-mode="office">Wed<br>Office</button><button data-mode="home">Thu<br>Home</button><button data-mode="home">Fri<br>Home</button></div>
 <div class="form" style="margin-top:18px"><div><label for="hp-t">One-way commute (minutes)</label><input id="hp-t" type="number" min="0" value="40"></div></div>
</div>
<div class="panel teal" aria-live="polite"><p class="mt0">Your week</p><p class="big-num" id="hp-sum">2 office · 3 home</p><p>Weekly commute: <strong id="hp-c">0 h</strong>. <span id="hp-tip"></span></p><p class="form-note">Plan together-work (workshops, one-to-ones) for office days and focus work for home days. <a href="../guides/hybrid-work-schedule.html">Read the hybrid guide</a>.</p></div></div>""",
r"""<script>(function(){var w=document.getElementById("hp-week"),t=document.getElementById("hp-t");
function c(){var o=w.querySelectorAll('[data-mode=office]').length,h=5-o;document.getElementById("hp-sum").textContent=o+" office, "+h+" home";
document.getElementById("hp-c").textContent=(o*2*(+t.value||0)/60).toFixed(1)+" h";
document.getElementById("hp-tip").textContent=o===0?"Fully remote: plan regular live collaboration so nobody drifts.":o>=4?"Mostly office: protect at least one focus block a day.":o===1?"One anchor day suits deep-focus styles. Pack it with together-work.":"A balanced week. Make your office days consecutive so the team overlaps.";}
w.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;var m=b.dataset.mode==="home"?"office":"home";b.dataset.mode=m;b.innerHTML=b.textContent.slice(0,3)+"<br>"+(m==="home"?"Home":"Office");c();});
t.addEventListener("input",c);c();})();</script>"""),
"freelance-rate": ("""<div class="calc"><form class="panel form" id="fr" onsubmit="return false">
 <div class="row"><div><label for="fr-i">Target take-home income per year</label><input id="fr-i" type="number" min="0" step="1000" value="70000"></div>
 <div><label for="fr-c">Business costs per year</label><input id="fr-c" type="number" min="0" step="500" value="8000"></div></div>
 <div class="row"><div><label for="fr-t">Tax rate estimate (%)</label><input id="fr-t" type="number" min="0" max="70" value="28"></div>
 <div><label for="fr-v">Weeks off per year</label><input id="fr-v" type="number" min="0" max="26" value="6"></div></div>
 <div class="row"><div><label for="fr-h">Hours worked per week</label><input id="fr-h" type="number" min="1" max="80" value="40"></div>
 <div><label for="fr-b">Share of hours that are billable (%)</label><input id="fr-b" type="number" min="5" max="100" value="65"></div></div>
 <p class="form-note">Billable share accounts for admin, sales and learning time. Tax rules vary — check with an accountant.</p>
</form>
<div class="panel pencil" aria-live="polite"><p class="mt0">Charge at least</p><p class="big-num" id="fr-r">$0/h</p><p>That's <strong id="fr-d">$0</strong> per 8-hour day and <strong id="fr-g">$0</strong> gross revenue a year across <strong id="fr-bh">0</strong> billable hours.</p></div></div>""",
r"""<script>(function(){var g=function(i){return +document.getElementById(i).value||0};
function c(){var gross=g("fr-i")/(1-Math.min(g("fr-t"),95)/100)+g("fr-c"),bh=(52-g("fr-v"))*g("fr-h")*g("fr-b")/100,r=bh?gross/bh:0;
document.getElementById("fr-r").textContent="$"+Math.ceil(r)+"/h";document.getElementById("fr-d").textContent="$"+Math.round(r*8).toLocaleString();
document.getElementById("fr-g").textContent="$"+Math.round(gross).toLocaleString();document.getElementById("fr-bh").textContent=Math.round(bh).toLocaleString();}
document.getElementById("fr").addEventListener("input",c);c();})();</script>"""),
}

TOOL_NOTES = {
 "meeting-cost": "Meetings are where many teams lose the most time without noticing. The calculator multiplies the number of people by their hourly cost and the meeting length, then by how often the meeting happens. Use it before adding a recurring meeting to your calendar, or during a quarterly calendar audit. Pair it with our guide to <a href=\"../guides/meeting-hygiene.html\">meeting hygiene</a>.",
 "commute-savings": "A commute costs time and money, and remote work shifts some of those costs to your home. This calculator nets out both so you can compare options honestly — useful when negotiating a hybrid arrangement or comparing job offers. Read the <a href=\"../guides/remote-work-guide.html\">complete remote work guide</a> next.",
 "focus-timer": "The timer runs entirely in your browser. Choose the classic Pomodoro rhythm for task-heavy days, 50/10 for writing and analysis, or 90/20 for deep work. Keep this tab open; a short tone plays when each session ends. Learn which rhythm suits you in <a href=\"../guides/productivity-methods.html\">9 productivity methods</a>.",
 "desk-setup": "Most aches from desk work come from a handful of measurements: seat, desk and screen heights. The results are starting points based on average body proportions; adjust until your elbows are at about 90 degrees, your feet are flat and your neck is neutral.",
 "hybrid-planner": "A hybrid week works when office days are for collaboration and home days are for focus. Mark your days, check the commute load, and then move your meetings to match. For team-wide schedules, see <a href=\"../teams.html\">team assessments</a>.",
 "freelance-rate": "Freelancers often price from what employees earn per hour and end up underpaid, because they forget unpaid admin time, costs, taxes and holidays. This calculator works backwards from the income you want to the rate you need.",
}


def build_tools():
    for slug, title, desc in TOOLS:
        ui, js = TOOL_BODIES[slug]
        others = "".join(f'<a class="tile" href="{s}.html"><h3>{t}</h3><p>{esc(d)}</p></a>' for s, t, d in TOOLS if s != slug)
        body = f"""<div class="wrap page-head"><p class="crumbs"><a href="../index.html">Home</a> / <a href="index.html">Tools</a></p><h1 style="max-width:18ch">{title}</h1><p class="lede">{esc(desc)}</p></div>
<div class="wrap">{ui}
<div class="article" style="margin:40px 0"><h2>How to use it</h2><p>{TOOL_NOTES[slug]}</p><p class="form-note">Results are estimates for planning only. Nothing you enter leaves your browser.</p></div>
<h2>More free tools</h2><div class="grid-3" style="margin-bottom:50px">{others}</div></div>"""
        ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": title, "applicationCategory": "BusinessApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
        page(f"tools/{slug}.html", title, desc, body, scripts=js, jsonld=ld, nav_key="tools/")
    tiles = "".join(f'<a class="tile{" feature" if i == 0 else ""}" href="{s}.html"><h3>{t}</h3><p>{esc(d)}</p><span class="go">Open tool</span></a>' for i, (s, t, d) in enumerate(TOOLS))
    body = f"""<div class="wrap page-head"><h1>Free work tools</h1><p class="lede">Calculators and timers for better workdays. No sign-up, and nothing you type leaves your browser.</p></div>
<div class="wrap" style="padding-bottom:50px"><div class="grid-3">{tiles}</div>
<div class="panel pencil" style="margin-top:30px"><h3>Want a tool we don't have?</h3><p>Tell us what you'd use. The most requested tools get built first. <a href="../contact.html">Suggest a tool</a>.</p></div></div>"""
    page("tools/index.html", "Free Work Tools and Calculators", "Free meeting cost, commute savings, freelance rate and desk height calculators, plus a focus timer and hybrid week planner.", body, nav_key="tools/")


# ---------------------------------------------------------------- lead gen: teams
def build_teams():
    body = f"""<section class="hero" style="padding-bottom:20px"><div class="wrap hero-grid" style="align-items:start">
 <div>
  <p class="crumbs"><a href="index.html">Home</a> / For teams</p>
  <h1 style="max-width:14ch">Fix team friction before it starts.</h1>
  <p class="lede">Most team conflict isn't about effort or skill — it's about style. A Work.Style team report maps everyone on one page and turns it into a working rhythm the whole team can live with.</p>
  <h3 style="margin-top:28px">What you get</h3>
  <ul>
   <li><strong>Team map:</strong> every member on the three work-style axes, on one page</li>
   <li><strong>Friction report:</strong> where your team's styles clash, with examples and fixes</li>
   <li><strong>Rhythm plan:</strong> meeting cadence, focus time and async norms tuned to your team</li>
   <li><strong>Hybrid schedule:</strong> recommended anchor days and office-day agenda</li>
   <li><strong>Pairing guide:</strong> which teammates complement each other</li>
   <li><strong>Optional workshop:</strong> a 90-minute facilitated session, live or remote</li>
  </ul>
  <h3>Who it's for</h3>
  <p>Team leads, founders, HR and people teams, agencies and consultants running team offsites. Teams from 3 to 500.</p>
 </div>
 <div class="panel" id="request">
  <h2 style="font-size:1.5rem">Request your team report</h2>
  <p class="form-note">Three quick steps. We reply within two business days with a plan and price.</p>
  <form class="form" data-form="Team report lead" data-steps data-redirect="thank-you.html">
   {hp()}
   <div class="steps-bar" aria-hidden="true"><i></i><i></i><i></i></div>
   <div class="step">
    <p style="font-weight:600;margin:0">What do you want to improve?</p>
    <div class="chips" data-need-one>
     <label><input type="checkbox" name="goals" value="Fewer, better meetings"><span>Fewer, better meetings</span></label>
     <label><input type="checkbox" name="goals" value="Hybrid schedule"><span>Hybrid schedule</span></label>
     <label><input type="checkbox" name="goals" value="Team conflict"><span>Team conflict</span></label>
     <label><input type="checkbox" name="goals" value="Onboarding new hires"><span>Onboarding new hires</span></label>
     <label><input type="checkbox" name="goals" value="Focus and productivity"><span>Focus and productivity</span></label>
     <label><input type="checkbox" name="goals" value="Offsite or workshop"><span>Offsite or workshop</span></label>
     <label><input type="checkbox" name="goals" value="Burnout and boundaries"><span>Burnout and boundaries</span></label>
    </div>
    <div class="step-nav"><span></span><button type="button" class="btn" data-next>Continue</button></div>
   </div>
   <div class="step">
    <div class="row"><div><label for="t-size">Team size</label><select id="t-size" name="team_size" required><option value="">Choose one</option><option>3–5</option><option>6–15</option><option>16–50</option><option>51–200</option><option>200+</option></select></div>
    <div><label for="t-model">How the team works</label><select id="t-model" name="work_model" required><option value="">Choose one</option><option>Fully remote</option><option>Hybrid</option><option>Mostly office</option><option>Mixed / it varies</option></select></div></div>
    <div class="row"><div><label for="t-when">When do you want to start?</label><select id="t-when" name="timeline" required><option value="">Choose one</option><option>This month</option><option>Next 1–3 months</option><option>Just exploring</option></select></div>
    <div><label for="t-format">Format</label><select id="t-format" name="format"><option>Report only</option><option>Report + remote workshop</option><option>Report + on-site workshop</option><option>Not sure yet</option></select></div></div>
    <div class="step-nav"><button type="button" class="btn alt" data-prev>Back</button><button type="button" class="btn" data-next>Continue</button></div>
   </div>
   <div class="step">
    <div class="row"><div><label for="t-name">Your name</label><input id="t-name" name="name" type="text" required autocomplete="name"></div>
    <div><label for="t-email">Work email</label><input id="t-email" name="email" type="email" required autocomplete="email"></div></div>
    <div class="row"><div><label for="t-co">Company</label><input id="t-co" name="company" type="text" required autocomplete="organization"></div>
    <div><label for="t-role">Your role</label><input id="t-role" name="role" type="text" autocomplete="organization-title"></div></div>
    <div><label for="t-msg">Anything we should know? (optional)</label><textarea id="t-msg" name="message" rows="3"></textarea></div>
    <label class="check"><input type="checkbox" name="consent" value="yes" required> I agree to be contacted about this request. See the <a href="privacy.html">privacy policy</a>.</label>
    <div class="step-nav"><button type="button" class="btn alt" data-prev>Back</button><button type="submit" class="btn teal">Send my request</button></div>
   </div>
   {form_status()}
  </form>
 </div>
</div></section>

<section class="band"><div class="wrap">
 <h2>How it works</h2>
 <div class="grid-3" style="margin-top:20px">
  <div class="panel"><h3>1. Tell us about your team</h3><p>Fill in the form. We reply with a short plan, a timeline and a fixed price.</p></div>
  <div class="panel"><h3>2. Everyone takes the assessment</h3><p>Each person spends about five minutes on the Work Style Assessment using a private team link.</p></div>
  <div class="panel"><h3>3. Get your report and plan</h3><p>Within a week you get the team map, friction report and rhythm plan — plus the workshop if you chose one.</p></div>
 </div>
</div></section>

<section><div class="wrap grid-2">
 <div><h2>Questions teams ask</h2>
  <details><summary>Is this a personality test?</summary><p>No. It measures work preferences — how you like to focus, collaborate and plan — not personality, ability or mental health.</p></details>
  <details><summary>Can we use it for hiring or performance reviews?</summary><p>No, and we won't support that use. It isn't designed or validated for selection decisions. Use it to improve how a team works together.</p></details>
  <details><summary>Who sees individual answers?</summary><p>Only the summary result for each person goes into the team map, and each person sees their own report. Raw answers are not shared with managers.</p></details>
  <details><summary>Do you work with remote teams in other time zones?</summary><p>Yes. Everything can be done online, and workshops can be run in two sessions for teams spread across time zones.</p></details>
  <details><summary>We're a small team. Is it worth it?</summary><p>Small teams often get the most out of it, because one mismatch affects everyone. Teams of three and up are welcome.</p></details>
 </div>
 <div class="panel pencil"><h2 style="font-size:1.6rem">Start free</h2><p>Not ready for a report? Ask your team to take the free assessment and share their results in your next meeting. Then read our guide to <a href="guides/team-work-styles.html">managing a team with different work styles</a>.</p><a class="btn" href="quiz.html">Open the free assessment</a>
 <h3 style="margin-top:26px">Partners and consultants</h3><p>Coaches, HR consultancies and coworking operators can offer Work.Style team reports to their clients. <a href="advertise.html#partner">Become a partner</a>.</p></div>
</div></section>"""
    page("teams.html", "Team Work Style Assessment and Workshop", "Map your team's work styles on one page and get a meeting rhythm, hybrid schedule and pairing plan that fits everyone. Request a team report.", body, nav_key="teams.html")


# ---------------------------------------------------------------- support / donations
def build_support():
    body = f"""<div class="wrap page-head"><h1>Keep Work.Style free</h1><p class="lede">No paywalls and no account needed — for anyone, anywhere. Reader support pays for hosting, new tools, research and the contest prizes.</p></div>
<div class="wrap grid-2" style="padding-bottom:40px;align-items:start">
 <div class="panel">
  <h2 style="font-size:1.5rem">Choose your support</h2>
  <div class="tiers" style="grid-template-columns:1fr 1fr;margin:16px 0">
   <button type="button" class="tier" data-amount="5" aria-pressed="false"><span>Coffee</span><strong>$5</strong><small>Keeps the timers ticking</small></button>
   <button type="button" class="tier" data-amount="25" aria-pressed="true"><span>Supporter</span><strong>$25</strong><small>Funds one new guide</small></button>
   <button type="button" class="tier" data-amount="100" aria-pressed="false"><span>Patron</span><strong>$100</strong><small>Funds a monthly prize</small></button>
   <button type="button" class="tier" data-amount="500" aria-pressed="false"><span>Builder</span><strong>$500</strong><small>Funds a new free tool</small></button>
  </div>
  <div id="pay-links" style="display:flex;gap:10px;flex-wrap:wrap"></div>
  <p class="form-note" id="pay-note" hidden>Payments are processed securely by the provider. Work.Style never sees your card details.</p>
  <form class="form" data-form="Support pledge" data-redirect="thank-you.html" style="margin-top:16px">
   {hp()}
   <p style="margin:0">Pledge your support and we'll send you a secure payment link and receipt.</p>
   <div class="row"><div><label for="amount">Amount (USD)</label><input id="amount" name="amount" type="number" min="1" value="25" required></div>
   <div><label for="s-freq">Frequency</label><select id="s-freq" name="frequency"><option>One-time</option><option>Monthly</option><option>Yearly</option></select></div></div>
   <div><label for="s-purpose">Put it toward</label><select id="s-purpose" name="purpose"><option>Wherever it's needed most</option><option>Ongoing operations and hosting</option><option>New free tools</option><option>Contest prizes</option><option>Promotion and marketing</option><option>Hiring writers and creators</option></select></div>
   <div class="row"><div><label for="s-name">Name</label><input id="s-name" name="name" type="text" required autocomplete="name"></div>
   <div><label for="s-email">Email</label><input id="s-email" name="email" type="email" required autocomplete="email"></div></div>
   <label class="check"><input type="checkbox" name="public_thanks" value="yes"> Thank me by name on the supporters page</label>
   <button class="btn teal" type="submit">Pledge my support</button>{form_status()}
  </form>
 </div>
 <div>
  <h2 style="font-size:1.5rem">Where the money goes</h2>
  <table class="article" style="display:table;width:100%;border-collapse:collapse;margin-bottom:24px">
   <tr><td style="padding:10px;border-bottom:1px solid var(--line)">Operations, hosting and security</td><td style="padding:10px;border-bottom:1px solid var(--line);text-align:right">30%</td></tr>
   <tr><td style="padding:10px;border-bottom:1px solid var(--line)">New tools and research</td><td style="padding:10px;border-bottom:1px solid var(--line);text-align:right">30%</td></tr>
   <tr><td style="padding:10px;border-bottom:1px solid var(--line)">Writers, creators and coaches</td><td style="padding:10px;border-bottom:1px solid var(--line);text-align:right">20%</td></tr>
   <tr><td style="padding:10px;border-bottom:1px solid var(--line)">Contest prizes</td><td style="padding:10px;border-bottom:1px solid var(--line);text-align:right">10%</td></tr>
   <tr><td style="padding:10px">Promotion and outreach</td><td style="padding:10px;text-align:right">10%</td></tr>
  </table>
  <div class="panel pencil"><h3>Other ways to help</h3><ul><li>Share the <a href="quiz.html">assessment</a> with your team</li><li>Sponsor a contest prize or a tool — see <a href="advertise.html">sponsorship</a></li><li>Write or film for us — see <a href="careers.html">open roles</a></li><li>Tell us what to build next on the <a href="contact.html">contact page</a></li></ul></div>
  <p class="form-note" style="margin-top:16px">Work.Style is an independent website, not a registered charity. Contributions are not tax-deductible.</p>
 </div>
</div>"""
    page("support.html", "Support Work.Style", "Help keep Work.Style's assessment, tools and guides free for everyone. One-time or monthly support for operations, new tools, prizes and creators.", body, nav_key="support.html")


# ---------------------------------------------------------------- contests
def build_contests():
    body = f"""<div class="wrap page-head"><h1>Contests and prizes</h1><p class="lede">Show us how you work. Every month we feature the best entries and send prizes to the winners.</p></div>
<div class="wrap" style="padding-bottom:40px">
 <div class="grid-3">
  <div class="panel pencil"><h3>Show Your Setup</h3><p>Send one photo of your workspace — home office, kitchen table, van, coworking desk — and 100–300 words on why it works for your style.</p><p><strong>Monthly prize:</strong> a featured profile plus a $100 gift card or sponsor-donated gear.</p></div>
  <div class="panel"><h3>My Work Style Story</h3><p>Tell us, in 300–800 words, about a time changing how you work changed your results. Winning stories are published with your byline.</p><p><strong>Quarterly prize:</strong> $250 and a published feature.</p></div>
  <div class="panel teal"><h3>Best Hybrid Teams</h3><p>Nominate a team (yours or someone else's) that's cracked remote or hybrid work. Winners get a profile and a digital badge.</p><p><strong>Yearly award:</strong> recognition and a free team workshop.</p></div>
 </div>
 <div class="grid-2" style="margin-top:34px;align-items:start">
  <div class="panel">
   <h2 style="font-size:1.5rem">Enter a contest</h2>
   <form class="form" data-form="Contest entry" data-redirect="thank-you.html">
    {hp()}
    <div><label for="c-contest">Contest</label><select id="c-contest" name="contest" required><option value="">Choose one</option><option>Show Your Setup</option><option>My Work Style Story</option><option>Best Hybrid Teams (nomination)</option></select></div>
    <div class="row"><div><label for="c-name">Name</label><input id="c-name" name="name" type="text" required autocomplete="name"></div>
    <div><label for="c-email">Email</label><input id="c-email" name="email" type="email" required autocomplete="email"></div></div>
    <div class="row"><div><label for="c-style">Your work style (if you know it)</label><select id="c-style" name="work_style"><option value="">Not sure yet</option>{''.join(f'<option>{s["name"]}</option>' for s in STYLES)}</select></div>
    <div><label for="c-country">Country</label><input id="c-country" name="country" type="text" autocomplete="country-name"></div></div>
    <div><label for="c-link">Link to your photo or story (Google Drive, Dropbox, Instagram, etc.)</label><input id="c-link" name="entry_link" type="url" placeholder="https://" required></div>
    <div><label for="c-msg">Description or story</label><textarea id="c-msg" name="message" required></textarea></div>
    <label class="check"><input type="checkbox" name="rules" value="accepted" required> I'm 18 or older, this is my own work, and I accept the contest rules.</label>
    <button class="btn pencil" type="submit">Submit my entry</button>{form_status()}
   </form>
  </div>
  <div>
   <h2 style="font-size:1.5rem">Rules in plain language</h2>
   <ol>
    <li>Open to people aged 18 or over, where contests are legal. No purchase or payment necessary.</li>
    <li>One entry per person per contest per period.</li>
    <li>Entries must be your own original work and must not show other people without their permission, or private or confidential information.</li>
    <li>By entering, you allow Work.Style to publish your entry, name and country on this site and its social channels. You keep ownership of your work.</li>
    <li>Winners are chosen by the Work.Style editorial team on originality, usefulness to readers and fit with the theme. Decisions are final.</li>
    <li>Winners are contacted by email and must reply within 14 days, or a runner-up is chosen.</li>
    <li>Prizes can't be exchanged. Winners are responsible for any taxes on prizes.</li>
    <li>We may change or cancel a contest if needed; any change will be posted here.</li>
   </ol>
   <div class="panel pencil"><h3>Sponsor a prize</h3><p>Brands that make office furniture, software or gear can sponsor a monthly prize and get featured on every winner announcement. <a href="advertise.html">See sponsorship options</a>.</p></div>
  </div>
 </div>
</div>"""
    page("contests.html", "Contests: Show Your Setup and Work Style Stories", "Enter the Work.Style contests: share your workspace, tell your work style story or nominate a great hybrid team. Monthly and quarterly prizes.", body, nav_key="contests.html")


# ---------------------------------------------------------------- careers
def build_careers():
    roles = [("Freelance writer", "Remote, paid per article", "Write practical guides on remote work, productivity, teams and workplace wellbeing. Experience in HR, management, coaching or a related field is a plus."),
             ("Video creator", "Remote, paid per project", "Make short explainers and tool walkthroughs for YouTube and social. Send links to your best work."),
             ("Workplace coach or facilitator", "Remote or regional, paid per workshop", "Run Work.Style team workshops for our clients. Coaching, HR or facilitation experience required."),
             ("Community ambassador", "Remote, volunteer with perks", "Share Work.Style in your community, host a meetup or run a coworking challenge."),
             ("Web developer (contract)", "Remote, paid per project", "Build new free tools in plain HTML, CSS and JavaScript. Accessibility skills welcome."),
             ("Partnerships and sales (commission)", "Remote, commission-based", "Introduce teams and sponsors to Work.Style and earn a share of every deal you bring in.")]
    cards = "".join(f'<div class="panel"><h3>{r}</h3><p class="form-note">{m}</p><p>{d}</p></div>' for r, m, d in roles)
    opts = "".join(f"<option>{r}</option>" for r, _, _ in roles)
    body = f"""<div class="wrap page-head"><h1>Work with us</h1><p class="lede">Work.Style is growing. We hire writers, creators, coaches and builders — remote, flexible and matched to how you work best.</p></div>
<div class="wrap" style="padding-bottom:40px"><div class="grid-3">{cards}</div>
<div class="panel" style="margin-top:34px;max-width:760px">
 <h2 style="font-size:1.5rem">Apply</h2>
 <form class="form" data-form="Talent application" data-redirect="thank-you.html">
  {hp()}
  <div class="row"><div><label for="a-name">Name</label><input id="a-name" name="name" type="text" required autocomplete="name"></div>
  <div><label for="a-email">Email</label><input id="a-email" name="email" type="email" required autocomplete="email"></div></div>
  <div class="row"><div><label for="a-role">Role</label><select id="a-role" name="role" required><option value="">Choose one</option>{opts}<option>Something else</option></select></div>
  <div><label for="a-loc">Location and time zone</label><input id="a-loc" name="location" type="text"></div></div>
  <div><label for="a-link">Portfolio, LinkedIn or samples</label><input id="a-link" name="portfolio" type="url" placeholder="https://" required></div>
  <div><label for="a-msg">Why you, in a few sentences</label><textarea id="a-msg" name="message" required></textarea></div>
  <button class="btn teal" type="submit">Send application</button>{form_status()}
  <p class="form-note">We review applications every two weeks and reply to everyone.</p>
 </form>
</div></div>"""
    page("careers.html", "Careers: Write, Create and Coach With Work.Style", "Open roles at Work.Style for freelance writers, video creators, workplace coaches, community ambassadors, developers and partnership reps.", body)


# ---------------------------------------------------------------- advertise
def build_advertise():
    pk = [("Newsletter presenting sponsor", "Your brand at the top of the Thursday note, with a short native message."),
          ("Assessment results sponsor", "A clearly labelled sponsor slot on the results page that every assessment taker sees."),
          ("Sponsored guide", "A practical guide co-created with you, labelled as sponsored, permanently hosted."),
          ("Contest prize sponsor", "Donate a monthly prize and get featured on entries and winner announcements."),
          ("Tool sponsor", "Sponsor one of our free calculators or timers for a month or a year."),
          ("Partnerships and affiliates", "Coaches, HR consultancies, coworking spaces and software makers: refer clients, resell team reports, or list your product.")]
    cards = "".join(f'<div class="panel"><h3>{a}</h3><p>{b}</p></div>' for a, b in pk)
    body = f"""<div class="wrap page-head"><h1>Advertise, sponsor or partner</h1><p class="lede">Reach people who care about how they work: remote and hybrid workers, managers, founders, HR teams and freelancers.</p></div>
<div class="wrap" style="padding-bottom:40px"><div class="grid-3">{cards}</div>
<div class="grid-2" style="margin-top:34px;align-items:start" id="partner">
 <div class="panel">
  <h2 style="font-size:1.5rem">Request the media kit</h2>
  <form class="form" data-form="Advertising / sponsorship / partnership inquiry" data-redirect="thank-you.html">
   {hp()}
   <div class="row"><div><label for="ad-name">Name</label><input id="ad-name" name="name" type="text" required autocomplete="name"></div>
   <div><label for="ad-email">Work email</label><input id="ad-email" name="email" type="email" required autocomplete="email"></div></div>
   <div class="row"><div><label for="ad-co">Company</label><input id="ad-co" name="company" type="text" required autocomplete="organization"></div>
   <div><label for="ad-web">Website</label><input id="ad-web" name="website" type="url" placeholder="https://"></div></div>
   <div><label for="ad-type">Interested in</label><select id="ad-type" name="interest" required><option value="">Choose one</option>{''.join(f'<option>{a}</option>' for a, _ in pk)}<option>Buying or partnering on this website / domain</option></select></div>
   <div><label for="ad-budget">Monthly budget (USD)</label><select id="ad-budget" name="budget"><option>Under $500</option><option>$500–$2,000</option><option>$2,000–$10,000</option><option>$10,000+</option><option>Prize or in-kind</option></select></div>
   <div><label for="ad-msg">Goals</label><textarea id="ad-msg" name="message"></textarea></div>
   <button class="btn teal" type="submit">Send inquiry</button>{form_status()}
  </form>
 </div>
 <div>
  <h2 style="font-size:1.5rem">Our standards</h2>
  <ul><li>Sponsored content is always clearly labelled.</li><li>Sponsors never influence assessment results or editorial reviews.</li><li>We only work with products we'd be comfortable recommending to readers.</li><li>Display advertising is served by Google AdSense, separately from direct sponsorships.</li></ul>
  <div class="panel pencil"><h3>Interested in the domain itself?</h3><p>For inquiries about acquiring or partnering on this website or the Work.Style domain name, <a href="{OWNER}" target="_blank" rel="noopener">contact the owner here</a>.</p></div>
 </div>
</div></div>"""
    page("advertise.html", "Advertise, Sponsor and Partner With Work.Style", "Sponsorship, advertising and partnership options: newsletter sponsorship, sponsored guides, contest prizes, tool sponsorships and partner programmes.", body)


# ---------------------------------------------------------------- simple pages
def build_simple():
    contact = f"""<div class="wrap page-head"><h1>Contact</h1><p class="lede">Questions, corrections, tool ideas or press — send a message and we'll reply within two business days.</p></div>
<div class="wrap grid-2" style="padding-bottom:40px;align-items:start">
 <div class="panel"><form class="form" data-form="Contact message" data-redirect="thank-you.html">
  {hp()}
  <div class="row"><div><label for="ct-name">Name</label><input id="ct-name" name="name" type="text" required autocomplete="name"></div>
  <div><label for="ct-email">Email</label><input id="ct-email" name="email" type="email" required autocomplete="email"></div></div>
  <div><label for="ct-topic">Topic</label><select id="ct-topic" name="topic"><option>General question</option><option>Correction or feedback</option><option>Tool or guide idea</option><option>Team report</option><option>Press</option><option>Advertising, sponsorship or partnership</option><option>Website or domain inquiry</option></select></div>
  <div><label for="ct-msg">Message</label><textarea id="ct-msg" name="message" required></textarea></div>
  <button class="btn teal" type="submit">Send message</button>{form_status()}
 </form></div>
 <div>
  <div class="panel pencil"><h3>Website, domain, sponsorship or partnership</h3><p>For interest in this website, the Work.Style domain name, sponsorship, advertising or partnership, <a href="{OWNER}" target="_blank" rel="noopener">contact the owner directly</a>.</p></div>
  <div class="panel" style="margin-top:18px"><h3>Quick links</h3><ul><li><a href="teams.html">Request a team report</a></li><li><a href="advertise.html">Advertising and sponsorship</a></li><li><a href="careers.html">Work with us</a></li><li><a href="support.html">Support the site</a></li></ul></div>
 </div>
</div>"""
    page("contact.html", "Contact Work.Style", "Contact Work.Style with questions, corrections, tool ideas, team report requests, press or partnership inquiries.", contact)

    about = """<div class="wrap page-head"><h1>About Work.Style</h1><p class="lede">An independent website that helps people find how they work best — and build their days, desks and teams around it.</p></div>
<div class="wrap article" style="padding-bottom:40px">
<h2>Why we exist</h2><p>Work changed faster in the last few years than in the previous few decades. Remote, hybrid and flexible arrangements gave people more choice — and more ways to get it wrong. Most advice assumes everyone works the same way. We don't. Work.Style starts with how <em>you</em> work, then gives you practical tools and guides to match.</p>
<h2>What we offer</h2><ul><li>A free <a href="quiz.html">Work Style Assessment</a> and eight style profiles</li><li><a href="tools/">Free calculators and timers</a></li><li><a href="guides/">Practical guides</a> on remote, hybrid and office work</li><li><a href="teams.html">Team reports and workshops</a> for organizations</li></ul>
<h2 id="method">Methodology</h2>
<p>The assessment uses 20 statements rated on a five-point agreement scale. Five statements each measure four dimensions: focus rhythm (deep vs sprint), social energy (independent vs collaborative), structure (planned vs flexible) and place (home vs office). Some statements are reverse-scored to reduce bias from agreeing with everything. Each dimension is scored from 0 to 100; the first three determine your style, and the fourth gives a place recommendation.</p>
<p>The dimensions draw on widely discussed ideas in workplace and organizational research — such as the costs of task switching, differences in preferred social stimulation, and preferences for structure versus ambiguity. The assessment is a self-reflection tool. It has not been clinically validated and must not be used for diagnosis, hiring, promotion or performance decisions.</p>
<h2>Editorial standards</h2><ul><li>Guides are written in plain language and reviewed for accuracy before publishing and when updated.</li><li>We avoid made-up statistics. Where rules vary by country — tax, employment law, visas — we say so and point you to official sources.</li><li>Sponsored content is clearly labelled and never affects assessment results.</li><li>Spot an error? <a href="contact.html">Tell us</a> and we'll fix it.</li></ul>
<h2>How we're funded</h2><p>Display advertising through Google AdSense, clearly labelled sponsorships, team reports and <a href="support.html">reader support</a>. That keeps the assessment, tools and guides free.</p>
</div>"""
    page("about.html", "About Work.Style and Our Methodology", "About Work.Style, how the Work Style Assessment is built and scored, our editorial standards and how the site is funded.", about)

    privacy = f"""<div class="wrap page-head"><h1>Privacy and cookie policy</h1><p class="lede">Last updated {datetime.date.today().strftime('%B %d, %Y')}.</p></div>
<div class="wrap article" style="padding-bottom:40px">
<h2>Summary</h2><p>The assessment and tools run in your browser. We only receive information you choose to send through a form. We use cookies for basic site function and, through Google AdSense, for advertising.</p>
<h2>Information you give us</h2><p>When you submit a form (newsletter, report request, team request, contest entry, application, pledge or contact message), we receive the details you enter, such as your name, email address and message. We use this information only to respond to you and provide what you asked for. Forms are delivered through a third-party form-processing service. We do not sell your personal information.</p>
<h2>Assessment answers</h2><p>Your answers are scored in your browser. They are not sent to us unless you request your report by email, in which case we receive your result summary (not your individual answers).</p>
<h2>Cookies and local storage</h2><p>We store a few small preferences in your browser, such as your theme and cookie choice. These never leave your device.</p>
<h2>Advertising (Google AdSense)</h2>
<p>We use Google AdSense to show ads. Third-party vendors, including Google, use cookies to serve ads based on your prior visits to this website or other websites. Google's use of advertising cookies enables it and its partners to serve ads to you based on your visit to this site and/or other sites on the internet.</p>
<p>You may opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" rel="noopener" target="_blank">Google Ads Settings</a>. You can also opt out of some third-party vendors' use of cookies for personalized advertising at <a href="https://www.aboutads.info/choices/" rel="noopener" target="_blank">www.aboutads.info</a>. Learn more about <a href="https://policies.google.com/technologies/partner-sites" rel="noopener" target="_blank">how Google uses information from sites that use its services</a>.</p>
<p>If you choose "Essential only" in our cookie notice, we ask Google to show non-personalized ads. Visitors in the European Economic Area, the UK and Switzerland may also see Google's consent message.</p>
<h2>Embedded videos</h2><p>YouTube videos are embedded in privacy-enhanced mode and only load after you press play. Once played, YouTube's own privacy policy applies.</p>
<h2>Fonts</h2><p>We load fonts from Google Fonts, which may receive your IP address when the page loads.</p>
<h2>Children</h2><p>This site is intended for adults and is not directed at children under 16. We do not knowingly collect information from children.</p>
<h2>Your rights</h2><p>Depending on where you live (for example under GDPR or CCPA/CPRA), you may have rights to access, correct, delete or restrict the use of your personal information. To make a request, use our <a href="contact.html">contact page</a>.</p>
<h2>Retention</h2><p>We keep form submissions only as long as needed to respond and for reasonable record-keeping, then delete them.</p>
<h2>Changes</h2><p>We may update this policy. The date at the top shows the latest version.</p>
</div>"""
    page("privacy.html", "Privacy and Cookie Policy", "How Work.Style handles your information, cookies, Google AdSense advertising, embedded videos and your privacy rights.", privacy)

    terms = """<div class="wrap page-head"><h1>Terms of use</h1></div>
<div class="wrap article" style="padding-bottom:40px">
<p>By using Work.Style you agree to these terms. If you don't agree, please don't use the site.</p>
<h2>Use of content</h2><p>All content, including guides, assessment items, archetype names and descriptions, tool code and design, is owned by Work.Style or its licensors and protected by copyright. You may read, share links to and print pages for personal or internal team use. You may not copy, republish or sell content without written permission.</p>
<h2>No professional advice</h2><p>Content and tools are for general information and self-reflection. They are not medical, psychological, legal, tax, financial or employment advice. See our <a href="disclaimer.html">disclaimer</a>.</p>
<h2>User submissions</h2><p>When you submit an entry, story or message, you confirm it is your own work and that you have the right to share it. For contest entries you grant us a non-exclusive licence to publish it as described in the contest rules.</p>
<h2>Acceptable use</h2><p>Don't misuse the site: no attempts to disrupt it, scrape it at scale, submit spam, or upload unlawful content.</p>
<h2>Third-party links and ads</h2><p>We link to other websites and show ads from third parties. We aren't responsible for their content or practices.</p>
<h2>Liability</h2><p>The site is provided "as is". To the extent permitted by law, Work.Style is not liable for losses arising from use of the site or reliance on its content.</p>
<h2>Changes</h2><p>We may update these terms; continued use means you accept the updated terms.</p>
</div>"""
    page("terms.html", "Terms of Use", "The terms that apply to using Work.Style, its content, tools, assessment and contests.", terms)

    disc = """<div class="wrap page-head"><h1>Disclaimer</h1></div>
<div class="wrap article" style="padding-bottom:40px">
<h2>General information only</h2><p>Work.Style publishes general information about work styles, productivity, workspaces and team practices. It is not professional advice. Always consider your own circumstances and, where appropriate, consult a qualified professional.</p>
<h2>Assessment</h2><p>The Work Style Assessment is a self-reflection tool. It is not a psychological, clinical, diagnostic or personnel-selection instrument and must not be used to make hiring, promotion, performance or medical decisions.</p>
<h2>Health and ergonomics</h2><p>Ergonomic and wellbeing content is general guidance. If you have pain, numbness, persistent fatigue or mental-health concerns, see a doctor or qualified health professional.</p>
<h2>Calculators</h2><p>Calculators provide estimates based on the figures you enter and simple assumptions. They are not financial, tax or legal advice. Rules on tax, employment and visas vary by location and change over time.</p>
<h2>Advertising and affiliates</h2><p>Work.Style shows ads via Google AdSense and may include clearly labelled sponsored content or partner links. These don't influence our editorial content or assessment results.</p>
<h2>External links</h2><p>We aren't responsible for the content of external websites linked from this site.</p>
</div>"""
    page("disclaimer.html", "Disclaimer", "Important information about the limits of Work.Style's content, assessment, calculators and advertising.", disc)

    tm = f"""<div class="wrap page-head"><h1>Trademark and copyright disclosure</h1></div>
<div class="wrap article" style="padding-bottom:40px">
<h2>Our name</h2><p>"Work.Style" (always written with the dot) is the name of this independent website, operated at the domain work.style. It is used descriptively to refer to people's styles of working.</p>
<h2>No affiliation</h2><p>Work.Style is <strong>not affiliated with, endorsed by, sponsored by or connected to</strong> any company, product, software, service, publication or brand that uses the names or marks "Workstyle", "WorkStyle", "Work Style", "Work-Style" or any similar name, in any country. Any such names or marks belong to their respective owners. We do not use any third party's logo, trade dress or product names to suggest a connection.</p>
<h2>Third-party names</h2><p>Names of companies, books, methods and products mentioned in our guides (for example the Pomodoro Technique®, which is a registered trademark of its creator, and Getting Things Done®) are used for identification and commentary only and belong to their owners. Mention does not imply endorsement.</p>
<h2>Videos</h2><p>Embedded videos remain the property of their creators and publishers and are shown using YouTube's standard embed feature. We do not host or modify them.</p>
<h2>Our copyright</h2><p>The assessment items, scoring model, archetype names and descriptions, guides, tool code, illustrations and site design are original works © Work.Style. All rights reserved.</p>
<h2>Report a concern</h2><p>If you believe content on this site infringes your trademark or copyright, please use the <a href="contact.html">contact page</a> with details of the work and the page concerned, and we'll review it promptly. Owner and partnership inquiries: <a href="{OWNER}" target="_blank" rel="noopener">contact here</a>.</p>
</div>"""
    page("trademark.html", "Trademark and Copyright Disclosure", "Work.Style is an independent website not affiliated with any company or product named Workstyle or similar. Trademark and copyright notice.", tm)

    ty = """<div class="wrap page-head center" style="padding:80px 20px"><h1>Thanks — it's on its way.</h1><p class="lede" style="margin:0 auto 26px">We've received your message and will reply within two business days.</p>
<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap"><a class="btn pencil" href="quiz.html">Take the assessment</a><a class="btn alt" href="guides/">Read a guide</a></div></div>"""
    page("thank-you.html", "Thank You", "Your submission was received.", ty, extra_head='<meta name="robots" content="noindex">')

    nf = """<div class="wrap page-head center" style="padding:80px 20px"><h1>That page isn't here.</h1><p class="lede" style="margin:0 auto 26px">The link may be old or mistyped. Try one of these instead.</p>
<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap"><a class="btn pencil" href="index.html">Home</a><a class="btn alt" href="quiz.html">Assessment</a><a class="btn alt" href="guides/">Guides</a></div></div>"""
    page("404.html", "Page Not Found", "Page not found.", nf, extra_head='<meta name="robots" content="noindex">', dynbase=True)


def build_sitemaps():
    groups = [("Main", [("index.html", "Home"), ("quiz.html", "Work Style Assessment"), ("styles/", "The 8 work styles"), ("tools/", "Free tools"), ("guides/", "Guides"), ("videos.html", "Videos")]),
              ("Work styles", [(f"styles/{s['slug']}.html", s["name"]) for s in STYLES]),
              ("Tools", [(f"tools/{s}.html", t) for s, t, _ in TOOLS]),
              ("Guides", [(f"guides/{g['slug']}.html", g["title"]) for g in GUIDES]),
              ("Get involved", [("teams.html", "Team reports"), ("contests.html", "Contests"), ("support.html", "Support"), ("careers.html", "Careers"), ("advertise.html", "Advertise and sponsor"), ("contact.html", "Contact")]),
              ("About and legal", [("about.html", "About and methodology"), ("privacy.html", "Privacy and cookies"), ("terms.html", "Terms of use"), ("disclaimer.html", "Disclaimer"), ("trademark.html", "Trademark and copyright")])]
    def col(n, items):
        lis = "".join('<li><a href="%s">%s</a></li>' % (h, esc(t)) for h, t in items)
        return f"<div><h3>{n}</h3><ul>{lis}</ul></div>"
    cols = "".join(col(n, items) for n, items in groups)
    body = f'<div class="wrap page-head"><h1>Site map</h1></div><div class="wrap grid-3" style="padding-bottom:50px">{cols}</div>'
    page("sitemap.html", "Site Map", "Every page on Work.Style.", body)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in sorted(set(PAGES)):
        xml += f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n"
    xml += "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(xml)


def static_files():
    w = lambda p, c: open(os.path.join(ROOT, p), "w").write(c)
    w("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /_build/\n\nSitemap: {BASE_URL}/sitemap.xml\n")
    w("ads.txt", "google.com, pub-6620975821265271, DIRECT, f08c47fec0942fa0\n")
    w("_config.yml", "title: Work.Style\nurl: https://work.style\nexclude:\n  - _build\n  - README.md\n  - PROMPTS.md\n  - RESEARCH.md\n  - .gitignore\n")
    w("site.webmanifest", json.dumps({"name": "Work.Style", "short_name": "Work.Style", "start_url": "./index.html", "display": "standalone",
                                       "background_color": "#F6F7F4", "theme_color": "#172033",
                                       "icons": [{"src": "assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, indent=1))
    w("assets/img/favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">' + LOGO[LOGO.index(">") + 1:])


if __name__ == "__main__":
    os.chdir(ROOT)
    write_layout()
    GUIDES.extend(load_guides())
    write_data_js()
    build_home(); build_quiz(); build_styles(); build_tools(); build_guides(); build_videos()
    build_teams(); build_support(); build_contests(); build_careers(); build_advertise(); build_simple()
    build_sitemaps(); static_files()
    print(f"Built {len(PAGES)} indexable pages.")
