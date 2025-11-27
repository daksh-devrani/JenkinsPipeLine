import json
import os

def flatten_json(y, prefix=""):
    """Recursively flatten nested JSON into a flat dict with dotted keys."""
    out = {}
    def flatten(x, name=""):
        if isinstance(x, dict):
            for k, v in x.items():
                flatten(v, f"{name}{k}.")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                flatten(v, f"{name}{i}.")
        else:
            out[name[:-1]] = x
    flatten(y, prefix)
    return out

# Input/output files
input_file = "reports/eve.json"
output_file = "reports/eve_report.html"

rows = []
all_keys = set()

# Read and flatten each JSON line
with open(input_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            flat = flatten_json(e)
            rows.append(flat)
            all_keys.update(flat.keys())
        except json.JSONDecodeError:
            continue

# Sort keys for consistent column order
all_keys = sorted(all_keys)

# Build HTML table
html = "<html><body><table border=1>"
html += "<tr>" + "".join(f"<th>{key}</th>" for key in all_keys) + "</tr>"

for row in rows:
    html += "<tr>" + "".join(f"<td>{row.get(key, '')}</td>" for key in all_keys) + "</tr>"

html += "</table></body></html>"

# Write output
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w") as f:
    f.write(html)

print(f"Report written to {output_file}")
