from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Recipe, Category, MealPlan, MealPlanRecipe
from . import db
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from sqlalchemy import func, desc
from datetime import datetime, date
import os
from datetime import datetime, timedelta
from flask import abort
from sqlalchemy import or_
import re
import calendar as cal
from calendar import month_name
from sqlalchemy import func

views = Blueprint('views', __name__)

# Configuration constants
RESULTS_PER_PAGE = 9
MIN_PASSWORD_LENGTH = 7
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

# Register the filter
views.add_app_template_filter(slugify, 'slugify')

@views.route('/')
@login_required
def home():
    try:
        trending_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(4).all()
        featured_chefs = User.query.join(Recipe).group_by(User.id)\
            .order_by(func.count(Recipe.id).desc()).limit(4).all()
        seasonal_recipes = Recipe.query.join(Category)\
            .filter(Category.name == 'Seasonal').limit(4).all()
        
        return render_template("home.html", 
                            user=current_user,
                            trending_recipes=trending_recipes,
                            featured_chefs=featured_chefs,
                            seasonal_recipes=seasonal_recipes)
    except Exception as e:
        current_app.logger.error(f"Error loading home page: {str(e)}")
        flash('An error occurred while loading the page', 'error')
        return redirect(url_for('views.home'))

@views.route('/search')
@login_required
def search():
    query = request.args.get('query', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    
    if not query:
        flash('Please enter a search term', 'warning')
        return redirect(url_for('views.home'))
    
    try:
        search_terms = query.split()
        base_query = Recipe.query
        
        for term in search_terms:
            base_query = base_query.filter(
                or_(
                    Recipe.title.ilike(f'%{term}%'),
                    Recipe.description.ilike(f'%{term}%'),
                    Recipe.ingredients.ilike(f'%{term}%')
                )
            )
        
        pagination = base_query.order_by(Recipe.created_at.desc()).paginate(
            page=page, 
            per_page=9, 
            error_out=False
        )
        results = pagination.items
        
        if not results:
            flash(f'No recipes found for "{query}"', 'info')
            
        return render_template('search_results.html',
                           user=current_user,
                           query=query,
                           recipes=results,
                           pagination=pagination,
                           total_results=pagination.total)

    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        flash('An error occurred during search', 'error')
        return redirect(url_for('views.home'))

@views.route('/my-recipes')
@login_required
def my_recipes():
    try:
        page = request.args.get('page', 1, type=int)
        recipes = Recipe.query.filter_by(user_id=current_user.id)\
                   .order_by(Recipe.created_at.desc())
        pagination = recipes.paginate(page=page, per_page=RESULTS_PER_PAGE, error_out=False)
        
        return render_template('my_recipes.html', 
                            user=current_user,
                            recipes=pagination.items,
                            pagination=pagination)
    except Exception as e:
        current_app.logger.error(f"Error loading my recipes: {str(e)}")
        flash('An error occurred while loading your recipes', 'error')
        return redirect(url_for('views.home'))

@views.route('/add-recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    categories = Category.query.order_by(Category.name).all()
    
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['title', 'ingredients', 'instructions']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return render_template('add_recipe.html',
                                         user=current_user,
                                         categories=categories)

            # Handle image upload
            image_url = None
            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '':
                    if not allowed_file(image.filename):
                        flash('Allowed image types are png, jpg, jpeg, gif', 'error')
                        return render_template('add_recipe.html',
                                            user=current_user,
                                            categories=categories)
                    
                    filename = secure_filename(image.filename)
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)
                    image_path = os.path.join(upload_folder, filename)
                    image.save(image_path)
                    image_url = url_for('static', filename=f'uploads/{filename}')

            # Create new recipe
            new_recipe = Recipe(
                title=request.form['title'],
                description=request.form.get('description', ''),
                ingredients=request.form['ingredients'],
                instructions=request.form['instructions'],
                prep_time=request.form.get('prep_time', type=int) or None,
                cook_time=request.form.get('cook_time', type=int) or None,
                servings=request.form.get('servings', type=int) or None,
                difficulty=request.form.get('difficulty', 'Medium'),
                category_id=request.form.get('category_id', type=int),
                image_url=image_url,
                user_id=current_user.id
            )

            db.session.add(new_recipe)
            db.session.commit()
            flash('Recipe added successfully!', 'success')
            
            # Redirect to the new recipe using slug
            return redirect(url_for('views.recipe_by_slug', 
                                 recipe_slug=slugify(new_recipe.title)))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding recipe: {str(e)}")
            flash('An error occurred while adding the recipe', 'error')
            return render_template('add_recipe.html',
                                user=current_user,
                                categories=categories)

    return render_template('add_recipe.html', 
                         user=current_user,
                         categories=categories)

@views.route('/update-password', methods=['POST'])
@login_required
def update_password():
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect', 'error')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'error')
        elif len(new_password) < MIN_PASSWORD_LENGTH:
            flash(f'Password must be at least {MIN_PASSWORD_LENGTH} characters', 'error')
        else:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Password updated successfully!', 'success')
        
        return redirect(url_for('views.edit_profile'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password update error: {str(e)}")
        flash('An error occurred while updating your password', 'error')
        return redirect(url_for('views.edit_profile'))
def generate_mini_calendar(year, month, user_id):
    calendar_obj = calendar.Calendar()
    month_days = cal.monthdays2calendar(year, month)
    
    today = date.today()
    calendar_data = {
        'year': year,
        'month': month,
        'month_name': cal.month_name[month],
        'days': []
    }
    
    for week in month_days:
        for day, weekday in week:
            if day == 0:
                continue
                
            day_date = date(year, month, day)
            has_meals = MealPlanRecipe.query.join(MealPlan)\
                .filter(
                    MealPlan.user_id == user_id,
                    MealPlanRecipe.meal_date == day_date
                )\
                .first() is not None
                
            calendar_data['days'].append({
                'date': day_date,
                'weekday': weekday,
                'has_meals': has_meals
            })
    
    return calendar_data
@views.route('/meal_planner')
@login_required
def meal_planner():
    try:
        today = date.today()
        meal_plan = MealPlan.query.filter_by(user_id=current_user.id).first()
        recipes = Recipe.query.filter_by(user_id=current_user.id).all()
        calendar_data = generate_mini_calendar(today.year, today.month, current_user.id)
        
        return render_template("meal_planner.html",
                            user=current_user,
                            meal_plan=meal_plan,
                            recipes=recipes,
                            today=today,
                            current_date=today,
                            mini_calendar=calendar_data)
    except Exception as e:
        current_app.logger.error(f"Meal planner error: {str(e)}")
        flash("Error loading meal planner", 'error')
        return redirect(url_for('views.home')) 

@login_required
def calendar_view():  # Renamed function
    now = datetime.now()
    
    # Get and validate month/year
    try:
        year = int(request.args.get('year', now.year))
        month = int(request.args.get('month', now.month))
        month = max(1, min(12, month))
    except ValueError:
        year, month = now.year, now.month
    
    # Calculate navigation
    if month == 1:
        prev_month, prev_year = 12, year-1
        next_month, next_year = 2, year
    elif month == 12:
        prev_month, prev_year = 11, year
        next_month, next_year = 1, year+1
    else:
        prev_month, prev_year = month-1, year
        next_month, next_year = month+1, year
    
    # Generate calendar data
    calendar_obj = cal.Calendar()
    month_days = calendar_obj.monthdays2calendar(year, month)
    
    month_weeks = []
    for week in month_days:
        week_days = []
        for day, _ in week:
            if day == 0:
                week_days.append(None)
            else:
                day_date = date(year, month, day)
                has_meals = MealPlanRecipe.query.join(MealPlan)\
                    .filter(
                        MealPlan.user_id == current_user.id,
                        MealPlanRecipe.meal_date == day_date
                    ).first() is not None
                
                week_days.append({
                    'day': day,
                    'date': day_date,
                    'is_today': day_date == now.date(),
                    'has_meals': has_meals
                })
        month_weeks.append(week_days)
    
    # Get upcoming meals
    upcoming_meals = MealPlanRecipe.query.join(MealPlan)\
        .filter(
            MealPlan.user_id == current_user.id,
            MealPlanRecipe.meal_date >= now.date(),
            MealPlanRecipe.meal_date <= now.date() + timedelta(days=7)
        )\
        .join(Recipe)\
        .order_by(MealPlanRecipe.meal_date)\
        .all()
    
    return render_template('calendar.html',
        current_month_name=cal.month_name[month],
        current_year=year,
        month_weeks=month_weeks,
        upcoming_meals=upcoming_meals,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        today=now.date(),
        recipes=Recipe.query.filter_by(user_id=current_user.id).all()
    )

@views.route('/daily-meals')
@login_required
def daily_meals():
    date_str = request.args.get('date')
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except ValueError:
        selected_date = date.today()
    
    meals = MealPlanRecipe.query.join(MealPlan)\
        .filter(
            MealPlan.user_id == current_user.id,
            MealPlanRecipe.meal_date == selected_date
        )\
        .join(Recipe)\
        .all()
    
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    
    return render_template('daily_meals.html',
                         date=selected_date,
                         meals=meals,
                         recipes=recipes)

@views.route('/add-meal', methods=['POST'])
@login_required
def add_meal():
    try:
        date_str = request.form.get('date')
        recipe_id = request.form.get('recipe_id')
        
        if not date_str or not recipe_id:
            flash('Missing required fields', 'error')
            return redirect(url_for('views.calendar'))
        
        meal_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        meal_plan = MealPlan.query.filter_by(
            user_id=current_user.id,
            date=meal_date
        ).first()
        
        if not meal_plan:
            meal_plan = MealPlan(
                user_id=current_user.id,
                date=meal_date
            )
            db.session.add(meal_plan)
            db.session.commit()
        
        meal_recipe = MealPlanRecipe(
            meal_plan_id=meal_plan.id,
            recipe_id=recipe_id,
            meal_type='dinner'
        )
        db.session.add(meal_recipe)
        db.session.commit()
        
        flash('Meal added to plan!', 'success')
        return redirect(url_for('views.daily_meals', date=date_str))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding meal: {str(e)}")
        flash('Error adding meal to plan', 'error')
        return redirect(url_for('views.calendar'))

@views.route('/add-meal-to-plan', methods=['POST'])
@login_required
def add_meal_to_plan():
    try:
        date_str = request.form.get('date')
        recipe_id = request.form.get('recipe_id')
        meal_type = request.form.get('meal_type', 'dinner')
        
        if not all([date_str, recipe_id, meal_type]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        # Convert date string to date object
        meal_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Verify recipe exists
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found'
            }), 404

        # Find or create meal plan for this user
        meal_plan = MealPlan.query.filter_by(user_id=current_user.id).first()
        if not meal_plan:
            meal_plan = MealPlan(user_id=current_user.id)
            db.session.add(meal_plan)
            db.session.commit()

        # Add the meal
        new_meal = MealPlanRecipe(
            meal_plan_id=meal_plan.id,
            recipe_id=recipe_id,
            meal_date=meal_date,
            meal_type=meal_type
        )
        db.session.add(new_meal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Meal added successfully!'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding meal: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while adding the meal'
        }), 500
@views.route('/remove-meal/<int:meal_id>', methods=['POST'])
@login_required
def remove_meal(meal_id):
    try:
        meal = MealPlanRecipe.query.get_or_404(meal_id)
        if meal.meal_plan.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        db.session.delete(meal)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Meal removed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
# Add this route
@views.route('/r/<string:recipe_slug>')  # Shortened URL pattern
@login_required
def recipe_by_slug(recipe_slug):
    title = recipe_slug.replace('-', ' ')
    recipe = Recipe.query.filter(
        func.lower(Recipe.title) == title.lower()
    ).first_or_404()
    return render_template('recipe_detail.html', 
                         user=current_user,
                         recipe=recipe)
@views.route('/get-meals')
@login_required
def get_meals():
    date_str = request.args.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        meals = MealPlanRecipe.query.join(MealPlan)\
            .filter(
                MealPlan.user_id == current_user.id,
                MealPlanRecipe.meal_date == date
            )\
            .join(Recipe)\
            .add_columns(Recipe.title.label('recipe_title'))\
            .all()
        
        return jsonify({
            'success': True,
            'meals': [{
                'id': meal.MealPlanRecipe.id,
                'recipe_title': meal.recipe_title,
                'meal_type': meal.MealPlanRecipe.meal_type
            } for meal in meals]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@views.route('/calendar')
@login_required
def calendar():
    today = datetime.today()
    
    # Get today's meals for the current user
    today_meals = db.session.query(MealPlanRecipe).join(MealPlan)\
        .filter(
            MealPlan.user_id == current_user.id,
            MealPlanRecipe.meal_date == today.date()
        ).all()
    
    return render_template('calendar.html',
        today=today,
        today_meals=today_meals,
        recipes=current_user.recipes
    )
def generate_calendar_data(year, month, user_id):
    """Generate calendar data structure with proper meal indicators"""
    # Create calendar with Sunday as first day
    calendar_obj = cal.Calendar(firstweekday=6)  # 6 = Sunday
    month_days = calendar_obj.monthdays2calendar(year, month)
    today = date.today()
    
    calendar_data = {
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'weeks': []
    }
    
    for week in month_days:
        week_days = []
        for day, weekday in week:
            if day == 0:  # Day belongs to previous/next month
                week_days.append(None)
                continue
                
            day_date = date(year, month, day)
            has_meals = MealPlanRecipe.query.join(MealPlan)\
                .filter(
                    MealPlan.user_id == user_id,
                    MealPlanRecipe.meal_date == day_date
                ).first() is not None
                
            week_days.append({
                'day': day,
                'date': day_date,
                'weekday': weekday,
                'has_meals': has_meals,
                'is_today': day_date == today,
                'is_past': day_date < today
            })
        calendar_data['weeks'].append(week_days)
    
    return calendar_data