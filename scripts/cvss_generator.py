import json
import os

report = {
    "summary": {},
    "vulnerabilities": [],
    "web_security": [],
    "network_alerts": []
}

def load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

trivy = load_json("reports/trivy_report.json")
if trivy:
    for result in trivy.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            report["vulnerabilities"].append({
                "tool": "Trivy",
                "id": vuln["VulnerabilityID"],
                "severity": vuln["Severity"],
                "score": vuln.get("CVSS", [{}])[0].get("Value", "N/A"),
                "package": vuln.get("PkgName", ""),
                "installed": vuln.get("InstalledVersion", "")
            })

def extract_snyk(file, tool_name):
    snyk = load_json(file)
    if snyk and "vulnerabilities" in snyk:
        for vuln in snyk["vulnerabilities"]:
            report["vulnerabilities"].append({
                "tool": tool_name,
                "id": vuln["id"],
                "severity": vuln["severity"].upper(),
                "score": vuln.get("cvssScore", "N/A"),
                "package": vuln.get("packageName", ""),
                "version": vuln.get("version", "")
            })


extract_snyk("reports/snyk_source_report.json", "Snyk-Source")
extract_snyk("reports/snyk_container_report.json", "Snyk-Container")
grype = load_json("reports/grype_report.json")
if grype and "matches" in grype:
    for m in grype["matches"]:
        vuln = m["vulnerability"]
        report["vulnerabilities"].append({
            "tool": "Grype",
            "id": vuln["id"],
            "severity": vuln["severity"],
            "score": vuln.get("cvss", [{}])[0].get("metrics", {}).get("baseScore", "N/A"),
            "package": m["artifact"]["name"],
            "version": m["artifact"]["version"]
        })

zap = load_json("reports/zap_full_report.json")
if zap and "site" in zap:
    for alert in zap["site"][0].get("alerts", []):
        report["web_security"].append({
            "alert": alert["alert"],
            "risk": alert["riskdesc"],
            "desc": alert["desc"]
        })

sur = load_json("reports/eve.json")
if sur:
    for event in sur:
        if event.get("event_type") == "alert":
            report["network_alerts"].append({
                "signature": event["alert"]["signature"],
                "severity": event["alert"]["severity"]
            })

report["summary"]["total_vulnerabilities"] = len(report["vulnerabilities"])
report["summary"]["total_web_alerts"] = len(report["web_security"])
report["summary"]["total_network_alerts"] = len(report["network_alerts"])

with open("reports/combined_report.json", "w") as out:
    json.dump(report, out, indent=4)

print("Combined report created: reports/combined_report.json")
