import json

html = "<html><body><table border=1>"
html += "<tr><th>Timestamp</th><th>Event Type</th><th>Source IP</th><th>Destination IP</th></tr>"

with open("reports/eve.json") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            html += f"<tr><td>{e.get('timestamp','')}</td><td>{e.get('event_type','')}</td><td>{e.get('src_ip','')}</td><td>{e.get('dest_ip','')}</td></tr>"
        except json.JSONDecodeError:
            # skip malformed lines
            continue

html += "</table></body></html>"

with open("reports/eve_report.html","w") as f:
    f.write(html)
