from flask import render_template, redirect, url_for, flash, request, session
from entry.forms import AdminRegisterForm, AdminLoginForm
from entry import db, app, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import logging
from entry.models import Admin, Product, Category, User
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('register_admin', methods=['GET', 'POST'])
def register_admin():
    form = AdminRegisterForm()
    if form.validate_on_submit():
        existing_admin = Admin.query.filter_by(email=form.email.data).first()
        if existing_admin:
            flash('Email address already exists', 'danger')
            return redirect(url_for('admin.register_admin'))
        new_admin = Admin(
            username = form.username.data,
            email = form.email.data,
            password_hash=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        )

        """if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('admin.register_admin'))"""

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Admin account created successfully!', 'success')
            return redirect(url_for('admin.admin_login'))
        except:
            db.session.rollback()
            flash('An error occurred while creating the admin account.', 'danger')

    return render_template('admin/register_admin.html', form=form)

# Admin login route
@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        # Verify admin credentials
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and bcrypt.check_password_hash(admin.password_hash, form.password.data):
            login_user(admin, remember=form.remember.data)
            flash('Successfully logged in as admin.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            print("COULD NOT LOGIN FOR SOME REASON")
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('admin.admin_login'))

    return render_template('admin/login.html', title='Admin Login', form=form)

# Admin logout route
@login_required
@admin.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('admin.admin_login'))

# Admin dashboard route
@login_required
@admin.route('/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin dashboard.', 'danger')
        return redirect(url_for('admin.admin_login'))
    
    # Fetch data for the dashboard
    products_count = Product.query.count()
    categories_count = Category.query.count()
    users_count = User.query.count()
    wishlists_count = Wishlist.query.count()
    carts_count = Cart.query.count()

    return render_template('admin/dashboard.html', 
                           products_count=products_count,
                           categories_count=categories_count,
                           users_count=users_count,
                           wishlists_count=wishlists_count,
                           carts_count=carts_count)

# Route to add new product
@admin.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin_logged_in'):
        flash('Please log in to add a product.', 'danger')
        return redirect(url_for('admin.admin_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category_id')

        new_product = Product(name=name, description=description, price=price, category_id=category_id)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

# Route to add new category
@admin.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if not session.get('admin_logged_in'):
        flash('Please log in to add a category.', 'danger')
        return redirect(url_for('admin.admin_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_category.html')

# Route to view user wishlists
@admin.route('/view_wishlists')
def view_wishlists():
    if not session.get('admin_logged_in'):
        flash('Please log in to view user wishlists.', 'danger')
        return redirect(url_for('admin.admin_login'))

    wishlists = Wishlist.query.all()
    return render_template('admin/view_wishlists.html', wishlists=wishlists)

# Route to view user carts
@admin.route('/view_carts')
def view_carts():
    if not session.get('admin_logged_in'):
        flash('Please log in to view user carts.', 'danger')
        return redirect(url_for('admin.admin_login'))

    carts = Cart.query.all()
    return render_template('admin/view_carts.html', carts=carts)
