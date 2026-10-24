"""Builds the static site into ./site from content.py.

Run:  py build.py
"""
import hashlib
import json
import shutil
from html import escape
from pathlib import Path

from content import (BUSINESS, GALLERY, HERO_PHOTO, HOME_GALLERY_COUNT, PHOTO_ALT, PHOTOS, REVIEW_LINKS,
                     REVIEWS, SERVICE_DATA, SERVICES, SITE_URL, T)

ROOT = Path(__file__).parent
OUT = ROOT / "site"
ASSETS = ROOT / "assets"
# Changes whenever the CSS or JS changes, so browsers don't keep a stale copy.
ASSET_V = hashlib.sha1((ASSETS / "style.css").read_bytes() + (ASSETS / "site.js").read_bytes()).hexdigest()[:8]

# Folder name of each top-level page, per language.
DIRS = {
    "services": {"en": "services", "es": "servicios"},
    "work": {"en": "work", "es": "trabajos"},
    "reviews": {"en": "reviews", "es": "resenas"},
    "contact": {"en": "contact", "es": "contacto"},
}
NAV = [("services", "nav_services"), ("work", "nav_work"), ("reviews", "nav_reviews"), ("contact", "nav_contact")]


# ---------- URLs ----------

def url_home(lang):
    return T[lang]["prefix"] + "/"


def url_page(lang, kind):
    return f"{T[lang]['prefix']}/{DIRS[kind][lang]}/"


def url_service(lang, key):
    return f"{url_page(lang, 'services')}{SERVICE_DATA[key][lang]['slug']}/"


def page_url(lang, page):
    kind, key = page
    if kind == "home":
        return url_home(lang)
    if kind == "service":
        return url_service(lang, key)
    return url_page(lang, kind)


# ---------- Shared pieces ----------

def e(s):
    return escape(s, quote=True)


_STAR = '<path d="M10 1.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L10 14.9l-5.2 2.7 1-5.8L1.5 7.7l5.9-.9z"/>'
STARS = ('<svg class="stars" viewBox="0 0 100 20" width="80" height="16" aria-hidden="true" focusable="false">'
         + "".join(f'<g transform="translate({i * 20} 0)">{_STAR}</g>' for i in range(5)) + "</svg>")

# A hand-painted brush stroke in the logo's green, used as a small accent.
STROKE = ('<svg class="stroke" viewBox="0 0 120 14" aria-hidden="true" focusable="false" preserveAspectRatio="none">'
          '<path d="M2 9.5c14-4.8 30-6.6 47-6.2 17 .3 30 2.6 46 2.1 8-.2 15-1.3 23-2.9-2 3.4-7.6 6.5-15 7.6-15 2.3-30-.2-46 .2-18 .5-36 3.3-52 2.6-2.2-.1-3.6-1.6-3-3.4z"/>'
          "</svg>")


def business_schema(lang):
    return {
        "@type": "HousePainter",
        "@id": f"{SITE_URL}/#business",
        "name": BUSINESS["name"],
        "legalName": BUSINESS["legal_name"],
        "url": SITE_URL + "/",
        "logo": BUSINESS["logo"],
        "image": PHOTOS["two_story"],
        "telephone": BUSINESS["phone_tel"],
        "email": BUSINESS["email"],
        "foundingDate": BUSINESS["founded"],
        "founder": {"@type": "Person", "name": "Danny Lopez"},
        "address": {
            "@type": "PostalAddress",
            "addressLocality": BUSINESS["city"],
            "addressRegion": BUSINESS["region"],
            "postalCode": BUSINESS["postal"],
            "addressCountry": "US",
        },
        "areaServed": {"@type": "City", "name": "Hialeah", "containedInPlace": {"@type": "State", "name": "Florida"}},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "opens": "08:00", "closes": "18:00",
        }],
        "knowsLanguage": ["en", "es"],
        "sameAs": BUSINESS["same_as"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": T[lang]["services_h2"],
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": SERVICE_DATA[k][lang]["name"], "url": SITE_URL + url_service(lang, k)}}
                for k in SERVICES
            ],
        },
    }


def faq_schema(faq):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq
        ],
    }


def breadcrumb_schema(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE_URL + href}
            for i, (name, href) in enumerate(items)
        ],
    }


def webpage_schema(lang, page, name, kind="WebPage"):
    return {"@type": kind, "url": SITE_URL + page_url(lang, page), "name": name, "inLanguage": lang,
            "about": {"@id": f"{SITE_URL}/#business"}}


def head(lang, page, title, desc, graph, og_image, noindex=False):
    t = T[lang]
    here = SITE_URL + page_url(lang, page)
    en_url = SITE_URL + page_url("en", page)
    es_url = SITE_URL + page_url("es", page)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{here}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="es" href="{es_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(BUSINESS['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{here}">
<meta property="og:image" content="{e(og_image)}">
<meta property="og:locale" content="{t['locale']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(og_image)}">
<meta name="theme-color" content="#1d3a2c">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gloock&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">{t['skip']}</a>
"""


def lang_switch(lang, page):
    # English always listed first; the current language is marked.
    links = []
    for code in ("en", "es"):
        current = ' aria-current="true"' if code == lang else ""
        links.append(f'<a href="{page_url(code, page)}" hreflang="{code}" lang="{code}"{current} aria-label="{T[code]["lang_name"]}">{code.upper()}</a>')
    return f'<div class="lang-switch">{"".join(links)}</div>'


def header(lang, page):
    t = T[lang]
    active = page[0] if page[0] != "service" else "services"
    nav = "\n".join(
        f'      <a href="{url_page(lang, kind)}"{" aria-current=\"page\"" if kind == active else ""}>{t[label]}</a>'
        for kind, label in NAV)
    # On the home page the header floats over the photo masthead until you scroll.
    overlay = " is-overlay" if page[0] == "home" else ""
    return f"""<header class="site-header{overlay}">
  <div class="wrap header-row">
    <a class="brand" href="{url_home(lang)}" aria-label="{e(BUSINESS['name'])}">
      <img class="brand-badge" src="{e(BUSINESS['logo'])}" alt="" width="44" height="44" referrerpolicy="no-referrer">
      <span class="brand-name">Barba's</span>
      <span class="brand-sub">Painting &amp; Services<br>Hialeah, Florida</span>
    </a>
    <nav class="site-nav" id="site-nav" aria-label="{t['menu']}">
{nav}
      <a class="btn btn-call nav-call" href="tel:{BUSINESS['phone_tel']}">{t['call']} {BUSINESS['phone_display']}</a>
    </nav>
    {lang_switch(lang, page)}
    <a class="btn btn-call header-call" href="tel:{BUSINESS['phone_tel']}">{BUSINESS['phone_display']}</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav"><span class="menu-icon" aria-hidden="true"></span><span class="menu-label">{t['menu']}</span></button>
  </div>
</header>
<main id="main">
"""


def footer(lang):
    t = T[lang]
    links = "\n".join(f'        <li><a href="{url_service(lang, k)}">{e(SERVICE_DATA[k][lang]["name"])}</a></li>' for k in SERVICES)
    pages = "\n".join(f'        <li><a href="{url_page(lang, kind)}">{t[label]}</a></li>' for kind, label in NAV)
    return f"""</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <img class="footer-badge" src="{e(BUSINESS['logo'])}" alt="{e(BUSINESS['name'])} logo" width="88" height="88" loading="lazy" referrerpolicy="no-referrer">
      <p class="footer-name">{e(BUSINESS['name'])}</p>
      {STROKE}
      <p>{t['footer_tag']}</p>
      <p><a href="tel:{BUSINESS['phone_tel']}">{BUSINESS['phone_display']}</a><br>
      <a href="mailto:{BUSINESS['email']}">{BUSINESS['email']}</a><br>
      {t['hours']}</p>
    </div>
    <div>
      <p class="footer-head">{t['nav_services']}</p>
      <ul class="footer-list">
{links}
      </ul>
    </div>
    <div>
      <p class="footer-head">{t['menu']}</p>
      <ul class="footer-list">
        <li><a href="{url_home(lang)}">{t['back_home']}</a></li>
{pages}
        <li><a href="{url_page(lang, 'reviews')}#leave">{t['leave_short']}</a></li>
      </ul>
      <p class="footer-head footer-follow">{t['footer_follow']}</p>
      <ul class="footer-list">
        <li><a href="https://www.instagram.com/barbas_paintingservices/" rel="noopener">Instagram</a></li>
        <li><a href="https://www.facebook.com/barbas.painting" rel="noopener">Facebook</a></li>
      </ul>
    </div>
  </div>
  <p class="wrap demo-note">{t['demo_note']} &copy; {BUSINESS['legal_name']}</p>
</footer>
<div class="call-bar">
  <a class="btn btn-call" href="tel:{BUSINESS['phone_tel']}">{t['call']} {BUSINESS['phone_display']}</a>
  <a class="btn btn-ghost" href="sms:{BUSINESS['phone_tel']}">{t['text_us']}</a>
</div>
<script src="/assets/site.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


def img(lang, key, cls="", eager=False, sizes="(max-width: 900px) 50vw, 25vw"):
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img class="{cls}" src="{e(PHOTOS[key])}" alt="{e(PHOTO_ALT[lang][key])}" width="640" height="640" '
            f'sizes="{sizes}" {loading} decoding="async" referrerpolicy="no-referrer">')


def crumbs(lang, trail):
    """trail: [(name, href), ...] after Home; the last item is the current page."""
    t = T[lang]
    parts = [f'<a href="{url_home(lang)}">{t["breadcrumb_home"]}</a>']
    for i, (name, href) in enumerate(trail):
        if i == len(trail) - 1:
            parts.append(f'<span aria-current="page">{e(name)}</span>')
        else:
            parts.append(f'<a href="{href}">{e(name)}</a>')
    return f'<nav class="wrap crumbs" aria-label="Breadcrumb">{" <span aria-hidden=\"true\">/</span> ".join(parts)}</nav>'


def page_hero(h1, lead, extra=""):
    return f"""<section class="page-hero">
  <div class="wrap">
    {STROKE}
    <h1>{e(h1)}</h1>
    <p class="hero-sub">{e(lead)}</p>
    {extra}
  </div>
</section>
"""


def faq_block(lang, faq):
    items = "\n".join(
        f"""    <details class="faq-item">
      <summary>{e(q)}</summary>
      <p>{e(a)}</p>
    </details>""" for q, a in faq)
    return f"""<section class="section faq" aria-labelledby="faq-h">
  <div class="wrap narrow">
    <h2 id="faq-h">{T[lang]['faq_h2']}</h2>
{items}
  </div>
</section>
"""


def review_quotes(rs):
    return "\n".join(
        f"""    <figure class="review" lang="en">
      <blockquote><p>{e(r['text'])}</p></blockquote>
      <figcaption><span>{e(r['name'])}</span>{STARS}<span class="visually-hidden">5/5</span></figcaption>
    </figure>""" for r in rs)


def reviews_block(lang, only=None, heading_id="reviews-h"):
    """Review teaser used on the home and service pages, linking to the reviews page."""
    t = T[lang]
    rs = [r for r in REVIEWS if only is None or only in r["services"]] or REVIEWS
    return f"""<section class="section reviews" aria-labelledby="{heading_id}">
  <div class="wrap">
    <div class="section-head">
      <h2 id="{heading_id}">{t['reviews_h2']}</h2>
      <p class="muted">{t['reviews_note']}</p>
    </div>
    <div class="review-list">
{review_quotes(rs)}
    </div>
    <p class="link-row">
      <a class="text-link" href="{url_page(lang, 'reviews')}">{t['all_reviews']}</a>
      <a class="text-link" href="{url_page(lang, 'reviews')}#leave">{t['leave_short']}</a>
    </p>
  </div>
</section>
"""


def leave_review_block(lang):
    t = T[lang]
    tips = "\n".join(f"        <li>{e(x)}</li>" for x in t["leave_tips"])
    return f"""<section class="section leave" id="leave" aria-labelledby="leave-h">
  <div class="wrap leave-grid">
    <div>
      {STROKE}
      <h2 id="leave-h">{t['leave_h2']}</h2>
      <p>{t['leave_p']}</p>
      <p class="leave-actions">
        <a class="btn btn-call btn-big" href="{e(REVIEW_LINKS['google_write'])}" rel="noopener" target="_blank">{t['leave_btn']}</a>
      </p>
      <p class="muted small">{t['leave_note']}</p>
      <p class="leave-other">{t['leave_other']} <a href="{e(REVIEW_LINKS['yelp'])}" rel="noopener">Yelp</a> {'or' if lang == 'en' else 'o'} <a href="{e(REVIEW_LINKS['bbb'])}" rel="noopener">BBB</a>.</p>
    </div>
    <div class="leave-tips">
      <h3>{t['leave_tips_h3']}</h3>
      <ul class="check-list single">
{tips}
      </ul>
    </div>
  </div>
</section>
"""


def contact_block(lang, heading_level="h2", heading=None):
    t = T[lang]
    heading = heading or t["contact_h2"]
    return f"""<section class="section contact" id="contact" aria-labelledby="contact-h">
  <div class="wrap contact-grid">
    <div>
      <{heading_level} id="contact-h">{heading}</{heading_level}>
      <p>{t['contact_p']}</p>
      <p class="contact-actions">
        <a class="btn btn-call btn-big" href="tel:{BUSINESS['phone_tel']}">{t['call']} {BUSINESS['phone_display']}</a>
        <a class="btn btn-ghost" href="sms:{BUSINESS['phone_tel']}">{t['text_us']}</a>
      </p>
    </div>
    <dl class="contact-facts">
      <div><dt>{t['phone_label']}</dt><dd><a href="tel:{BUSINESS['phone_tel']}">{BUSINESS['phone_display']}</a></dd></div>
      <div><dt>{t['email_label']}</dt><dd><a href="mailto:{BUSINESS['email']}">{BUSINESS['email']}</a></dd></div>
      <div><dt>{t['hours_label']}</dt><dd>{t['hours']}</dd></div>
      <div><dt>{t['area_label']}</dt><dd>{t['area_value']}</dd></div>
    </dl>
  </div>
</section>
"""


def compare_slider(lang):
    t = T[lang]
    ba = e(PHOTOS["before_after"])
    return f"""<figure class="compare-wrap">
      <div class="compare" style="--pos:50%">
        <div class="compare-img compare-before" role="img" aria-label="{t['before']}" style="background-image:url('{ba}')"></div>
        <div class="compare-img compare-after" role="img" aria-label="{t['after']}" style="background-image:url('{ba}')"></div>
        <span class="compare-tag tag-before">{t['before']}</span>
        <span class="compare-tag tag-after">{t['after']}</span>
        <input class="compare-range" type="range" min="0" max="100" value="50" aria-label="{t['slider_label']}">
        <span class="compare-handle" aria-hidden="true"></span>
      </div>
      <figcaption>{t['slider_caption']}</figcaption>
    </figure>"""


def gallery_html(lang, items, feature=True):
    return "\n".join(
        f"""      <figure class="shot{' shot-feature' if feature and i == 0 else ''}">{img(lang, key, sizes='(max-width: 900px) 100vw, 50vw' if feature and i == 0 else '(max-width: 900px) 50vw, 25vw')}<figcaption>{e(en if lang == 'en' else es)}</figcaption></figure>"""
        for i, (key, en, es) in enumerate(items))


def service_rows(lang, detailed=False):
    rows = []
    for k in SERVICES:
        s = SERVICE_DATA[k][lang]
        text = s["intro"] if detailed else s["short"]
        rows.append(f"""      <li><a class="service-row{' service-row-detailed' if detailed else ''}" href="{url_service(lang, k)}">
        <span class="service-name">{e(s['name'])}</span>
        <span class="service-short">{e(text)}</span>
      </a></li>""")
    return "\n".join(rows)


# ---------- Pages ----------

def home(lang):
    t = T[lang]
    page = ("home", None)
    graph = [
        business_schema(lang),
        {"@type": "WebSite", "@id": f"{SITE_URL}/#website", "url": SITE_URL + "/", "name": BUSINESS["name"], "inLanguage": ["en", "es"]},
        webpage_schema(lang, page, t["home_title"]),
        faq_schema(t["home_faq"]),
    ]
    steps = "\n".join(f"""      <li><h3>{e(h)}</h3><p>{e(p)}</p></li>""" for h, p in t["steps"])
    creds = "\n".join(f"      <li>{e(c)}</li>" for c in t["creds"])
    standards = "\n".join(
        f"""      <div class="standard">
        <h3>{e(h)}</h3>
        <p>{e(p)}</p>
        <blockquote lang="en"><p>{e(q)}</p><footer>{e(who)}, Google</footer></blockquote>
      </div>""" for h, p, q, who in t["standards"])
    hp = HERO_PHOTO["base"]
    srcset = ", ".join(f"{hp}?w={w}&q=78&auto=format&fit=crop {w}w" for w in (800, 1200, 1800, 2400))
    body = f"""<section class="masthead" aria-label="{e(BUSINESS['name'])}">
  <img class="masthead-photo" src="{hp}?w=1800&q=78&auto=format&fit=crop" srcset="{srcset}" sizes="100vw"
       alt="{t['hero_alt']}" width="2400" height="1600" fetchpriority="high" decoding="async">
  <div class="masthead-shade" aria-hidden="true"></div>
  <div class="wrap masthead-inner">
    {STROKE}
    <h1 class="masthead-name"><span class="mn-main">Barba's</span> <span class="mn-sub">Painting &amp; Services</span></h1>
    <p class="masthead-line">{t['hero_line']}</p>
    <p class="masthead-actions">
      <a class="btn btn-light btn-big" href="tel:{BUSINESS['phone_tel']}">{t['call']} {BUSINESS['phone_display']}</a>
      <a class="btn btn-outline-light btn-big" href="{url_page(lang, 'work')}">{t['see_work']}</a>
    </p>
    <a class="masthead-rating" href="{url_page(lang, 'reviews')}">{STARS}<span>{t['hero_rating']}</span></a>
  </div>
  <a class="masthead-credit" href="{HERO_PHOTO['credit_url']}" rel="noopener">{t['photo_credit']}: {HERO_PHOTO['credit']} / Unsplash</a>
</section>

<div class="wrap">
  <a class="creds" href="{url_page(lang, 'reviews')}">
    {STARS}
    <ul>
{creds}
    </ul>
  </a>
</div>

<section class="hero" aria-labelledby="intro-h">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <h2 id="intro-h">{t['hero_h1']}</h2>
      <p class="hero-sub">{t['hero_sub']}</p>
    </div>
    {compare_slider(lang)}
  </div>
</section>

<section class="section standards" aria-labelledby="std-h">
  <div class="wrap">
    {STROKE}
    <h2 id="std-h">{t['standards_h2']}</h2>
    <div class="standard-grid">
{standards}
    </div>
  </div>
</section>

<section class="section work" aria-labelledby="work-h">
  <div class="wrap">
    <div class="section-head">
      <h2 id="work-h">{t['work_h2']}</h2>
      <p class="muted">{t['work_intro']}</p>
    </div>
    <div class="gallery gallery-home">
{gallery_html(lang, GALLERY[:HOME_GALLERY_COUNT])}
    </div>
    <p class="link-row"><a class="text-link" href="{url_page(lang, 'work')}">{t['all_work']}</a></p>
  </div>
</section>

<section class="section services" aria-labelledby="services-h">
  <div class="wrap">
    <div class="section-head">
      <h2 id="services-h">{t['services_h2']}</h2>
      <p class="muted">{t['services_intro']}</p>
    </div>
    <ul class="service-list">
{service_rows(lang)}
    </ul>
    <p class="link-row"><a class="text-link" href="{url_page(lang, 'services')}">{t['all_services']}</a></p>
  </div>
</section>

{reviews_block(lang)}
<section class="section meet" aria-labelledby="meet-h">
  <div class="wrap meet-grid">
    <img class="meet-logo" src="{e(BUSINESS['logo'])}" alt="{e(BUSINESS['name'])} logo" width="240" height="240" loading="lazy" referrerpolicy="no-referrer">
    <div>
      <h2 id="meet-h">{t['meet_h2']}</h2>
      <p>{t['meet_p']}</p>
    </div>
  </div>
</section>

<section class="section steps" aria-labelledby="steps-h">
  <div class="wrap">
    <h2 id="steps-h">{t['steps_h2']}</h2>
    <ol class="step-list">
{steps}
    </ol>
  </div>
</section>

{faq_block(lang, t['home_faq'])}
{contact_block(lang)}"""
    # Start fetching the masthead photo before the stylesheet finishes.
    preload = f'<link rel="preload" as="image" imagesrcset="{srcset}" imagesizes="100vw" fetchpriority="high">\n'
    top = head(lang, page, t["home_title"], t["home_desc"], graph, f"{hp}?w=1200&q=78&auto=format&fit=crop")
    top = top.replace('<link rel="preconnect" href="https://fonts.googleapis.com">',
                      '<link rel="preconnect" href="https://images.unsplash.com">\n' + preload
                      + '<link rel="preconnect" href="https://fonts.googleapis.com">', 1)
    return top + header(lang, page) + body + footer(lang)


def services_index(lang):
    t = T[lang]
    page = ("services", None)
    graph = [
        business_schema(lang),
        webpage_schema(lang, page, t["services_title"], "CollectionPage"),
        breadcrumb_schema([(t["breadcrumb_home"], url_home(lang)), (t["nav_services"], url_page(lang, "services"))]),
        {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": SERVICE_DATA[k][lang]["name"], "url": SITE_URL + url_service(lang, k)}
            for i, k in enumerate(SERVICES)]},
    ]
    body = f"""{crumbs(lang, [(t['nav_services'], url_page(lang, 'services'))])}
{page_hero(t['services_h1'], t['services_lead'])}
<section class="section services services-page" aria-label="{t['nav_services']}">
  <div class="wrap">
    <ul class="service-list service-list-detailed">
{service_rows(lang, detailed=True)}
    </ul>
  </div>
</section>

{reviews_block(lang)}
{contact_block(lang)}"""
    return head(lang, page, t["services_title"], t["services_desc"], graph, PHOTOS["two_story"]) + header(lang, page) + body + footer(lang)


def work_page(lang):
    t = T[lang]
    page = ("work", None)
    graph = [
        business_schema(lang),
        webpage_schema(lang, page, t["work_title"], "CollectionPage"),
        breadcrumb_schema([(t["breadcrumb_home"], url_home(lang)), (t["nav_work"], url_page(lang, "work"))]),
    ]
    body = f"""{crumbs(lang, [(t['nav_work'], url_page(lang, 'work'))])}
{page_hero(t['work_h1'], t['work_lead'])}
<section class="section work-feature" aria-label="{t['before']} / {t['after']}">
  <div class="wrap narrow-wide">
    {compare_slider(lang)}
  </div>
</section>

<section class="section work" aria-labelledby="work-h">
  <div class="wrap">
    <h2 id="work-h">{t['work_h2']}</h2>
    <div class="gallery">
{gallery_html(lang, GALLERY)}
    </div>
  </div>
</section>

{contact_block(lang)}"""
    return head(lang, page, t["work_title"], t["work_desc"], graph, PHOTOS["two_story"]) + header(lang, page) + body + footer(lang)


def reviews_page(lang):
    t = T[lang]
    page = ("reviews", None)
    graph = [
        business_schema(lang),
        webpage_schema(lang, page, t["reviews_title"]),
        breadcrumb_schema([(t["breadcrumb_home"], url_home(lang)), (t["nav_reviews"], url_page(lang, "reviews"))]),
    ]
    summary = f"""<p class="rating-summary">{STARS} <strong>5.0</strong> <span>Google</span></p>
    <p class="hero-actions">
      <a class="btn btn-call" href="#leave">{t['leave_short']}</a>
      <a class="btn btn-ghost" href="{e(REVIEW_LINKS['google_read'])}" rel="noopener" target="_blank">{t['reviews_link']}</a>
    </p>"""
    body = f"""{crumbs(lang, [(t['nav_reviews'], url_page(lang, 'reviews'))])}
{page_hero(t['reviews_h1'], t['reviews_lead'], summary)}
<section class="section reviews" aria-label="{t['nav_reviews']}">
  <div class="wrap">
    <p class="muted">{t['reviews_note']}</p>
    <div class="review-list">
{review_quotes(REVIEWS)}
    </div>
  </div>
</section>

{leave_review_block(lang)}
{contact_block(lang)}"""
    return head(lang, page, t["reviews_title"], t["reviews_desc"], graph, PHOTOS["two_story"]) + header(lang, page) + body + footer(lang)


def service(lang, key):
    t = T[lang]
    d = SERVICE_DATA[key]
    s = d[lang]
    page = ("service", key)
    trail = [(t["nav_services"], url_page(lang, "services")), (s["name"], url_service(lang, key))]
    graph = [
        business_schema(lang),
        {"@type": "Service", "name": s["name"], "serviceType": s["name"], "description": s["desc"],
         "provider": {"@id": f"{SITE_URL}/#business"},
         "areaServed": {"@type": "City", "name": "Hialeah"}, "url": SITE_URL + url_service(lang, key)},
        breadcrumb_schema([(t["breadcrumb_home"], url_home(lang))] + trail),
        faq_schema(s["faq"]),
    ]
    included = "\n".join(f"        <li>{e(i)}</li>" for i in s["included"])
    related = "\n".join(
        f'      <li><a href="{url_service(lang, k)}">{e(SERVICE_DATA[k][lang]["name"])}</a></li>'
        for k in SERVICES if k != key)
    if d["photo"]:
        visual = f'<figure class="service-photo">{img(lang, d["photo"], eager=True, sizes="(max-width: 760px) 100vw, 45vw")}</figure>'
    else:
        # No job photos for this service yet: show the paint swatch panel instead.
        visual = '<div class="service-photo swatches" aria-hidden="true"><span></span><span></span><span></span><span></span></div>'
    extra = ""
    if d["gallery"]:
        shots = "\n".join(f'      <figure class="shot">{img(lang, k)}</figure>' for k in d["gallery"])
        extra = f"""<section class="section work" aria-label="{t['work_h2']}">
  <div class="wrap">
    <div class="gallery gallery-small">
{shots}
    </div>
  </div>
</section>
"""
    review_key = {"fences": "fences", "drywall": "drywall"}.get(key, "exterior")
    og = PHOTOS[d["photo"]] if d["photo"] else PHOTOS["two_story"]
    body = f"""{crumbs(lang, trail)}
<section class="service-hero">
  <div class="wrap service-grid">
    <div>
      {STROKE}
      <h1>{e(s['h1'])}</h1>
      <p class="hero-sub">{e(s['intro'])}</p>
      <p class="hero-actions">
        <a class="btn btn-call btn-big" href="tel:{BUSINESS['phone_tel']}">{t['call']} {BUSINESS['phone_display']}</a>
      </p>
      <p class="hero-rating">{STARS} <a href="{url_page(lang, 'reviews')}">{t['hero_rating']}</a></p>
    </div>
    {visual}
  </div>
</section>

<section class="section included" aria-labelledby="inc-h">
  <div class="wrap narrow">
    <h2 id="inc-h">{t['included_h2']}</h2>
    <ul class="check-list">
{included}
    </ul>
  </div>
</section>

{extra}{reviews_block(lang, review_key)}
{faq_block(lang, s['faq'])}
{contact_block(lang, heading=t['service_cta'].format(name=s['name'].lower()))}
<section class="section related" aria-labelledby="rel-h">
  <div class="wrap">
    <h2 id="rel-h">{t['related_h2']}</h2>
    <ul class="related-list">
{related}
    </ul>
  </div>
</section>
"""
    return head(lang, page, s["title"], s["desc"], graph, og) + header(lang, page) + body + footer(lang)


def contact(lang):
    t = T[lang]
    page = ("contact", None)
    graph = [
        business_schema(lang),
        webpage_schema(lang, page, t["contact_title"], "ContactPage"),
        breadcrumb_schema([(t["breadcrumb_home"], url_home(lang)), (t["contact_h1"], url_page(lang, "contact"))]),
    ]
    body = f"""{crumbs(lang, [(t['contact_h1'], url_page(lang, 'contact'))])}
{contact_block(lang, heading_level="h1", heading=t['contact_h1'])}
{reviews_block(lang)}"""
    return head(lang, page, t["contact_title"], t["contact_desc"], graph, PHOTOS["two_story"]) + header(lang, page) + body + footer(lang)


def not_found():
    t = T["en"]
    page = ("home", None)
    body = f"""<section class="section">
  <div class="wrap narrow">
    <h1>{t['not_found_h1']}</h1>
    <p>{t['not_found_p']}</p>
    <p class="hero-actions"><a class="btn btn-ghost" href="/">{t['not_found_home']}</a>
    <a class="btn btn-call" href="tel:{BUSINESS['phone_tel']}">{t['call']} {BUSINESS['phone_display']}</a></p>
  </div>
</section>
"""
    return (head("en", page, t["not_found_title"], t["home_desc"], [business_schema("en")], PHOTOS["two_story"], noindex=True)
            + header("en", page) + body + footer("en"))


# ---------- Extras: sitemap, robots, llms.txt ----------

def sitemap(pages):
    urls = []
    for page in pages:
        en, es = SITE_URL + page_url("en", page), SITE_URL + page_url("es", page)
        for loc in (en, es):
            urls.append(f"""  <url>
    <loc>{loc}</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>
    <xhtml:link rel="alternate" hreflang="es" href="{es}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{en}"/>
  </url>""")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def llms_txt():
    t = T["en"]
    lines = [
        f"# {BUSINESS['name']}",
        "",
        f"> House painting and repair company in Hialeah, Florida, run by Danny Lopez. Registered in Florida since {BUSINESS['founded']}. Rated {BUSINESS['rating']} from {BUSINESS['review_count']} Google reviews. Free estimates. English and Spanish.",
        "",
        f"- Phone: {BUSINESS['phone_display']}",
        f"- Email: {BUSINESS['email']}",
        f"- Hours: {t['hours']}",
        "- Service area: Hialeah, FL",
        "",
        "## Services",
        "",
    ]
    for k in SERVICES:
        s = SERVICE_DATA[k]["en"]
        lines.append(f"- [{s['name']}]({SITE_URL}{url_service('en', k)}): {s['short']}")
    lines += ["", "## Pages", "", f"- [Home]({SITE_URL}/)"]
    lines += [f"- [{t[label]}]({SITE_URL}{url_page('en', kind)})" for kind, label in NAV]
    lines += [f"- [Inicio en español]({SITE_URL}/es/)", ""]
    return "\n".join(lines)


def write(path, text):
    p = OUT / path.lstrip("/")
    if path.endswith("/"):
        p = p / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ASSETS, OUT / "assets")
    shutil.copy(ROOT / "favicon.svg", OUT / "favicon.svg")

    builders = {"services": services_index, "work": work_page, "reviews": reviews_page, "contact": contact}
    pages = ([("home", None)] + [(kind, None) for kind in builders]
             + [("service", k) for k in SERVICES])
    for lang in ("en", "es"):
        write(url_home(lang), home(lang))
        for kind, build in builders.items():
            write(url_page(lang, kind), build(lang))
        for k in SERVICES:
            write(url_service(lang, k), service(lang, k))
    write("/404.html", not_found())
    write("/sitemap.xml", sitemap(pages))
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    write("/llms.txt", llms_txt())
    print(f"Built {len(pages) * 2 + 1} pages into {OUT}")


if __name__ == "__main__":
    main()
