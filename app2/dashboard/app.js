const API = "http://127.0.0.1:8000";

async function loadDashboard() {

    const metrics = await fetch(
        `${API}/dashboard/metrics`
    );

    const metricData = await metrics.json();

    document.getElementById("records").innerText =
        metricData.total_records;

    document.getElementById("zones").innerText =
        metricData.total_zones;

    document.getElementById("alerts").innerText =
        metricData.total_alerts;

    document.getElementById("forecast_alerts").innerText =
        metricData.forecast_alerts;

}


async function loadAnalytics() {

    const response =
        await fetch(
            "http://127.0.0.1:8000/analytics"
        );

    const data =
        await response.json();

    console.log(data);
}

loadAnalytics();



async function loadAnalytics() {

    const response = await fetch(
        `${API}/analytics`
    );

    const data = await response.json();

    const tbody =
        document.querySelector(
            "#analyticsTable tbody"
        );

    tbody.innerHTML = "";

    data.forEach(row => {

        tbody.innerHTML += `
        <tr>
            <td>${row.zone_id}</td>
            <td>${row.avg_power_kw}</td>
            <td>${row.avg_voltage}</td>
            <td>${row.avg_current}</td>
            <td>${row.utilization_percent.toFixed(2)}</td>
        </tr>
        `;
    });
}


async function loadAlerts() {

    const response = await fetch(
        `${API}/alerts`
    );

    const data = await response.json();

    const tbody =
        document.querySelector(
            "#alertTable tbody"
        );

    tbody.innerHTML = "";

    data.forEach(row => {

        tbody.innerHTML += `
        <tr>
            <td>${row.zone_id}</td>
            <td>${row.alert_message}</td>
            <td>${row.alert_time}</td>
        </tr>
        `;
    });
}


loadDashboard();
loadAnalytics();
loadAlerts();

setInterval(() => {

    loadDashboard();
    loadAnalytics();
    loadAlerts();

}, 10000);