from fastapi import APIRouter
from router_logs import router_log
from router_background import router_bg
from router_foreground import router_fg

router = APIRouter(tags=["общий роутер"])

router.include_router(router_log)
router.include_router(router_bg)
router.include_router(router_fg)
