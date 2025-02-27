import asyncio

from aiogram import Bot, Dispatcher

from internal.handlers import admin_router, client_router
from internal.utils import get_admins_telegram_id, create_admin_if_not_exist
from pkg.config import settings
from pkg.database import create_db
from pkg.logger import get_logger

logger = get_logger(__name__)


async def on_startup(bot: Bot):
    info = "Bot started"
    logger.info(info)
    create_db()
    create_admin_if_not_exist()
    for admin_telegram_id in get_admins_telegram_id():
        await bot.send_message(admin_telegram_id, info)


async def on_shutdown(bot: Bot):
    info = "Bot stopped"
    logger.info(info)
    for admin_telegram_id in get_admins_telegram_id():
        await bot.send_message(admin_telegram_id, info)


async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_API_TOKEN.get_secret_value())
    dp = Dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(admin_router)
    dp.include_router(client_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
