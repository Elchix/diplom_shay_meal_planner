"""Канонические приёмы пищи и дни недели."""

from enum import Enum

PLACEHOLDERS = {"", "string", "str", "none", "null", "undefined"}


class MealSlot(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack1 = "snack1"
    snack2 = "snack2"


class WeekDay(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


VALID_SLOTS = [s.value for s in MealSlot]
VALID_DAYS = [d.value for d in WeekDay]

SLOT_ALIASES = {
    "snack": "snack1",
    "перекус": "snack1",
    "перекус1": "snack1",
    "перекус 1": "snack1",
    "перекус2": "snack2",
    "перекус 2": "snack2",
    "завтрак": "breakfast",
    "обед": "lunch",
    "ужин": "dinner",
    "breakfast": "breakfast",
    "lunch": "lunch",
    "dinner": "dinner",
    "snack1": "snack1",
    "snack2": "snack2",
}

DAY_ALIASES = {
    "понедельник": "monday",
    "вторник": "tuesday",
    "среда": "wednesday",
    "четверг": "thursday",
    "пятница": "friday",
    "суббота": "saturday",
    "воскресенье": "sunday",
    **{d: d for d in VALID_DAYS},
}


def is_placeholder(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip().lower() in PLACEHOLDERS:
        return True
    return False


def clean_text(value):
    if is_placeholder(value):
        return None
    if isinstance(value, str):
        return value.strip()
    return value


def normalize_slot(value) -> str | None:
    if is_placeholder(value):
        return None
    raw = str(value).strip().lower()
    if raw in VALID_SLOTS:
        return raw
    return SLOT_ALIASES.get(raw)


def normalize_day(value) -> str | None:
    if is_placeholder(value):
        return None
    raw = str(value).strip().lower()
    if raw in VALID_DAYS:
        return raw
    return DAY_ALIASES.get(raw)


def normalize_slot_list(values) -> list[str]:
    out = []
    for item in values or []:
        slot = normalize_slot(item)
        if slot and slot not in out:
            out.append(slot)
    return out


def clean_str_list(values) -> list[str]:
    out = []
    for item in values or []:
        text = clean_text(item)
        if text:
            out.append(text)
    return out
