"""Render a weekly trend report (reports/<date>/data.json) to PDF.

Usage: python scripts/render_pdf.py reports/2026-11-01/data.json  ->  reports/2026-11-01/trend-brief-2026-11-01.pdf

Visual identity reused from the "Agent pub" project: Plus Jakarta Sans, brand greens #126C49 / #1DE094,
pastel-green hero with glass orbs, light-grey rounded cards, pills, black numbered badges, thin big KPI numbers.
CHROMIUM_PATH: optional path to an existing Chromium (otherwise the one installed by `playwright install`).
"""
import html
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BRAND = "#126C49"
MINT = "#1DE094"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">')

CSS = f"""
@page {{ size: A4; }}
* {{ box-sizing: border-box; }}
body {{ font-family: 'Plus Jakarta Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #17191a; font-size: 9.2pt;
        line-height: 1.5; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
h1, h2, h3 {{ font-weight: 500; letter-spacing: -.02em; margin: 0; }}
b, strong {{ font-weight: 650; }}
p {{ margin: 5px 0; }}
.page {{ page-break-after: always; }}
.page:last-child {{ page-break-after: auto; }}

.hero {{ position: relative; overflow: hidden; border-radius: 20px; padding: 22px 24px 20px;
         background: linear-gradient(115deg, #d7f5e7 0%, #c4f0dc 45%, #e8faf2 100%); margin-bottom: 12px; }}
.hero .art {{ position: absolute; right: -50px; top: -30px; width: 230px; height: 230px; border-radius: 50%;
              background: radial-gradient(circle at 30% 30%, #fff 0 6%, #8af0c4 32%, {MINT} 58%, {BRAND} 100%); opacity: .9; }}
.hero .art2 {{ position: absolute; right: 120px; top: 18px; width: 70px; height: 70px; border-radius: 50%;
               background: radial-gradient(circle at 35% 30%, #fff 0 10%, rgba(255,255,255,.6) 45%, rgba(185,239,214,.3) 100%);
               border: 1px solid rgba(255,255,255,.8); }}
.hero > div {{ position: relative; max-width: 68%; }}
.hero.big {{ padding: 30px 28px 28px; }}
.pill {{ display: inline-block; font-size: 7.5pt; font-weight: 600; padding: 3px 10px; border-radius: 999px; }}
.hero .pill {{ background: rgba(255,255,255,.75); color: {BRAND}; }}
.hero h1 {{ font-size: 26pt; line-height: 1.05; margin: 8px 0 2px; color: #0f1d17; }}
.hero.big h1 {{ font-size: 32pt; }}
.hero .period {{ color: #3d4a44; font-size: 9.5pt; }}
.hero .decision {{ margin-top: 12px; font-size: 10.5pt; line-height: 1.35; color: #0f1d17; }}
.hero .k {{ display: block; font-size: 7.5pt; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; color: {BRAND}; margin-bottom: 3px; }}

.kpis {{ display: flex; gap: 8px; margin-bottom: 10px; }}
.kpi {{ flex: 1; background: #f5f6f5; border-radius: 16px; padding: 10px 12px 11px; }}
.kpi .l {{ font-size: 7.6pt; color: #4a504d; font-weight: 500; }}
.kpi .v {{ font-size: 20pt; font-weight: 400; letter-spacing: -.04em; line-height: 1.1; margin: 5px 0 3px; }}
.kpi .n {{ font-size: 7.2pt; color: #858c88; }}

section {{ background: #f6f7f6; border-radius: 18px; padding: 12px 15px 9px; margin-bottom: 9px; page-break-inside: avoid; }}
section h2 {{ font-size: 12.5pt; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }}
.num {{ display: inline-block; width: 20px; height: 20px; line-height: 20px; text-align: center; border-radius: 50%;
        background: #111312; color: #fff; font-size: 7.5pt; font-weight: 600; letter-spacing: 0; flex: none; }}
ul, ol {{ margin: 4px 0; padding-left: 17px; }}
li {{ margin: 3px 0; }}
li::marker {{ color: {BRAND}; font-weight: 600; }}
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }}
.grid2 section {{ margin-bottom: 9px; }}

.brief {{ list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 7px; counter-reset: b; }}
.brief li {{ counter-increment: b; background: #fff; border-radius: 14px; padding: 9px 11px 9px 36px; position: relative; margin: 0; color: #4a504d; }}
.brief li::before {{ content: counter(b); position: absolute; left: 10px; top: 9px; width: 18px; height: 18px; line-height: 18px;
                     text-align: center; border-radius: 50%; background: #dcf7ea; color: {BRAND}; font-weight: 700; font-size: 7.5pt; }}
.brief li b {{ color: #17191a; }}

table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 5px 0 6px; font-size: 8.4pt; background: #fff;
         border: 1px solid #eceeed; border-radius: 12px; overflow: hidden; }}
th {{ background: #fff; color: #858c88; text-align: left; padding: 6px 9px; font-weight: 600; font-size: 7.6pt; border-bottom: 1px solid #eceeed; }}
td {{ padding: 5px 9px; border-bottom: 1px solid #f1f2f1; vertical-align: top; }}
tr:last-child td {{ border-bottom: 0; }}
td.n, th.n {{ text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
td.price {{ text-align: right; font-weight: 650; color: {BRAND}; white-space: nowrap; }}
.muted {{ color: #858c88; font-size: 7.6pt; }}
.chan {{ background: #dcf7ea; color: {BRAND}; }}
.chan.pin {{ background: #111312; color: {MINT}; }}
.store-head {{ display: flex; align-items: flex-end; justify-content: space-between; margin: 2px 2px 8px; }}
.store-head h1 {{ font-size: 24pt; }}
.store-head .meta {{ color: #6b726e; font-size: 8pt; margin-top: 3px; }}
.store-head .num {{ width: 30px; height: 30px; line-height: 30px; font-size: 10pt; margin-right: 10px; }}
.brow {{ display: grid; grid-template-columns: 27mm 1fr; gap: 8px; padding: 4px 0; border-bottom: 1px solid #eceeed; }}
.brow:last-child {{ border-bottom: 0; }}
.brow .bl {{ font-weight: 600; color: {BRAND}; }}
section.learn {{ background: linear-gradient(115deg, #d7f5e7 0%, #c4f0dc 45%, #e8faf2 100%); }}
.chart svg {{ width: 100%; height: auto; display: block; }}
.upd {{ background: #fff; border-radius: 14px; padding: 9px 12px; margin-bottom: 7px; }}
.upd .t {{ font-weight: 650; font-size: 9.6pt; display: flex; justify-content: space-between; gap: 10px; }}
.upd .t span {{ font-size: 7.6pt; color: {BRAND}; font-weight: 600; white-space: nowrap; }}
.upd .w {{ color: {BRAND}; font-weight: 600; margin-top: 3px; }}
.note {{ color: #858c88; font-size: 7.4pt; margin-top: 6px; padding: 0 4px; }}
"""


def footer(label):
    return f"""<div style="font-size:7pt;width:100%;padding:0 14mm;color:#858c88;display:flex;justify-content:space-between;
font-family:Helvetica,Arial,sans-serif"><span><span style="display:inline-block;width:7px;height:7px;border-radius:50%;
background:{MINT};margin-right:5px"></span>{html.escape(label)}</span>
<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>"""


def bars_svg(labels, values, w=330, h=120):
    mx = max(values) or 1
    n = len(values)
    m_b = 16
    bw = w / n
    out = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="Plus Jakarta Sans, Helvetica, Arial" font-size="8">']
    for i, v in enumerate(values):
        bar_w = min(26, bw - 10)
        cx = bw * i + bw / 2
        bh = max(2, v / mx * (h - m_b - 20))
        top = h - m_b - bh
        color = BRAND if i == n - 1 else "#2fb57e"
        out.append(f'<rect x="{cx - bar_w / 2:.1f}" y="{top:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="{min(6, bar_w / 2, bh / 2):.1f}" fill="{color}"/>')
        out.append(f'<text x="{cx:.1f}" y="{h - 4}" text-anchor="middle" fill="#858c88">{html.escape(labels[i])}</text>')
    lv = values[-1]
    cx = bw * (n - 1) + bw / 2
    ly = h - m_b - max(2, lv / mx * (h - m_b - 20)) - 6
    lab = f"{lv / 1000:.0f}k" if lv >= 1000 else str(lv)
    out.append(f'<rect x="{cx - 20:.1f}" y="{ly - 11:.1f}" width="40" height="15" rx="7.5" fill="#111312"/>'
               f'<text x="{cx:.1f}" y="{ly:.1f}" text-anchor="middle" fill="#fff" font-weight="600">{lab}</text></svg>')
    return "".join(out)


def kpi_tiles(kpis):
    return '<div class="kpis">' + "".join(
        f'<div class="kpi"><div class="l">{html.escape(k["label"])}</div><div class="v">{html.escape(k["value"])}</div>'
        f'<div class="n">{html.escape(k.get("note", ""))}</div></div>' for k in kpis) + "</div>"


def chan_pill(ch):
    return f'<span class="pill chan{" pin" if "interest" in ch else ""}">{html.escape(ch)}</span>'


def store_page(i, s):
    best = "".join(f'<tr><td>{html.escape(b["name"])}</td><td class="price">{html.escape(b["price"])}</td></tr>' for b in s["best_sellers"])
    brand = "".join(f'<div class="brow"><div class="bl">{html.escape(b["label"])}</div><div>{b["text"]}</div></div>' for b in s["branding"])
    ads = "".join(f"<li>{a}</li>" for a in s["ads"])
    learn = "".join(f"<li>{a}</li>" for a in s["lessons"])
    return f"""<div class="page">
<div class="store-head"><div style="display:flex;align-items:center"><span class="num">{i:02d}</span><div>
<div>{chan_pill(s["channel"])} <span class="pill" style="background:#f0f1f0;color:#4a504d">{html.escape(s["niche"])}</span></div>
<h1>{html.escape(s["name"])}</h1>
<div class="meta">{html.escape(s["domain"])} · launched {html.escape(s["launched"])} · {html.escape(s["origin"])} · {html.escape(s["market"])}</div>
</div></div></div>
{kpi_tiles(s["kpis"])}
<div class="grid2">
<section class="chart"><h2>Traffic trend</h2><div class="muted">Monthly visits</div>{bars_svg(s["traffic"]["labels"], s["traffic"]["values"])}</section>
<section><h2>Best-sellers</h2><table>{best}</table></section>
</div>
<section><h2><span class="num">1</span>Website &amp; branding</h2>{brand}</section>
<div class="grid2">
<section><h2><span class="num">2</span>Ad platforms</h2><ul>{ads}</ul></section>
<section class="learn"><h2><span class="num">3</span>What to learn</h2><ul>{learn}</ul></section>
</div></div>"""


def build_html(d):
    stores = d["stores"]
    rows = "".join(
        f'<tr><td><b>{html.escape(s["name"])}</b><br><span class="muted">{html.escape(s["domain"])}</span></td>'
        f'<td>{html.escape(s["niche"])}</td><td class="n">{html.escape(s["kpis"][0]["value"])}</td>'
        f'<td class="n">{html.escape(s["kpis"][2]["value"])}</td><td>{chan_pill(s["channel"])}</td></tr>' for s in stores)
    actions = "".join(f"<li>{a}</li>" for a in d["actions"])
    pin = "".join(
        f'<div class="upd"><div class="t">{html.escape(u["title"])}<span>{html.escape(u["date"])}</span></div>'
        f'<div>{u["what"]}</div><div class="w">→ {u["why"]}</div><div class="muted">{html.escape(u["source"])}</div></div>'
        for u in d["pinterest_updates"])
    other = "".join(f'<tr><td style="width:18mm"><b style="color:{BRAND}">{html.escape(u["platform"])}</b></td>'
                    f'<td><b>{html.escape(u["title"])}</b><br>{u["what"]}</td></tr>' for u in d["other_updates"])
    cover = f"""<div class="page">
<div class="hero big"><span class="art"></span><span class="art2"></span><div>
<span class="pill">Weekly e-commerce brief · Edition #{d["edition"]}</span>
<h1>{html.escape(d["headline"])}</h1><div class="period">{html.escape(d["week_label"])} · English-speaking markets</div>
<div class="decision"><span class="k">Key takeaway</span>{d["key_takeaway"]}</div>
</div></div>
<section style="background:#fff;padding:4px 2px"><p style="font-size:10.5pt;color:#3d4a44">{d["intro"]}</p></section>
<section><h2>The 3 stores</h2><table><thead><tr><th>Store</th><th>Niche</th><th class="n">Revenue 30d</th><th class="n">Visits (last month)</th><th>Main channel</th></tr></thead>{rows}</table></section>
<section style="background:#fff;padding:2px 0"><h2 style="padding:0 2px">Actions for this week</h2><ul class="brief">{actions}</ul></section>
<section><h2>How the stores were picked</h2><p>{d["method"]}</p></section>
</div>"""
    ads_page = f"""<div class="page">
<div class="hero"><span class="art"></span><span class="art2"></span><div>
<span class="pill">Ad channel watch</span><h1>Pinterest Ads</h1><div class="period">What changed recently, and what it means for a Shopify brand</div></div></div>
{pin}
<section><h2>Meta · TikTok · Google</h2><table>{other}</table></section>
<div class="note">Sources: {html.escape(d["sources"])}</div>
</div>"""
    body = cover + "".join(store_page(i + 1, s) for i, s in enumerate(stores)) + ads_page
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8">{FONTS}<style>{CSS}</style></head><body>{body}</body></html>'


def render(data_path):
    data_path = Path(data_path)
    d = json.loads(data_path.read_text())
    out = data_path.parent / f"trend-brief-{d['date']}.pdf"
    page_html = build_html(d)
    with sync_playwright() as p:
        exe = os.getenv("CHROMIUM_PATH")
        browser = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        page = browser.new_page()
        try:
            page.set_content(page_html, wait_until="networkidle", timeout=20000)
        except Exception:  # Google font unavailable: keep the fallback font
            page.set_content(page_html, wait_until="load")
        page.pdf(path=str(out), format="A4", print_background=True, display_header_footer=True,
                 header_template="<span></span>", footer_template=footer(f"Trend brief · Edition #{d['edition']} · {d['date']}"),
                 margin={"top": "12mm", "bottom": "15mm", "left": "12mm", "right": "12mm"})
        browser.close()
    print(out)
    return out


if __name__ == "__main__":
    render(sys.argv[1])
