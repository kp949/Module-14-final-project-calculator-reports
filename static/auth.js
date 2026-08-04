function showMessage(text, type) {
    const message = document.getElementById("message");
    message.textContent = text;
    message.className = type;
}

function validEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function usernameFromEmail(email) {
    return email.split("@")[0].replaceAll(".", "_").replaceAll("-", "_").slice(0, 50);
}

async function postJson(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data),
    });

    const body = await response.json();
    if (!response.ok) {
        throw new Error(body.detail || "Request failed");
    }
    return body;
}

async function registerUser(event) {
    event.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (!validEmail(email)) {
        showMessage("Please enter a valid email address.", "error");
        return;
    }

    if (password.length < 8) {
        showMessage("Password must be at least 8 characters.", "error");
        return;
    }

    if (password !== confirmPassword) {
        showMessage("Passwords do not match.", "error");
        return;
    }

    try {
        const data = await postJson("/register", {
            email,
            password,
            username: usernameFromEmail(email),
        });
        localStorage.setItem("access_token", data.access_token);
        showMessage("Registration successful. Token saved.", "success");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function loginUser(event) {
    event.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!validEmail(email)) {
        showMessage("Please enter a valid email address.", "error");
        return;
    }

    if (password.length < 8) {
        showMessage("Password must be at least 8 characters.", "error");
        return;
    }

    try {
        const data = await postJson("/login", {email, password});
        localStorage.setItem("access_token", data.access_token);
        showMessage("Login successful. Token saved.", "success");
    } catch (error) {
        showMessage("Invalid email or password.", "error");
    }
}
