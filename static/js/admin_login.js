document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("admin-login-form");
  const errorEl = document.getElementById("login-error");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");

  if (usernameInput) {
    usernameInput.focus();
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
      showError("Por favor, completa todos los campos.");
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Verificando...';

    try {
      const response = await fetch("/admin/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: username,
          password: password,
        }),
      });

      if (response.redirected) {
        window.location.href = response.url;
      } else if (response.ok) {
        const text = await response.text();
        if (text.includes("admin_login.html")) {
          showError("Credenciales incorrectas. Por favor, inténtalo de nuevo.");
        }
      } else {
        showError("Error del servidor. Inténtalo más tarde.");
      }
    } catch (error) {
      console.error("Error en login:", error);
      showError("Error de conexión. Verifica tu red e inténtalo de nuevo.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });

  [usernameInput, passwordInput].forEach((input) => {
    input.addEventListener("input", () => {
      if (!errorEl.classList.contains("hidden")) {
        errorEl.classList.add("hidden");
      }
    });
  });

  form.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      const focused = document.activeElement;
      if (focused === usernameInput || focused === passwordInput) {
        form.requestSubmit();
      }
    }
  });

  function showError(message) {
    errorEl.textContent = message;
    errorEl.className = "error";
    errorEl.scrollIntoView({ behavior: "smooth", block: "nearest" });

    if (!usernameInput.value.trim()) {
      usernameInput.focus();
    } else if (!passwordInput.value) {
      passwordInput.focus();
    }
  }
});
