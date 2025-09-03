import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.config import settings

router = Router()

@router.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer(
        "<b>Welcome to the Telegram Gym Coach Bot!</b>",
        parse_mode="HTML"
    )

@router.message(Command(commands=["help"]))
async def on_help(message: Message) -> None:
    await message.answer(
        "<b>Available commands:</b>\n"
        "/start - Start the bot\n"
        "/help - Show this help message",
        parse_mode="HTML"
    )

async def main() -> None:
    token = settings.BOT_TOKEN or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Put it in .env or environment.")
    
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)


    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())