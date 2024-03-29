from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

# App initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = ""


# Database initialization
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy()
db.init_app(app)


#Registering Blueprints
from .api import api
app.register_blueprint(api, url_prefix='/api')


# Authentication
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(app)


# Function to create a database if not exists
def create_database(app) -> None:
    if not path.exists('musicf/database.db'):
        app.app_context().push()
        db.create_all()
        # db.session.execute('pragma foreign_keys=on')
        print("DATABASE CREATED")

# we imported here cuz of circular import
from musicf import routes