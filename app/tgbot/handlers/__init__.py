import logging

from .start import router as router_start
from .log import router as router_log
from .settings_log import router as router_settings_log
from .settings_log_add import router as router_settings_log_add
from .settings_log_change import router as router_settings_log_change
from .settings_log_del import router as router_settings_log_del
from .plug import router as router_plug
from aiogram import Router


logger = logging.getLogger(__name__)

router = Router()
router.include_router(router_start)
router.include_router(router_log)
router.include_router(router_settings_log)
router.include_router(router_settings_log_add)
router.include_router(router_settings_log_change)
router.include_router(router_settings_log_del)
router.include_router(router_plug)

__app__ = [
    'router',
    'router_log',
    'router_start',
    'router_settings_log',
    'router_settings_log_add',
    'router_settings_log_change',
    'router_settings_log_del',
]