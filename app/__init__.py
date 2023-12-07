# Acknowledgements:
# All icons used in this project are from https://spectrum.adobe.com/page/icons/
# Design of this app is inspired by the Adobe Spectrum design system

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Load environment variables from .env file (used for SECRET_KEY)


# If I don't include this, I get an error when running db_create.py
# It's about the app running outside of the context of the application instance
app.app_context().push()

app.config.from_object('config')
# app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

migrate = Migrate(app, db)

from app import views