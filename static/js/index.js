document.addEventListener("DOMContentLoaded", async () => {
  const grid = document.getElementById("grid-productos");
  
  if (!grid) return;

  try {
    // Obtener parámetros de búsqueda
    const params = new URLSearchParams(window.location.search);
    const termino = params.get("search");
    const categoriaId = params.get("categoria");

    // Construir URL según parámetros
    let url = '/api/v1/productos/';
    
    if (categoriaId) {
      url = `/api/v1/productos/categoria/${categoriaId}`;
    }

    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Error al cargar productos');
    }

    const productos = await response.json();

    // Filtrar por término de búsqueda si existe
    let productosFiltrados = productos;
    if (termino) {
      productosFiltrados = productos.filter(p => 
        p.nombre.toLowerCase().includes(termino.toLowerCase()) ||
        (p.descripcion && p.descripcion.toLowerCase().includes(termino.toLowerCase()))
      );
    }

    // Renderizar productos
    grid.innerHTML = '';
    
    if (productosFiltrados.length === 0) {
      grid.innerHTML = '<p class="no-products">No se encontraron productos</p>';
      return;
    }

    productosFiltrados.forEach((p) => {
      // Crear contenedor de tarjeta
      const cardContainer = document.createElement("div");
      cardContainer.classList.add("producto-card");
      
      // Crear enlace que cubre toda la tarjeta
      const link = document.createElement("a");
      link.href = `/product?id=${p.id_producto}`;
      link.style.textDecoration = 'none';
      link.style.color = 'inherit';
      link.style.display = 'block';
      link.style.height = '100%';
      
      link.innerHTML = `
        <img src="${p.imagen || 'https://via.placeholder.com/300x200?text=Sin+imagen'}" 
             alt="${p.nombre}"
             onerror="this.src='/static/img/placeholder.jpg'">
        <div class="producto-nombre">${p.nombre}</div>
        <div class="producto-precio">$${p.precio.toFixed(2)}</div>
      `;
      
      cardContainer.appendChild(link);
      grid.appendChild(cardContainer);
    });

  } catch (error) {
    console.error('Error cargando productos:', error);
    grid.innerHTML = '<p class="error">Error al cargar los productos</p>';
  }
});