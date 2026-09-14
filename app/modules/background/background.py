import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.db_controller.controller import db_controller

from requester import monitor_job

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s.%(msecs)05d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    await db_controller.connect()
    scheduler = AsyncIOScheduler(timezone="UTC")  # или "Europe/Moscow" и т.д.

    scheduler.add_job(
        monitor_job,
        trigger=CronTrigger(minute='*/10', second=0),
        id='monitor_job',
        name='Мониторинг сайтов',
        misfire_grace_time=60,  # Если запуск опоздал на < 60 сек — всё равно выполнить
        max_instances=1,  # Не запускать вторую копию, если первая ещё работает
        coalesce=True,  # Если пропущено несколько запусков — выполнить один
    )

    scheduler.start()
    logger.info("планировщик запущен. Жду следующего запуска в XX:X0...")

    # Держим скрипт запущенным бесконечно
    try:
        while True:
            await asyncio.sleep(3600)  # спим часами, планировщик сам разбудит
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Остановка...")
        scheduler.shutdown()
    finally:
        await db_controller.disconnect()


if __name__ == '__main__':
    asyncio.run(main())