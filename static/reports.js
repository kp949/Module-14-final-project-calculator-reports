const message = document.getElementById("message");
const recentCalculations = document.getElementById("recent-calculations");

function getToken() {
    return localStorage.getItem("access_token");
}

function showValue(id, value) {
    document.getElementById(id).textContent = value === null ? "None" : value;
}

function calculationText(calculation) {
    return `${calculation.a} ${calculation.type} ${calculation.b}`;
}

async function loadReport() {
    const token = getToken();

    if (!token) {
        message.textContent = "Please log in before viewing reports.";
        return;
    }

    const response = await fetch("/reports/summary", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        message.textContent = "Could not load report.";
        return;
    }

    const report = await response.json();

    showValue("total-calculations", report.total_calculations);
    showValue("add-count", report.add_count);
    showValue("subtract-count", report.subtract_count);
    showValue("multiply-count", report.multiply_count);
    showValue("divide-count", report.divide_count);
    showValue("average-result", report.average_result);
    showValue("highest-result", report.highest_result);
    showValue("lowest-result", report.lowest_result);

    recentCalculations.innerHTML = "";

    for (const calculation of report.recent_calculations) {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${calculation.id}</td>
            <td>${calculationText(calculation)}</td>
            <td>${calculation.result}</td>
        `;

        recentCalculations.appendChild(row);
    }

    message.textContent = "Report loaded successfully.";
}

loadReport();