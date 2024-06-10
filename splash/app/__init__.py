from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_moment import Moment




app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
CMC_API_KEY = 'your_secret_key'
login = LoginManager(app)
login.login_view='index'
login.session_protection = 'strong'
#auth = Blueprint('auth', __name__)
mail = Mail(app)
socketio = SocketIO(app)
moment = Moment(app)


        
                        
from app import views, models, error





