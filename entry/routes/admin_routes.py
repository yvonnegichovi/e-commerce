from flask import render_template, redirect, url_for, flash, request, session
from entry.forms import AdminRegisterForm, AdminLoginForm, ProductForm, CategoryForm
from entry import db, app, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import logging
from entry.models import Admin, Product, Category, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename
import os

from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Set of allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Add it to your app configuration if necessary
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS



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
@login_required
@admin.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()

    categories = Category.query.all()

    if form.validate_on_submit():
        print("FORM VALIDATED SUCCESSFULLY.....")
        # Retrieve form data
        product_name = form.product_name.data
        description = form.description.data
        category_id = form.category.data
        price = form.price.data
        stock = form.stock.data
        is_starred = form.is_starred.data

        # Handle image upload
        image_file = form.image.data
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)  # Save the uploaded image to the upload folder

            image_url = os.path.join('static/uploads', filename)  # Relative URL for the image
        else:
            image_url = None  # Handle case where no image is uploaded

        # Create new product instance
        new_product = Product(
            product_name=product_name,
            description=description,
            category_id=category_id,
            price=price,
            stock=stock,
            image=image_url,  # Store image filename in the database
            is_starred=is_starred
        )

        # Add and commit to the database
        try:
            # Add and commit to the database
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            print(f"Error saving product to the database: {e}")
            flash('There was an error adding the product. Please try again.', 'danger')

        return redirect(url_for('admin.admin_dashboard'))

    else:
        # Debugging - print any form validation errors
        print("Form did not validate.")
        print(form.errors)

    return render_template('admin/add_product.html', form=form, categories=categories)

# Route to add new category
@login_required
@admin.route('/add_category', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            # Create new category object from form data
            new_category = Category(name=form.name.data.strip())
            # Add to the database session and commit
            db.session.add(new_category)
            db.session.commit()
            flash(f"Category '{new_category.name}' added successfully!", 'success')
            return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding category: {str(e)}", 'error')

    return render_template('admin/add_category.html', form=form)


@login_required
@admin.route('/admin/edit-product')
def edit_product():
    # Logic for editing product
    return render_template('edit_product.html')


@login_required
@admin.route('/admin/delete-product')
def delete_product():
    # Logic for deleting product
    return redirect(url_for('admin.admin_dashboard'))


@login_required
@admin.route('/admin/edit-category')
def edit_category():
    # Logic for editing product
    return render_template('edit_category.html')

@login_required
@admin.route('/admin/delete-category')
def delete_category():
    # Logic for deleting product
    return redirect(url_for('admin.admin_dashboard'))

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
