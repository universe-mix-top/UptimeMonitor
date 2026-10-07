from asyncpg import create_pool, Record, Pool
from app.core.config import config
from cachetools import TTLCache
from cachetools_async import cached


class ControllerDb:
    pool: Pool|None = None
    db_config = config["DataBase"]

    user = db_config['db_user']
    password = db_config['db_user_pass'] if db_config['db_user_pass'] else None
    database = db_config['db_name'] if db_config['db_name'] else 'postgres'
    host = db_config['db_host'] if db_config['db_host'] else 'localhost'
    port = db_config['db_port'] if db_config['db_port'] else '5432'
    search_path = db_config['db_schema_name'] if db_config['db_schema_name'] else 'public'
    cache = TTLCache(maxsize=1024, ttl=600)  # 10 минут


    async def connect(self):
        if self.pool is None:
            self.pool = create_pool(
                user=self.user,
                password=self.password,
                database=self.database,
                host=self.host,
                port=self.port,
                server_settings={'search_path': self.search_path}
            )
            await self.pool

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def user_registration(self, tg_id: int) -> str:
        return await self.pool.execute('INSERT INTO '
                                              '     users(tg_id) '
                                              'values ($1) '
                                              'ON CONFLICT DO NOTHING '
                                              'RETURNING 1', tg_id)

    @cached(cache=cache)
    async def get_user_id(self, tg_id: int) -> str | None:
        user_id = await self.pool.fetchrow(
            'SELECT user_id FROM users WHERE tg_id = $1;', tg_id
        )
        if user_id is None:
            return None
        return user_id.get('user_id')

    @cached(cache=cache)
    async def get_url_id(self, url: str) -> str | None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                url_id = await conn.fetchrow(
                    'SELECT urls.url_id FROM urls WHERE url = $1', url
                )
                if url_id is None:
                    url_id = await conn.fetchrow(
                        'INSERT INTO urls (url) VALUES ($1) '
                        'ON CONFLICT (url) DO NOTHING RETURNING url_id', url
                    )
        if url_id is None:
            return None
        return url_id.get('url_id')

    @cached(cache=cache)
    async def get_monitor_id(self, url_id: str, timing_id: str | int) -> str | None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                monitor_id = await conn.fetchrow(
                    'SELECT monitor_id FROM monitors '
                    'WHERE url_id = $1 AND timing_id = $2',
                    url_id, timing_id
                )
                if monitor_id is None:
                    monitor_id = await conn.fetchrow(
                        'INSERT INTO monitors (url_id, timing_id) '
                        'VALUES ($1, $2) RETURNING monitor_id',
                        url_id, timing_id
                    )
        if monitor_id is None:
            return None
        return monitor_id.get('monitor_id')

    async def del_monitor(self, monitor_id:str):
        """удалить монитор ели не используется"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                res = await conn.fetchrow('SELECT '
                                          '     user_id, '
                                          '     monitor_id '
                                          'FROM monitors_presets '
                                          'WHERE monitor_id = $1 ', monitor_id)
                if res is None:
                    return await conn.execute('DELETE FROM monitors '
                                              'WHERE monitor_id = $1', monitor_id)

    async def get_monitor_addr_list(self, timing_id:int) -> list[Record]:
        return await self.pool.fetch('SELECT '
                                     '    url, '
                                     '    monitors.url_id '
                                     'FROM monitors '
                                     'JOIN urls ON monitors.url_id = urls.url_id '
                                     'WHERE timing_id <= $1', timing_id)

    async def get_user_addr_list(self, tg_id:int) -> list[Record]:
        user_id = await self.get_user_id(tg_id)
        return await self.pool.fetch('SELECT '
                                     '      url, '
                                     '      monitors.url_id '
                                     'FROM monitors_presets '
                                     'JOIN monitors ON monitors_presets.monitor_id = monitors.monitor_id '
                                     'JOIN urls ON monitors.url_id = urls.url_id '
                                     'WHERE user_id = $1', user_id)

    async def get_user_logs(self, tg_id:int, url:str) -> list[Record]:
        user_id = await self.get_user_id(tg_id)
        url_id = await self.get_url_id(url)
        return await self.pool.fetch('SELECT '
                                     '    requests_log.datetime, '
                                     '    requests_log.res_code, '
                                     '    requests_log.ping '
                                     'FROM monitors '
                                     '        JOIN monitors_presets ON monitors.monitor_id = monitors_presets.monitor_id '
                                     '        JOIN requests_log ON monitors.url_id = requests_log.url_id '
                                     'WHERE monitors_presets.user_id = $1 and '
                                     '      requests_log.timing_id >= monitors.timing_id and '
                                     '      requests_log.url_id = $2', user_id, url_id)

    async def get_user_monitors_presets(self, tg_id:int) -> list[Record]:
        user_id = await self.get_user_id(tg_id)
        return await self.pool.fetch('SELECT '
                                     '    urls.url, '
                                     '    timings.description '
                                     'FROM monitors_presets '
                                     'JOIN monitors ON monitors_presets.monitor_id = monitors.monitor_id '
                                     'JOIN urls ON urls.url_id = monitors.url_id '
                                     'JOIN timings ON monitors.timing_id = timings.timing_id '
                                     'WHERE user_id = $1', user_id)

    async def get_timings(self) -> list[Record]:
        """выводится по возрастанию по размеру интервала в минутах"""
        return await self.pool.fetch('SELECT '
                                     '    timing_id, '
                                     '    timing, '
                                     '    description '
                                     'FROM timings '
                                     'ORDER BY timing')

    async def set_requests_log(self, result:dict, timing_id:int) -> str:
        url_id = result.get('url').get('url_id')
        res_code = result.get('status')
        ping = result.get('ping_ms')
        return await self.pool.execute(
            'INSERT INTO '
            '    requests_log(url_id, timing_id, res_code, ping) '
            'VALUES ($1, $2, $3, $4)',
            url_id,
            timing_id,
            res_code,
            ping
        )

    async def set_user_monitor(self, tg_id:int, url:str, timing_id:int) -> list[Record]:
        user_id = await self.get_user_id(tg_id)
        url_id = await self.get_url_id(url)
        monitor_id = await self.get_monitor_id(url_id, timing_id)

        return await self.pool.fetch('INSERT INTO '
                                      '    monitors_presets (user_id, monitor_id) '
                                      'VALUES ($1, $2) ' 
                                      'ON CONFLICT  DO NOTHING '
                                      'RETURNING user_id, monitor_id', user_id, monitor_id)

    async def change_user_monitor(self, tg_id:int, url:str, timing_id:int) -> str:
        user_id = await self.get_user_id(tg_id)
        url_id = await self.get_url_id(url)
        new_monitor_id = await self.get_monitor_id(url_id, timing_id)

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                old_monitor_id = await conn.fetchrow('SELECT '
                                                     '    monitors_presets.monitor_id '
                                                     'FROM monitors_presets '
                                                     'JOIN monitors ON monitors_presets.monitor_id = monitors.monitor_id '
                                                     'WHERE user_id = $1 and '
                                                     '      url_id = $2', user_id, url_id)
                old_monitor_id = old_monitor_id.get('monitor_id')

                if old_monitor_id is None:
                    raise ValueError('нет монитора который можно изменить')

                res = await conn.execute('UPDATE '
                                          '    monitors_presets '
                                          'SET monitor_id = $1 '
                                          'WHERE monitor_id = $2 AND '
                                          '      user_id = $3', new_monitor_id, old_monitor_id, user_id)
        await self.del_monitor(old_monitor_id)
        return res

    async def del_user_monitor(self, tg_id: int, url: str) -> str | None:
        user_id = await self.get_user_id(tg_id)
        if user_id is None:
            return None
        url_id = await self.get_url_id(url)

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                monitor_id_list = await conn.fetch(
                    'SELECT monitor_id FROM monitors WHERE url_id = $1', url_id
                )
                if not monitor_id_list:
                    return None

                monitor_ids = [int(m.get('monitor_id')) for m in monitor_id_list]
                placeholders = ', '.join(f'${i+2}' for i in range(len(monitor_ids)))

                monitor_id = await conn.fetchrow(
                    f'DELETE FROM monitors_presets '
                    f'WHERE user_id = $1 AND monitor_id IN ({placeholders}) '
                    f'RETURNING monitor_id',
                    user_id, *monitor_ids
                )
                monitor_id = monitor_id.get('monitor_id') if monitor_id else None

        if monitor_id:
            await self.del_monitor(monitor_id)
        return monitor_id


db_controller = ControllerDb()
