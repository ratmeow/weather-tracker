document.addEventListener("DOMContentLoaded", function () {
    console.log("Sign-in script loaded");

    const form = document.querySelector("form");
    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const response = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                login: username,
                password: password
            })
        });

        if (response.ok) {
            const data = await response.json()
            localStorage.setItem('userName', data.username);
            localStorage.setItem('isAuthenticated', 'true');
            window.location.href = "/";
        } else {
            const errorData = await response.json();
            showError(errorData.message);
        }
    });
});

function showError(message) {
    let errorAlert = document.querySelector(".alert-danger");
    if (!errorAlert) {
        errorAlert = document.createElement("div");
        errorAlert.className = "alert alert-danger";
        errorAlert.setAttribute("role", "alert");

        const container = document.querySelector(".container");
        container.insertBefore(errorAlert, container.children[2]);
    }
    errorAlert.textContent = message;
}