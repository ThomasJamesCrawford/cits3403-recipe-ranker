from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
# sets the route for login required
login_manager.login_view = 'login'
# sets the style for the message of login required
login_manager.login_message_category = 'info'

from app import routes, models
