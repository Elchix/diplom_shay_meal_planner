from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from services.slots import (
    MealSlot, WeekDay, normalize_slot, normalize_day,
    normalize_slot_list, clean_text, clean_str_list, VALID_SLOTS,
)


class UserCreate(BaseModel):
    email: str = Field(examples=["demo@nedelka.ru"])
    password: str = Field(examples=["demo1234"])
    name: Optional[str] = None
    age: Optional[int] = Field(None, examples=[30])
    weight: Optional[float] = Field(None, examples=[70])
    height: Optional[float] = Field(None, examples=[170])
    sex: Optional[str] = Field(None, examples=["female"])
    activity: Optional[str] = "medium"
    goal: Optional[str] = Field(None, examples=["maintain"])
    diet_type: Optional[str] = None
    allergies: Optional[List[str]] = []
    disliked_ingredients: Optional[List[str]] = []
    budget: Optional[float] = None
    family_size: Optional[int] = 1

    @field_validator("diet_type", "goal", "sex", "activity", "name", mode="before")
    @classmethod
    def drop_placeholders(cls, v):
        return clean_text(v)

    @field_validator("allergies", "disliked_ingredients", mode="before")
    @classmethod
    def drop_placeholder_lists(cls, v):
        return clean_str_list(v) if v else v


class LoginRequest(BaseModel):
    email: str = Field(examples=["demo@nedelka.ru"])
    password: str = Field(examples=["demo1234"])


class UserSettings(BaseModel):
    meal_slots: Optional[List[MealSlot]] = Field(
        default=["breakfast", "lunch", "dinner", "snack1", "snack2"]
    )
    week_starts_on: Optional[str] = "monday"
    units: Optional[str] = "metric"
    theme: Optional[str] = "light"
    reminders: Optional[bool] = True
    cooking_time_limit: Optional[int] = None
    auto_staples: Optional[bool] = True

    @field_validator("meal_slots", mode="before")
    @classmethod
    def clean_slots(cls, v):
        cleaned = normalize_slot_list(v)
        return cleaned or ["breakfast", "lunch", "dinner", "snack1", "snack2"]


class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    sex: Optional[str] = None
    activity: Optional[str] = None
    goal: Optional[str] = None
    diet_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    disliked_ingredients: Optional[List[str]] = None
    favorite_recipe_ids: Optional[List[int]] = None
    banned_recipe_ids: Optional[List[int]] = None
    budget: Optional[float] = None
    family_size: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None

    @field_validator("name", "sex", "activity", "goal", "diet_type", mode="before")
    @classmethod
    def drop_placeholders(cls, v):
        return clean_text(v)

    @field_validator("allergies", "disliked_ingredients", mode="before")
    @classmethod
    def drop_placeholder_lists(cls, v):
        return None if v is None else clean_str_list(v)

    @field_validator("settings", mode="before")
    @classmethod
    def clean_settings(cls, v):
        if not v or not isinstance(v, dict):
            return v
        data = dict(v)
        if "meal_slots" in data:
            data["meal_slots"] = normalize_slot_list(data.get("meal_slots")) or VALID_SLOTS
        return data


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    sex: Optional[str] = None
    activity: Optional[str] = None
    goal: Optional[str] = None
    diet_type: Optional[str] = None
    allergies: Optional[List[str]] = []
    disliked_ingredients: Optional[List[str]] = []
    favorite_recipe_ids: Optional[List[int]] = []
    banned_recipe_ids: Optional[List[int]] = []
    budget: Optional[float] = None
    family_size: Optional[int] = 1
    settings: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class IngredientIn(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = ""
    notes: Optional[str] = ""


class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    ingredients: List[Any] = []
    steps: List[Any] = []
    category: Optional[str] = ""
    cuisine: Optional[str] = ""
    complexity: Optional[str] = "легко"
    image_url: Optional[str] = None
    tags: Optional[List[str]] = []
    substitutions: Optional[List[Any]] = []
    video_url: Optional[str] = None
    prep_time: Optional[int] = 0
    cook_time: Optional[int] = 0
    servings: Optional[int] = 2
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    dish_type: Optional[str] = None
    estimated_cost: Optional[float] = None
    url: Optional[str] = None
    quick: Optional[bool] = False


class DayMeals(BaseModel):
    breakfast: Optional[int] = Field(None, description="ID рецепта на завтрак")
    lunch: Optional[int] = Field(None, description="ID рецепта на обед")
    dinner: Optional[int] = Field(None, description="ID рецепта на ужин")
    snack1: Optional[int] = Field(None, description="ID рецепта на перекус 1")
    snack2: Optional[int] = Field(None, description="ID рецепта на перекус 2")


class WeekMeals(BaseModel):
    monday: Optional[DayMeals] = None
    tuesday: Optional[DayMeals] = None
    wednesday: Optional[DayMeals] = None
    thursday: Optional[DayMeals] = None
    friday: Optional[DayMeals] = None
    saturday: Optional[DayMeals] = None
    sunday: Optional[DayMeals] = None


class MenuUpdate(BaseModel):
    meals: WeekMeals = Field(
        examples=[{
            "monday": {"breakfast": 1, "lunch": 2, "dinner": 3, "snack1": None, "snack2": None},
            "tuesday": {"breakfast": 4, "lunch": 5, "dinner": 6},
        }]
    )


class WeeklyMenuCreate(BaseModel):
    user_id: int
    week_start: datetime
    week_end: datetime
    meals: WeekMeals


class WeeklyMenuResponse(BaseModel):
    id: int
    user_id: int
    week_start: datetime
    week_end: datetime
    meals: Dict[str, Any]
    total_calories: float
    total_protein: float
    total_fat: float
    total_carbs: float
    avg_calories: float
    avg_protein: float
    avg_fat: float
    avg_carbs: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AutoPlanRequest(BaseModel):
    user_id: Optional[int] = None
    family_size: Optional[int] = None
    diet_type: Optional[str] = Field(None, examples=["vegetarian"])
    disliked: Optional[List[str]] = Field(None, examples=[["лук"]])
    favorites: Optional[List[int]] = None
    budget: Optional[float] = Field(None, examples=[5000])
    max_time: Optional[int] = Field(None, examples=[40])
    template: Optional[str] = Field(
        None,
        examples=["family"],
        description="healthy | weight_loss | mass | vegetarian | family | budget | quick",
    )
    meal_slots: Optional[List[MealSlot]] = Field(
        None,
        examples=[["breakfast", "lunch", "dinner", "snack1", "snack2"]],
        description="Какие приёмы пищи заполнять",
    )
    quick_only: Optional[bool] = False
    iterations: Optional[int] = 80

    @field_validator("diet_type", "template", mode="before")
    @classmethod
    def drop_placeholders(cls, v):
        return clean_text(v)

    @field_validator("disliked", mode="before")
    @classmethod
    def drop_placeholder_lists(cls, v):
        return None if v is None else clean_str_list(v)

    @field_validator("meal_slots", mode="before")
    @classmethod
    def clean_slots(cls, v):
        if v is None:
            return None
        cleaned = normalize_slot_list(v)
        return cleaned or None


class SlotAssign(BaseModel):
    day: WeekDay = Field(examples=["monday"], description="День недели")
    slot: MealSlot = Field(examples=["dinner"], description="Приём пищи")
    recipe_id: Optional[int] = Field(None, examples=[1])
    custom: Optional[Dict[str, Any]] = None

    @field_validator("day", mode="before")
    @classmethod
    def clean_day(cls, v):
        day = normalize_day(v)
        if not day:
            raise ValueError("День должен быть monday…sunday, не string")
        return day

    @field_validator("slot", mode="before")
    @classmethod
    def clean_slot(cls, v):
        slot = normalize_slot(v)
        if not slot:
            raise ValueError("Слот должен быть breakfast, lunch, dinner, snack1 или snack2")
        return slot


class FamilyMemberIn(BaseModel):
    name: str
    role: str = Field("adult", examples=["adult"])
    allergies: Optional[List[str]] = []
    dislikes: Optional[List[str]] = []
    favorites: Optional[List[str]] = []
    portions: float = 1.0


class PantryIn(BaseModel):
    name: str = Field(examples=["яйца"])
    amount: float = 1
    unit: str = "шт"
    location: str = Field("шкаф", examples=["холодильник"])
    expires_on: Optional[date] = None


class ShoppingPatch(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    unit: Optional[str] = None
    note: Optional[str] = None
    checked: Optional[bool] = None
    in_pantry: Optional[bool] = None
    category: Optional[str] = None


class ShoppingAdd(BaseModel):
    name: str
    amount: Optional[float] = 1
    unit: Optional[str] = "шт"
    note: Optional[str] = None
    category: Optional[str] = "other"


class CollectionIn(BaseModel):
    recipe_id: int
    list_name: str = "favorites"


class ImportLinkIn(BaseModel):
    url: str
