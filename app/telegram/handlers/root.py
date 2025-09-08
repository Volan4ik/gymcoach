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

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    # здесь можно сделать upsert пользователя в БД
    await state.clear()              # сбрасываем любые незавершенные сцены
    await show_main_screen(message)

# Кнопка «Главная» (текст) и команда /home
@router.message(F.text == BTN_HOME)
@router.message(Command("home"))
async def go_home(message: Message, state: FSMContext) -> None:
    await state.clear()
    await show_main_screen(message)

# --- Навигация к настройкам ---

@router.message(F.text == BTN_SETTINGS)
@router.message(Command("settings"))
async def open_settings(message: Message, state: FSMContext) -> None:
    # если есть активная сцена (ввод числа и т.п.), лучше ее завершить
    await state.clear()
    await show_settings_screen(message)

@router.message(F.text == BTN_BACK)
async def back_to_main(message: Message, state: FSMContext) -> None:
    await state.clear()
    await show_main_screen(message)

# --- Пункты главного меню (как команды, так и кнопки) ---

@router.message(Command("me"))
@router.message(F.text == BTN_ME)
async def open_profile(message: Message) -> None:
    # TODO: достать профиль из БД и красиво вывести
    await message.answer("👤 Профиль (демо). Тут будут TZ/цель/опыт/инвентарь.", reply_markup=main_kb())

@router.message(Command("plan"))
@router.message(F.text == BTN_PLAN)
async def open_plan(message: Message) -> None:
    # TODO: мастер плана или показ текущего
    await message.answer("📅 План (демо). Тут будет мастер создания/просмотра.", reply_markup=main_kb())

@router.message(Command("today"))
@router.message(F.text == BTN_TODAY)
async def open_today(message: Message) -> None:
    # TODO: запуск/продолжение WorkoutSession
    await message.answer("🔥 Сегодня (демо). Запуск тренировки и карточки упражнений.", reply_markup=main_kb())

@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
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

@router.message(Command("remind"))
@router.message(F.text == BTN_REMIND)
async def open_remind(message: Message) -> None:
    # TODO: показать сетку дней/времен (Reply/Inline), сохранить окна
    await message.answer("⏰ Напоминания (демо). Выбор дней и времени.", reply_markup=settings_kb())

@router.message(Command("log"))
@router.message(F.text == BTN_LOG)
async def open_log(message: Message) -> None:
    # TODO: лист последних сетов, кнопки «Редактировать/Удалить»
    await message.answer("📜 Журнал (демо). Последние тренировки/сеты.", reply_markup=settings_kb())

@router.message(Command("privacy"))
@router.message(F.text == BTN_PRIVACY)
async def open_privacy(message: Message) -> None:
    # TODO: /export и /wipe с двойным подтверждением
    await message.answer("🔐 Приватность (демо). Экспорт/удаление данных.", reply_markup=settings_kb())
