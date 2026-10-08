from asyncpg import Record
from app.db_controller.controller import db_controller


URL_REG = r'^(www\.)?([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
IP_ADDR_REG = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
TIMING_DESCRIPTION = r'\d{1,2} [a-zа-я]{1,12}'

async def db_controller_connect():
    await db_controller.connect()

async def db_controller_disconnect():
    await db_controller.disconnect()

async def user_registration(tg_id:int) -> int | None:
    return await db_controller.user_registration(tg_id)

async def get_user_id(tg_id:int):
    return await db_controller.get_user_id(tg_id)

async def get_user_addr_list(tg_id:int) -> list[Record]:
    return await db_controller.get_user_addr_list(tg_id)

async def get_user_logs(tg_id:int, addr:str) -> list[Record]:
    return await db_controller.get_user_logs(tg_id, addr)

async def get_user_monitors_presets(tg_id:int) -> list[Record]:
    return await db_controller.get_user_monitors_presets(tg_id)

async def get_timings() -> list[Record]:
    return await db_controller.get_timings()

async def set_user_monitor(tg_id:int, url:str, timing:int) -> str:
    return await db_controller.set_user_monitor(tg_id, url, timing)

async def change_user_monitor(tg_id:int, url:str, timing:int) -> str:
    return await db_controller.change_user_monitor(tg_id, url, timing)

async def del_user_monitor(tg_id:int, url:str) -> str | None:
    return await db_controller.del_user_monitor(tg_id, url)
