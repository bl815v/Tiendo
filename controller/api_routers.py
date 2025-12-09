"""Router aggregation module for FastAPI application.

This module serves as the main router hub that imports and includes
all sub-routers from different functional domains of the application:
- categorias: Product category management
- productos: Product management
- clientes: Customer management
- carritos: Shopping cart management
- pedidos: Order management
- pagos: Payment processing
- envios: Shipping/delivery management

The routers are registered in a specific order to maintain logical
API endpoint organization and dependency relationships.

"""

from fastapi import APIRouter

from .carritos import router as carritos_router
from .categorias import router as categorias_router
from .clientes import router as clientes_router
from .envios import router as envios_router
from .pagos import router as pagos_router
from .pedidos import router as pedidos_router
from .productos import router as productos_router

router = APIRouter()

router.include_router(categorias_router)
router.include_router(productos_router)
router.include_router(clientes_router)
router.include_router(carritos_router)
router.include_router(pedidos_router)
router.include_router(pagos_router)
router.include_router(envios_router)
