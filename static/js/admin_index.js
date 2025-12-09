document.addEventListener("DOMContentLoaded", () => {
  const menuItems = Array.from(document.querySelectorAll(".menu-item"));
  const contentArea = document.getElementById("content-area");
  const modal = document.getElementById("admin-modal");
  const modalBody = document.getElementById("modal-body");
  const modalClose = document.getElementById("modal-close");
  const logoutBtn = document.getElementById("logout-btn");

  checkSession();

  menuItems.forEach((item) => {
    item.addEventListener("click", () => {
      const url = item.dataset.load;
      if (!url) return;

      menuItems.forEach((i) => i.classList.remove("active"));
      item.classList.add("active");

      fetch(url, {
        credentials: "include",
      })
        .then((resp) => {
          if (resp.status === 401) {
            window.location.href = "/admin/login";
            throw new Error("No autorizado");
          }
          if (!resp.ok) throw new Error("Error loading module");
          return resp.text();
        })
        .then((html) => {
          contentArea.innerHTML = html;

          executeScripts(contentArea);
        })
        .catch((err) => {
          if (err.message !== "No autorizado") {
            contentArea.innerHTML = `<div class="error">No se pudo cargar el módulo: ${err.message}</div>`;
          }
        });
    });
  });

  modalClose?.addEventListener("click", closeModal);
  modal?.addEventListener("click", (ev) => {
    if (ev.target === modal) closeModal();
  });

  logoutBtn?.addEventListener("click", () => {
    fetch("/admin/logout", {
      method: "POST",
      credentials: "include",
    })
      .then(() => {
        window.location.href = "/admin/login";
      })
      .catch(() => {
        window.location.href = "/admin/login";
      });
  });

  /**
   * Checks if the user's session is still valid by making a request to the server.
   * If the session is invalid or an error occurs, redirects the user to the login page.
   * 
   * @async
   * @function checkSession
   * @returns {Promise<void>}
   * @throws {Error} Logs any fetch errors to the console but handles them gracefully by redirecting to login.
   */
  async function checkSession() {
    try {
      const response = await fetch("/admin/check-session", {
        credentials: "include",
      });

      if (!response.ok) {
        window.location.href = "/admin/login";
      }
    } catch (error) {
      console.error("Error verificando sesión:", error);
      window.location.href = "/admin/login";
    }
  }

  /**
   * Opens a modal dialog and populates it with the provided HTML content.
   * @param {string} html - The HTML content to be displayed in the modal body
   * @returns {void}
   */
  function openModal(html) {
    modalBody.innerHTML = html;
    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");

    setTimeout(() => executeScripts(modalBody), 100);
  }

  /**
   * Closes the modal dialog by hiding it, updating its accessibility attribute,
   * and clearing its content.
   *
   * @function
   * @returns {void}
   */
  function closeModal() {
    modal.classList.add("hidden");
    modal.setAttribute("aria-hidden", "true");
    modalBody.innerHTML = "";
  }

  /**
   * Executes all <script> elements found within the specified container element.
   * For external scripts (with a src attribute), the script is appended to the document head.
   * For inline scripts, the script is executed by creating a new script element and appending it to the body.
   * 
   * @param {HTMLElement} container - The DOM element containing <script> elements to execute.
   */
  function executeScripts(container) {
    const scripts = container.querySelectorAll("script");

    scripts.forEach((oldScript) => {
      const newScript = document.createElement("script");

      Array.from(oldScript.attributes).forEach(attr => {
        newScript.setAttribute(attr.name, attr.value);
      });

      if (oldScript.src) {
        newScript.src = oldScript.src;
        newScript.async = false;
        document.head.appendChild(newScript);
      } else {
        try {
          newScript.textContent = oldScript.textContent;
          document.body.appendChild(newScript);
          document.body.removeChild(newScript);
        } catch (error) {
          console.error("Error ejecutando script:", error);
        }
      }
    });
  }

  window.adminOpenModal = openModal;
  window.adminCloseModal = closeModal;
  window.executeScripts = executeScripts;
});