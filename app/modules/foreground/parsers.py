from asyncpg import Record

def parse_logs(logs: list[Record], url: str):
    def parse(log: Record):
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
