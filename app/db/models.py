from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Any

from sqlalchemy import (
    Column,
    JSON,
    UniqueConstraint,
    Index,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlmodel import Field, SQLModel, Relationship


# --- Mixin'ы для таймстемпов/soft-delete (на будущее) -------------------------

class Timestamped(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class SoftDelete(SQLModel):
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


# --- Справочники / пользователи ----------------------------------------------

class User(Timestamped, SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    tg_id: int = Field(index=True, unique=True, description="Telegram user id")
    tz: str = Field(default="UTC", description="IANA TZ, e.g. Europe/Berlin")
    level: Optional[str] = Field(default=None)       # beginner/intermediate/advanced
    goal: Optional[str] = Field(default=None)        # hypertrophy/strength/...
    equipment: Optional[str] = Field(default=None)   # home/gym/bodyweight...
    injuries_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # отношения (по необходимости)
    # sessions: list["WorkoutSession"] = Relationship(back_populates="user")


class Exercise(SQLModel, table=True):
    __tablename__ = "exercises"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    muscle: Optional[str] = Field(default=None, index=True)      # chest/back/legs...
    equipment: Optional[str] = Field(default=None, index=True)   # barbell/dumbbell/...
    video_url: Optional[str] = Field(default=None)
    cues_text: Optional[str] = Field(default=None)


# --- Планирование -------------------------------------------------------------

class Plan(Timestamped, SQLModel, table=True):
    __tablename__ = "plans"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id"),  # добавим ON DELETE CASCADE в миграции
            nullable=False,
            index=True,
        )
    )
    name: str = Field(default="My Plan")
    weeks: int = Field(default=4)
    split_type: Optional[str] = Field(default=None)  # full-body / PPL / ...
    state: str = Field(default="active")             # active / archived / draft

    user: "User" = Relationship()


class WorkoutDay(SQLModel, table=True):
    __tablename__ = "workout_days"

    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("plans.id"),  # ON DELETE CASCADE в миграции
            nullable=False,
            index=True,
        )
    )
    day_idx: int = Field(index=True, description="0..6 within a week (or sequential)")

    __table_args__ = (
        UniqueConstraint("plan_id", "day_idx", name="uq_workout_day_plan_idx"),
    )


class WorkoutItem(SQLModel, table=True):
    __tablename__ = "workout_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    day_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("workout_days.id"),  # ON DELETE CASCADE в миграции
            nullable=False,
            index=True,
        )
    )
    exercise_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("exercises.id"),
            nullable=False,
            index=True,
        )
    )
    # Порядок показа/выполнения в рамках дня:
    order_idx: int = Field(default=0, description="ordering within the day")

    sets: int = Field(default=3)
    reps_min: int = Field(default=6)
    reps_max: int = Field(default=10)
    rir_target: Optional[int] = Field(default=None, description="reps in reserve target")
    rest_sec: int = Field(default=90)
    progression_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False, server_default="{}"),
    )

    __table_args__ = (
        UniqueConstraint("day_id", "order_idx", name="uq_workout_item_day_order"),
        CheckConstraint("sets >= 1", name="ck_workout_item_sets"),
        CheckConstraint("reps_min >= 1 AND reps_max >= reps_min", name="ck_workout_item_reps"),
        CheckConstraint("rest_sec >= 0", name="ck_workout_item_rest"),
    )


# --- Сессия тренировки (новое) -----------------------------------------------

class WorkoutSession(Timestamped, SQLModel, table=True):
    """
    Одна «тренировка». Может быть связана с днём плана (day_id) или быть ad-hoc.
    """
    __tablename__ = "workout_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id"),  # ON DELETE CASCADE в миграции
            nullable=False,
            index=True,
        )
    )
    started_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    finished_at: Optional[datetime] = Field(default=None)
    day_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("workout_days.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )
    notes: Optional[str] = Field(default=None)

    # user: User = Relationship(back_populates="sessions")


# --- Логи сетов --------------------------------------------------------------

class SetLog(SQLModel, table=True):
    __tablename__ = "set_logs"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id"),  # ON DELETE CASCADE в миграции
            nullable=False,
            index=True,
        )
    )
    session_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("workout_sessions.id"),  # ON DELETE CASCADE в миграции
            nullable=False,
            index=True,
        )
    )
    # сет может относиться к конкретному пункту плана (если тренировка из плана)
    workout_item_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("workout_items.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )

    # Временная метка сета: полезно для графиков и «таймера отдыха»
    ts: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Номер сета внутри упражнения (0..N)
    set_index: int = Field(default=0)

    # Вес лучше хранить как NUMERIC; в SQLModel тип Python остаётся float
    weight_kg: float = Field(
        default=0.0,
        sa_column=Column(Numeric(7, 2), nullable=False, server_default="0")
    )
    reps: int = Field(default=0)
    rpe: Optional[float] = Field(default=None)  # шкала 1..10
    rest_sec: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)

    __table_args__ = (
        Index("ix_set_logs_user_session", "user_id", "session_id"),
        Index("ix_set_logs_user_ex_date", "user_id", "workout_item_id", "ts"),
        CheckConstraint("reps >= 0", name="ck_setlog_reps"),
        CheckConstraint("weight_kg >= 0", name="ck_setlog_weight_nonneg"),
        CheckConstraint("(rpe IS NULL) OR (rpe >= 0 AND rpe <= 10)", name="ck_setlog_rpe_0_10"),
        CheckConstraint("(rest_sec IS NULL) OR (rest_sec >= 0)", name="ck_setlog_rest_nonneg"),
    )


# --- Personal Records --------------------------------------------------------

class PR(SQLModel, table=True):
    __tablename__ = "prs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id"),  # ON DELETE CASCADE в миграции
            nullable=False,
            index=True,
        )
    )
    exercise_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("exercises.id"),
            nullable=False,
            index=True,
        )
    )
    one_rm: float = Field(
        default=0.0,
        sa_column=Column(Numeric(7, 2), nullable=False, server_default="0")
    )
    date: date = Field(index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "exercise_id", "date", name="uq_pr_user_exercise_date"),
    )