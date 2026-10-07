from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.foreground.foreground import (
    get_timings,
    set_user_monitor,
    change_user_monitor,
    del_user_monitor,
)

router_bg = APIRouter(prefix="/background", tags=["background settings"])


# --- Pydantic Models ---

class MonitorRequest(BaseModel):
    tg_id: int
    url: str
    timing_id: int


class TimingItem(BaseModel):
    timing_id: int
    timing: int
    description: str


# --- Endpoints ---

@router_bg.get("/timings", response_model=list[TimingItem], summary="Список интервалов опроса")
async def get_timings_list():
    """Получить все доступные интервалы опроса (аналог выбора тайминга в боте)."""
    timings = await get_timings()
    result = []
    for t in timings:
        result.append(TimingItem(
            timing_id=t.get("timing_id"),
            timing=t.get("timing"),
            description=t.get("description"),
        ))
    return result


@router_bg.post("/monitor", summary="Добавить монитор")
async def add_monitor(req: MonitorRequest):
    """Добавить сайт в список мониторинга."""
    try:
        res = await set_user_monitor(req.tg_id, req.url, req.timing_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при добавлении: {str(e)}")

    if not res:
        raise HTTPException(
            status_code=409,
            detail=f"Сайт {req.url} уже есть в списке мониторинга"
        )
    return {"message": f"Монитор для {req.url} добавлен"}


@router_bg.put("/monitor", summary="Изменить монитор")
async def change_monitor(req: MonitorRequest):
    """Изменить интервал опроса для существующего сайта."""
    try:
        res = await change_user_monitor(req.tg_id, req.url, req.timing_id)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Сайт {req.url} не найден в списке мониторинга. Сначала добавьте его."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при изменении: {str(e)}")

    if not res:
        raise HTTPException(
            status_code=409,
            detail=f"Для сайта {req.url} уже стоят такие настройки опроса"
        )
    return {"message": f"Настройки монитора для {req.url} изменены"}


@router_bg.delete("/monitor", summary="Удалить монитор")
async def delete_monitor(req: MonitorRequest):
    """Удалить сайт из списка мониторинга."""
    try:
        res = await del_user_monitor(req.tg_id, req.url)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении: {str(e)}"
        )

    if res is None:
        raise HTTPException(
            status_code=404,
            detail=f"Сайт {req.url} не найден в списке мониторинга"
        )
    return {"message": f"Сайт {req.url} удалён из списка мониторинга"}
