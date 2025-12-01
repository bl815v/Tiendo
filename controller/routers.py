from fastapi import APIRouter
from .categorias import router as categorias_router
from .productos import router as productos_router
from .clientes import router as clientes_router
from .carritos import router as carritos_router
from .pedidos import router as pedidos_router
from .pagos import router as pagos_router
from .envios import router as envios_router

router = APIRouter()

router.include_router(categorias_router)
router.include_router(productos_router)
router.include_router(clientes_router)
router.include_router(carritos_router)
router.include_router(pedidos_router)
router.include_router(pagos_router)
router.include_router(envios_router)
