function setMessage(text, type) {
    const message = document.getElementById("message");
    message.textContent = text;
    message.className = type;
}

function token() {
    return localStorage.getItem("access_token");
}

function headers() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token()}`,
    };
}

async function apiRequest(url, options = {}) {
    if (!token()) {
        throw new Error("Please log in first.");
    }

    const response = await fetch(url, {
        ...options,
        headers: headers(),
    });
    const body = response.status === 204 ? {} : await response.json();
    if (!response.ok) {
        throw new Error(body.detail || "Request failed");
    }
    return body;
}

function calculationText(calculation) {
    return `${calculation.a} ${calculation.type} ${calculation.b}`;
}

function resetForm() {
    document.getElementById("calculation-id").value = "";
    document.getElementById("a").value = "";
    document.getElementById("b").value = "";
    document.getElementById("type").value = "Add";
    document.getElementById("save-button").textContent = "Add Calculation";
}

function formData() {
    const a = Number(document.getElementById("a").value);
    const b = Number(document.getElementById("b").value);
    const type = document.getElementById("type").value;

    if (Number.isNaN(a) || Number.isNaN(b)) {
        throw new Error("Both values must be numbers.");
    }

    if (type === "Divide" && b === 0) {
        throw new Error("Cannot divide by zero.");
    }

    return {a, b, type};
}

async function loadCalculations() {
    try {
        const calculations = await apiRequest("/calculations");
        const list = document.getElementById("calculation-list");
        list.innerHTML = "";

        calculations.forEach((calculation) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${calculation.id}</td>
                <td>${calculationText(calculation)}</td>
                <td>${calculation.result}</td>
                <td>
                    <button class="small" data-action="read" data-id="${calculation.id}">Read</button>
                    <button class="small" data-action="edit" data-id="${calculation.id}">Edit</button>
                    <button class="small danger" data-action="delete" data-id="${calculation.id}">Delete</button>
                </td>
            `;
            list.appendChild(row);
        });
    } catch (error) {
        setMessage(error.message, "error");
    }
}

async function saveCalculation(event) {
    event.preventDefault();
    try {
        const id = document.getElementById("calculation-id").value;
        const data = formData();
        if (id) {
            await apiRequest(`/calculations/${id}`, {
                method: "PUT",
                body: JSON.stringify(data),
            });
            setMessage("Calculation updated.", "success");
        } else {
            await apiRequest("/calculations", {
                method: "POST",
                body: JSON.stringify(data),
            });
            setMessage("Calculation added.", "success");
        }
        resetForm();
        await loadCalculations();
    } catch (error) {
        setMessage(error.message, "error");
    }
}

async function handleTableClick(event) {
    const button = event.target.closest("button");
    if (!button) {
        return;
    }

    const id = button.dataset.id;
    const action = button.dataset.action;
    try {
        if (action === "read") {
            const calculation = await apiRequest(`/calculations/${id}`);
            document.getElementById("detail").textContent =
                `Calculation ${calculation.id}: ${calculationText(calculation)} = ${calculation.result}`;
        }

        if (action === "edit") {
            const calculation = await apiRequest(`/calculations/${id}`);
            document.getElementById("calculation-id").value = calculation.id;
            document.getElementById("a").value = calculation.a;
            document.getElementById("b").value = calculation.b;
            document.getElementById("type").value = calculation.type;
            document.getElementById("save-button").textContent = "Update Calculation";
            setMessage("Editing selected calculation.", "success");
        }

        if (action === "delete") {
            await apiRequest(`/calculations/${id}`, {method: "DELETE"});
            setMessage("Calculation deleted.", "success");
            document.getElementById("detail").textContent = "";
            await loadCalculations();
        }
    } catch (error) {
        setMessage(error.message, "error");
    }
}

document.getElementById("calculation-form").addEventListener("submit", saveCalculation);
document.getElementById("reset-button").addEventListener("click", resetForm);
document.getElementById("calculation-list").addEventListener("click", handleTableClick);
loadCalculations();
