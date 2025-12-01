document.addEventListener("DOMContentLoaded", () => {
  const carrito = [
    {
      nombre: "Audífonos inalámbricos QCY H3 Pro",
      precio: 199.99,
      cantidad: 1,
      imagen:
        "https://www.qcy.com/cdn/shop/files/2_83d8c1eb-c4c1-43fe-a2be-8ddccedf984a_2048x2048.png?v=1732002940",
    },
  ];

  const contenedor = document.getElementById("cart-items");

  function renderCarrito() {
    contenedor.innerHTML = "";
    let subtotal = 0;

    carrito.forEach((item) => {
      subtotal += item.precio * item.cantidad;

      const div = document.createElement("div");
      div.classList.add("cart-product");

      div.innerHTML = `
        <img src="${item.imagen}" alt="">
        <div class="cart-product-info">
          <h4>${item.nombre}</h4>
          <p>Cantidad: ${item.cantidad}</p>
          <p>Precio: $${item.precio.toFixed(2)}</p>
        </div>
      `;

      contenedor.appendChild(div);
    });

    document.getElementById("subtotal").textContent = "$" + subtotal.toFixed(2);

    const envio = subtotal > 0 ? 8.99 : 0;
    document.getElementById("envio").textContent = "$" + envio.toFixed(2);

    document.getElementById("total").textContent =
      "$" + (subtotal + envio).toFixed(2);
  }

  renderCarrito();

  const btnRef = document.getElementById("btn-ref");
  const refText = document.getElementById("ref-text");
  const btnPagar = document.getElementById("btn-pagar");

  let referenciaGenerada = null;

  btnPagar.disabled = true;

  function actualizarEstadoBoton() {
    const metodo = document.querySelector('input[name="pago"]:checked');

    btnPagar.disabled = !(metodo && referenciaGenerada);
  }

  btnRef.addEventListener("click", () => {
    referenciaGenerada = "REF-" + Math.floor(Math.random() * 1000000);

    alert("Referencia generada: " + referenciaGenerada);

    refText.textContent = "Referencia: " + referenciaGenerada;

    actualizarEstadoBoton();
  });

  document.querySelectorAll('input[name="pago"]').forEach((radio) => {
    radio.addEventListener("change", actualizarEstadoBoton);
  });

  btnPagar.addEventListener("click", () => {
    const metodo = document.querySelector('input[name="pago"]:checked');

    if (!metodo) {
      alert("Debes seleccionar un método de pago.");
      return;
    }

    if (!referenciaGenerada) {
      alert("Debes generar una referencia antes de pagar.");
      return;
    }

    alert("Enviando pago...");
    alert("Pago procesado correctamente.");
  });
});
