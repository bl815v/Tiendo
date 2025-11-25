document.addEventListener("DOMContentLoaded", () => {
  fetch("view/header.html")
    .then((r) => r.text())
    .then((h) => {
      document.getElementById("header-placeholder").innerHTML = h;
      const script = document.createElement("script");
      script.src = "view/js/header.js";
      document.body.appendChild(script);
    });

  // Simulación de producto cargado por JS
  const producto = {
    nombre: "Audífonos Inalámbricos Bluetooth",
    precio: 199.99,
    descripcion:
      "Bluetooth 5.0, cancelación de ruido, estuche de carga rápida, batería 20h.",
    categoria: "Audífonos",
    imagen:
      "https://www.qcy.com/cdn/shop/files/2_83d8c1eb-c4c1-43fe-a2be-8ddccedf984a_2048x2048.png?v=1732002940",
  };

  document.getElementById("img-producto").src = producto.imagen;
  document.getElementById("nombre-producto").textContent = producto.nombre;
  document.getElementById("precio-producto").textContent =
    "$" + producto.precio;
  document.getElementById("desc-producto").textContent = producto.descripcion;

  const form = document.getElementById("formCantidad");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const cantidad = parseInt(document.getElementById("cantidad").value);

    alert(`Se agregaron ${cantidad} unidad(es) al carrito ✔️`);
  });
});
