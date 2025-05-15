"""Initial migration with all 6 featured recipes

Revision ID: d8b4f2f51095
Revises: 
Create Date: 2025-05-05 17:14:00.867159
"""

from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'd8b4f2f51095'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create tables with proper constraints
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_categories'),
        sa.UniqueConstraint('name', name='uq_category_name')
    )
    
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('profile_image', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_user'),
        sa.UniqueConstraint('email', name='uq_user_email')
    )
    
    op.create_table('recipe',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ingredients', sa.Text(), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=False),
        sa.Column('prep_time', sa.Integer(), nullable=True),
        sa.Column('cook_time', sa.Integer(), nullable=True),
        sa.Column('servings', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_recipe_category'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_recipe_user'),
        sa.PrimaryKeyConstraint('id', name='pk_recipe')
    )
    
    op.create_table('meal_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False, default='My Meal Plan'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_meal_plan_user'),
        sa.PrimaryKeyConstraint('id', name='pk_meal_plan')
    )
    
    op.create_table('meal_plan_recipe',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meal_plan_id', sa.Integer(), nullable=False),
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('day', sa.String(length=10), nullable=False),
        sa.Column('meal_type', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['meal_plan_id'], ['meal_plan.id'], name='fk_mpr_meal_plan'),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], name='fk_mpr_recipe'),
        sa.PrimaryKeyConstraint('id', name='pk_meal_plan_recipe')
    )

    # Insert initial data
    conn = op.get_bind()
    now = datetime.utcnow()
    password_hash = generate_password_hash('temp_password', method='pbkdf2:sha256')

    # Insert categories
    if not conn.execute(sa.text("SELECT 1 FROM categories LIMIT 1")).scalar():
        op.bulk_insert(
            sa.table('categories',
                sa.Column('id'),
                sa.Column('name'),
                sa.Column('description'),
                sa.Column('image_url')
            ),
            [
                {
                    'id': 1, 
                    'name': 'Dinner',
                    'description': 'Hearty meals for the evening',
                    'image_url': 'https://cdn.usegalileo.ai/sdxl10/7d1ab10c-515f-44dc-b879-24fce1a9ad63.png'
                },
                {
                    'id': 2,
                    'name': 'Seasonal',
                    'description': 'Recipes perfect for the current season',
                    'image_url': 'https://cdn.usegalileo.ai/sdxl10/7d1ab10c-515f-44dc-b879-24fce1a9ad63.png'
                }
            ]
        )

    # Insert admin user
    if not conn.execute(sa.text("SELECT 1 FROM user WHERE email = 'admin@example.com'")).scalar():
        op.execute(
            sa.text("""
                INSERT INTO user (id, email, password, first_name, last_name, profile_image, bio)
                VALUES (
                    1, 
                    'admin@example.com', 
                    :password, 
                    'Admin', 
                    'User', 
                    '', 
                    'Administrator account'
                )
            """).bindparams(password=password_hash)
        )

    # Insert 6 featured recipes
    if not conn.execute(sa.text("SELECT 1 FROM recipe LIMIT 1")).scalar():
        recipes = [
            {
                'title': 'Braised Short Ribs',
                'description': 'Tender beef short ribs braised to perfection in a rich red wine sauce',
                'ingredients': '<ul><li>2 lbs beef short ribs</li><li>1 onion, chopped</li><li>3 cloves garlic, minced</li><li>2 cups beef broth</li><li>1 cup red wine</li><li>salt and pepper to taste</li></ul>',
                'instructions': '<ol><li>Preheat oven to 325°F (163°C)</li><li>Season ribs with salt and pepper. Sear in a hot pan until browned</li><li>Remove ribs. In the same pan, sauté onions and garlic.</li><li>Add red wine and beef broth. Bring to a simmer</li><li>Return ribs to the pan, cover, and transfer to oven.</li><li>Braise for 2.5 to 3 hours, until tender.</li></ol>',
                'prep_time': 30,
                'cook_time': 180,
                'servings': 4,
                'difficulty': 'Intermediate',
                'image_url': 'https://cdn.usegalileo.ai/sdxl10/ce541c37-fb8c-48a1-b5c9-29baad737a0d.png',
                'category_id': 1
            },
            {
                'title': 'Chicken Parmesan',
                'description': 'Crispy breaded chicken topped with marinara sauce and melted cheese',
                'ingredients': '<ul><li>4 boneless, skinless chicken breasts</li><li>1 cup all-purpose flour</li><li>2 eggs, beaten</li><li>2 cups breadcrumbs</li><li>1 cup marinara sauce</li><li>1 cup mozzarella cheese</li><li>1/2 cup parmesan cheese</li></ul>',
                'instructions': '<ol><li>Preheat oven to 375°F (190°C)</li><li>Pound chicken to even thickness</li><li>Dredge in flour, then egg, then breadcrumbs</li><li>Fry until golden, then top with sauces and cheese</li><li>Bake until cheese melts</li></ol>',
                'prep_time': 20,
                'cook_time': 25,
                'servings': 4,
                'difficulty': 'Easy',
                'image_url': 'https://cdn.usegalileo.ai/sdxl10/7d1ab10c-515f-44dc-b879-24fce1a9ad63.png',
                'category_id': 1
            },
            {
                'title': 'Coconut Curry Shrimp',
                'description': 'Creamy coconut curry with plump shrimp and vegetables',
                'ingredients': '<ul><li>1 lb shrimp</li><li>1 onion, chopped</li><li>1 can coconut milk</li><li>2 tbsp curry powder</li><li>1 bell pepper, sliced</li></ul>',
                'instructions': '<ol><li>Sauté onions and peppers</li><li>Add curry powder and coconut milk</li><li>Simmer and add shrimp</li><li>Cook until shrimp are pink</li></ol>',
                'prep_time': 15,
                'cook_time': 15,
                'servings': 4,
                'difficulty': 'Easy',
                'image_url': 'https://cdn.usegalileo.ai/sdxl10/7d1ab10c-515f-44dc-b879-24fce1a9ad63.png',
                'category_id': 2
            },
            {
                'title': 'Beef and Broccoli',
                'description': 'Classic Chinese takeout dish made at home',
                'ingredients': '<ul><li>1 lb flank steak</li><li>4 cups broccoli florets</li><li>3 tbsp soy sauce</li><li>2 tbsp oyster sauce</li><li>1 tbsp cornstarch</li></ul>',
                'instructions': '<ol><li>Slice beef and marinate</li><li>Stir-fry broccoli</li><li>Add beef and cook through</li><li>Add sauce and thicken</li></ol>',
                'prep_time': 15,
                'cook_time': 15,
                'servings': 4,
                'difficulty': 'Easy',
                'image_url': 'https://cdn.usegalileo.ai/sdxl10/883db8e2-d7c2-468a-8645-d9fa8df1ce7f.png',
                'category_id': 2
            },
            {
                'title': 'Miso Glazed Cod',
                'description': 'Delicate white fish with sweet miso glaze',
                'ingredients': '<ul><li>4 cod fillets</li><li>3 tbsp white miso</li><li>1 tbsp mirin</li><li>1 tbsp honey</li><li>1 tbsp soy sauce</li></ul>',
                'instructions': '<ol><li>Mix glaze ingredients</li><li>Brush on cod</li><li>Bake at 400°F for 12 mins</li><li>Broil for 2 mins to caramelize</li></ol>',
                'prep_time': 10,
                'cook_time': 15,
                'servings': 4,
                'difficulty': 'Easy',
                'image_url': 'https://cdn.usegalileo.ai/sdxl10/2aecf54f-0446-4e19-b196-cc6ba6d70d77.png',
                'category_id': 2
            },
            {
                'title': 'Pork Chop with Apples',
                'description': 'Juicy pork with caramelized apples',
                'ingredients': '<ul><li>4 pork chops</li><li>2 apples, sliced</li><li>2 tbsp butter</li><li>1 tbsp brown sugar</li><li>1 tsp cinnamon</li></ul>',
                'instructions': '<ol><li>Sear pork chops</li><li>Sauté apples with sugar</li><li>Combine and finish in oven</li></ol>',
                'prep_time': 15,
                'cook_time': 20,
                'servings': 4,
                'difficulty': 'Easy',
                'image_url': 'https://cdn.usegalileo.ai/sdxl10/31d9ef43-299b-4b7c-80e1-09f47e6b2adf.png',
                'category_id': 2
            }
        ]

        for recipe in recipes:
            op.execute(
                sa.text("""
                    INSERT INTO recipe (
                        title, description, ingredients, instructions,
                        prep_time, cook_time, servings, difficulty,
                        image_url, created_at, user_id, category_id
                    ) VALUES (
                        :title, :description, :ingredients, :instructions,
                        :prep_time, :cook_time, :servings, :difficulty,
                        :image_url, :created_at, :user_id, :category_id
                    )
                """).bindparams(
                    created_at=now,
                    user_id=1,
                    **recipe
                )
            )

def downgrade():
    op.drop_table('meal_plan_recipe', schema=None)
    op.drop_table('meal_plan', schema=None)
    op.drop_table('recipe', schema=None)
    op.drop_table('user', schema=None)
    op.drop_table('categories', schema=None)
