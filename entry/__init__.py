from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)

from config import Config
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

migrate = Migrate(app, db)

from entry.routes.main_routes import main
from entry.routes.user_routes import auth
from entry.routes.product_routes import product
from entry.routes.admin_routes import admin

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(product)
app.register_blueprint(admin)

from entry.models import User
from entry.models import Product
from entry.models import Category
from entry.models import Wishlist
from entry.models import Cart
from entry.models import Admin
