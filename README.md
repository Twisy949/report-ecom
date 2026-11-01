# report-ecom

Weekly e-commerce trend brief: 3 young, fast-growing Shopify stores in English-speaking markets
(branding, best-sellers, orders, trend, ad platforms, with at least one Pinterest-driven store) plus an
ad-channel watch focused on Pinterest Ads. Data comes from Trend Track, Similarweb public pages and the web.

- `reports/<date>/data.json`: content of one edition.
- `scripts/render_pdf.py`: renders the PDF (same visual identity as the Agent pub project:
  Plus Jakarta Sans, greens #126C49 / #1DE094).
- `scripts/send_discord.py`: posts the summary + PDF to Discord via the `DISCORD_WEBHOOK_URL` secret.
- `.github/workflows/report.yml`: on every push of a new `data.json` to `main`, renders and sends the report.
- `WEEKLY_PROMPT.md`: the weekly procedure. `stores-covered.md`: stores already featured.

Local render: `pip install playwright && python -m playwright install chromium && python scripts/render_pdf.py reports/2026-11-01/data.json`
