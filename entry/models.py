from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from entry import db, login_manager
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


@login_manager.user_loader
def load_user(user_id):
    try:
        print(f"Loading user with ID:{user_id}")
        """ First, try loading as an Admin"""
        user = Admin.query.filter_by(id=str(user_id)).first()
        if user:
            print(f"Loaded Admin: {user}")
            return user
        user = User.query.filter_by(id=str(user_id)).first()
        if user:
            """ If not an Admin, try loading as a regular User"""
            print(f"This is the user id:{user.id}")
            return user

        print("No user found")
        return None
    except ValueError:
        print("Invalid user ID format")
        return None

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    wishlists = db.relationship('Wishlist', back_populates='user', lazy=True)
    cart_items = db.relationship('CartList', back_populates='user', lazy=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

    def __str__(self):
        return f"User('{self.name}', '{self.email}', '{self.password_hash}')"


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    more_details = db.Column(db.String(1000), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_starred = db.Column(db.Boolean, default=False)

    # Foreign key to Category
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # Relationships
    category = db.relationship('Category', back_populates='products')
    wishlists = db.relationship('Wishlist', back_populates='product', lazy=True)
    cart_items = db.relationship('CartList', back_populates='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.product_name}>"

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=True)

    # Relationships
    products = db.relationship('Product', back_populates='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # Relationships
    product = db.relationship('Product', back_populates='wishlists')
    user = db.relationship('User', back_populates='wishlists')

    def __repr__(self):
        return f"<Wishlist id={self.id}, product_id={self.product_id}, user_id={self.user_id}>"

class CartList(db.Model):
    __tablename__ = 'cartlists'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    product = db.relationship('Product', back_populates='cart_items')
    user = db.relationship('User', back_populates='cart_items')

    def __repr__(self):
        return f"<CartList id={self.id}, product_id={self.product_id}, user_id={self.user_id}, quantity={self.quantity}>"

