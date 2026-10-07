from asyncpg import Record
from app.db_controller.controller import db_controller


URL_REG = r'^(www\.)?([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
IP_ADDR_REG = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
TIMING_DESCRIPTION = r'\d{1,2} [a-zа-я]{1,12}'

async def db_controller_connect():
    await db_controller.connect()

async def db_controller_disconnect():
    await db_controller.disconnect()

def is_link_on_item_in_list(link: str, addr_list: list[Record], item_name:str) -> str|None:
    if link.isdecimal():
        if 0 < int(link) <= len(addr_list):
            return addr_list[int(link) - 1].get(item_name)

    if link in addr_list:
        return link.get(item_name)
    return None

def timing_id_dy_description(description:str, timings:list[Record]) -> int|None:
    for timing in timings:
        if timing.get('description') == description:
            return int(timing.get('timing_id'))


def is_addr_link(link: str, addr_list: list[Record]) -> str|None:
    return is_link_on_item_in_list(link, addr_list, 'url')

def is_timing_link(link: str, addr_list: list[Record]) -> str|None:
    return is_link_on_item_in_list(link, addr_list, 'description')

def parse_logs(logs:list[Record], url:str):
    def parse(log:Record):
        datetime = log.get('datetime').strftime("%d.%m.%Y %H:%M:%S")
        res_code = log.get('res_code')
        ping = log.get('ping')
        if log.get('res_code'):
            return (f"{'✅' if 200 <= res_code < 400 else '❌'}"
                    f"{url} | "
                    f"{datetime} | "
                    f"{res_code} | "
                    f"{int(ping)}мс ")
        return (f"❌"
                f"{url} | "
                f"{datetime} | "
                f"ERROR")

    parsed_logs = '\n'.join(map(
        lambda log: parse(log),
        logs
    ))
    return parsed_logs

def parse_timings(timings:list[Record]) -> str:
    parsed_timings = '\n'.join(
        map(
            lambda x: f'{x[0] + 1}. {x[1].get('description')}',
            enumerate(timings)
        )
    )
    return parsed_timings

def parse_address_list(addr_list:list[Record]) -> str:
    parsed_addr_list = '\n'.join(
        map(
            lambda x: f'{x[0] + 1}. {x[1].get('url')}',
            enumerate(addr_list)
        )
    )
    return parsed_addr_list

def parse_monitors_preset(monitors_preset:list[Record]) -> str:
    parsed_monitors_preset = '\n'.join(
        map(
            lambda x: f'{x.get('url')} раз в {x.get('description')}',
            monitors_preset
        )
    )
    if parsed_monitors_preset is None:
        parsed_monitors_preset = 'список сайтов пуст'
    return parsed_monitors_preset

async def user_registration(tg_id:int):
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

async def del_user_monitor(tg_id:int, url:str) -> str:
    return await db_controller.del_user_monitor(tg_id, url)
