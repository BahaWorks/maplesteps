#!/usr/bin/env python3
"""MapleSteps static site builder.

Usage:
  python3 build.py            -> builds dist/ (for Cloudflare Pages, clean URLs)
  python3 build.py --preview  -> builds preview/ (links end in .html, works anywhere)

Edit SITE_URL below once you own your domain, then rebuild.
"""
import json, sys, shutil, html
from pathlib import Path

SITE_URL = "https://maplesteps.ca"   # <-- change to your real domain
BRAND = "MapleSteps"
STUDIO = "BahaWorks"
REVIEWED = "2026-11-06"
LANG_ORDER = ["en", "fr", "ar", "zh", "hi", "fa"]
GUIDES = ["first-steps", "housing", "work", "health", "money"]
PAGES = ["index"] + GUIDES + ["about"]

ROOT = Path(__file__).parent
PREVIEW = "--preview" in sys.argv
OUT = ROOT / ("preview" if PREVIEW else "dist")

LINKS = {
    "id": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/carry-identification.html"},
    "health": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/health-care.html"},
    "healthcare": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/health-care.html"},
    "money": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/money.html"},
    "phone": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/communications.html"},
    "school": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/education.html", "fr": "https://www.canada.ca/fr/immigration-refugies-citoyennete/services/setablir-canada/education.html"},
    "driving": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/driving.html"},
    "language": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/language-skills.html"},
    "housing": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/housing.html"},
    "jobsearch": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/job-search.html"},
    "credentials": {"en": "https://www.canada.ca/en/employment-social-development/programs/foreign-credential-recognition.html"},
    "sin": {"en": "https://www.canada.ca/en/employment-social-development/services/sin.html",
            "fr": "https://www.canada.ca/fr/emploi-developpement-social/services/numero-assurance-sociale.html"},
    "finder": {"en": "https://ircc.canada.ca/english/newcomers/services/index.asp"},
    "cra": {"en": "https://www.canada.ca/benefits-newcomers"},
    "ircc": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/new-immigrants.html",
             "fr": "https://www.canada.ca/fr/immigration-refugies-citoyennete/services/nouveaux-immigrants.html"},
    "jobbank": {"en": "https://www.jobbank.gc.ca", "fr": "https://www.guichetemplois.gc.ca"},
    "211": {"en": "https://211.ca"},
    "988": {"en": "https://988.ca"},
    "taxhelp": {"en": "https://www.canada.ca/get-tax-help"},
    "fraud": {"en": "https://www.canada.ca/taxes-fraud-prevention"},
    "fcac": {"en": "https://www.canada.ca/en/financial-consumer-agency.html",
             "fr": "https://www.canada.ca/fr/agence-consommation-matiere-financiere.html"},
    "adsettings": {"en": "https://adssettings.google.com"},
    "partnersites": {"en": "https://policies.google.com/technologies/partner-sites"},
}

FONTS = {
    "en": ("'Bricolage Grotesque'", "'Noto Sans'", "family=Noto+Sans:wght@400;500;700"),
    "fr": ("'Bricolage Grotesque'", "'Noto Sans'", "family=Noto+Sans:wght@400;500;700"),
    "ar": ("'Noto Kufi Arabic'", "'Noto Sans Arabic'", "family=Noto+Kufi+Arabic:wght@600;800&family=Noto+Sans+Arabic:wght@400;500;700"),
    "fa": ("'Vazirmatn'", "'Vazirmatn'", "family=Vazirmatn:wght@400;500;700;800"),
    "zh": ("'Noto Sans SC'", "'Noto Sans SC'", "family=Noto+Sans+SC:wght@400;500;700;900"),
    "hi": ("'Noto Sans Devanagari'", "'Noto Sans Devanagari'", "family=Noto+Sans+Devanagari:wght@400;500;700;800"),
}
BRAND_FONT = "family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800"
WELCOME = {"en": "Welcome to Canada", "fr": "Bienvenue au Canada", "ar": "أهلاً بك في كندا",
           "zh": "欢迎来到加拿大", "hi": "कनाडा में आपका स्वागत है", "fa": "به کانادا خوش آمدید"}

ICONS = {
    "first-steps": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="m3.5 6 1.2 1.2L7 5M3.5 12l1.2 1.2L7 11"/><circle cx="5" cy="18" r="1.3"/>',
    "housing": '<path d="M3 11 12 4l9 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5h4v5"/>',
    "work": '<rect x="3" y="7.5" width="18" height="12" rx="2"/><path d="M8.5 7.5V5.5a1.5 1.5 0 0 1 1.5-1.5h4a1.5 1.5 0 0 1 1.5 1.5v2"/><path d="M3 13h18"/>',
    "health": '<path d="M12 20s-7.5-4.4-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.6-7.5 10-7.5 10Z"/><path d="M12 10.5v5M9.5 13h5"/>',
    "money": '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/><path d="M6.5 9.5v5M17.5 9.5v5"/>',
}
MARK = ('<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="var(--spruce)"/>'
        '<path d="M10 22 21 11M13.5 10.5H21.5V18.5" fill="none" stroke="var(--on-spruce)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="7.5" y="20" width="5" height="5" rx="1.2" fill="var(--maple)"/></svg>')

e = html.escape
AC_PAGE = ' aria-current="page"'
AC_TRUE = ' aria-current="true"'

def load():
    return {c: json.loads((ROOT / "content" / f"{c}.json").read_text(encoding="utf-8")) for c in LANG_ORDER}

def page_file(slug):
    if PREVIEW:
        return f"{slug}.html"
    return "./" if slug == "index" else slug

def href(from_lang, to_lang, slug):
    target = page_file(slug)
    if from_lang == to_lang:
        return target
    if PREVIEW:
        return f"../{to_lang}/{target}"
    return f"../{to_lang}/" + ("" if slug == "index" else slug)

def canonical(lang, slug):
    return f"{SITE_URL}/{lang}/" + ("" if slug == "index" else slug)

def link_url(key, lang):
    v = LINKS[key]
    return v.get(lang, v["en"])

def icon(slug, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[slug]}</svg>'

ARROW = '<svg class="arrow" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10h11M11 5.5 15.5 10 11 14.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
EXT = '<svg class="ext" viewBox="0 0 20 20" aria-hidden="true"><path d="M8 4.5H4.5v11h11V12M11 4.5h4.5V9M15.5 4.5 9 11" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def ad_slot(name):
    # Paste an AdSense ad unit inside this aside when approved. Empty slots stay hidden.
    return f'<aside class="ad-slot" data-slot="{name}" aria-label="Advertisement"><!-- AD SLOT: {name} --></aside>'

def head(L, slug, P, langs):
    code = L["code"]
    disp, body, fam = FONTS[code]
    alts = "\n".join(f'<link rel="alternate" hreflang="{langs[c]["hreflang"]}" href="{canonical(c, slug)}">' for c in LANG_ORDER)
    xdef = f"{SITE_URL}/" if slug == "index" else canonical("en", slug)
    tracking = "-0.025em" if code in ("en", "fr") else "0"
    lh = {"ar": 1.85, "fa": 1.9, "hi": 1.8, "zh": 1.8}.get(code, 1.6)
    if slug == "index":
        ld = {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND,
              "url": canonical(code, slug), "inLanguage": L["hreflang"], "description": P["desc"]}
    else:
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": P["h1"],
              "description": P["desc"], "inLanguage": L["hreflang"], "dateModified": REVIEWED,
              "mainEntityOfPage": canonical(code, slug),
              "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/assets/icon-512.png"}},
              "image": f"{SITE_URL}/assets/og.png"}
    return f"""<!doctype html>
<html lang="{L['hreflang']}" dir="{L['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(P['title'])}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{e(P['desc'])}">
<link rel="canonical" href="{canonical(code, slug)}">
{alts}
<link rel="alternate" hreflang="x-default" href="{xdef}">
<meta property="og:type" content="{'website' if slug == 'index' else 'article'}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(P['title'])}">
<meta property="og:description" content="{e(P['desc'])}">
<meta property="og:url" content="{canonical(code, slug)}">
<meta property="og:locale" content="{L['og_locale']}">
<meta property="og:image" content="{SITE_URL}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1d5a48">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../assets/icon-512.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{BRAND_FONT}&{fam}&display=swap">
<link rel="stylesheet" href="../assets/style.css">
<style>:root{{--font-display:{disp},'Bricolage Grotesque',system-ui,sans-serif;--font-body:{body},system-ui,-apple-system,'Segoe UI',sans-serif;--tracking:{tracking};--lh:{lh}}}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<!-- Google AdSense: once approved, paste your AdSense <script> tag here, on every page (it's in build.py). -->
</head>"""

def header(L, slug, langs):
    code, ui = L["code"], L["ui"]
    nav = [("index", ui["home"])] + [(g, L["pages"][g]["nav"]) for g in GUIDES]
    nav_html = "".join(
        f'<a href="{href(code, code, s)}"{AC_PAGE if s == slug else ""}>{e(t)}</a>' for s, t in nav)
    langs_html = "".join(
        f'<a href="{href(code, c, slug)}" lang="{langs[c]["hreflang"]}" data-lang="{c}"{AC_TRUE if c == code else ""}>{e(langs[c]["name"])}</a>'
        for c in LANG_ORDER)
    return f"""<body>
<a class="skip" href="#main">{e(ui['skip'])}</a>
<header class="site-head">
  <div class="wrap head-row">
    <a class="brand" href="{href(code, code, 'index')}">{MARK}<span>{BRAND}</span></a>
    <details class="lang">
      <summary aria-label="{e(ui['lang_label'])}"><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7.2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2.8 10h14.4M10 2.8c2 2 3 4.4 3 7.2s-1 5.2-3 7.2c-2-2-3-4.4-3-7.2s1-5.2 3-7.2Z" fill="none" stroke="currentColor" stroke-width="1.5"/></svg><span>{e(L['name'])}</span></summary>
      <div class="lang-menu">{langs_html}</div>
    </details>
  </div>
  <nav class="wrap nav" aria-label="{e(ui['guides'])}">{nav_html}</nav>
</header>"""

def footer(L):
    code, ui = L["code"], L["ui"]
    year = REVIEWED[:4]
    return f"""<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <a class="brand" href="{href(code, code, 'index')}">{MARK}<span>{BRAND}</span></a>
      <p class="muted">{e(ui['tagline'])}</p>
    </div>
    <div>
      <p class="muted small">{e(ui['disclaimer'])}</p>
      <p class="small"><a href="{href(code, code, 'about')}">{e(ui['about_link'])}</a> · © {year} {BRAND}</p>
    </div>
  </div>
  <div class="wrap"><p class="built-by small muted">{e(ui['built_by']).replace('{studio}', '<span dir="ltr">' + STUDIO + '</span>')}</p></div>
</footer>
<script src="../assets/app.js" defer></script>
</body>
</html>
"""

def official_links(L, P):
    items = "".join(
        f'<li><a href="{link_url(k, L["code"])}" target="_blank" rel="noopener">{e(t)}{EXT}</a></li>' for t, k in P["links"])
    return f'<section class="official"><h2>{e(L["ui"]["official"])}</h2><ul>{items}</ul></section>'

def render_index(L, langs):
    code = L["code"]
    P = L["pages"]["index"]
    card = "".join(f'<li><span class="tag">{e(t)}</span><span>{e(x)}</span><i aria-hidden="true"></i></li>' for t, x in P["card_items"])
    first = L["pages"]["first-steps"]
    others = "".join(
        f'<a class="guide" href="{href(code, code, g)}">{icon(g)}<span class="g-title">{e(L["pages"][g]["nav"])}</span><span class="g-text">{e(L["pages"][g]["card"])}</span>{ARROW}</a>'
        for g in GUIDES[1:])
    nums = "".join(f'<div class="num"><span class="n">{e(n)}</span><span class="n-label">{e(a)}</span><span class="n-text">{e(b)}</span></div>' for n, a, b in P["numbers"])
    body = f"""<main id="main">
  <section class="hero">
    <div class="wrap hero-grid">
      <div class="hero-copy">
        <h1>{e(P['h1'])}</h1>
        <p class="lead">{e(P['lead'])}</p>
        <div class="ctas">
          <a class="btn primary" href="{href(code, code, 'first-steps')}">{e(P['cta1'])}{ARROW}</a>
          <a class="btn ghost" href="{link_url('finder', code)}" target="_blank" rel="noopener">{e(P['cta2'])}{EXT}</a>
        </div>
      </div>
      <a class="ticket" href="{href(code, code, 'first-steps')}" aria-label="{e(P['card_title'])}">
        <div class="ticket-head"><span>{e(P['card_title'])}</span><span class="ticket-code">CA · {len(first['checklist'])}</span></div>
        <ol>{card}</ol>
      </a>
    </div>
  </section>
  <div class="wrap">{ad_slot('home-top')}</div>
  <section class="wrap block">
    <div class="block-head"><h2>{e(P['guides_h'])}</h2><p class="muted">{e(P['guides_lead'])}</p></div>
    <div class="guides">
      <a class="guide feature" href="{href(code, code, 'first-steps')}">{icon('first-steps')}<span class="g-title">{e(first['nav'])}</span><span class="g-text">{e(first['card'])}</span>{ARROW}</a>
      {others}
    </div>
  </section>
  <section class="wrap block">
    <div class="block-head"><h2>{e(P['help_h'])}</h2></div>
    <div class="nums">{nums}</div>
  </section>
  <section class="wrap block">
    <div class="help-band">
      <div><h2>{e(P['free_h'])}</h2><p>{e(P['free_p'])}</p></div>
      <a class="btn light" href="{link_url('finder', code)}" target="_blank" rel="noopener">{e(P['free_cta'])}{EXT}</a>
    </div>
  </section>
  <div class="wrap">{ad_slot('home-bottom')}</div>
</main>"""
    return head(L, "index", P, langs) + header(L, "index", langs) + body + footer(L)

def render_sections(P):
    out = []
    for s in P["sections"]:
        if "items" in s:
            lis = "".join(f"<li>{e(i)}</li>" for i in s["items"])
            out.append(f'<section class="sec"><h2>{e(s["h"])}</h2><ul class="ticks">{lis}</ul></section>')
        else:
            out.append(f'<section class="sec"><h2>{e(s["h"])}</h2><p>{e(s["p"])}</p></section>')
    return "".join(out)

def render_guide(L, slug, langs):
    code, ui = L["code"], L["ui"]
    P = L["pages"][slug]
    checklist = ""
    if "checklist" in P:
        items = "".join(
            f'<li><input type="checkbox" id="step-{i+1}" data-check="{i+1}"><label for="step-{i+1}"><span class="tag">{e(w)}</span><strong>{e(t)}</strong><span class="d">{e(d)}</span>'
            f'<a class="step-link" href="{link_url(k, code)}" target="_blank" rel="noopener">{e(ui["official_page"])}{EXT}</a></label></li>'
            for i, (w, t, d, k) in enumerate(P["checklist"]))
        checklist = f"""<section class="checklist" data-progress-text="{e(ui['progress'])}">
  <div class="progress"><span class="progress-text" aria-live="polite">{e(ui['progress'].replace('{done}', '0').replace('{total}', str(len(P['checklist']))))}</span><span class="bar"><span></span></span></div>
  <ol>{items}</ol>
  <p class="small muted check-foot"><span>{e(ui['saved'])}</span> <button type="button" class="reset">{e(ui['reset'])}</button></p>
</section>"""
    mid = ad_slot(f"{slug}-mid")
    nxt = ""
    if slug in GUIDES:
        n = GUIDES[(GUIDES.index(slug) + 1) % len(GUIDES)]
        nxt = f'<a class="next" href="{href(code, code, n)}"><span class="small muted">{e(ui["next"])}</span><span class="next-title">{icon(n)}{e(L["pages"][n]["nav"])}{ARROW}</span></a>'
    ico = icon(slug, "ico big") if slug in ICONS else ""
    body = f"""<main id="main">
  <section class="page-head">
    <div class="wrap narrow">
      <p class="eyebrow">{ico}{e(P['eyebrow'])}</p>
      <h1>{e(P['h1'])}</h1>
      <p class="lead">{e(P['lead'])}</p>
    </div>
  </section>
  <article class="wrap narrow article">
    {checklist}
    {render_sections(P)}
    {mid}
    {official_links(L, P)}
    <p class="small muted reviewed">{e(ui['reviewed'])}</p>
    {nxt}
  </article>
</main>"""
    return head(L, slug, P, langs) + header(L, slug, langs) + body + footer(L)

def render_root(langs):
    tiles = "".join(
        f'<a class="lang-tile" href="{c}/{"index.html" if PREVIEW else ""}" lang="{langs[c]["hreflang"]}" dir="{langs[c]["dir"]}" data-lang="{c}">'
        f'<span class="lt-name">{e(langs[c]["name"])}</span><span class="lt-welcome">{e(WELCOME[c])}</span>{ARROW}</a>'
        for c in LANG_ORDER)
    fams = "&".join([BRAND_FONT, "family=Noto+Sans:wght@400;600", "family=Noto+Sans+Arabic:wght@500", "family=Vazirmatn:wght@500",
                     "family=Noto+Sans+SC:wght@500", "family=Noto+Sans+Devanagari:wght@500"])
    alts = "\n".join(f'<link rel="alternate" hreflang="{langs[c]["hreflang"]}" href="{canonical(c, "index")}">' for c in LANG_ORDER)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{BRAND}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="Free guides for newcomers to Canada in English, French, Arabic, Chinese, Hindi and Persian.">
<link rel="canonical" href="{SITE_URL}/">
{alts}
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/">
<meta property="og:title" content="{BRAND}: free guides for newcomers to Canada">
<meta property="og:description" content="Free guides for newcomers to Canada in six languages.">
<meta property="og:image" content="{SITE_URL}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fams}&display=swap">
<link rel="stylesheet" href="assets/style.css">
<style>:root{{--font-display:'Bricolage Grotesque',system-ui,sans-serif;--font-body:'Noto Sans','Noto Sans Arabic','Vazirmatn','Noto Sans SC','Noto Sans Devanagari',system-ui,sans-serif;--tracking:-0.025em;--lh:1.6}}</style>
</head>
<body class="root-page">
<main id="main" class="root-main">
  <div class="wrap root-wrap">
    <a class="brand big" href="./">{MARK}<span>{BRAND}</span></a>
    <h1>Choose your language</h1>
    <p class="lead muted">Free guides for your first months in Canada.</p>
    <div class="lang-tiles">{tiles}</div>
    <p class="built-by small muted">Designed &amp; built by {STUDIO}</p>
  </div>
</main>
<script src="assets/app.js" defer></script>
</body>
</html>
"""

def render_404(langs):
    links = " · ".join(f'<a href="/{c}/" lang="{langs[c]["hreflang"]}">{e(langs[c]["name"])}</a>' for c in LANG_ORDER)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found · {BRAND}</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="/assets/style.css">
<style>:root{{--font-display:system-ui,sans-serif;--font-body:system-ui,sans-serif;--tracking:0;--lh:1.6}}</style></head>
<body class="root-page"><main class="root-main"><div class="wrap root-wrap"><a class="brand big" href="/">{MARK}<span>{BRAND}</span></a>
<h1>Page not found</h1><p class="lead">{links}</p></div></main></body></html>"""

def build():
    langs = load()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for f in (ROOT / "assets").iterdir():
        shutil.copy(f, OUT / "assets" / f.name)
    count = 0
    for c in LANG_ORDER:
        L = langs[c]
        (OUT / c).mkdir()
        for slug in PAGES:
            html_out = render_index(L, langs) if slug == "index" else render_guide(L, slug, langs)
            (OUT / c / f"{slug}.html").write_text(html_out, encoding="utf-8")
            count += 1
    (OUT / "index.html").write_text(render_root(langs), encoding="utf-8")
    if not PREVIEW:
        (OUT / "404.html").write_text(render_404(langs), encoding="utf-8")
        urls = [f"{SITE_URL}/"] + [canonical(c, s) for c in LANG_ORDER for s in PAGES]
        sm = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        sm += [f"  <url><loc>{u}</loc><lastmod>{REVIEWED}</lastmod></url>" for u in urls]
        sm.append("</urlset>")
        (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {count} pages + root into {OUT}")

if __name__ == "__main__":
    build()
