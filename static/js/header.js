(function () {
  console.log("header.js cargado");

  function waitForHeader(timeout = 3000) {
    return new Promise((resolve, reject) => {
      const start = Date.now();
      const check = setInterval(() => {
        const header = document.querySelector("header");
        const searchBtn = document.querySelector("#btn-search");
        const searchInput = document.querySelector("#input-busqueda");
        const cuenta = document.querySelector("#btn-cuenta");
        const modal = document.getElementById("modal");
        const modalContent = document.getElementById("modal-content");

        if (
          header &&
          searchBtn &&
          searchInput &&
          cuenta &&
          modal &&
          modalContent
        ) {
          clearInterval(check);
          console.log("Todos los elementos del header encontrados");
          resolve({
            header,
            searchBtn,
            searchInput,
            cuenta,
            modal,
            modalContent,
          });
        } else if (Date.now() - start > timeout) {
          clearInterval(check);
          reject(new Error("Elementos del header no encontrados"));
        }
      }, 30);
    });
  }

  async function initHeader() {
    let elements;
    try {
      elements = await waitForHeader();
    } catch (err) {
      console.error("Error inicializando header:", err);
      return;
    }

    const { searchBtn, searchInput, cuenta, modal, modalContent } = elements;

    function addCloseButton(content) {
      return `
        <div class="modal-close" id="modal-close">✕</div>
        ${content}
      `;
    }

    const modalInicial = addCloseButton(`
      <h2 class="modal-titulo">Mi cuenta</h2>
      <div class="modal-opciones">
        <button class="btn-modal-primary" id="btn-register">Registrarse</button>
        <button class="btn-modal-outline" id="btn-login">Iniciar sesión</button>
      </div>
    `);

    function resetModal() {
      modalContent.innerHTML = modalInicial;
      modalContent.classList.remove("modal-large");
      modalContent.classList.add("modal-small");
    }

    function showModal() {
      resetModal();
      modal.classList.remove("hidden");
      console.log("Modal mostrado");
    }

    function hideModal() {
      modal.classList.add("hidden");
      resetModal();
    }

    cuenta.addEventListener("click", showModal);

    function setupCloseHandler() {
      const closeBtn = document.getElementById("modal-close");
      if (closeBtn) {
        closeBtn.addEventListener("click", hideModal);
      }
    }

    modal.addEventListener("click", (e) => {
      if (e.target === modal || e.target.id === "modal-close") {
        hideModal();
      }
    });

    modalContent.addEventListener("click", async (e) => {
      const target = e.target;

      if (target.id === "btn-register" || target.id === "go-register") {
        try {
          const res = await fetch("/register-template");
          if (!res.ok) throw new Error("Error cargando registro");
          const content = await res.text();
          modalContent.innerHTML = addCloseButton(content);
          modalContent.classList.add("modal-large");
          modalContent.classList.remove("modal-small");
          setupCloseHandler();
        } catch (err) {
          console.error("Error:", err);
          modalContent.innerHTML = addCloseButton(
            `<p style="color:#c00">Error cargando formulario.</p>`
          );
          setupCloseHandler();
        }
      }

      if (target.id === "btn-login" || target.id === "go-login") {
        try {
          const res = await fetch("/login-template");
          if (!res.ok) throw new Error("Error cargando login");
          const content = await res.text();
          modalContent.innerHTML = addCloseButton(content);
          modalContent.classList.remove("modal-large");
          modalContent.classList.add("modal-small");
          setupCloseHandler();
        } catch (err) {
          console.error("Error:", err);
          modalContent.innerHTML = addCloseButton(
            `<p style="color:#c00">Error cargando formulario.</p>`
          );
          setupCloseHandler();
        }
      }
    });

    setupCloseHandler();

    function ejecutarBusqueda() {
      const termino = (searchInput.value || "").trim();
      console.log("Buscando:", termino);
      if (!termino) return;
      const q = encodeURIComponent(termino);
      window.location.href = `/?search=${q}`;
    }

    searchBtn.addEventListener("click", ejecutarBusqueda);
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        ejecutarBusqueda();
      }
    });

    console.log("Header inicializado correctamente");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHeader);
  } else {
    initHeader();
  }
})();
