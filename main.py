from website import create_app, db
from flask_migrate import Migrate

# Create the app instance
app = create_app()

# Initialize the migration object
migrate = Migrate(app, db)

# Run the app in debug mode if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
