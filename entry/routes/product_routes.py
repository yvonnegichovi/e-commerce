from flask import Blueprint, render_template, flash, redirect, url_for, request
from entry.forms import RegistrationForm, LoginForm
from entry.models import User, Product, Admin
from entry.forms import ProductForm
from entry import app, db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import logging


product = Blueprint('product', __name__)

@login_required
@product.route('/dashboard')
def dashboard():
    """ Fetches information for the dashboard """
    products = Product.query.all()
    starred_products = Product.query.filter_by(is_starred=True).all()

    return render_template('dashboard.html', products=products, starred_products=starred_products)


@login_required
@product.route('/product/<int:product_id>')
def product_detail(product_id):
    """ Retrieves product details and displays it"""
    product = Product.query.get_or_404(product_id)
    category_products = Product.query.filter_by(category_id=product.category_id).filter(Product.id != product_id).limit(5).all()
    return render_template('products/product_detail.html', category_products=category_products, product=product)


@login_required
@product.route('/wishlist/add/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    """Adds a product to a user wishlist"""
    product = Produst.query.get_or_404(product_id)

    if product.status == "wishlist":
        flash("Product already in your wishlist! Click Cart to purchase", "info")
    else:
        product.status == 'wishlist'
        db.session.commit()
        flash('Product added to your wishlist! Click Cart to purchase', 'success')

    return redirect(url_for('product.view_wishlist'), user_id=current_user.id)


@login_required
@product.route('/wishlist/<int:user_id>', methods=['GET', 'POST'])
def view_wishlist(user_id):
    """Displays a user's Wishlist page"""
    wishlist_products = Product.query.filter_by(status="wishlist", user_id=user_id).all()
    return render_template('/products/view_wishlist', wishlist_products=wishlist_products)
