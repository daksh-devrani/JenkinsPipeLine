import json

with open("reports/eve.json") as f:
    events = json.load(f)

html = "<html><body><table border=1>"
html += "<tr><th>Timestamp</th><th>Event Type</th><th>Source IP</th><th>Destination IP</th></tr>"

for e in events:
    html += f"<tr><td>{e.get('timestamp','')}</td><td>{e.get('event_type','')}</td><td>{e.get('src_ip','')}</td><td>{e.get('dest_ip','')}</td></tr>"

html += "</table></body></html>"

with open("reports/eve_report.html","w") as f:
    f.write(html)
