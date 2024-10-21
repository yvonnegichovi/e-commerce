from flask import render_template, redirect, url_for, flash, request, session
from entry.forms import AdminRegisterForm, AdminLoginForm, ProductForm
from entry import db, app, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import logging
from entry.models import Admin, Product, Category, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            print("YOU ARE OFFICIALLY LOGGED IN")
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
    products =  Product.query.all()
    starred_products = Product.query.filter_by(is_starred=True).all()

    return render_template('admin/dashboard.html', products=products, starred_products=starred_products)


# Route to add new product
@admin.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        product_name = form.product_name.data
        category = form.category.data
        price = form.priice.data
        description = form.description.data
        stock = form.stock.data
        image = form.image.data

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
        else:
            image_path = None

        new_product = Product(
            product_name=product_name,
            category=category,
            price=price,
            description=description,
            stock=stock,
            image=image_path
        )
        db.session.add(new_product)
        db.session.commit()

        flask('Product added successfuly!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/add_product.html', form=form)

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
