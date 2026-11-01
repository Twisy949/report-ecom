"""Send a weekly trend report to Discord through a webhook (secret DISCORD_WEBHOOK_URL).

Usage: python scripts/send_discord.py reports/2026-11-01/data.json
Posts a short summary (headline, the 3 stores, key takeaway) with the PDF attached
(reports/<date>/trend-brief-<date>.pdf, created by scripts/render_pdf.py).
"""
import json
import os
import re
import sys
from pathlib import Path

import requests


def plain(text):
    return re.sub(r"<[^>]+>", "", text)


def summary(d):
    lines = [f"**Weekly E-commerce Trend Brief · Edition #{d['edition']} · {d['week_label']}**"]
    for i, s in enumerate(d["stores"], 1):
        lines.append(f"{i}. **{s['name']}** ({s['domain']}) · {s['niche']} · {s['kpis'][0]['value']} / 30d · {s['channel']}")
    lines.append(f"\n💡 {plain(d['key_takeaway'])}")
    lines.append("\n📎 Full report attached.")
    return "\n".join(lines)[:1900]


def main(path):
    url = (os.getenv("DISCORD_WEBHOOK_URL") or "").strip().strip("'\"")
    if not url:
        print("DISCORD_WEBHOOK_URL missing: report not sent (add the repository secret to enable sending)")
        return
    data_path = Path(path)
    d = json.loads(data_path.read_text())
    pdf = data_path.parent / f"trend-brief-{d['date']}.pdf"
    files = {"files[0]": (pdf.name, pdf.read_bytes(), "application/pdf")} if pdf.exists() else {}
    resp = requests.post(url, data={"payload_json": json.dumps({"content": summary(d)})}, files=files, timeout=60)
    if resp.status_code >= 300:
        sys.exit(f"Discord refused the upload ({resp.status_code}): {resp.text[:200]}")
    print("Report sent to Discord")


if __name__ == "__main__":
    main(sys.argv[1])
