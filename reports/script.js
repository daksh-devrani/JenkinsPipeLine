// Load multiple JSON reports and combine vulnerabilities
async function loadReports() {
  const files = [
    "grype_report.json",
    "snyk_container_report.json",
    "trivy_report.json",
    "zap_full_report.json",
    "eve.json"
  ];

  let allVulns = [];

  for (let file of files) {
    try {
      const res = await fetch(file);
      const data = await res.json();

      // Normalize vulnerabilities depending on report type
      if (data.matches) {
        // Grype
        data.matches.forEach(m => {
          if (m.vulnerability && m.vulnerability.cvss) {
            allVulns.push({
              cve: m.vulnerability.id,
              pkg: m.artifact.name,
              version: m.artifact.version,
              cvss: m.vulnerability.cvss[0]?.metrics?.baseScore || null,
              severity: m.vulnerability.severity,
              fix: m.vulnerability.fix?.versions?.[0] || "None"
            });
          }
        });
      } else if (data.vulnerabilities) {
        // Snyk
        data.vulnerabilities.forEach(v => {
          allVulns.push({
            cve: v.identifiers?.CVE?.[0] || v.title,
            pkg: v.packageName,
            version: v.version,
            cvss: v.cvssScore || null,
            severity: v.severity,
            fix: v.nearestFixedInVersion || "None"
          });
        });
      } else if (data.Results) {
        // Trivy
        data.Results.forEach(r => {
          if (r.Vulnerabilities) {
            r.Vulnerabilities.forEach(v => {
              allVulns.push({
                cve: v.VulnerabilityID,
                pkg: v.PkgName,
                version: v.InstalledVersion,
                cvss: v.CVSS?.nvd?.V3Score || null,
                severity: v.Severity,
                fix: v.FixedVersion || "None"
              });
            });
          }
        });
      } else if (data.site) {
        // ZAP (no CVSS, just alerts)
        data.site.forEach(s => {
          s.alerts.forEach(a => {
            allVulns.push({
              cve: a.alert,
              pkg: "WebApp",
              version: "-",
              cvss: null,
              severity: a.riskdesc,
              fix: a.solution
            });
          });
        });
      }
    } catch (err) {
      console.error("Error loading", file, err);
    }
  }

  return allVulns;
}

function calculateScores(vulns) {
  const scores = vulns.map(v => v.cvss).filter(s => s !== null);
  const avg = (scores.reduce((a,b) => a+b, 0) / scores.length).toFixed(2);
  const max = Math.max(...scores).toFixed(2);
  return { avg, max };
}

function renderTable(vulns) {
  const tbody = document.querySelector("#vulnTable tbody");
  tbody.innerHTML = "";
  vulns.forEach(v => {
    const row = `<tr>
      <td>${v.cve}</td>
      <td>${v.pkg}</td>
      <td>${v.version}</td>
      <td>${v.cvss || "-"}</td>
      <td>${v.severity}</td>
      <td>${v.fix}</td>
    </tr>`;
    tbody.innerHTML += row;
  });
}

function renderChart(vulns) {
  const ctx = document.getElementById("severityChart").getContext("2d");
  const counts = { High:0, Medium:0, Low:0, Critical:0 };

  vulns.forEach(v => {
    if (v.severity) {
      if (counts[v.severity] !== undefined) counts[v.severity]++;
      else counts[v.severity] = (counts[v.severity]||0)+1;
    }
  });

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: Object.keys(counts),
      datasets: [{
        data: Object.values(counts),
        backgroundColor: ["red","orange","yellow","purple"]
      }]
    }
  });
}

(async function(){
  const vulns = await loadReports();
  const { avg, max } = calculateScores(vulns);

  document.getElementById("avgScore").textContent = avg;
  document.getElementById("maxScore").textContent = max;

  renderTable(vulns);
  renderChart(vulns);
})();
