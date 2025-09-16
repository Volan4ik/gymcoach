# app/telegram/handlers/root.py
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.telegram.keyboards.reply import (
    main_kb, settings_kb,
    BTN_HOME, BTN_SETTINGS, BTN_BACK,
    BTN_ME, BTN_PLAN, BTN_TODAY, BTN_HELP,
    BTN_REMIND, BTN_LOG, BTN_PRIVACY,
)

from app.db.session import get_session
from app.db.models import User
from sqlmodel import select
from app.telegram.handlers.onboarding import start_onboarding, is_profile_complete

router = Router(name="root")

# --- Утилиты для экранов ---

async def show_main_screen(message: Message) -> None:
    text = (
        "🏋️‍♂️ *Главная*\n\n"
        "— /today — начать тренировку сегодня\n"
        "— /plan — создать/посмотреть план\n"
        "— /me — профиль\n"
        "— /settings — напоминания, журнал, приватность\n"
        "— /help — помощь\n"
    )
    await message.answer(text, reply_markup=main_kb(), parse_mode="Markdown")

async def show_settings_screen(message: Message) -> None:
    text = (
        "⚙️ *Настройки*\n\n"
        "— /remind — окна напоминаний\n"
        "— /log — журнал и правки\n"
        "— /privacy — данные и выгрузка\n"
        "Нажми «Назад», чтобы вернуться на главную."
    )
    await message.answer(text, reply_markup=settings_kb(), parse_mode="Markdown")

# --- Старт/главная ---

@router.message(F.chat.type == "private", CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    # upsert пользователя в БД
    with get_session() as s:
        u = s.exec(select(User).where(User.tg_id == message.from_user.id)).first()
        if not u:
            u = User(tg_id=message.from_user.id, tz="UTC")
            s.add(u)
            s.commit()
            s.refresh(u)

    # если профиль неполный — запускаем онбординг
    if not is_profile_complete(u):
        await start_onboarding(message, state)
        return

    # иначе просто показываем главную
    await state.clear()
    await show_main_screen(message)

# Кнопка «Главная» (текст) и команда /home
@router.message(F.chat.type == "private", F.text == BTN_HOME)
@router.message(F.chat.type == "private", Command("home"))
async def go_home(message: Message, state: FSMContext) -> None:
    await state.clear()
    await show_main_screen(message)

# --- Навигация к настройкам ---

@router.message(F.chat.type == "private", F.text == BTN_SETTINGS)
@router.message(F.chat.type == "private", Command("settings"))
async def open_settings(message: Message, state: FSMContext) -> None:
    await state.clear()
    await show_settings_screen(message)

@router.message(F.chat.type == "private", F.text == BTN_BACK)
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.clear()
    await show_main_screen(message)

# --- Пункты главного меню (как команды, так и кнопки) ---

@router.message(F.chat.type == "private", Command("me"))
@router.message(F.chat.type == "private", F.text == BTN_ME)
async def open_profile(message: Message) -> None:
    # ⬇️ Реально читаем профиль из БД
    with get_session() as s:
        u = s.exec(select(User).where(User.tg_id == message.from_user.id)).first()
    if not u:
        await message.answer("Профиль не найден. Нажми /start, чтобы создать его.", reply_markup=main_kb())
        return

    injuries = (u.injuries_json or {}).get("text", "—")
    text = (
        "👤 *Профиль*\n"
        f"• TZ: *{u.tz or '—'}*\n"
        f"• Цель: *{u.goal or '—'}*\n"
        f"• Опыт: *{u.level or '—'}*\n"
        f"• Оборудование: *{u.equipment or '—'}*\n"
        f"• Травмы: _{injuries}_\n\n"
        "Чтобы изменить — зайди в /settings."
    )
    await message.answer(text, reply_markup=main_kb(), parse_mode="Markdown")

@router.message(F.chat.type == "private", Command("plan"))
@router.message(F.chat.type == "private", F.text == BTN_PLAN)
async def open_plan(message: Message) -> None:
    await message.answer("📅 План (демо). Тут будет мастер создания/просмотра.", reply_markup=main_kb())

@router.message(F.chat.type == "private", Command("today"))
@router.message(F.chat.type == "private", F.text == BTN_TODAY)
async def open_today(message: Message) -> None:
    await message.answer("🔥 Сегодня (демо). Запуск тренировки и карточки упражнений.", reply_markup=main_kb())

@router.message(F.chat.type == "private", Command("help"))
@router.message(F.chat.type == "private", F.text == BTN_HELP)
async def open_help(message: Message) -> None:
    await message.answer(
        "❓ *Помощь*\n"
        "/start — главная\n"
        "/today — тренировка сегодня\n"
        "/plan — план\n"
        "/me — профиль\n"
        "/settings — настройки\n",
        parse_mode="Markdown",
        reply_markup=main_kb(),
    )

# --- Пункты меню «Настройки» ---

@router.message(F.chat.type == "private", Command("remind"))
@router.message(F.chat.type == "private", F.text == BTN_REMIND)
async def open_remind(message: Message) -> None:
    await message.answer("⏰ Напоминания (демо). Выбор дней и времени.", reply_markup=settings_kb())

@router.message(F.chat.type == "private", Command("log"))
@router.message(F.chat.type == "private", F.text == BTN_LOG)
async def open_log(message: Message) -> None:
    await message.answer("📜 Журнал (демо). Последние тренировки/сеты.", reply_markup=settings_kb())

@router.message(F.chat.type == "private", Command("privacy"))
@router.message(F.chat.type == "private", F.text == BTN_PRIVACY)
async def open_privacy(message: Message) -> None:
    await message.answer("🔐 Приватность (демо). Экспорт/удаление данных.", reply_markup=settings_kb())