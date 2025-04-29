document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    removeErrorMessage();

    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const repeatPasswordInput = document.getElementById("repeat-password");

    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    const repeatPassword = repeatPasswordInput.value;

    if (password !== repeatPassword) {
      displayError("Passwords don't match.");
      repeatPasswordInput.classList.add("is-invalid");
      return;
    }

    const payload = {
      login: username,
      password: password,
    };

    try {
      const response = await fetch("/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const redirectUrl = "/login";
        window.location.href = redirectUrl;
      } else {
        const errorData = await response.json();
        displayError(errorData.message || "Registration failed.");
      }
    } catch (error) {
      displayError("An error occurred. Please try again later.");
    }
  });
});


function displayError(message) {
  let errorContainer = document.getElementById("error-container");
  if (!errorContainer) {
    errorContainer = document.createElement("div");
    errorContainer.id = "error-container";
    errorContainer.className = "alert alert-danger";
    // Вставляем контейнер с ошибкой перед формой (или в нужное место по дизайну)
    const formContainer = document.querySelector(".row.justify-content-center");
    formContainer.parentNode.insertBefore(errorContainer, formContainer);
  }
  errorContainer.textContent = message;
}


function removeErrorMessage() {
  const errorContainer = document.getElementById("error-container");
  if (errorContainer) {
    errorContainer.remove();
  }
}
