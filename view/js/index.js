document.addEventListener("DOMContentLoaded", () => {
  // Ejemplos de productos (luego se reemplazan con backend)
  const productos = [
    {
      nombre: "Audífonos inalámbricos Pro",
      precio: 199.99,
      imagen: "https://images.unsplash.com/photo-1585386959984-a4155224a1ad",
    },
    {
      nombre: "Mouse Gamer RGB",
      precio: 79.9,
      imagen: "https://images.unsplash.com/photo-1589578527966-107ea3c6b37c",
    },
    {
      nombre: "Teclado Mecánico Azul",
      precio: 149.5,
      imagen: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
    },
    {
      nombre: "Portátil 15'' Core i7",
      precio: 3299.0,
      imagen: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
    },
  ];

  const grid = document.getElementById("grid-productos");

  productos.forEach((p) => {
    const card = document.createElement("div");
    card.classList.add("producto-card");

    card.innerHTML = `
      <img src="${p.imagen}" alt="${p.nombre}">
      <div class="producto-nombre">${p.nombre}</div>
      <div class="producto-precio">$${p.precio}</div>
    `;

    grid.appendChild(card);
  });

  const btnCuenta = document.querySelector(".btn-cuenta");
  const modal = document.getElementById("modal");
  const modalContent = document.getElementById("modal-content");

  // contenido inicial del modal (Mi cuenta)
  const modalInicial = `
  <h2 class="modal-titulo">Mi cuenta</h2>
  <div class="modal-opciones">
      <button class="btn-modal-primary" id="btn-register">Registrarse</button>
      <button class="btn-modal-outline" id="btn-login">Iniciar sesión</button>
  </div>
`;

  // Función para resetear modal
  function resetModal() {
    modalContent.innerHTML = modalInicial;
    modalContent.classList.remove("modal-large");
    modalContent.classList.add("modal-small");
  }

  function addCloseButton() {
    const closeBtn = document.createElement("div");
    closeBtn.classList.add("modal-close");
    closeBtn.innerHTML = "✕";
    closeBtn.style.position = "absolute";
    closeBtn.style.top = "10px";
    closeBtn.style.right = "15px";
    closeBtn.style.fontSize = "22px";
    closeBtn.style.cursor = "pointer";
    closeBtn.style.color = "#004B2D";
    closeBtn.style.fontWeight = "bold";

    modalContent.appendChild(closeBtn);

    closeBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
      resetModal();
    });
  }

  btnCuenta.addEventListener("click", () => {
    modal.classList.remove("hidden");

    resetModal();

    addCloseButton();
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.classList.add("hidden");
      resetModal();
    }
  });

  document.addEventListener("click", async (e) => {
    if (e.target.id === "btn-register") {
      const response = await fetch("view/register.html");
      const html = await response.text();

      modalContent.innerHTML = html;
      modalContent.classList.remove("modal-small");
      modalContent.classList.add("modal-large");

      addCloseButton();
    }

    if (e.target.id === "btn-login") {
      const response = await fetch("view/login.html");
      const html = await response.text();

      modalContent.innerHTML = html;
      modalContent.classList.remove("modal-large");
      modalContent.classList.add("modal-small");

      addCloseButton();
    }

    if (e.target.id === "go-register") {
      const response = await fetch("view/register.html");
      const html = await response.text();

      modalContent.innerHTML = html;
      modalContent.classList.remove("modal-small");
      modalContent.classList.add("modal-large");

      addCloseButton();
    }
  });
});
