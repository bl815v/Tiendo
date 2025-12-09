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

  /**
   * Initializes the header functionality, including:
   * - Waiting for header elements to be available.
   * - Setting up modal dialogs for user account actions (register/login).
   * - Handling modal open/close logic and dynamic content loading via fetch.
   * - Managing search input and button to perform search navigation.
   * 
   * @async
   * @function
   * @returns {Promise<void>} Resolves when the header is initialized or logs errors if initialization fails.
   */
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

    /**
     * Resets the modal content to its initial state and adjusts its size.
     * 
     * This function restores the modal's inner HTML to the initial content,
     * removes the "modal-large" class, and adds the "modal-small" class to
     * ensure the modal appears in its default small size.
     */
    function resetModal() {
      modalContent.innerHTML = modalInicial;
      modalContent.classList.remove("modal-large");
      modalContent.classList.add("modal-small");
    }

    /**
     * Displays the modal by resetting its state and removing the "hidden" class.
     * Also logs a message to the console when the modal is shown.
     */
    function showModal() {
      resetModal();
      modal.classList.remove("hidden");
      console.log("Modal mostrado");
    }

    /**
     * Hides the modal by adding the "hidden" class and resets its content.
     */
    function hideModal() {
      modal.classList.add("hidden");
      resetModal();
    }

    cuenta.addEventListener("click", showModal);

    /**
     * Sets up an event handler for the modal close button.
     * Attaches a click event listener to the element with the ID "modal-close"
     * that triggers the `hideModal` function when clicked.
     */
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

    /**
     * Executes a search based on the user's input.
     * Retrieves the value from the search input, trims whitespace,
     * and if the input is not empty, redirects the browser to the search results page
     * with the search term as a URL query parameter.
     *
     * @function
     * @returns {void}
     */
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
