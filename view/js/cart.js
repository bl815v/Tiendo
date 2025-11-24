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
});
