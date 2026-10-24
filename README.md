# Barba's Painting & Services

Demo website for Barba's Painting & Services, a house painter in Hialeah, FL.
English and Spanish, 24 pages plus a 404 page, plain HTML and CSS with no framework.

## How it's built

All text lives in `content.py`. `build.py` turns it into the finished site in `site/`.

```
py build.py        # Windows
python3 build.py   # macOS / Linux
```

Needs Python 3.12 or newer and nothing else.

`site/` is committed on purpose. Vercel serves it as-is with no build step, so
**run the build and commit `site/` after every change**.

## Files

| Path | What it is |
|---|---|
| `content.py` | All English and Spanish text, business details, photo links, reviews |
| `build.py` | Generates every page, the schema markup, `sitemap.xml`, `robots.txt` and `llms.txt` |
| `assets/style.css`, `assets/site.js` | Styling, mobile menu, before/after slider |
| `site/` | The built site that gets deployed |
| `vercel.json` | Tells Vercel to serve `site/`, plus caching and header rules |

## Deploying on Vercel

1. Push this repo to GitHub.
2. In Vercel, choose **Add New > Project** and import the repo.
3. Leave **Framework Preset** as **Other**. `vercel.json` already sets the output folder to `site`.
4. Deploy. If Vercel gives an address other than `https://barbas-painting.vercel.app`,
   put the real one in `SITE_URL` in `content.py`, rebuild, commit and push.

## Before this goes live for real

- **Search engines are blocked.** `vercel.json` sends `X-Robots-Tag: noindex` because the
  demo uses a placeholder phone number. Remove that header at launch.
- **Placeholders** marked `TODO` in `content.py`: the phone number, hours and site URL.
- **Photos** are linked from Danny's Instagram and Facebook and stop loading after a few days.
  Replace them with his original photos stored in the repo.
- **Review link:** swap `REVIEW_LINKS["google_write"]` for the official "Ask for reviews" link
  from his Google Business Profile.
- **License and insurance** aren't shown yet. Add them once Danny confirms they're current.
