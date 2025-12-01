document.addEventListener("DOMContentLoaded", () => {
  const menuBtns = document.querySelectorAll(".menu-btn");
  const sections = document.querySelectorAll(".content-section");

  menuBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      menuBtns.forEach((b) => b.classList.remove("active"));
      sections.forEach((s) => s.classList.remove("active"));
      btn.classList.add("active");
      const section = btn.dataset.section;
      document.getElementById(`section-${section}`).classList.add("active");
    });
  });

  // Ejemplo: esto vendrá del backend FastAPI luego
  const userData = {
    nombre: "Juan",
    apellido: "Bedoya",
    correo: "juan@example.com",
    telefono: "+57 300 000 0000",
    pais: "Colombia",
    ciudad: "Bogotá",
    direccion: "Calle 00 #00-00",
  };

  const pedidosEjemplo = [
    {
      id: "PED-001",
      producto: "Audífonos inalámbricos QCY H3",
      precio: 129900,
      estado: "En camino",
      imagen: "/static/img/producto1.jpg",

      envio: {
        pais: "Colombia",
        ciudad: "Bogotá",
        direccion: "Calle 00 #00-00",
        fecha_envio: "2025-11-20",
        fecha_entrega: "2025-11-25",
        empresa: "Servientrega",
        guia: "SRV-998812345",
      },
    },
  ];

  const historialEjemplo = [
    {
      id: "HIS-001",
      producto: "Mouse Logitech G305",
      precio: 159.9,
      fecha: "2025-03-10",
      imagen: "/static/img/producto2.jpg",
    },
  ];

  function renderUsuario() {
    document.getElementById(
      "user-name"
    ).textContent = `${userData.nombre} ${userData.apellido}`;

    document.getElementById("user-nombre").value = userData.nombre;
    document.getElementById("user-apellido").value = userData.apellido;
    document.getElementById("user-correo").value = userData.correo;
    document.getElementById("user-telefono").value = userData.telefono;

    document.getElementById("user-pais").value = userData.pais;
    document.getElementById("user-ciudad").value = userData.ciudad;
    document.getElementById("user-direccion").value = userData.direccion;
  }

  function renderPedidos() {
    const cont = document.getElementById("pedidos-list");
    cont.innerHTML = "";

    pedidosEjemplo.forEach((p, index) => {
      cont.innerHTML += `
      <div class="item-pedido" data-index="${index}">
        <img src="${p.imagen}" alt="producto">
        
        <div class="item-info">
          <p><strong>${p.producto}</strong></p>
          <p>Pedido: ${p.id}</p>
          <p>Precio: $${p.precio.toLocaleString()}</p>
          <p class="estado">${p.estado}</p>
        </div>

        <button class="btn-rastrear">Rastrear</button>

        <div class="detalle-envio">
          <p><strong>Enviar a:</strong> ${p.envio.pais}, ${p.envio.ciudad}, ${
        p.envio.direccion
      }</p>
          <p><strong>Fecha de envío:</strong> ${p.envio.fecha_envio}</p>
          <p><strong>Fecha estimada de entrega:</strong> ${
            p.envio.fecha_entrega
          }</p>
          <p><strong>Empresa transportadora:</strong> ${p.envio.empresa}</p>
          <p><strong>Número de guía:</strong> ${p.envio.guia}</p>
        </div>
      </div>
    `;
    });

    document.querySelectorAll(".btn-rastrear").forEach((btn) => {
      btn.addEventListener("click", () => {
        const parent = btn.parentElement;
        const detalle = parent.querySelector(".detalle-envio");

        if (detalle.style.display === "block") {
          detalle.style.display = "none";
          btn.textContent = "Rastrear";
        } else {
          detalle.style.display = "block";
          btn.textContent = "Ocultar";
        }
      });
    });
  }

  function renderHistorial() {
    const cont = document.getElementById("historial-list");
    cont.innerHTML = "";

    historialEjemplo.forEach((h) => {
      cont.innerHTML += `
        <div class="item-pedido">
          <img src="${h.imagen}" alt="producto">
          <div class="item-info">
            <p><strong>${h.producto}</strong></p>
            <p>Compra: ${h.id}</p>
            <p>Precio: $${h.precio.toLocaleString()}</p>
            <p>Fecha: ${h.fecha}</p>
          </div>
        </div>
      `;
    });
  }

  renderUsuario();
  renderPedidos();
  renderHistorial();
});
