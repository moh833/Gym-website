import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin

app = Flask(__name__)

app.config.from_pyfile('config.cfg')


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# pass the name of the login func to be redirected to when tring access login_required pages
login_manager.login_message_category = 'info'
# the bootstrap class of the message displayed when tring to access login_required pages whithout logging in

admin = Admin(app, name='DATABASE', template_mode='bootstrap3')

mail = Mail(app)

from gym import routes