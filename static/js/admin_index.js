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

          // Ejecutar scripts después de insertar el HTML
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

  function openModal(html) {
    modalBody.innerHTML = html;
    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");

    // Ejecutar scripts en el modal
    setTimeout(() => executeScripts(modalBody), 100);
  }

  function closeModal() {
    modal.classList.add("hidden");
    modal.setAttribute("aria-hidden", "true");
    modalBody.innerHTML = "";
  }

  // Función para ejecutar scripts después de insertar HTML
  function executeScripts(container) {
    const scripts = container.querySelectorAll("script");

    scripts.forEach((oldScript) => {
      const newScript = document.createElement("script");

      // Copiar todos los atributos
      Array.from(oldScript.attributes).forEach(attr => {
        newScript.setAttribute(attr.name, attr.value);
      });

      // Si tiene src, cargar el script externo
      if (oldScript.src) {
        newScript.src = oldScript.src;
        newScript.async = false;
        document.head.appendChild(newScript);
      } else {
        // Script inline - ejecutar el código
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