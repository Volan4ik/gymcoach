import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.core.config import settings
from app.telegram.handlers.onboarding import router as onboarding_router
from app.telegram.handlers.root import router as root_router

async def main() -> None:
    token = settings.BOT_TOKEN or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Put it in .env or environment.")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    bot = Bot(token=token, parse_mode=ParseMode.HTML)

    dp = Dispatcher()

    dp.include_router(onboarding_router)
    dp.include_router(root_router)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())