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
  }

  function closeModal() {
    modal.classList.add("hidden");
    modal.setAttribute("aria-hidden", "true");
    modalBody.innerHTML = "";
  }

  window.adminOpenModal = openModal;
  window.adminCloseModal = closeModal;
});
