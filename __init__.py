from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from slugify import slugify

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sen311'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "database.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views)
    app.register_blueprint(auth)

    # Setup login manager
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User  # Avoid circular imports

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register CLI commands
    register_commands(app)

    return app

def register_commands(app):
    """Register custom CLI commands"""

    @app.cli.command("verify-db")
    def verify_db():
        """Verify database structure"""
        from sqlalchemy import text, inspect

        with app.app_context():
            print("\n=== Database Verification ===")
            print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")

            # Verify connection
            try:
                db.session.execute(text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return

            # Check tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\nFound {len(tables)} tables: {', '.join(tables)}")

            # Verify migrations
            if 'alembic_version' in tables:
                version = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
                print(f"\n🔖 Applied Migration: {version}")
            else:
                print("\n⚠️ No alembic_version table - migrations may not be applied")

            # Verify models
            required_tables = {'user', 'recipe', 'category', 'meal_plan', 'meal_plan_recipe'}
            missing_tables = required_tables - set(tables)
            if missing_tables:
                print(f"\n❌ Missing tables: {', '.join(missing_tables)}")
            else:
                print("\n✅ All expected tables exist")

    @app.cli.command("seed-db")
    def seed_db_command():
        """Seed the database with initial data"""
        from website.seeds import seed_database
        seed_database()


# Only this line outside — used by Flask CLI and external scripts
app = create_app()
