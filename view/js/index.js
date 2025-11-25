document.addEventListener("DOMContentLoaded", () => {
  fetch("view/header.html")
    .then((r) => r.text())
    .then((h) => {
      document.getElementById("header-placeholder").innerHTML = h;
      const script = document.createElement("script");
      script.src = "view/js/header.js";
      document.body.appendChild(script);
    });

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
});
