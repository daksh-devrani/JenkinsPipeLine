#!/usr/bin/env python3
import json
import os

# Input files (what your tools already generate)
TRIVY_JSON = "reports/trivy_report.json"
SNYK_SOURCE_JSON = "reports/snyk_source_report.json"
SNYK_CONTAINER_JSON = "reports/snyk_container_report.json"
GRYPE_JSON = "reports/grype_report.json"
ZAP_JSON = "reports/zap_full_report.json"
SURICATA_JSON = "reports/eve.json"

# Output combined file
COMBINED_JSON = "reports/combined_report.json"


def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


# ---------- CVSS HELPERS ----------

def get_trivy_cvss(vuln):
    """
    Trivy can expose CVSS as:
    - list: [{"Source": "...", "Type": "...", "Value": 7.8}, ...]
    - dict: {"nvd": {"V3Score": 9.8, ...}, "redhat": {...}}
    """
    cvss = vuln.get("CVSS")
    if not cvss:
        return "N/A"

    # Case 1: list of CVSS entries
    if isinstance(cvss, list):
        first = cvss[0] if cvss else {}
        # older schema: "Value"
        return str(first.get("Value") or first.get("Score") or "N/A")

    # Case 2: dict of vendors
    if isinstance(cvss, dict):
        # Prefer some common vendors in order
        for key in ("nvd", "redhat", "ghsa", "github"):
            if key in cvss:
                entry = cvss[key] or {}
                return str(
                    entry.get("V3Score")
                    or entry.get("V2Score")
                    or entry.get("Score")
                    or entry.get("Value")
                    or "N/A"
                )
        # Otherwise just pick the first vendor
        try:
            first = next(iter(cvss.values()))
            return str(
                first.get("V3Score")
                or first.get("V2Score")
                or first.get("Score")
                or first.get("Value")
                or "N/A"
            )
        except StopIteration:
            return "N/A"

    return "N/A"


def get_grype_cvss(vuln):
    """
    Grype usually has:
       "cvss": [
         {
           "version": "3.1",
           "metrics": {"baseScore": 7.8, ...}
         }, ...
       ]
    but we guard it anyway.
    """
    cvss = vuln.get("cvss")
    if not cvss:
        return "N/A"

    # List of entries
    if isinstance(cvss, list) and cvss:
        first = cvss[0] or {}
        metrics = first.get("metrics") or {}
        return str(
            metrics.get("baseScore")
            or metrics.get("base_score")
            or first.get("score")
            or "N/A"
        )

    # Dict (just in case)
    if isinstance(cvss, dict):
        try:
            first = next(iter(cvss.values())) or {}
        except StopIteration:
            return "N/A"
        metrics = first.get("metrics") or {}
        return str(
            metrics.get("baseScore")
            or metrics.get("base_score")
            or first.get("score")
            or "N/A"
        )

    return "N/A"


# ---------- MAIN COMBINER ----------

def main():
    report = {
        "summary": {},
        "vulnerabilities": [],
        "web_security": [],
        "network_alerts": []
    }

    # ---- 1. Trivy ----
    trivy = load_json(TRIVY_JSON)
    if trivy:
        for result in trivy.get("Results", []):
            for vuln in result.get("Vulnerabilities", []) or []:
                report["vulnerabilities"].append({
                    "tool": "Trivy",
                    "id": vuln.get("VulnerabilityID", ""),
                    "severity": vuln.get("Severity", "Unknown"),
                    "score": get_trivy_cvss(vuln),
                    "package": vuln.get("PkgName", ""),
                    "installed": vuln.get("InstalledVersion", "")
                })

    # ---- 2. Snyk (source + container) ----
    def extract_snyk(path, tool_name):
        snyk = load_json(path)
        if snyk and isinstance(snyk, dict) and "vulnerabilities" in snyk:
            for vuln in snyk.get("vulnerabilities", []) or []:
                report["vulnerabilities"].append({
                    "tool": tool_name,
                    "id": vuln.get("id", ""),
                    "severity": (vuln.get("severity") or "unknown").capitalize(),
                    "score": str(vuln.get("cvssScore", "N/A")),
                    "package": vuln.get("packageName", ""),
                    "version": vuln.get("version", "")
                })

    extract_snyk(SNYK_SOURCE_JSON, "Snyk-Source")
    extract_snyk(SNYK_CONTAINER_JSON, "Snyk-Container")

    # ---- 3. Grype ----
    grype = load_json(GRYPE_JSON)
    if grype and isinstance(grype, dict) and "matches" in grype:
        for m in grype.get("matches", []) or []:
            vuln = m.get("vulnerability", {}) or {}
            artifact = m.get("artifact", {}) or {}
            report["vulnerabilities"].append({
                "tool": "Grype",
                "id": vuln.get("id", ""),
                "severity": vuln.get("severity", "Unknown"),
                "score": get_grype_cvss(vuln),
                "package": artifact.get("name", ""),
                "version": artifact.get("version", "")
            })

    # ---- 4. ZAP ----
    zap = load_json(ZAP_JSON)
    if zap and isinstance(zap, dict) and "site" in zap:
        sites = zap.get("site") or []
        if sites:
            for alert in sites[0].get("alerts", []) or []:
                report["web_security"].append({
                    "alert": alert.get("alert", ""),
                    "risk": alert.get("riskdesc", ""),
                    "desc": alert.get("desc", "")
                })

    # ---- 5. Suricata ----
    sur = load_json(SURICATA_JSON)
    if sur and isinstance(sur, list):
        for event in sur:
            if not isinstance(event, dict):
                continue
            if event.get("event_type") == "alert":
                alert = event.get("alert", {}) or {}
                report["network_alerts"].append({
                    "signature": alert.get("signature", ""),
                    "severity": alert.get("severity", "")
                })

    # ---- SUMMARY ----
    sev_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Unknown": 0}
    for v in report["vulnerabilities"]:
        sev = (v.get("severity") or "").capitalize()
        if sev not in sev_counts:
            sev = "Unknown"
        sev_counts[sev] += 1

    report["summary"] = {
        "total_vulnerabilities": len(report["vulnerabilities"]),
        "total_web_alerts": len(report["web_security"]),
        "total_network_alerts": len(report["network_alerts"]),
        "severity_counts": sev_counts
    }

    # ---- WRITE OUTPUT ----
    os.makedirs(os.path.dirname(COMBINED_JSON), exist_ok=True)
    with open(COMBINED_JSON, "w") as out:
        json.dump(report, out, indent=4)

    print(f"Combined JSON report written to: {COMBINED_JSON}")


if __name__ == "__main__":
    main()
