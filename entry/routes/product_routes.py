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
    return render_template('dashboard.html', products=products)
