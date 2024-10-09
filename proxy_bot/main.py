import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from loguru import logger

from proxy_bot.db.models import create_tables
from proxy_bot.settings import settings
from proxy_bot.start import start_router

bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()


async def main() -> None:
    await create_tables()
    dp.include_router(start_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # Запуск long-polling


if __name__ == "__main__":
    logger.add(sys.stdout, level="DEBUG", format="{time} {level} {message}")
    logger.add("loguru.log", rotation="1 week", retention="1 month", compression="zip", level="ERROR")
    try:
        logger.info("Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('Bot stopped manually (KeyboardInterrupt)')
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
