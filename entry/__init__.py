from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

from entry.routes.main_routes import main
from entry.routes.user_routes import auth

app.register_blueprint(main)
app.register_blueprint(auth)

from entry.models import User
