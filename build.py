#!/usr/bin/env python3
"""MapleSteps static site builder.

Usage:
  python3 build.py            -> builds dist/ (for Cloudflare Pages, clean URLs)
  python3 build.py --preview  -> builds preview/ (links end in .html, works anywhere)

Edit SITE_URL below once you own your domain, then rebuild.
"""
import json, sys, shutil, html
from urllib.parse import quote
from pathlib import Path

SITE_URL = "https://maplesteps.ca"   # <-- change to your real domain
BRAND = "MapleSteps"
STUDIO = "BahaWorks"
REVIEWED = "2026-11-09"
LANG_ORDER = ["en", "fr", "ar", "zh", "hi", "fa"]
GUIDES = ["first-steps", "housing", "work", "health", "money"]
CITIES = ["toronto", "montreal", "vancouver", "calgary", "ottawa", "edmonton", "winnipeg", "halifax"]
ARTICLES = ["switch-banks", "health-card", "bank-account", "drivers-licence", "first-winter"]
ARTICLE_ICONS = {"switch-banks": "money", "health-card": "health", "bank-account": "money", "drivers-licence": "first-steps", "first-winter": "info"}
CALC = "pay-calculator"
PAGES = ["index"] + GUIDES + ["about", "privacy", "cities"] + CITIES + ["articles"] + [f"articles/{a}" for a in ARTICLES] + [CALC]
CONTACT_EMAIL = "hello@maplesteps.ca"
# city slug -> (official city website, transit agency name, transit website)
CITY_LINKS = {
    "toronto": ("https://www.toronto.ca", "TTC", "https://www.ttc.ca"),
    "montreal": ("https://montreal.ca", "STM", "https://www.stm.info"),
    "vancouver": ("https://vancouver.ca", "TransLink", "https://www.translink.ca"),
    "calgary": ("https://www.calgary.ca", "Calgary Transit", "https://www.calgarytransit.com"),
    "ottawa": ("https://ottawa.ca", "OC Transpo", "https://www.octranspo.com"),
    "edmonton": ("https://www.edmonton.ca", "Edmonton Transit Service", "https://www.edmonton.ca/ets"),
    "winnipeg": ("https://www.winnipeg.ca", "Winnipeg Transit", "https://winnipegtransit.com"),
    "halifax": ("https://www.halifax.ca", "Halifax Transit", "https://www.halifax.ca/transportation/halifax-transit"),
}

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
    "youradchoices": {"en": "https://youradchoices.ca/en/", "fr": "https://youradchoices.ca/fr/"},
    "aboutads": {"en": "https://www.aboutads.info/choices"},
    "ohip": {"en": "https://www.ontario.ca/page/apply-ohip-and-get-health-card", "fr": "https://www.ontario.ca/fr/page/demande-de-carte-sante-et-dassurance-sante"},
    "bcmsp": {"en": "https://www2.gov.bc.ca/gov/content/health/health-drug-coverage/msp"},
    "ramq": {"en": "https://www.ramq.gouv.qc.ca/en", "fr": "https://www.ramq.gouv.qc.ca/fr"},
    "ahcip": {"en": "https://www.alberta.ca/ahcip"},
    "fcac_open": {"en": "https://www.canada.ca/en/financial-consumer-agency/services/banking/opening-bank-account.html"},
    "cdic": {"en": "https://www.cdic.ca/", "fr": "https://www.sadc.ca/"},
    "lowcost": {"en": "https://www.canada.ca/en/financial-consumer-agency/services/industry/laws-regulations/low-cost-no-cost-accounts"},
    "cra_dd": {"en": "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/direct-deposit/individuals.html"},
    "close_acct": {"en": "https://www.getsmarteraboutmoney.ca/learning-path/bank-accounts/how-to-close-a-bank-account/"},
    "drivetest": {"en": "https://www.drivetest.ca/licences/licence-exchanges/licence_exchange.html"},
    "icbc": {"en": "https://www.icbc.com/driver-licensing"},
    "saaq": {"en": "https://saaq.gouv.qc.ca/en/", "fr": "https://saaq.gouv.qc.ca/"},
    "abdl": {"en": "https://www.alberta.ca/exchange-non-alberta-licences"},
    "weather": {"en": "https://weather.gc.ca", "fr": "https://meteo.gc.ca"},
    "windchill": {"en": "https://www.canada.ca/content/dam/eccc/migration/main/meteo-weather/80b0f2af-9697-4bee-ab17-d401ebba5b4b/windchill_factsheet_en.pdf"},
    "climate": {"en": "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada/land-climate.html"},
    "via": {"en": "https://www.viarail.ca/en", "fr": "https://www.viarail.ca/fr"},
    "pdoc": {"en": "https://www.canada.ca/pdoc"},
    "taxrates": {"en": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/tax-rates-brackets/current-year.html"},
    "rq_changes": {"en": "https://www.revenuquebec.ca/en/businesses/source-deductions-and-employer-contributions/employers-principal-changes-for-2026/"},
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
    "cities": '<path d="M3 20h18"/><path d="M5 20V9l5-3v14"/><path d="M10 20V4l9 4v12"/><path d="M13 10h3M13 13h3M13 16h3M7 12h1M7 15h1"/>',
    "pin": '<path d="M12 21s-6.5-6.2-6.5-11.2a6.5 6.5 0 0 1 13 0C18.5 14.8 12 21 12 21Z"/><circle cx="12" cy="9.8" r="2.3"/>',
    "transit": '<rect x="5" y="3.5" width="14" height="13" rx="3"/><path d="M5 11h14M8.5 20l1.5-3.5M15.5 20 14 16.5"/><circle cx="8.8" cy="13.8" r=".9"/><circle cx="15.2" cy="13.8" r=".9"/>',
    "star": '<path d="m12 4 2.4 4.9 5.4.8-3.9 3.8.9 5.4L12 16.4 7.2 18.9l.9-5.4-3.9-3.8 5.4-.8Z"/>',
    "info": '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5M12 8h.01"/>',
}
MARK = ('<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="var(--spruce)"/>'
        '<path d="M10 22 21 11M13.5 10.5H21.5V18.5" fill="none" stroke="var(--on-spruce)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="7.5" y="20" width="5" height="5" rx="1.2" fill="var(--maple)"/></svg>')

e = html.escape
AC_PAGE = ' aria-current="page"'
AC_TRUE = ' aria-current="true"'

def load():
    out = {}
    for c in LANG_ORDER:
        L = json.loads((ROOT / "content" / f"{c}.json").read_text(encoding="utf-8"))
        L["cities"] = json.loads((ROOT / "content" / "cities" / f"{c}.json").read_text(encoding="utf-8"))
        L["articles"] = json.loads((ROOT / "content" / "articles" / f"{c}.json").read_text(encoding="utf-8"))
        L["tools"] = json.loads((ROOT / "content" / "tools" / f"{c}.json").read_text(encoding="utf-8"))
        out[c] = L
    return out

CUR = {"slug": "index"}
V = "1"

def page_file(slug):
    if slug == "articles":
        return "articles/index.html" if PREVIEW else "articles/"
    if PREVIEW:
        return f"{slug}.html"
    return "./" if slug == "index" else slug

def up():
    return "../" if ("/" in CUR["slug"] or CUR["slug"] == "articles") else ""

def href(from_lang, to_lang, slug):
    if from_lang == to_lang:
        if not PREVIEW and slug == "index":
            return up() + "./" if not up() else up()
        return up() + page_file(slug)
    if PREVIEW:
        return f"{up()}../{to_lang}/{page_file(slug)}"
    return f"{up()}../{to_lang}/" + ("" if slug == "index" else page_file(slug))

def canonical(lang, slug):
    if slug == "articles":
        return f"{SITE_URL}/{lang}/articles/"
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
    if slug == CALC:
        ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": P["h1"], "url": canonical(code, slug),
              "description": P["desc"], "inLanguage": L["hreflang"], "applicationCategory": "FinanceApplication",
              "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CAD"}}
    elif slug == "index":
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
<link rel="icon" href="{up()}../assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{up()}../assets/icon-512.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{BRAND_FONT}&{fam}&display=swap">
<link rel="stylesheet" href="{up()}../assets/style.css?v={V}">
<style>:root{{--font-display:{disp},'Bricolage Grotesque',system-ui,sans-serif;--font-body:{body},system-ui,-apple-system,'Segoe UI',sans-serif;--tracking:{tracking};--lh:{lh}}}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<!-- Google AdSense: once approved, paste your AdSense <script> tag here, on every page (it's in build.py). -->
</head>"""

def header(L, slug, langs):
    code, ui = L["code"], L["ui"]
    nav = [("index", ui["home"])] + [(g, L["pages"][g]["nav"]) for g in GUIDES] + [("cities", L["cities"]["ui"]["nav"]), ("articles", L["articles"]["ui"]["nav"])]
    active = "cities" if slug in CITIES else ("articles" if slug.startswith("articles") else slug)
    nav_html = "".join(
        f'<a href="{href(code, code, s)}"{AC_PAGE if s == active else ""}>{e(t)}</a>' for s, t in nav)
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
      <p class="small foot-links"><a href="{href(code, code, 'about')}">{e(ui['about_link'])}</a> · <a href="{href(code, code, 'privacy')}">{e(ui['privacy_link'])}</a> · <a href="{href(code, code, CALC)}">{e(L['tools']['nav'])}</a> · <a href="mailto:{CONTACT_EMAIL}">{e(ui['contact_link'])}: <span dir="ltr">{CONTACT_EMAIL}</span></a></p>
      <p class="small muted">© {year} {BRAND}</p>
    </div>
  </div>
  <div class="wrap"><p class="built-by small muted">{e(ui['built_by']).replace('{studio}', '<span dir="ltr">' + STUDIO + '</span>')}</p></div>
</footer>
<script src="{up()}../assets/app.js?v={V}" defer></script>
</body>
</html>
"""

def official_links(L, P):
    if not P.get("links"):
        return ""
    items = "".join(
        f'<li><a href="{link_url(k, L["code"])}" target="_blank" rel="noopener">{e(t)}{EXT}</a></li>' for t, k in P["links"])
    heading = L["ui"]["links_h"] if P.get("eyebrow") and P is L["pages"].get("privacy") else L["ui"]["official"]
    return f'<section class="official"><h2>{e(heading)}</h2><ul>{items}</ul></section>'

def render_index(L, langs):
    code = L["code"]
    P = L["pages"]["index"]
    card = "".join(f'<li><span class="tag">{e(t)}</span><span>{e(x)}</span><i aria-hidden="true"></i></li>' for t, x in P["card_items"])
    first = L["pages"]["first-steps"]
    others = "".join(
        f'<a class="guide" href="{href(code, code, g)}">{icon(g)}<span class="g-title">{e(L["pages"][g]["nav"])}</span><span class="g-text">{e(L["pages"][g]["card"])}</span>{ARROW}</a>'
        for g in GUIDES[1:])
    C = L["cities"]
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
    <div class="block-head"><h2>{e(L['articles']['home']['h'])}</h2><p class="muted">{e(L['articles']['home']['lead'])}</p></div>
    {article_list(L)}
  </section>
  {tools_block(L)}
  <section class="wrap block">
    <div class="block-head"><h2>{e(C['home']['h'])}</h2><p class="muted">{e(C['home']['lead'])}</p></div>
    {city_grid(L)}
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
    mid = ad_slot(f"{slug}-mid") if slug in GUIDES else ""
    nxt = ""
    if slug in GUIDES:
        n = GUIDES[(GUIDES.index(slug) + 1) % len(GUIDES)]
        nxt = f'<a class="next" href="{href(code, code, n)}"><span class="small muted">{e(ui["next"])}</span><span class="next-title">{icon(n)}{e(L["pages"][n]["nav"])}{ARROW}</span></a>'
    ico = icon(slug, "ico big") if slug in ICONS else ""
    rel_arts = [a for a in ARTICLES if L["articles"]["items"][a]["related"] == slug]
    if rel_arts:
        lis = "".join(f'<li><a href="{href(code, code, "articles/" + a)}">{e(L["articles"]["items"][a]["h1"])}</a></li>' for a in rel_arts)
        nxt = f'<section class="more-arts"><h2>{e(L["articles"]["ui"]["nav"])}</h2><ul>{lis}</ul></section>' + nxt
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
    {tool_cta(L) if slug in ("work", "money") else ""}
    {official_links(L, P)}
    {('<p class="small muted reviewed">' + e(ui['reviewed']) + '</p>') if slug in GUIDES else ''}
    {share_bar(L, slug, P['title']) if slug in GUIDES else ''}
    {nxt}
  </article>
</main>"""
    return head(L, slug, P, langs) + header(L, slug, langs) + body + footer(L)

def city_grid(L):
    code, C = L["code"], L["cities"]
    cards = "".join(
        f'<a class="city-card" href="{href(code, code, c)}"><span class="cc-prov">{icon("pin", "ico tiny")}{e(C["cities"][c]["prov"])}</span>'
        f'<span class="cc-name">{e(C["cities"][c]["name"])}</span><span class="cc-text">{e(C["cities"][c]["card"])}</span>{ARROW}</a>'
        for c in CITIES)
    return f'<div class="city-grid">{cards}</div>'

def render_cities_index(L, langs):
    code, C = L["code"], L["cities"]
    P = C["index"]
    travel = "".join(f"<li>{e(t)}</li>" for t in P["travel"])
    body = f"""<main id="main">
  <section class="page-head">
    <div class="wrap">
      <p class="eyebrow">{icon("cities", "ico big")}{e(P['eyebrow'])}</p>
      <h1>{e(P['h1'])}</h1>
      <p class="lead">{e(P['lead'])}</p>
    </div>
  </section>
  <section class="wrap block">{city_grid(L)}</section>
  <div class="wrap">{ad_slot('cities-mid')}</div>
  <article class="wrap narrow article">
    <section class="sec"><h2>{e(P['travel_h'])}</h2><ul class="ticks">{travel}</ul></section>
    <section class="official"><h2>{e(L["ui"]["official"])}</h2><ul><li><a href="{link_url('via', code)}" target="_blank" rel="noopener">{e(P['travel_link'])}{EXT}</a></li></ul></section>
    <p class="small muted reviewed">{e(L['ui']['reviewed'])}</p>
  </article>
</main>"""
    return head(L, "cities", P, langs) + header(L, "cities", langs) + body + footer(L)

def render_city(L, slug, langs):
    code, C = L["code"], L["cities"]
    U, P = C["ui"], C["cities"][slug]
    city_url, agency, transit_url = CITY_LINKS[slug]
    page = {"title": P["title"], "desc": P["desc"], "h1": P["name"]}
    transit = "".join(f"<li>{e(t)}</li>" for t in P["transit"])
    EN = LANGS_ALL["en"]["cities"]["cities"][slug]
    def en_tag(local, eng):
        return "" if code in ("en", "fr") or local == eng else f'<span class="en-name" lang="en" dir="ltr">{e(eng)}</span>'
    sights = "".join(f'<li><strong>{e(n)}</strong>{en_tag(n, EN["see"][i][0])}<span>{e(d)}</span></li>' for i, (n, d) in enumerate(P["see"]))
    tips = "".join(f"<li>{e(t)}</li>" for t in P["tips"])
    n = CITIES[(CITIES.index(slug) + 1) % len(CITIES)]
    body = f"""<main id="main">
  <section class="page-head">
    <div class="wrap narrow">
      <p class="eyebrow"><a href="{href(code, code, 'cities')}">{icon("cities", "ico big")}{e(U['nav'])}</a></p>
      <h1>{e(P['name'])}{en_tag(P['name'], EN['name']).replace('en-name', 'en-name h1-en')}</h1>
      <p class="lead">{e(P['lead'])}</p>
      <dl class="facts">
        <div><dt>{e(U['province'])}</dt><dd>{e(P['prov'])}</dd></div>
        <div><dt>{e(U['timezone'])}</dt><dd>{e(P['tz'])}</dd></div>
      </dl>
    </div>
  </section>
  <article class="wrap narrow article">
    <section class="sec"><h2>{icon("transit", "ico h-ico")}{e(U['getting_around'])}</h2><ul class="ticks">{transit}</ul><p class="small muted">{e(U['fares_note'])}</p></section>
    <section class="sec"><h2>{icon("star", "ico h-ico")}{e(U['see_do'])}</h2><ul class="sights">{sights}</ul></section>
    {ad_slot(slug + '-mid')}
    <section class="sec"><h2>{icon("info", "ico h-ico")}{e(U['tips'])}</h2><ul class="ticks">{tips}</ul></section>
    <section class="official"><h2>{e(L['ui']['official'])}</h2><ul>
      <li><a href="{city_url}" target="_blank" rel="noopener">{e(U['city_site'].replace('{name}', P['name']))}{EXT}</a></li>
      <li><a href="{transit_url}" target="_blank" rel="noopener">{e(U['transit_site'].replace('{agency}', agency))}{EXT}</a></li>
    </ul></section>
    <p class="small muted reviewed">{e(L['ui']['reviewed'])}</p>
    {share_bar(L, slug, P['title'])}
    <div class="next-row">
      <a class="next" href="{href(code, code, n)}"><span class="small muted">{e(L['ui']['next'])}</span><span class="next-title">{icon("pin")}{e(C['cities'][n]['name'])}{ARROW}</span></a>
      <a class="all-link" href="{href(code, code, 'cities')}">{e(U['all_cities'])}</a>
    </div>
  </article>
</main>"""
    return head(L, slug, page, langs) + header(L, slug, langs) + body + footer(L)

def article_list(L):
    code, A = L["code"], L["articles"]
    cards = "".join(
        f'<a class="art-card" href="{href(code, code, "articles/" + a)}">{icon(ARTICLE_ICONS[a])}'
        f'<span class="g-title">{e(A["items"][a]["h1"])}</span><span class="g-text">{e(A["items"][a]["summary"])}</span>'
        f'<span class="art-more">{e(A["ui"]["read"])}{ARROW}</span></a>' for a in ARTICLES)
    return f'<div class="art-grid">{cards}</div>'

def render_articles_index(L, langs):
    code, A = L["code"], L["articles"]
    P = A["index"]
    body = f"""<main id="main">
  <section class="page-head"><div class="wrap">
    <p class="eyebrow">{icon("first-steps", "ico big")}{e(P['eyebrow'])}</p>
    <h1>{e(P['h1'])}</h1><p class="lead">{e(P['lead'])}</p>
  </div></section>
  <section class="wrap block">{article_list(L)}</section>
  <div class="wrap">{ad_slot('articles-mid')}</div>
</main>"""
    return head(L, "articles", P, langs) + header(L, "articles", langs) + body + footer(L)

def render_article(L, slug, langs):
    code, A = L["code"], L["articles"]
    key = slug.split("/", 1)[1]
    P = A["items"][key]
    page = {"title": P["title"], "desc": P["desc"], "h1": P["h1"]}
    toc = "".join(f'<li><a href="#s{i+1}">{e(s["h"])}</a></li>' for i, s in enumerate(P["sections"]))
    secs = []
    for i, s in enumerate(P["sections"]):
        inner = ('<ul class="ticks">' + "".join(f"<li>{e(x)}</li>" for x in s["items"]) + "</ul>") if "items" in s else f'<p>{e(s["p"])}</p>'
        secs.append(f'<section class="sec" id="s{i+1}"><h2>{e(s["h"])}</h2>{inner}</section>')
        if i == 1:
            secs.append(ad_slot(key + "-mid"))
    rel = P["related"]
    rel_name = L["cities"]["ui"]["nav"] if rel == "cities" else L["pages"][rel]["nav"]
    rel_icon = "cities" if rel == "cities" else rel
    others = [a for a in ARTICLES if a != key]
    more = "".join(f'<li><a href="{href(code, code, "articles/" + a)}">{e(A["items"][a]["h1"])}</a></li>' for a in others)
    body = f"""<main id="main">
  <section class="page-head"><div class="wrap narrow">
    <p class="eyebrow"><a href="{href(code, code, 'articles')}">{icon(ARTICLE_ICONS[key], "ico big")}{e(A['ui']['nav'])}</a></p>
    <h1>{e(P['h1'])}</h1>
    {('<p class="h1-sub">' + e(P['sub']) + '</p>') if P.get('sub') else ''}
    <p class="lead">{e(P['lead'])}</p>
    <p class="small muted">{e(A['ui']['updated'])}</p>
  </div></section>
  <article class="wrap narrow article">
    <nav class="toc" aria-label="{e(A['ui']['in_this'])}"><p class="toc-h">{e(A['ui']['in_this'])}</p><ol>{toc}</ol></nav>
    {"".join(secs)}
    {official_links(L, P)}
    <p class="small muted reviewed">{e(L['ui']['reviewed'])}</p>
    {tool_cta(L) if rel in ("work", "money") else ""}
    {share_bar(L, slug, P['title'])}
    <a class="next" href="{href(code, code, rel)}"><span class="small muted">{e(A['ui']['related'])}</span><span class="next-title">{icon(rel_icon)}{e(rel_name)}{ARROW}</span></a>
    <section class="more-arts"><h2>{e(A['ui']['more'])}</h2><ul>{more}</ul></section>
  </article>
</main>"""
    return head(L, slug, page, langs) + header(L, slug, langs) + body + footer(L)

NEWTAB = ' target="_blank" rel="noopener"'
NETCLS = ' class="c-net"'
SHARE_ICO = '<svg class="ico tiny" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5.5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="18.5" r="2.5"/><path d="m8.2 10.8 7.6-4.1M8.2 13.2l7.6 4.1"/></svg>'

def share_bar(L, slug, title):
    ui = L["ui"]
    url = canonical(L["code"], slug)
    u, t = quote(url, safe=""), quote(title, safe="")
    links = [
        ("WhatsApp", f"https://wa.me/?text={t}%20{u}", "wa"),
        ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={u}", ""),
        ("Telegram", f"https://t.me/share/url?url={u}&text={t}", ""),
        ("X", f"https://x.com/intent/post?url={u}&text={t}", ""),
        (ui["email"], f"mailto:?subject={t}&body={u}", ""),
    ]
    btns = "".join(f'<a class="sh {c}" href="{e(h)}"{"" if h.startswith("mailto") else NEWTAB}>{e(n)}</a>' for n, h, c in links)
    return (f'<section class="share" aria-label="{e(ui["share_h"])}"><p class="share-h">{SHARE_ICO}{e(ui["share_h"])}</p><div class="share-row">{btns}'
            f'<button type="button" class="sh copy" data-url="{e(url)}" data-done="{e(ui["copied"])}">{e(ui["copy"])}</button>'
            f'<button type="button" class="sh native" hidden data-url="{e(url)}" data-title="{e(title)}">{e(ui["more"])}</button></div></section>')

def tool_cta(L):
    code = L["code"]
    return f'<a class="tool-cta" href="{href(code, code, CALC)}">{icon("money")}<span>{e(L["ui"]["tool_try"])}</span>{ARROW}</a>'

def tools_block(L):
    code, T = L["code"], L["tools"]
    return f"""<section class="wrap block">
    <div class="block-head"><h2>{e(T['home_h'])}</h2><p class="muted">{e(T['home_lead'])}</p></div>
    <a class="guide feature tool" href="{href(code, code, CALC)}">{icon('money')}<span class="g-title">{e(T['h1'])}</span><span class="g-text">{e(T['card'])}</span>{ARROW}</a>
  </section>"""

NUM_LOCALE = {"en": "en-CA", "fr": "fr-CA", "ar": "en-CA", "zh": "zh-CN", "hi": "hi-IN-u-nu-latn", "fa": "en-CA"}

def render_calc(L, langs):
    code, T = L["code"], L["tools"]
    provs = "".join(f'<option value="{k}">{e(v)}</option>' for k, v in T["provs"].items())
    pers = "".join(f'<option value="{k}"{" selected" if k == "year" else ""}>{e(v)}</option>' for k, v in T["per"].items())
    outs = "".join(f'<div class="c-out"><span class="c-num" data-out="{k}">–</span><span class="c-lab">{e(v)}</span></div>' for k, v in T["r_per"].items())
    rows = "".join(f'<tr data-row="{k}"{NETCLS if k == "net" else ""}><th scope="row">{e(v)}</th><td data-y="{k}">–</td><td data-m="{k}">–</td></tr>' for k, v in T["rows"].items())
    i18n = json.dumps({"avg": T["avg"], "empty": T["empty"]}, ensure_ascii=False).replace("</", "<\\/")
    page = {"title": T["title"], "desc": T["desc"], "h1": T["h1"]}
    secs = render_sections(T)
    body = f"""<main id="main">
  <section class="page-head"><div class="wrap narrow">
    <p class="eyebrow">{icon("money", "ico big")}{e(T['eyebrow'])}</p>
    <h1>{e(T['h1'])}</h1>
    <p class="lead">{e(T['lead'])}</p>
  </div></section>
  <article class="wrap narrow article">
    <section class="calc" data-locale="{NUM_LOCALE[code]}">
      <form class="c-form" onsubmit="return false">
        <label class="c-field"><span>{e(T['f_prov'])}</span><select name="prov">{provs}</select></label>
        <div class="c-pair">
          <label class="c-field"><span>{e(T['f_pay'])}</span><input name="pay" type="text" inputmode="decimal" autocomplete="off" dir="ltr" placeholder="60000"></label>
          <label class="c-field"><span>{e(T['f_per'])}</span><select name="per">{pers}</select></label>
        </div>
        <label class="c-field c-hours" hidden><span>{e(T['f_hours'])}</span><input name="hours" type="text" inputmode="decimal" value="40" dir="ltr"></label>
      </form>
      <div class="c-result" aria-live="polite">
        <p class="c-h">{e(T['r_h'])}</p>
        <div class="c-outs">{outs}</div>
        <p class="c-avg small muted">{e(T['empty'])}</p>
        <table class="c-table"><thead><tr><td></td><th scope="col">{e(T['col_year'])}</th><th scope="col">{e(T['per']['month'])}</th></tr></thead><tbody>{rows}</tbody></table>
      </div>
      <p class="small muted c-note">{e(T['note'])}</p>
      <script type="application/json" class="c-i18n">{i18n}</script>
    </section>
    {secs}
    {ad_slot('calc-mid')}
    {official_links(L, T)}
    <p class="small muted reviewed">{e(L['ui']['reviewed'])}</p>
    {share_bar(L, CALC, T['title'])}
  </article>
</main>
<script src="{up()}../assets/pay.js?v={V}" defer></script>"""
    return head(L, CALC, page, langs) + header(L, CALC, langs) + body + footer(L)

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
<link rel="stylesheet" href="assets/style.css?v={V}">
<style>:root{{--font-display:'Bricolage Grotesque',system-ui,sans-serif;--font-body:'Noto Sans','Noto Sans Arabic','Vazirmatn','Noto Sans SC','Noto Sans Devanagari',system-ui,sans-serif;--tracking:-0.025em;--lh:1.6}}</style>
</head>
<body class="root-page">
<main id="main" class="root-main">
  <div class="wrap root-wrap">
    <a class="brand big" href="./">{MARK}<span>{BRAND}</span></a>
    <h1>Choose your language</h1>
    <p class="lead muted">Free guides for your first months in Canada.</p>
    <div class="lang-tiles">{tiles}</div>
    <p class="small foot-links"><a href="en/{page_file('about')}">About</a> · <a href="en/{page_file('privacy')}">Privacy Policy</a> · <a href="mailto:{CONTACT_EMAIL}">Contact: {CONTACT_EMAIL}</a></p>
    <p class="built-by small muted">Designed &amp; built by {STUDIO}</p>
  </div>
</main>
<script src="assets/app.js?v={V}" defer></script>
</body>
</html>
"""

def render_404(langs):
    links = " · ".join(f'<a href="/{c}/" lang="{langs[c]["hreflang"]}">{e(langs[c]["name"])}</a>' for c in LANG_ORDER)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found · {BRAND}</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="/assets/style.css?v={V}">
<style>:root{{--font-display:system-ui,sans-serif;--font-body:system-ui,sans-serif;--tracking:0;--lh:1.6}}</style></head>
<body class="root-page"><main class="root-main"><div class="wrap root-wrap"><a class="brand big" href="/">{MARK}<span>{BRAND}</span></a>
<h1>Page not found</h1><p class="lead">{links}</p></div></main></body></html>"""

LANGS_ALL = {}

def asset_version():
    import hashlib
    h = hashlib.md5()
    for n in ("style.css", "app.js", "pay.js"):
        h.update((ROOT / "assets" / n).read_bytes())
    return h.hexdigest()[:8]

def build():
    global V
    V = asset_version()
    langs = load()
    LANGS_ALL.update(langs)
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for f in (ROOT / "assets").iterdir():
        shutil.copy(f, OUT / "assets" / f.name)
    count = 0
    for c in LANG_ORDER:
        L = langs[c]
        (OUT / c).mkdir()
        (OUT / c / "articles").mkdir()
        for slug in PAGES:
            CUR["slug"] = slug
            if slug == "index":
                html_out = render_index(L, langs)
            elif slug == "cities":
                html_out = render_cities_index(L, langs)
            elif slug in CITIES:
                html_out = render_city(L, slug, langs)
            elif slug == "articles":
                html_out = render_articles_index(L, langs)
            elif slug.startswith("articles/"):
                html_out = render_article(L, slug, langs)
            elif slug == CALC:
                html_out = render_calc(L, langs)
            else:
                html_out = render_guide(L, slug, langs)
            dest = OUT / c / ("articles/index.html" if slug == "articles" else f"{slug}.html")
            dest.write_text(html_out, encoding="utf-8")
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
