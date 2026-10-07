from fastapi import APIRouter, Query
from .router_register import router_reg
from .router_logs import router_log
from .router_background import router_bg


router = APIRouter(tags=["UptimeMonitor API"])
router.include_router(router_reg)
router.include_router(router_log)
router.include_router(router_bg)

__app__ = [
    'router',
    'router_reg',
    'router_log',
    'router_bg',
]