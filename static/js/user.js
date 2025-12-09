document.addEventListener("DOMContentLoaded", async () => {
  const menuBtns = document.querySelectorAll(".menu-btn");
  const sections = document.querySelectorAll(".content-section");

  // Manejar navegación entre secciones
  menuBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      menuBtns.forEach((b) => b.classList.remove("active"));
      sections.forEach((s) => s.classList.remove("active"));
      btn.classList.add("active");
      const section = btn.dataset.section;
      document.getElementById(`section-${section}`).classList.add("active");
    });
  });

  // Asumimos cliente con ID 1 (debes implementar autenticación)
  const clienteId = 1;

  try {
    // Cargar datos del cliente
    const clienteResponse = await fetch(`/api/v1/clientes/${clienteId}`);
    
    if (!clienteResponse.ok) {
      throw new Error('Error cargando datos del cliente');
    }

    const clienteData = await clienteResponse.json();
    renderUsuario(clienteData);

    // Cargar pedidos del cliente
    const pedidosResponse = await fetch(`/api/v1/pedidos/cliente/${clienteId}`);
    
    if (pedidosResponse.ok) {
      const pedidosData = await pedidosResponse.json();
      renderPedidos(pedidosData);
    }

    // Configurar formulario de edición
    const formEditar = document.getElementById("form-editar-usuario");
    if (formEditar) {
      formEditar.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const datosActualizados = {
          nombre: document.getElementById("user-nombre").value,
          apellido: document.getElementById("user-apellido").value,
          correo: document.getElementById("user-correo").value,
          telefono: document.getElementById("user-telefono").value,
          direccion: document.getElementById("user-direccion").value,
          ciudad: document.getElementById("user-ciudad").value,
          pais: document.getElementById("user-pais").value,
        };

        try {
          const response = await fetch(`/api/v1/clientes/${clienteId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosActualizados)
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error actualizando datos');
          }

          const clienteActualizado = await response.json();
          alert("Datos actualizados correctamente");
          renderUsuario(clienteActualizado);
          
        } catch (error) {
          console.error('Error actualizando datos:', error);
          alert(`Error: ${error.message}`);
        }
      });
    }

  } catch (error) {
    console.error('Error cargando datos de usuario:', error);
  }

  function renderUsuario(cliente) {
    document.getElementById("user-name").textContent = `${cliente.nombre} ${cliente.apellido}`;
    
    if (document.getElementById("user-nombre")) {
      document.getElementById("user-nombre").value = cliente.nombre || "";
    }
    if (document.getElementById("user-apellido")) {
      document.getElementById("user-apellido").value = cliente.apellido || "";
    }
    if (document.getElementById("user-correo")) {
      document.getElementById("user-correo").value = cliente.correo || "";
    }
    if (document.getElementById("user-telefono")) {
      document.getElementById("user-telefono").value = cliente.telefono || "";
    }
    if (document.getElementById("user-pais")) {
      document.getElementById("user-pais").value = cliente.pais || "";
    }
    if (document.getElementById("user-ciudad")) {
      document.getElementById("user-ciudad").value = cliente.ciudad || "";
    }
    if (document.getElementById("user-direccion")) {
      document.getElementById("user-direccion").value = cliente.direccion || "";
    }
  }

  async function renderPedidos(pedidos) {
    const cont = document.getElementById("pedidos-list");
    
    if (!cont) return;
    
    cont.innerHTML = "";
    
    if (pedidos.length === 0) {
      cont.innerHTML = '<p class="no-orders">No tienes pedidos aún</p>';
      return;
    }

    for (const pedido of pedidos) {
      // Obtener detalles del pedido
      const detallesResponse = await fetch(`/api/v1/pedidos/${pedido.id_pedido}/detalles`);
      let detalles = [];
      
      if (detallesResponse.ok) {
        detalles = await detallesResponse.json();
      }

      // Obtener envío si existe
      let envio = null;
      try {
        const envioResponse = await fetch(`/api/v1/envios/pedido/${pedido.id_pedido}`);
        if (envioResponse.ok) {
          envio = await envioResponse.json();
        }
      } catch (error) {
        console.error('Error cargando envío:', error);
      }

      // Para cada producto en los detalles, obtener información completa
      const productosCompletos = await Promise.all(
        detalles.map(async (detalle) => {
          try {
            const productoResponse = await fetch(`/api/v1/productos/${detalle.id_producto}`);
            if (productoResponse.ok) {
              return await productoResponse.json();
            }
          } catch (error) {
            console.error('Error cargando producto:', error);
          }
          return null;
        })
      );

      // Renderizar pedido
      const pedidoDiv = document.createElement("div");
      pedidoDiv.classList.add("item-pedido");
      pedidoDiv.setAttribute("data-pedido-id", pedido.id_pedido);
      
      let productosHTML = "";
      productosCompletos.forEach((producto, index) => {
        if (producto) {
          productosHTML += `
            <div class="producto-pedido">
              <img src="${producto.imagen || 'https://via.placeholder.com/50x50'}" alt="${producto.nombre}">
              <div>
                <p><strong>${producto.nombre}</strong></p>
                <p>Cantidad: ${detalles[index].cantidad}</p>
                <p>Precio: $${detalles[index].precio_unitario.toFixed(2)}</p>
              </div>
            </div>
          `;
        }
      });

      pedidoDiv.innerHTML = `
        <div class="pedido-header">
          <h3>Pedido #${pedido.id_pedido}</h3>
          <span class="estado-pedido ${pedido.estado.toLowerCase()}">${pedido.estado}</span>
        </div>
        
        <div class="pedido-productos">
          ${productosHTML}
        </div>
        
        <div class="pedido-info">
          <p><strong>Fecha:</strong> ${new Date(pedido.fecha_pedido).toLocaleDateString()}</p>
          <p><strong>Total:</strong> $${pedido.total?.toFixed(2) || '0.00'}</p>
        </div>
        
        ${envio ? `
          <button class="btn-rastrear">Ver detalles de envío</button>
          <div class="detalle-envio" style="display: none;">
            <h4>Información de envío</h4>
            <p><strong>Dirección:</strong> ${envio.direccion_envio || 'No especificada'}</p>
            <p><strong>Ciudad:</strong> ${envio.ciudad || 'No especificada'}</p>
            <p><strong>País:</strong> ${envio.pais || 'No especificada'}</p>
            <p><strong>Estado:</strong> ${envio.estado_envio || 'PENDIENTE'}</p>
            ${envio.fecha_envio ? `<p><strong>Fecha envío:</strong> ${new Date(envio.fecha_envio).toLocaleDateString()}</p>` : ''}
            ${envio.fecha_entrega ? `<p><strong>Fecha entrega estimada:</strong> ${new Date(envio.fecha_entrega).toLocaleDateString()}</p>` : ''}
          </div>
        ` : ''}
      `;
      
      cont.appendChild(pedidoDiv);
    }

    // Configurar botones de rastreo
    document.querySelectorAll(".btn-rastrear").forEach((btn) => {
      btn.addEventListener("click", () => {
        const detalle = btn.nextElementSibling;
        if (detalle.style.display === "block") {
          detalle.style.display = "none";
          btn.textContent = "Ver detalles de envío";
        } else {
          detalle.style.display = "block";
          btn.textContent = "Ocultar detalles";
        }
      });
    });
  }
});