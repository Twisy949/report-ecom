# Weekly trend report: procedure

Goal: every Thursday, a 5-page English PDF on 3 young, fast-growing Shopify stores in English-speaking
markets, plus an ad-channel watch (Pinterest Ads first), delivered to Elyan's Discord.

## 1. Pick 3 new stores (Trend Track connector)
- `search_shops`: created in the last ~12 months, `main_market_countries` US/GB/CA/AU,
  traffic growth > 30–50% over 90 days, `min_monthly_sales` ≥ 40000. Skip anything in `stores-covered.md`.
- At least **one Pinterest-driven store**: add `pixel_ids: ["75554cc2-5498-5524-8d37-3617a4484f38"]`
  (Pinterest Tag), few or no Meta ads, then confirm on similarweb.com/website/<domain>/ that Pinterest is
  the top social source and paid social is high. Say clearly when this is an inference.
- Prefer variety (niches, acquisition channels).

## 2. Analyse each store
- `brief_competitor`: revenue (with min–max range), units, traffic history, best-sellers, emails.
- `search_ads` with `search_in: domain`: Meta ad count, angles, top creatives. Google Ads / TikTok signals from the shop row.
- Homepage (web fetch): branding, hero copy, offers, trust elements, social links.
- Orders: estimate from units and bundle offers and label it as an estimate.
- Flag risky ad practices (health or fear claims) instead of recommending them.

## 3. Ad channel watch
Web search for the past week: Pinterest Ads first, then Meta, TikTok, Google. Date and source every item.

## 4. Write `reports/<YYYY-MM-DD>/data.json`
Same schema as `reports/2026-11-01/data.json` (increment `edition`). Render locally to check the layout:
`python scripts/render_pdf.py reports/<date>/data.json` (5 pages; nothing should overflow).
Do not commit the PDF.

## 5. Deliver
Add the stores to `stores-covered.md`, commit `reports/<date>/data.json` + `stores-covered.md`, push to `main`.
The `report.yml` GitHub Action renders the PDF and posts it to Discord (secret `DISCORD_WEBHOOK_URL`).
Check that the run succeeded. Never put the webhook URL in the repository.
Then reply to Elyan in French with a 3-line summary and the PDF attached.
