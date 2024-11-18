import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    """
        Function to create and configure the Flask application.

        Initializes the application, configures the database, file upload folder,
        and login manager. It also registers blueprints for authentication and main routes.

        Returns:
            Flask app instance.
    """
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Load configurations from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, os.getenv('UPLOAD_FOLDER'))
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.init_app(app)

    # Set up the login manager for user sessions
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    # Load user from the database for login management
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints for authentication and main routes
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Create tables in the database
    from project import models
    with app.app_context():
        db.create_all()

    return app
