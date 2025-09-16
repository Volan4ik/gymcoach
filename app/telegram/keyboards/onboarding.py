from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_BACK = "⬅️ Назад"
BTN_SKIP = "⏭ Пропустить"
BTN_CANCEL = "✖️ Отмена"
BTN_AUTO_TZ = "🌍 Определить автоматически"

COMMON_TZ = [
    "UTC", "Europe/Moscow", "Europe/Kyiv",
    "Asia/Almaty", "Asia/Tbilisi", "Asia/Yekaterinburg",
]

GOALS = ["Гипертрофия", "Сила", "Выносливость", "Похудение"]
LEVELS = ["Новичок", "Средний", "Продвинутый"]
EQUIPMENT = ["Дом", "Зал", "Только тело", "Смешанное"]

def tz_kb() -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=t)] for t in COMMON_TZ]
    rows.append([KeyboardButton(text=BTN_AUTO_TZ)])
    rows.append([KeyboardButton(text=BTN_SKIP), KeyboardButton(text=BTN_CANCEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

def goals_kb() -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=g)] for g in GOALS]
    rows.append([KeyboardButton(text=BTN_BACK), KeyboardButton(text=BTN_SKIP), KeyboardButton(text=BTN_CANCEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

def levels_kb() -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=l)] for l in LEVELS]
    rows.append([KeyboardButton(text=BTN_BACK), KeyboardButton(text=BTN_SKIP), KeyboardButton(text=BTN_CANCEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

def equipment_kb() -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=e)] for e in EQUIPMENT]
    rows.append([KeyboardButton(text=BTN_BACK), KeyboardButton(text=BTN_SKIP), KeyboardButton(text=BTN_CANCEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

def injuries_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_SKIP)],
            [KeyboardButton(text=BTN_BACK), KeyboardButton(text=BTN_CANCEL)],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Опиши травмы или нажми «Пропустить»",
    )
