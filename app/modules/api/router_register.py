from fastapi import APIRouter, Query
from app.modules.foreground.foreground import user_registration, get_user_id

router_reg = APIRouter(tags=["UptimeMonitor API"])

@router_reg.post("/register", summary="Регистрация пользователя")
async def register_user(tg_id: int = Query(..., description="Telegram ID пользователя (должен быть > 0)", gt=0)):
    """Регистрация нового пользователя (аналог /start в Telegram-боте)."""
    res = await user_registration(tg_id)
    is_new_user = res is not None and res.split()[-1] == '1'
    user_id = await get_user_id(tg_id)
    return {
        "tg_id": tg_id,
        "user_id": user_id,
        "is_new_user": is_new_user,
    }
