document.addEventListener("DOMContentLoaded", async () => {
  // Asumimos que el usuario tiene ID 1 (debes implementar autenticación)
  const clienteId = 1;
  
  try {
    // Obtener carritos del cliente
    const response = await fetch(`/api/v1/carritos/cliente/${clienteId}`);
    
    if (!response.ok) {
      throw new Error('Error al cargar el carrito');
    }

    const carritos = await response.json();
    
    if (carritos.length === 0) {
      renderCarritoVacio();
      return;
    }

    // Usar el primer carrito activo (deberías tener lógica para carrito activo)
    const carritoActivo = carritos[0];
    
    // Obtener detalles del carrito
    const detallesResponse = await fetch(`/api/v1/carritos/${carritoActivo.id_carrito}/detalles`);
    
    if (!detallesResponse.ok) {
      throw new Error('Error al cargar detalles del carrito');
    }

    const detalles = await detallesResponse.json();
    
    // Para cada detalle, obtener información del producto
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

    // Configurar botones de pago
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
        // 1. Crear pedido
        const pedidoData = {
          id_cliente: clienteId,
          estado: "PENDIENTE", // Usa el enum EstadoPedido
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

        // 2. Crear detalles del pedido
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

        // 3. Crear pago
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

        // 4. Opcional: Crear envío
        const envioData = {
          id_pedido: pedido.id_pedido,
          direccion_envio: "Dirección del cliente", // Obtener de perfil
          ciudad: "Ciudad",
          pais: "País",
          estado_envio: "PREPARACION"
        };

        await fetch('/api/v1/envios/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(envioData)
        });

        // 5. Limpiar carrito
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

  function calcularTotal(detalles) {
    return detalles.reduce((total, detalle) => {
      return total + (detalle.precio_unitario * detalle.cantidad);
    }, 0);
  }

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