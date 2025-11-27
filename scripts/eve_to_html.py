import json
import os

def extract_important(e):
    """Pick only important fields from the JSON event."""
    stats = e.get("stats", {})
    return {
        "General": {
            "Timestamp": e.get("timestamp", ""),
            "Event Type": e.get("event_type", ""),
            "Uptime": stats.get("uptime", "")
        },
        "Capture": {
            "Kernel Packets": stats.get("capture", {}).get("kernel_packets", ""),
            "Kernel Drops": stats.get("capture", {}).get("kernel_drops", ""),
            "Errors": stats.get("capture", {}).get("errors", "")
        },
        "Decoder": {
            "Packets": stats.get("decoder", {}).get("pkts", ""),
            "Bytes": stats.get("decoder", {}).get("bytes", ""),
            "IPv4": stats.get("decoder", {}).get("ipv4", ""),
            "IPv6": stats.get("decoder", {}).get("ipv6", ""),
            "UDP": stats.get("decoder", {}).get("udp", ""),
            "ICMPv6": stats.get("decoder", {}).get("icmpv6", "")
        },
        "Flow": {
            "Total Flows": stats.get("flow", {}).get("total", ""),
            "Active Flows": stats.get("flow", {}).get("active", ""),
            "TCP Flows": stats.get("flow", {}).get("tcp", ""),
            "UDP Flows": stats.get("flow", {}).get("udp", ""),
            "ICMPv6 Flows": stats.get("flow", {}).get("icmpv6", "")
        },
        "Detect": {
            "Alerts": stats.get("detect", {}).get("alert", ""),
            "Rules Loaded": stats.get("detect", {}).get("engines", [{}])[0].get("rules_loaded", "")
        },
        "App Layer": {
            "Failed UDP": stats.get("app_layer", {}).get("flow", {}).get("failed_udp", ""),
            "HTTP": stats.get("app_layer", {}).get("flow", {}).get("http", ""),
            "TLS": stats.get("app_layer", {}).get("flow", {}).get("tls", "")
        }
    }

def dict_to_html_table(title, d):
    """Convert dictionary to HTML table."""
    html = f"<h2>{title}</h2><table border=1>"
    for k, v in d.items():
        if v not in ("", 0, None):  # skip empty/zero
            html += f"<tr><th>{k}</th><td>{v}</td></tr>"
    html += "</table>"
    return html

input_file = "reports/eve.json"
output_file = "reports/eve_report.html"

html = "<html><body>"

with open(input_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            important = extract_important(e)
            for section, data in important.items():
                html += dict_to_html_table(section, data)
        except json.JSONDecodeError:
            continue

html += "</body></html>"

os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w") as f:
    f.write(html)

print(f"Report written to {output_file}")
