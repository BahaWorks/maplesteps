# MapleSteps website

A free, six-language guide for newcomers to Canada (English, French, Arabic, Chinese, Hindi, Persian).
42 pages plus a language picker, built as plain HTML so it hosts free on Cloudflare Pages.

## Folders
- `dist/` – the finished website. This is the folder you upload.
- `content/` – all the text, one file per language (`en.json`, `ar.json`, ...). Edit text here.
- `assets/` – design (style.css), checklist script (app.js), logo and share images.
- `build.py` – turns `content/` into `dist/`.

## 1. Put it online (free, about 5 minutes)
1. Create a free account at dash.cloudflare.com.
2. Go to **Workers & Pages → Create → Pages → Upload assets**.
3. Name the project (for example `maplesteps`) and drag in the **dist** folder.
4. Your site is live at `maplesteps.pages.dev` (or whatever name you chose).

## 2. Connect your own domain
1. Buy maplesteps.ca (Porkbun). Turn on auto-renew.
2. In your Cloudflare Pages project: **Custom domains → Set up a domain**, enter `maplesteps.ca`, and follow the steps
   (Cloudflare will tell you which nameservers or DNS record to set at Porkbun).
3. Add `www.maplesteps.ca` too, so both addresses work.
The site is already set up for https://maplesteps.ca (see `SITE_URL` in `build.py`).

## 3. Before applying to Google AdSense
- The site lists `hello@maplesteps.ca` as the contact email. Set up free email forwarding for it
  (Porkbun offers this, or use Cloudflare Email Routing) so messages reach your personal inbox.
- Add the AdSense `<script>` tag where `build.py` says "Google AdSense" (in the `head()` function), then rebuild.
- When AdSense gives you your publisher ID, create `dist/ads.txt` containing:
  `google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0`
- Ad units go inside the empty `<aside class="ad-slot">` boxes (home page top and bottom, middle of each guide). Empty slots stay invisible.
- If you get visitors from Europe or the UK, turn on Google's consent message in AdSense (Privacy & messaging).

## 4. Tell Google about the site
Add the site in Google Search Console and submit `https://yourdomain/sitemap.xml`.

## Rebuilding after edits
```
python3 build.py            # builds dist/ for hosting
python3 build.py --preview  # builds preview/ that opens directly from your computer
```

## Important
Translations were written carefully but should be checked by a native speaker of each language before launch.
Rules (health waiting periods, benefits, licences) change, so review the guides every few months.
