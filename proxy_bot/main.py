import asyncio
import logging
import sys

from loguru import logger

from proxy_bot.constants.load_constants import Constant
from proxy_bot.db.models import create_tables
from proxy_bot.handlers.user.discount_handler import discount_router
from proxy_bot.handlers.user.payments_handler import pay_router
from proxy_bot.handlers.user.profile_handler import profile_router
from proxy_bot.handlers.user.start_handler import start_router
from proxy_bot.handlers.user.unique_handler import unique_router
from proxy_bot.imports import dp, bot


async def main() -> None:
    await create_tables()
    await Constant().load_data()  # load constant for work bot
    dp.include_routers(start_router,
                       profile_router,
                       pay_router,
                       unique_router,
                       discount_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # Запуск long-polling


if __name__ == "__main__":
    logger.add(sys.stdout, level="DEBUG", format="{time} {level} {message}")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger.add("loguru.log", rotation="1 week", retention="1 month", compression="zip", level="ERROR")
    try:
        logger.info("Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('Bot stopped manually (KeyboardInterrupt)')
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
