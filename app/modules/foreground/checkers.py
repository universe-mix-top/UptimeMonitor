from asyncpg import Record

def is_link_on_item_in_list(link: str, addr_list: list[Record], item_name:str) -> str|None:
    if link.isdecimal():
        if 0 < int(link) <= len(addr_list):
            return addr_list[int(link) - 1].get(item_name)

    if link in addr_list:
        return link.get(item_name)
    return None

def timing_id_by_description(description: str, timings: list[Record]) -> int | None:
    for timing in timings:
        if timing.get('description') == description:
            return int(timing.get('timing_id'))


def is_addr_link(link: str, addr_list: list[Record]) -> str|None:
    return is_link_on_item_in_list(link, addr_list, 'url')

def is_timing_link(link: str, addr_list: list[Record]) -> str|None:
    return is_link_on_item_in_list(link, addr_list, 'description')
