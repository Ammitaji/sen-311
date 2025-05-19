from website import create_app, db
from flask_migrate import Migrate

# Create the app instance
app = create_app()

# Initialize the migration object
migrate = Migrate(app, db)

# Run the app in debug mode if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)

from website import create_app, db
from flask_migrate import Migrate

# Create the app instance
app = create_app()

# Initialize the migration object
migrate = Migrate(app, db)

# Run the app in debug mode if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
    from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db.init_app(app)
    return app
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
from website import create_app, db
from flask_migrate import Migrate

# Create the app instance
app = create_app()

# Initialize the migration object
migrate = Migrate(app, db)

# Run the app in debug mode if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
    from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db.init_app(app)
    return app
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
