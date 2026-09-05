from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.product import router as product_router
from routers.order import router as order_router

__all__ = ["auth_router", "user_router", "product_router", "order_router"]
