# app/telegram/handlers/onboarding.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.db.session import get_session
from app.db.models import User
from sqlmodel import select

from app.telegram.keyboards.reply import main_kb
from app.telegram.keyboards.onboarding import (
    tz_kb, goals_kb, levels_kb, equipment_kb,
    # ⬇️ добавим мини-клаву для шага травм
    injuries_kb,                     # <- добавь эту функцию в keyboards/onboarding.py (см. ниже)
    BTN_BACK, BTN_SKIP, BTN_CANCEL, BTN_AUTO_TZ,
    GOALS, LEVELS, EQUIPMENT,
)

router = Router(name="onboarding")

# --------- FSM States ----------
class OnboardingStates(StatesGroup):
    tz = State()
    goal = State()
    level = State()
    equipment = State()
    injuries = State()

# --------- helpers ----------
def is_profile_complete(u: User) -> bool:
    # достаточно TZ; остальное можно заполнить позже через /settings
    return bool(u.tz)

async def _get_or_create_user(tg_id: int) -> User:
    with get_session() as s:
        u = s.exec(select(User).where(User.tg_id == tg_id)).first()
        if not u:
            u = User(tg_id=tg_id, tz="UTC")
            s.add(u)
            s.commit()
            s.refresh(u)
        return u

# публичная функция, чтобы вызывать из /start
async def start_onboarding(message: Message, state: FSMContext) -> None:
    await state.set_state(OnboardingStates.tz)
    await message.answer(
        "Выбери свой часовой пояс (или нажми «Определить автоматически»/«Пропустить»):",
        reply_markup=tz_kb(),
    )

# --------- Flow: TZ ----------
@router.message(F.chat.type == "private", OnboardingStates.tz, F.text == BTN_CANCEL)
async def ob_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Онбординг отменён. Можно вернуться позже командой /start.", reply_markup=main_kb())

@router.message(F.chat.type == "private", OnboardingStates.tz)
async def ob_set_tz(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    u = await _get_or_create_user(message.from_user.id)

    if text == BTN_AUTO_TZ:
        lang = (message.from_user.language_code or "en").lower()
        tz = "Europe/Moscow" if lang.startswith("ru") else "UTC"
        with get_session() as s:
            u.tz = tz
            s.add(u); s.commit()
        await state.set_state(OnboardingStates.goal)
        await message.answer(f"Ок, ставлю TZ: <b>{tz}</b>. Теперь выбери цель:", reply_markup=goals_kb())
        return

    if text == BTN_SKIP:
        await state.set_state(OnboardingStates.goal)
        await message.answer("Пропустили TZ (по умолчанию UTC). Теперь выбери цель:", reply_markup=goals_kb())
        return

    if "/" in text or text.upper() == "UTC":
        with get_session() as s:
            u.tz = text
            s.add(u); s.commit()
        await state.set_state(OnboardingStates.goal)
        await message.answer(f"TZ установлен: <b>{text}</b>. Теперь цель:", reply_markup=goals_kb())
        return

    await message.answer("Не похоже на часовой пояс. Пример: Europe/Moscow или UTC. Либо нажми «Пропустить».", reply_markup=tz_kb())

# --------- Flow: Goal ----------
@router.message(F.chat.type == "private", OnboardingStates.goal, F.text == BTN_CANCEL)
async def ob_cancel_goal(message: Message, state: FSMContext):
    await ob_cancel(message, state)

@router.message(F.chat.type == "private", OnboardingStates.goal, F.text == BTN_BACK)
async def ob_back_to_tz(message: Message, state: FSMContext):
    await state.set_state(OnboardingStates.tz)
    await message.answer("Вернулись к выбору часового пояса:", reply_markup=tz_kb())

@router.message(F.chat.type == "private", OnboardingStates.goal)
async def ob_set_goal(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    u = await _get_or_create_user(message.from_user.id)
    if text in GOALS or text == BTN_SKIP:
        with get_session() as s:
            u.goal = text if text in GOALS else u.goal
            s.add(u); s.commit()
        await state.set_state(OnboardingStates.level)
        await message.answer("Отлично! Теперь оцени свой опыт:", reply_markup=levels_kb())
    else:
        await message.answer("Выбери один из вариантов или нажми «Пропустить».", reply_markup=goals_kb())

# --------- Flow: Level ----------
@router.message(F.chat.type == "private", OnboardingStates.level, F.text == BTN_CANCEL)
async def ob_cancel_level(message: Message, state: FSMContext):
    await ob_cancel(message, state)

@router.message(F.chat.type == "private", OnboardingStates.level, F.text == BTN_BACK)
async def ob_back_to_goal(message: Message, state: FSMContext):
    await state.set_state(OnboardingStates.goal)
    await message.answer("Вернулись к цели:", reply_markup=goals_kb())

@router.message(F.chat.type == "private", OnboardingStates.level)
async def ob_set_level(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    u = await _get_or_create_user(message.from_user.id)
    if text in LEVELS or text == BTN_SKIP:
        with get_session() as s:
            u.level = text if text in LEVELS else u.level
            s.add(u); s.commit()
        await state.set_state(OnboardingStates.equipment)
        await message.answer("Чем располагаешь для тренировок?", reply_markup=equipment_kb())
    else:
        await message.answer("Выбери вариант из списка или «Пропустить».", reply_markup=levels_kb())

# --------- Flow: Equipment ----------
@router.message(F.chat.type == "private", OnboardingStates.equipment, F.text == BTN_CANCEL)
async def ob_cancel_equipment(message: Message, state: FSMContext):
    await ob_cancel(message, state)

@router.message(F.chat.type == "private", OnboardingStates.equipment, F.text == BTN_BACK)
async def ob_back_to_level(message: Message, state: FSMContext):
    await state.set_state(OnboardingStates.level)
    await message.answer("Вернулись к опыту:", reply_markup=levels_kb())

@router.message(F.chat.type == "private", OnboardingStates.equipment)
async def ob_set_equipment(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    u = await _get_or_create_user(message.from_user.id)
    if text in EQUIPMENT or text == BTN_SKIP:
        with get_session() as s:
            u.equipment = text if text in EQUIPMENT else u.equipment
            s.add(u); s.commit()
        await state.set_state(OnboardingStates.injuries)
        await message.answer(
            "Есть ли травмы/ограничения? Опиши кратко одним сообщением или нажми «Пропустить».",
            reply_markup=injuries_kb(),   # ← маленькая клавиатура: Пропустить/Назад/Отмена
        )
    else:
        await message.answer("Выбери вариант или «Пропустить».", reply_markup=equipment_kb())

# --------- Flow: Injuries ----------
@router.message(F.chat.type == "private", OnboardingStates.injuries, F.text == BTN_CANCEL)
async def ob_cancel_injuries(message: Message, state: FSMContext):
    await ob_cancel(message, state)

@router.message(F.chat.type == "private", OnboardingStates.injuries, F.text == BTN_BACK)
async def ob_back_to_equipment(message: Message, state: FSMContext):
    await state.set_state(OnboardingStates.equipment)
    await message.answer("Вернулись к выбору оборудования:", reply_markup=equipment_kb())

@router.message(F.chat.type == "private", OnboardingStates.injuries)
async def ob_set_injuries(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    u = await _get_or_create_user(message.from_user.id)
    if text != BTN_SKIP and text not in (BTN_BACK, BTN_CANCEL) and text:
        with get_session() as s:
            u.injuries_json = {"text": text[:500]}
            s.add(u); s.commit()

    await state.clear()
    with get_session() as s:
        u = s.exec(select(User).where(User.tg_id == message.from_user.id)).first()

    summary = (
        "Готово! Профиль сохранён:\n"
        f"• TZ: <b>{u.tz or '—'}</b>\n"
        f"• Цель: <b>{u.goal or '—'}</b>\n"
        f"• Опыт: <b>{u.level or '—'}</b>\n"
        f"• Оборудование: <b>{u.equipment or '—'}</b>\n"
        f"• Травмы: <i>{(u.injuries_json or {}).get('text','—')}</i>\n\n"
        "Можно перейти к /plan или сразу начать /today."
    )
    await message.answer(summary, reply_markup=main_kb())
