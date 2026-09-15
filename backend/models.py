from sqlalchemy import Column, Integer, String, Float, JSON, Text, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from pgvector.sqlalchemy import Vector


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    sex = Column(String, nullable=True)
    activity = Column(String, nullable=True)
    goal = Column(String, nullable=True)
    diet_type = Column(String, nullable=True)
    allergies = Column(JSON, nullable=True)
    disliked_ingredients = Column(JSON, nullable=True)
    favorite_recipe_ids = Column(JSON, nullable=True)
    banned_recipe_ids = Column(JSON, nullable=True)
    budget = Column(Float, nullable=True)
    family_size = Column(Integer, default=1)
    settings = Column(JSON, nullable=True)
    weekly_menus = relationship("WeeklyMenu", back_populates="user")
    family_members = relationship("FamilyMember", back_populates="user", cascade="all, delete-orphan")
    pantry_items = relationship("PantryItem", back_populates="user", cascade="all, delete-orphan")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, nullable=True)
    author = Column(String, nullable=True)
    date_published = Column(DateTime, nullable=True)
    ingredients = Column(JSON, nullable=True)
    calories = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    avg_rating = Column(Float, nullable=True)
    total_ratings = Column(Integer, nullable=True)
    reviews = Column(Integer, nullable=True)
    prep_time = Column(Integer, nullable=True)
    cook_time = Column(Integer, nullable=True)
    total_time = Column(Integer, nullable=True)
    servings = Column(Integer, nullable=True)
    steps = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    cuisine = Column(String, nullable=True)
    complexity = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    substitutions = Column(JSON, nullable=True)
    video_url = Column(String, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    dish_type = Column(String, nullable=True)
    is_user_recipe = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    popularity = Column(Integer, default=0)
    embedding = Column(Vector(312), nullable=True)


class WeeklyMenu(Base):
    __tablename__ = "weekly_menus"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(DateTime, nullable=False)
    week_end = Column(DateTime, nullable=False)
    meals = Column(JSON, nullable=False)
    total_calories = Column(Float, default=0)
    total_protein = Column(Float, default=0)
    total_fat = Column(Float, default=0)
    total_carbs = Column(Float, default=0)
    avg_calories = Column(Float, default=0)
    avg_protein = Column(Float, default=0)
    avg_fat = Column(Float, default=0)
    avg_carbs = Column(Float, default=0)
    estimated_cost = Column(Float, default=0)
    template = Column(String, nullable=True)
    banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="weekly_menus")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="adult")
    allergies = Column(JSON, nullable=True)
    dislikes = Column(JSON, nullable=True)
    favorites = Column(JSON, nullable=True)
    portions = Column(Float, default=1.0)
    user = relationship("User", back_populates="family_members")


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, default=1)
    unit = Column(String, default="шт")
    location = Column(String, default="шкаф")
    expires_on = Column(Date, nullable=True)
    user = relationship("User", back_populates="pantry_items")


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(DateTime, nullable=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    category = Column(String, default="other")
    note = Column(String, nullable=True)
    checked = Column(Boolean, default=False)
    from_menu = Column(Boolean, default=True)
    in_pantry = Column(Boolean, default=False)
    cheaper_swap = Column(JSON, nullable=True)


class RecipeCollection(Base):
    __tablename__ = "recipe_collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    list_name = Column(String, default="favorites")
    created_at = Column(DateTime, default=datetime.utcnow)


class StapleItem(Base):
    __tablename__ = "staple_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, default=1)
    unit = Column(String, default="шт")
    category = Column(String, default="other")
    enabled = Column(Boolean, default=True)
