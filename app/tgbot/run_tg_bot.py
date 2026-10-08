import asyncio
import logging
from app.modules.foreground.foreground import db_controller_connect, db_controller_disconnect

from aiogram import Bot, Dispatcher
from core.config import config
from handlers import router


logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s.%(msecs)05d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

logger = logging.getLogger(__name__)

async def main():
    bot = Bot(config['TgBot']['token'])
    dp = Dispatcher()

    dp.include_router(router)
    await db_controller_connect()

    logger.info('тг бот начал работу')
    try:
        await dp.start_polling(bot)
    finally:
        await db_controller_disconnect()

if __name__ == '__main__':
        asyncio.run(main())