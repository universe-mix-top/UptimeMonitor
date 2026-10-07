from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.modules.foreground.foreground import (
    get_user_monitors_presets,
    get_user_addr_list,
    get_user_logs
)

router_log = APIRouter(prefix="/logs", tags=["logs & foreground"])

# --- Pydantic Models ---

class LogEntry(BaseModel):
    url: str
    datetime: str
    res_code: Optional[int]
    ping: Optional[float]


class MonitorItem(BaseModel):
    url: str
    description: str


# --- Endpoints ---


@router_log.get("/monitors", response_model=list[MonitorItem], summary="Список мониторов пользователя")
async def get_monitors(tg_id: int = Query(..., description="ID пользователя (tg_id)")):
    """Получить список сайтов пользователя с интервалами опроса."""
    try:
        monitors = await get_user_monitors_presets(tg_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при получении мониторов: {str(e)}"
        )

    if not monitors:
        return []
    result = []
    for m in monitors:
        result.append(MonitorItem(
            url=m.get("url"),
            description=m.get("description"),
        ))
    return result


@router_log.get("/user/{tg_id}", summary="Логи пользователя с выбором URL")
async def get_user_logs_endpoint(
    tg_id: int,
    url: Optional[str] = Query(None, description="URL для фильтрации логов (необязательно)"),
):
    """
    Получить логи опросов пользователя.
    Если url не указан — возвращает список всех URL пользователя.
    Если url указан — возвращает логи для конкретного URL.
    """
    try:
        if url is None:
            addr_list = await get_user_addr_list(tg_id)
            if not addr_list:
                return {'urls':[]}
            return {'urls':[a.get("url") for a in addr_list]}

        logs = await get_user_logs(tg_id, url)
        if not logs:
            return {"logs": []}

        result = []
        for log in logs:
            dt = log.get("datetime")
            dt_str = dt.strftime("%d.%m.%Y %H:%M:%S") if dt else ""
            result.append(LogEntry(
                url=url,
                datetime=dt_str,
                res_code=log.get("res_code"),
                ping=log.get("ping"),
            ))
        return {"logs": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при получении логов: {str(e)}"
        )


