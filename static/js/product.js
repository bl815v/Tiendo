document.addEventListener("DOMContentLoaded", async () => {
  console.log("product.js cargado");

  const params = new URLSearchParams(window.location.search);
  const productoId = params.get("id");

  console.log("Producto ID obtenido de URL:", productoId);

  if (!productoId) {
    mostrarError("No se especificó ID de producto en la URL");
    return;
  }

  try {
    console.log("Solicitando producto a API...");
    const response = await fetch(`/api/v1/productos/${productoId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Producto no encontrado');
      }
      const errorText = await response.text();
      throw new Error(`Error ${response.status}: ${errorText}`);
    }

    const producto = await response.json();
    console.log("Producto recibido:", producto);

    actualizarProductoEnDOM(producto);

    configurarFormulario(producto);

  } catch (error) {
    console.error('Error cargando producto:', error);
    mostrarError(error.message);
  }
});

/**
 * Actualiza los elementos del DOM con la información de un producto.
 *
 * Busca y actualiza los siguientes elementos por su ID o clase:
 * - Imagen del producto (con fallback a una imagen por defecto si no hay imagen disponible)
 * - Nombre del producto
 * - Precio del producto (formateado a dos decimales)
 * - Descripción del producto
 * - Categoría del producto (si está disponible)
 *
 * @param {Object} producto - Objeto que contiene los datos del producto.
 * @param {string} [producto.imagen] - URL de la imagen del producto.
 * @param {string} [producto.nombre] - Nombre del producto.
 * @param {number} [producto.precio] - Precio del producto.
 * @param {string} [producto.descripcion] - Descripción del producto.
 * @param {string} [producto.categoria] - Categoría del producto.
 */
function actualizarProductoEnDOM(producto) {
  const imagen = document.getElementById("img-producto");
  const nombre = document.getElementById("nombre-producto");
  const precio = document.getElementById("precio-producto");
  const desc = document.getElementById("desc-producto");
  const categoria = document.querySelector(".categoria");

  if (imagen) {
    if (producto.imagen && producto.imagen.trim() !== '') {
      imagen.src = producto.imagen;
    } else {
      imagen.src = '/static/img/placeholder.jpg';
    }
    imagen.alt = producto.nombre || 'Producto';
  }

  if (nombre) nombre.textContent = producto.nombre || "Producto sin nombre";
  if (precio) precio.textContent = `$${(producto.precio || 0).toFixed(2)}`;
  if (desc) desc.textContent = producto.descripcion || "Sin descripción disponible";

  if (categoria && producto.categoria) {
    categoria.textContent = producto.categoria;
  }
}

/**
 * Configura el formulario de cantidad para agregar un producto al carrito.
 * 
 * Este método agrega un event listener al formulario identificado por "formCantidad".
 * Al enviar el formulario, valida la cantidad, obtiene o crea un carrito para el cliente,
 * y agrega el producto seleccionado al carrito mediante llamadas a la API.
 * 
 * @param {Object} producto - Objeto que representa el producto a agregar.
 * @param {number} producto.id_producto - ID único del producto.
 * @param {string} producto.nombre - Nombre del producto.
 * @param {number} producto.precio - Precio unitario del producto.
 */
function configurarFormulario(producto) {
  const form = document.getElementById("formCantidad");

  if (!form) {
    console.warn("Formulario no encontrado");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const cantidad = parseInt(document.getElementById("cantidad").value);

    if (cantidad < 1) {
      alert("La cantidad debe ser al menos 1");
      return;
    }

    try {
      const clienteId = 1;

      const carritosResponse = await fetch(`/api/v1/carritos/cliente/${clienteId}`);
      let carritoId;

      if (carritosResponse.ok) {
        const carritos = await carritosResponse.json();
        if (carritos.length > 0) {
          carritoId = carritos[0].id_carrito;
        } else {
          const nuevoCarrito = {
            id_cliente: clienteId,
            fecha_creacion: new Date().toISOString()
          };

          const crearResponse = await fetch('/api/v1/carritos/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(nuevoCarrito)
          });

          if (crearResponse.ok) {
            const carritoCreado = await crearResponse.json();
            carritoId = carritoCreado.id_carrito;
          }
        }
      }

      if (!carritoId) {
        throw new Error('No se pudo obtener o crear el carrito');
      }

      const detalleCarrito = {
        id_producto: producto.id_producto,
        cantidad: cantidad,
        precio_unitario: producto.precio
      };

      const response = await fetch(`/api/v1/carritos/${carritoId}/detalles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(detalleCarrito)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al agregar al carrito');
      }

      const detalleAgregado = await response.json();

      mostrarMensajeExito(`Se agregaron ${cantidad} unidad(es) de "${producto.nombre}" al carrito ✔️`);

      setTimeout(() => {
        window.location.href = '/cart';
      }, 2000);

    } catch (error) {
      console.error('Error:', error);
      alert(`Error: ${error.message}`);
    }
  });
}

/**
 * Displays a success notification message on the screen with custom styling.
 * The notification appears at the top-right corner, shows the provided message,
 * and indicates redirection to the cart in 2 seconds. It automatically disappears after 3 seconds.
 *
 * @param {string} mensaje - The success message to display in the notification.
 */
function mostrarMensajeExito(mensaje) {
  const notificacion = document.createElement('div');
  notificacion.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #004b2d;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
  `;

  notificacion.innerHTML = `
    ${mensaje}
    <br>
    <small>Redirigiendo al carrito en 2 segundos...</small>
  `;

  document.body.appendChild(notificacion);

  setTimeout(() => {
    notificacion.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => notificacion.remove(), 300);
  }, 3000);
}

/**
 * Displays an error message inside the element with the class 'producto-container'.
 * Replaces the container's content with a styled error message and a link to return to the store.
 *
 * @param {string} mensaje - The error message to display to the user.
 */
function mostrarError(mensaje) {
  const contenedor = document.querySelector('.producto-container');
  if (!contenedor) return;

  contenedor.innerHTML = `
    <div style="
      text-align: center;
      padding: 40px;
      background: #f8d7da;
      border: 1px solid #f5c6cb;
      border-radius: 8px;
      color: #721c24;
      width: 100%;
    ">
      <h2 style="margin-top: 0;">Error al cargar el producto</h2>
      <p>${mensaje}</p>
      <a href="/" 
         style="
           display: inline-block;
           margin-top: 20px;
           padding: 10px 20px;
           background: #004b2d;
           color: white;
           text-decoration: none;
           border-radius: 8px;
         ">
        Volver a la tienda
      </a>
    </div>
  `;
}

const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);