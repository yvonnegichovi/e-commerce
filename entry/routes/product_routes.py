from flask import Blueprint, render_template, flash, redirect, url_for, request
from entry.forms import RegistrationForm, LoginForm
from entry.models import User, Product, Admin
from entry.forms import ProductForm
from entry import app, db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import logging


product = Blueprint('product', __name__)

@product.route('/dashboard')
def dashboard():
    products = Product.query.all()
    starred_products = Product.query.filter_by(is_starred=True).all()

    return render_template('dashboard.html', products=products, starred_products=starred_products)


@product.route('/product/<int:product_id>')
def product_detail(product_id):
    # Retrieve the prodduct from the database by ID
    product = Product.query.get_or_404(product_id)
    category_products = Product.query.filter_by(category_id=product.category_id).filter(Product.id != product_id).limit(5).all()
    return render_template('products/product_detail.html', category_products=category_products, product=product)

# Adds to the cart

