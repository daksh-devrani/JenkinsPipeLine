#!/usr/bin/env python3
import json
import os
from datetime import datetime
from html import escape

COMBINED_JSON = "reports/combined_report.json"
OUTPUT_HTML = "reports/combined_report.html"


def load_report(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Combined report JSON not found at: {path}")
    with open(path, "r") as f:
        return json.load(f)


def html_head(title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{escape(title)}</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      padding: 0;
      background: #0b1120;
      color: #e5e7eb;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 1.5rem 3rem;
    }}

    h1, h2, h3 {{
      color: #f9fafb;
      margin-bottom: 0.5rem;
    }}

    h1 {{
      font-size: 2rem;
      margin-bottom: 1rem;
    }}

    h2 {{
      font-size: 1.4rem;
      margin-top: 2rem;
    }}

    .subtitle {{
      color: #9ca3af;
      font-size: 0.9rem;
      margin-bottom: 1.5rem;
    }}

    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }}

    .card {{
      background: #020617;
      border-radius: 0.75rem;
      padding: 1rem 1.2rem;
      border: 1px solid #1e293b;
      box-shadow: 0 10px 40px rgba(15,23,42,0.7);
    }}

    .card-title {{
      font-size: 0.9rem;
      color: #9ca3af;
      margin-bottom: 0.3rem;
    }}

    .card-value {{
      font-size: 1.4rem;
      font-weight: 600;
    }}

    .severity-pill {{
      display: inline-block;
      padding: 0.15rem 0.6rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
    }}

    .sev-Critical {{ background: #7f1d1d; color: #fee2e2; }}
    .sev-High     {{ background: #b91c1c; color: #fee2e2; }}
    .sev-Medium   {{ background: #78350f; color: #fef3c7; }}
    .sev-Low      {{ background: #064e3b; color: #d1fae5; }}
    .sev-Unknown  {{ background: #111827; color: #e5e7eb; }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0 2rem;
      font-size: 0.85rem;
      background: #020617;
      border-radius: 0.75rem;
      overflow: hidden;
      border: 1px solid #1f2937;
    }}

    thead {{
      background: #020617;
    }}

    th, td {{
      padding: 0.6rem 0.8rem;
      text-align: left;
      border-bottom: 1px solid #1f2937;
    }}

    th {{
      font-weight: 600;
      color: #9ca3af;
      white-space: nowrap;
    }}

    tr:nth-child(even) td {{
      background: #020617;
    }}

    tr:nth-child(odd) td {{
      background: #020617;
    }}

    tr:hover td {{
      background: #111827;
    }}

    .tool-pill {{
      font-size: 0.7rem;
      padding: 0.1rem 0.5rem;
      border-radius: 999px;
      border: 1px solid #1d4ed8;
      color: #bfdbfe;
      background: #111827;
      display: inline-block;
    }}

    .muted {{
      color: #9ca3af;
      font-size: 0.8rem;
    }}

    .section-desc {{
      color: #9ca3af;
      font-size: 0.85rem;
      margin-top: 0.1rem;
      margin-bottom: 0.7rem;
    }}

    .badge {{
      display: inline-block;
      font-size: 0.7rem;
      padding: 0.1rem 0.45rem;
      border-radius: 999px;
      border: 1px solid #4b5563;
      color: #d1d5db;
      margin-left: 0.3rem;
    }}

    footer {{
      text-align: center;
      padding-top: 1rem;
      margin-top: 2rem;
      border-top: 1px solid #1f2937;
      color: #6b7280;
      font-size: 0.75rem;
    }}
  </style>
</head>
<body>
<div class="container">
"""


def html_footer() -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
<footer>
  Generated at {escape(ts)} by Jenkins security pipeline.
</footer>
</div>
</body>
</html>
"""


def severity_class(sev: str) -> str:
    sev = (sev or "").capitalize()
    if sev in ("Critical", "High", "Medium", "Low"):
        return f"sev-{sev}"
    return "sev-Unknown"


def build_summary_cards(report: dict) -> str:
    s = report.get("summary", {})
    total_vulns = s.get("total_vulnerabilities", 0)
    total_web = s.get("total_web_alerts", 0)
    total_net = s.get("total_network_alerts", 0)

    # Count severities
    sev_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Unknown": 0}
    for v in report.get("vulnerabilities", []):
        sev = (v.get("severity") or "").capitalize()
        if sev not in sev_counts:
            sev = "Unknown"
        sev_counts[sev] += 1

    return f"""
<div class="cards">
  <div class="card">
    <div class="card-title">Total Vulnerabilities</div>
    <div class="card-value">{total_vulns}</div>
  </div>
  <div class="card">
    <div class="card-title">Web Security Alerts (ZAP)</div>
    <div class="card-value">{total_web}</div>
  </div>
  <div class="card">
    <div class="card-title">Network Alerts (Suricata)</div>
    <div class="card-value">{total_net}</div>
  </div>
  <div class="card">
    <div class="card-title">Severity Breakdown</div>
    <div class="muted">
      Critical: {sev_counts['Critical']} · High: {sev_counts['High']} ·
      Medium: {sev_counts['Medium']} · Low: {sev_counts['Low']} ·
      Unknown: {sev_counts['Unknown']}
    </div>
  </div>
</div>
"""


def build_vuln_table(report: dict) -> str:
    vulns = report.get("vulnerabilities", [])
    if not vulns:
        return """
<h2>Vulnerabilities</h2>
<p class="muted">No vulnerabilities found or reports missing.</p>
"""

    rows = []
    for v in vulns:
        tool = escape(str(v.get("tool", "")))
        vid = escape(str(v.get("id", "")))
        sev = escape(str(v.get("severity", "")))
        score = escape(str(v.get("score", "N/A")))
        pkg = escape(str(v.get("package", v.get("component", ""))))
        ver = escape(str(v.get("version", v.get("installed", ""))))

        rows.append(f"""
<tr>
  <td><span class="tool-pill">{tool}</span></td>
  <td>{vid}</td>
  <td><span class="severity-pill {severity_class(sev)}">{sev or 'Unknown'}</span></td>
  <td>{score}</td>
  <td>{pkg}</td>
  <td>{ver}</td>
</tr>
""")

    return f"""
<h2>Vulnerabilities</h2>
<p class="section-desc">
  Consolidated issues from Trivy, Snyk (source & container), and Grype.
</p>
<table>
  <thead>
    <tr>
      <th>Tool</th>
      <th>ID</th>
      <th>Severity</th>
      <th>CVSS</th>
      <th>Package / Component</th>
      <th>Version</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""


def build_web_table(report: dict) -> str:
    alerts = report.get("web_security", [])
    if not alerts:
        return """
<h2>Web Application Security (ZAP)</h2>
<p class="muted">No ZAP alerts recorded or report missing.</p>
"""

    rows = []
    for a in alerts:
        alert = escape(str(a.get("alert", "")))
        risk = escape(str(a.get("risk", "")))
        desc = escape(str(a.get("desc", "")))
        rows.append(f"""
<tr>
  <td>{alert}</td>
  <td>{risk}</td>
  <td>{desc}</td>
</tr>
""")

    return f"""
<h2>Web Application Security (ZAP)</h2>
<p class="section-desc">
  Aggregated alerts from OWASP ZAP full scan.
</p>
<table>
  <thead>
    <tr>
      <th>Alert</th>
      <th>Risk</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""


def build_network_table(report: dict) -> str:
    alerts = report.get("network_alerts", [])
    if not alerts:
        return """
<h2>Network IDS Alerts (Suricata)</h2>
<p class="muted">No Suricata alerts recorded or eve.json missing.</p>
"""

    rows = []
    for a in alerts:
        sig = escape(str(a.get("signature", "")))
        sev = escape(str(a.get("severity", "")))
        rows.append(f"""
<tr>
  <td>{sig}</td>
  <td>{sev}</td>
</tr>
""")

    return f"""
<h2>Network IDS Alerts (Suricata)</h2>
<p class="section-desc">
  Alerts from Suricata IDS during traffic inspection to the running container.
</p>
<table>
  <thead>
    <tr>
      <th>Signature</th>
      <th>Severity</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""


def main():
    report = load_report(COMBINED_JSON)

    html = []
    html.append(html_head("Combined Security Report"))
    html.append("""
<h1>Combined Security Report</h1>
<div class="subtitle">
  Unified view of container, dependency, web, and network security findings
  across Trivy, Snyk, Grype, Suricata, and OWASP ZAP.
</div>
""")
    html.append(build_summary_cards(report))
    html.append(build_vuln_table(report))
    html.append(build_web_table(report))
    html.append(build_network_table(report))
    html.append(html_footer())

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w") as f:
        f.write("".join(html))

    print(f"Combined HTML report written to: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
