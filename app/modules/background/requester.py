import httpx
import asyncio
from asyncpg import Record
from datetime import datetime
import logging
from app.core.config import config
from app.db_controller.controller import db_controller


config = config['Requester']
SIMULTANEOUS_REQUESTS = int(config['simultaneous_requests']) if config['simultaneous_requests'] else 100
SEMAPHORE = asyncio.Semaphore(SIMULTANEOUS_REQUESTS)
logger = logging.getLogger(__name__)

async def get_timing_id(minutes:int) -> int:
    timings = await db_controller.get_timings()
    timings = [timing.values() for timing in timings]

    for timing_id, timing, description in reversed(timings):
        if minutes % timing == 0:
            return int(timing_id)

    raise KeyError('ошибка при нахождении тайминга для опроса')

async def get_monitor_addr_list(timing_id: int) -> list[Record]:
    return await db_controller.get_monitor_addr_list(timing_id)

async def set_requests_log(result, timing_id):
    await db_controller.set_requests_log(result, timing_id)

async def check_site(client: httpx.AsyncClient, url: Record, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            response = await client.get('http://' + url.get('url'), follow_redirects=True)
            ping_ms = response.elapsed.total_seconds() * 1000
            logger.info(f"  ✅ {url.get('url'):30} | {response.status_code} | {round(ping_ms, 2):.2f} ms")
            return {
                "url": url,
                "status": response.status_code,
                "ping_ms": round(ping_ms, 2),
                "is_up": 200 <= response.status_code < 400,
            }

        except httpx.TimeoutException:
            logger.warning(f"  ❌ {url.get('url'):30} | DOWN | timeout")
            return {
                "url": url,
                "status": None,
                "ping_ms": None,
                "is_up": False,
                "error": "timeout"
            }

        except Exception as e:
            logger.warning(f"  ❌ {url.get('url'):30} | DOWN | {e}")
            return {
                "url": url,
                "status": None,
                "ping_ms": None,
                "is_up": False,
                "error": str(e)
            }


async def monitor_job():
    """Функция, которая будет запускаться по расписанию."""
    start_time = datetime.now()
    logger.info(f"начало опроса в {start_time.strftime('%H:%M:%S')}")

    minutes = start_time.hour * 60 + start_time.minute
    if __name__ == '__main__':
        minutes = 360
    timing_id = await get_timing_id(minutes)
    addr_list = await get_monitor_addr_list(timing_id)

    if not addr_list:
        logger.info(f"Опрос пропущен, тк нет мониторов для опроса")
        return

    async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_connections=200, max_keepalive_connections=50),
            headers={"User-Agent": "MyMonitor/1.0"},
            follow_redirects=True,
    ) as client:

        tasks = [check_site(client, url, SEMAPHORE) for url in addr_list]
        results = await asyncio.gather(*tasks)

    for result in results:
        await set_requests_log(result, timing_id=timing_id)

    up_count = sum(1 for r in results if r["is_up"])
    logger.info(f"✅ UP: {up_count} | ❌ DOWN: {len(results) - up_count}")

    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"Опрос завершен за {duration:.2f} сек")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)05d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
    )
    async def activate():
        await db_controller.connect()
        await monitor_job()
        await db_controller.disconnect()

    asyncio.run(activate())