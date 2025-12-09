document.addEventListener("DOMContentLoaded", async () => {
  const clienteId = 1;

  try {
    const response = await fetch(`/api/v1/carritos/cliente/${clienteId}`);

    if (!response.ok) {
      throw new Error('Error al cargar el carrito');
    }

    const carritos = await response.json();

    if (carritos.length === 0) {
      renderCarritoVacio();
      return;
    }

    const carritoActivo = carritos[0];

    const detallesResponse = await fetch(`/api/v1/carritos/${carritoActivo.id_carrito}/detalles`);

    if (!detallesResponse.ok) {
      throw new Error('Error al cargar detalles del carrito');
    }

    const detalles = await detallesResponse.json();

    const detallesCompletos = await Promise.all(
      detalles.map(async (detalle) => {
        const productoResponse = await fetch(`/api/v1/productos/${detalle.id_producto}`);
        if (productoResponse.ok) {
          const producto = await productoResponse.json();
          return {
            ...detalle,
            producto: producto
          };
        }
        return detalle;
      })
    );

    renderCarrito(detallesCompletos);

    const btnRef = document.getElementById("btn-ref");
    const refText = document.getElementById("ref-text");
    const btnPagar = document.getElementById("btn-pagar");

    let referenciaGenerada = null;
    btnPagar.disabled = true;

    /**
     * Updates the state of the payment button based on the selected payment method
     * and whether a reference has been generated.
     *
     * Disables the payment button if no payment method is selected or if the
     * reference has not been generated.
     *
     * @function
     */
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

    btnPagar.addEventListener("click", async () => {
      const metodo = document.querySelector('input[name="pago"]:checked');

      if (!metodo) {
        alert("Debes seleccionar un método de pago.");
        return;
      }

      if (!referenciaGenerada) {
        alert("Debes generar una referencia antes de pagar.");
        return;
      }

      try {
        const pedidoData = {
          id_cliente: clienteId,
          estado: "PENDIENTE",
          fecha_pedido: new Date().toISOString(),
          total: calcularTotal(detallesCompletos)
        };

        const pedidoResponse = await fetch('/api/v1/pedidos/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(pedidoData)
        });

        if (!pedidoResponse.ok) throw new Error('Error creando pedido');

        const pedido = await pedidoResponse.json();

        for (const detalle of detallesCompletos) {
          const detallePedido = {
            id_producto: detalle.id_producto,
            cantidad: detalle.cantidad,
            precio_unitario: detalle.precio_unitario
          };

          await fetch(`/api/v1/pedidos/${pedido.id_pedido}/detalles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(detallePedido)
          });
        }

        const pagoData = {
          id_pedido: pedido.id_pedido,
          monto: calcularTotal(detallesCompletos),
          metodo: metodo.value.toUpperCase(),
          referencia: referenciaGenerada,
          estado: "COMPLETADO"
        };

        await fetch('/api/v1/pagos/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(pagoData)
        });

        const envioData = {
          id_pedido: pedido.id_pedido,
          direccion_envio: "Dirección del cliente",
          ciudad: "Ciudad",
          pais: "País",
          estado_envio: "PREPARACION"
        };

        await fetch('/api/v1/envios/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(envioData)
        });

        await fetch(`/api/v1/carritos/${carritoActivo.id_carrito}`, {
          method: 'DELETE'
        });

        alert("Pago procesado correctamente. Pedido #" + pedido.id_pedido);
        window.location.href = `/user?pedido=${pedido.id_pedido}`;

      } catch (error) {
        console.error('Error en el proceso de pago:', error);
        alert("Error procesando el pago: " + error.message);
      }
    });

  } catch (error) {
    console.error('Error:', error);
    renderCarritoVacio();
  }

  /**
   * Calculates the total price from an array of detail objects.
   *
   * @param {Array<{precio_unitario: number, cantidad: number}>} detalles - Array of objects containing unit price and quantity.
   * @returns {number} The total price calculated as the sum of (precio_unitario * cantidad) for each detail.
   */
  function calcularTotal(detalles) {
    return detalles.reduce((total, detalle) => {
      return total + (detalle.precio_unitario * detalle.cantidad);
    }, 0);
  }

  /**
   * Renders the shopping cart items and updates subtotal, shipping, and total amounts in the DOM.
   *
   * @param {Array<Object>} detalles - Array of cart item details.
   * @param {Object} detalles[].producto - Product information.
   * @param {string} [detalles[].producto.imagen] - URL of the product image.
   * @param {string} [detalles[].producto.nombre] - Name of the product.
   * @param {number} detalles[].precio_unitario - Unit price of the product.
   * @param {number} detalles[].cantidad - Quantity of the product in the cart.
   *
   * Updates the following DOM elements by their IDs:
   * - "cart-items": Displays the list of cart products.
   * - "subtotal": Shows the subtotal amount.
   * - "envio": Shows the shipping cost (fixed at $8.99 if subtotal > 0).
   * - "total": Shows the total amount (subtotal + shipping).
   */
  function renderCarrito(detalles) {
    const contenedor = document.getElementById("cart-items");
    contenedor.innerHTML = "";

    let subtotal = 0;

    detalles.forEach((detalle) => {
      subtotal += detalle.precio_unitario * detalle.cantidad;

      const div = document.createElement("div");
      div.classList.add("cart-product");

      div.innerHTML = `
        <img src="${detalle.producto?.imagen || 'https://via.placeholder.com/100x100'}" alt="${detalle.producto?.nombre || 'Producto'}">
        <div class="cart-product-info">
          <h4>${detalle.producto?.nombre || 'Producto'}</h4>
          <p>Cantidad: ${detalle.cantidad}</p>
          <p>Precio unitario: $${detalle.precio_unitario.toFixed(2)}</p>
          <p>Subtotal: $${(detalle.precio_unitario * detalle.cantidad).toFixed(2)}</p>
        </div>
      `;

      contenedor.appendChild(div);
    });

    document.getElementById("subtotal").textContent = "$" + subtotal.toFixed(2);

    const envio = subtotal > 0 ? 8.99 : 0;
    document.getElementById("envio").textContent = "$" + envio.toFixed(2);

    document.getElementById("total").textContent = "$" + (subtotal + envio).toFixed(2);
  }

  function renderCarritoVacio() {
    const contenedor = document.getElementById("cart-items");
    contenedor.innerHTML = '<p class="empty-cart">El carrito está vacío</p>';

    document.getElementById("subtotal").textContent = "$0.00";
    document.getElementById("envio").textContent = "$0.00";
    document.getElementById("total").textContent = "$0.00";

    document.getElementById("btn-ref").disabled = true;
    document.getElementById("btn-pagar").disabled = true;
  }
});