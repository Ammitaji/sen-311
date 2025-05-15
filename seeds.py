from website import create_app, db
from website.models import User, Recipe, Category
from werkzeug.security import generate_password_hash
from datetime import datetime


def seed_database():
    app = create_app()
    with app.app_context():
        print("Starting database seeding...")

        # Clear existing data (only for development!)
        db.session.query(Recipe).delete()
        db.session.query(Category).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create categories
        categories = [
            Category(
                name='Dinner',
                description='Hearty meals for the evening',
                image_url='https://cdn.usegalileo.ai/sdxl10/7d1ab10c-515f-44dc-b879-24fce1a9ad63.png'
            ),
            Category(
                name='Seasonal',
                description='Recipes perfect for current season',
                image_url='https://cdn.usegalileo.ai/sdxl10/7d1ab10c-515f-44dc-b879-24fce1a9ad63.png'
            )
        ]
        db.session.add_all(categories)

        # Create users
        users = [
            User(
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                first_name='Admin',
                last_name='User',
                profile_image='',
                bio='Administrator account'
            ),
            User(
                email='maria@example.com',
                password=generate_password_hash('chef123'),
                first_name='Maria',
                last_name='Chef',
                profile_image='',
                bio='Professional chef specializing in Italian cuisine'
            ),
            User(
                email='tom@example.com',
                password=generate_password_hash('chef123'),
                first_name='Tom',
                last_name='Chef',
                profile_image='',
                bio='Executive chef with 15 years of experience'
            )
        ]
        db.session.add_all(users)
        db.session.commit()

        # Get user references after commit
        admin, maria, tom = users

        # Recipe data - shortened for example, include all your recipes
        recipes_data = [
            {
                'title': 'Braised Short Ribs',
                'description': 'Tender beef short ribs braised to perfection...',
                'ingredients': '<ul><li>2 lbs beef short ribs</li>    <li>1 onion, chopped</li> <li>3 cloves garlic, minced</li> <li>2 cups beef broth</li> <li>1 cup red wine</li> <li>2 carrots, chopped</li> <li>2 celery stalks, chopped</li> <li>2 tbsp tomato paste</li>  <li>Salt and pepper to taste</li></ul>',
                'instructions': 
                '<ol><li>Preheat oven to 325°F (163°C)</li> <li>Season ribs with salt and pepper<li> <li>Sear ribs in hot pan until browned on all sides</li> <li>Remove ribs and sauté onions, garlic, carrots, and celery</li> <li>Add tomato paste and cook for 1 minute</li> <li>Deglaze with red wine, then add beef broth</li> <li>Return ribs to pan, cover, and braise in oven for 2.5-3 hours</li> <li>Serve with mashed potatoes or polenta</li></ol>',
                'prep_time': 30,
                'cook_time': 180,
                'servings': 4,
                'difficulty': 'Intermediate',
                'image_url': 'https://cdn.usegalileo.ai/sdxl10/ce541c37-fb8c-48a1-b5c9-29baad737a0d.png',
                'category_id': categories[0].id,
                'user_id': tom.id
            },
            {
                'title': 'Chicken Parmesan',
                'description': 'Crispy breaded chicken topped with marinara...',
                # ... other recipe fields
                'category_id': categories[0].id,
                'user_id': maria.id
            },
            # Include all your recipes here with proper user assignments
        ]

        # Add all recipes to database
        for recipe_data in recipes_data:
            recipe = Recipe(
                created_at=datetime.utcnow(),
                **recipe_data
            )
            db.session.add(recipe)

        db.session.commit()
        print(f"Successfully seeded database with {len(recipes_data)} recipes by different users!")