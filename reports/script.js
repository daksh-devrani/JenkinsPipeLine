document.addEventListener('DOMContentLoaded', () => {
    const files = {
        suricata: 'eve.json',
        grype: 'grype.json',
        'snyk-container': 'snyk_container_report.json',
        'snyk-source': 'snyk_source_report.json',
        trivy: 'trivy_report.json',
        zap: 'zap_full_report.json'
    };

    Object.keys(files).forEach(key => {
        fetch(files[key])
            .then(response => {
                if (!response.ok) throw new Error('File not found');
                return response.json();
            })
            .then(data => {
                const content = document.getElementById(`${key}-content`);
                content.innerHTML = parseData(key, data);
            })
            .catch(error => {
                const content = document.getElementById(`${key}-content`);
                content.innerHTML = `<p class="error">Error loading ${files[key]}: ${error.message}</p>`;
            });
    });

    function parseData(tool, data) {
        switch (tool) {
            case 'suricata':
                // Assume eve.json is an array of events with 'alert' objects
                const alerts = data.filter(event => event.alert).map(event => event.alert.category);
                const alertCount = alerts.length;
                const topCategories = alerts.reduce((acc, cat) => {
                    acc[cat] = (acc[cat] || 0) + 1;
                    return acc;
                }, {});
                return `<p>Total Alerts: ${alertCount}</p><ul>${Object.entries(topCategories).slice(0, 5).map(([cat, count]) => `<li>${cat}: ${count}</li>`).join('')}</ul>`;

            case 'grype':
                // Assume grype.json has 'matches' array with 'vulnerability.severity'
                const grypeSeverities = data.matches?.reduce((acc, match) => {
                    const sev = match.vulnerability?.severity || 'Unknown';
                    acc[sev] = (acc[sev] || 0) + 1;
                    return acc;
                }, {}) || {};
                return Object.entries(grypeSeverities).map(([sev, count]) => `<div class="severity"><span>${sev}:</span> ${count}</div>`).join('');

            case 'snyk-container':
            case 'snyk-source':
                // Assume Snyk reports have 'issues.vulnerabilities' or similar with 'severity'
                const issues = data.issues?.vulnerabilities || data.issues || [];
                const snykSeverities = issues.reduce((acc, issue) => {
                    const sev = issue.severity || 'Unknown';
                    acc[sev] = (acc[sev] || 0) + 1;
                    return acc;
                }, {});
                return Object.entries(snykSeverities).map(([sev, count]) => `<div class="severity"><span class="${sev.toLowerCase()}">${sev}:</span> ${count}</div>`).join('');

            case 'trivy':
                // Assume trivy_report.json has 'Results' with 'Vulnerabilities' array
                const trivyVulns = data.Results?.flatMap(result => result.Vulnerabilities || []).reduce((acc, vuln) => {
                    const sev = vuln.Severity || 'Unknown';
                    acc[sev] = (acc[sev] || 0) + 1;
                    return acc;
                }, {}) || {};
                return Object.entries(trivyVulns).map(([sev, count]) => `<div class="severity"><span class="${sev.toLowerCase()}">${sev}:</span> ${count}</div>`).join('');

            case 'zap':
                // Assume zap_full_report.json has 'site' with 'alerts' array
                const zapAlerts = data.site?.[0]?.alerts || [];
                const zapRisks = zapAlerts.reduce((acc, alert) => {
                    const risk = alert.riskdesc || 'Unknown';
                    acc[risk] = (acc[risk] || 0) + 1;
                    return acc;
                }, {});
                return Object.entries(zapRisks).map(([risk, count]) => `<div class="severity"><span class="${risk.toLowerCase().split(' ')[0]}">${risk}:</span> ${count}</div>`).join('');

            default:
                return '<p>No data available.</p>';
        }
    }
});