# app/telegram/keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Тексты кнопок (удобно держать в одном месте) ---
BTN_ME       = "/me"
BTN_PLAN     = "/plan"
BTN_TODAY    = "/today"
BTN_SETTINGS = "/settings"
BTN_HELP     = "/help"
BTN_HOME     = "🏠 Главная"

BTN_REMIND   = "/remind"
BTN_LOG      = "/log"
BTN_PRIVACY  = "/privacy"
BTN_BACK     = "⬅️ Назад"

def main_kb() -> ReplyKeyboardMarkup:
    """
    Постоянная «нижняя панель» — главные действия. Кнопки с / запускают команды,
    а «Главная» — просто текстовая кнопка.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TODAY), KeyboardButton(text=BTN_PLAN)],
            [KeyboardButton(text=BTN_ME),    KeyboardButton(text=BTN_HELP)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,              # оставляет клавиатуру закреплённой
        input_field_placeholder="Выбери действие…",
    )

def settings_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_REMIND), KeyboardButton(text=BTN_LOG)],
            [KeyboardButton(text=BTN_PRIVACY)],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Настройки…",
    )
