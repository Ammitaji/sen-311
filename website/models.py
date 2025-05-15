from . import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150))
    recipes = db.relationship('Recipe', backref='author', lazy=True)
    meal_plans = db.relationship('MealPlan', backref='user', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'  # Changed to singular to match FK reference
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    recipes = db.relationship('Recipe', backref='categories', lazy=True)

class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    prep_time = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    servings = db.Column(db.Integer)
    difficulty = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # Matches Category.__tablename__
    meal_plans = db.relationship('MealPlanRecipe', backref='recipe', lazy=True)

class MealPlan(db.Model):
    __tablename__ = 'meal_plan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='My Meal Plan')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    meals = db.relationship('MealPlanRecipe', backref='meal_plan', lazy=True)

class MealPlanRecipe(db.Model):
    __tablename__ = 'meal_plan_recipe'
    id = db.Column(db.Integer, primary_key=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plan.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    meal_date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20))