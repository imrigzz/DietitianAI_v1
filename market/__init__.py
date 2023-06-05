from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
# run_with_ngrok(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY']='3790e43fe46c103ebf40b526'

with app.app_context():
    db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # for hasing of password
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

from market import routes


