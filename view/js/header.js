(function () {
  async function initHeader() {
    const modal = document.getElementById("modal");
    const modalContent = document.getElementById("modal-content");

    const modalInicial = `
      <h2 class="modal-titulo">Mi cuenta</h2>
      <div class="modal-opciones">
        <button class="btn-modal-primary" id="btn-register">Registrarse</button>
        <button class="btn-modal-outline" id="btn-login">Iniciar sesión</button>
      </div>
    `;

    if (!modal || !modalContent) {
      console.warn(
        "header.js: modal o modal-content no encontrados en la página. Asegúrate de tenerlos en el HTML principal."
      );
    }

    function resetModal() {
      if (!modalContent) return;
      modalContent.innerHTML = modalInicial;
      modalContent.classList.remove("modal-large");
      modalContent.classList.add("modal-small");
    }

    function removeExistingCloseBtn() {
      if (!modalContent) return;
      const existing = modalContent.querySelector(".modal-close");
      if (existing) existing.remove();
    }

    function addCloseButton() {
      if (!modalContent) return;
      removeExistingCloseBtn();

      const closeBtn = document.createElement("div");
      closeBtn.classList.add("modal-close");
      closeBtn.textContent = "✕";
      modalContent.appendChild(closeBtn);

      closeBtn.addEventListener("click", () => {
        if (modal) modal.classList.add("hidden");
        resetModal();
      });
    }

    document.body.addEventListener("click", (e) => {
      if (e.target.closest && e.target.closest(".btn-cuenta")) {
        if (modal) {
          modal.classList.remove("hidden");
          resetModal();
          addCloseButton();
        }
      }
    });

    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) {
          modal.classList.add("hidden");
          resetModal();
        }
      });
    }

    document.body.addEventListener("click", async (e) => {
      const target = e.target;
      if (target.id === "btn-register") {
        if (!modalContent) return;
        try {
          const res = await fetch("view/register.html");
          const html = await res.text();
          modalContent.innerHTML = html;
          modalContent.classList.remove("modal-small");
          modalContent.classList.add("modal-large");
          addCloseButton();
        } catch (err) {
          console.error("Error loading register.html", err);
        }
      }
      if (target.id === "btn-login") {
        if (!modalContent) return;
        try {
          const res = await fetch("view/login.html");
          const html = await res.text();
          modalContent.innerHTML = html;
          modalContent.classList.remove("modal-large");
          modalContent.classList.add("modal-small");
          addCloseButton();
        } catch (err) {
          console.error("Error loading login.html", err);
        }
      }

      if (target.id === "go-register") {
        if (!modalContent) return;
        try {
          const res = await fetch("view/register.html");
          const html = await res.text();
          modalContent.innerHTML = html;
          modalContent.classList.remove("modal-small");
          modalContent.classList.add("modal-large");
          addCloseButton();
        } catch (err) {
          console.error("Error loading register.html", err);
        }
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHeader);
  } else {
    initHeader();
  }
})();
