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
import functools
from functools import wraps

from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Set of allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Add it to your app configuration if necessary
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(func):
    """
    Custom decorator to handle redirection based on whether the user is an admin or not
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        print(f"admin: {current_user.is_authenticated}, ID: {current_user.get_id()}")
        if not current_user.is_authenticated:
            flash('You need to log in as an admin to access this page.', 'warning')
            print("ADMIN IS NOT AUTHENTICATED")
            return redirect(url_for('admin.admin_login'))
        elif not isinstance(current_user._get_current_object(), Admin):  # Ensure user is an Admin
            flash('Admin access only.', 'danger')
            return redirect(url_for('auth.login'))
        print("ADMIN AUTHENTICATED")
        return func(*args, **kwargs)
    return decorated_view


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
            print(f"Logged in as admin: {current_user.is_authenticated}, ID: {current_user.get_id()}")
            return redirect(url_for('admin.dashboard'))
        else:
            print("COULD NOT LOGIN FOR SOME REASON")
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('admin.admin_login'))

    return render_template('admin/login.html', title='Admin Login', form=form)

# Admin logout route
@admin.route('/logout')
@login_required
def admin_logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('admin.admin_login'))

# Admin dashboard route
@admin.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')


# List all products
@admin.route('/products', methods=['GET'])
@login_required
def list_products():
    products =  Product.query.all()
    starred_products = Product.query.filter_by(is_starred=True).all()

    return render_template('admin/list.html', products=products, starred_products=starred_products)


# Route to add new product
@admin.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = Category.query.all()
    print(f" Admin authenticated: {current_user.is_authenticated}")
    print(f"Admin ID: {current_user.id}")

    if not current_user.is_authenticated or not isinstance(current_user.id, Admin):
        flash('You need to be logged in to add a product.', 'warning')
        return redirect(url_for('admin.admin_login'))

    # Check if it's a POST request
    if request.method == 'POST':
        # Retrieve form data directly from request
        product_name = request.form.get('product_name')
        description = request.form.get('description')
        more_details = request.form.get('more_details')
        category_id = request.form.get('category')
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        is_starred = request.form.get('is_starred') == 'on'

        # Handle image upload
        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)  # Save the uploaded image to the upload folder

            image_url =  f'uploads/{filename}'  # Save relative path # Relative URL for the image
        else:
            image_url = None  # Handle case where no image is uploaded

        # Check if current_user.id is set
        """if not current_user.is_authenticated or not current_user.id:
            flash('You need to be logged in to add a product.', 'warning')
            return redirect(url_for('admin.admin_login'))"""

        # Create new product instance
        new_product = Product(
            product_name=product_name,
            description=description,
            more_details=more_details,
            category_id=category_id,
            price=price,
            stock=stock,
            user_id=current_user.id,
            status='unordered',
            image=image_url,  # Store image filename in the database
            is_starred=is_starred
        )

        # Add and commit to the database
        try:
            db.session.add(new_product)
            db.session.commit()
            print("PRODUCT SUCCESSFULLY ADDED")
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin.list_products'))
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            print(f"Error saving product to the database: {e}")
            flash('There was an error adding the product. Please try again.', 'danger')

    return render_template('admin/add_product.html', categories=categories)


# Route to add new category
@admin.route('/add_category', methods=['GET', 'POST'])
@login_required
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
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding category: {str(e)}", 'error')

    return render_template('admin/add_category.html', form=form)


@admin.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    # Retrieve the product from the database
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        # Update product details
        product.product_name = request.form['product_name']
        product.description = request.form['description']
        product.more_details= request.form['more_details']
        product.price = request.form['price']
        product.stock = request.form['stock']

        # Update is_starred status
        product.is_starred = 'is_starred' in request.form

        # Handle image upload if a new image is provided
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save the new image
            file.save(file_path)

            # Update the product image path
            product.image = f'uploads/{filename}'  # Save relative path

        # Save the updated product to the database
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.list_products'))  # Redirect to the dashboard after updating

    # Render the edit form with the current product details
    return render_template('admin/edit_product.html', product=product)


@admin.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)

    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    else:
        flash('Product not found.', 'danger')

    return redirect(url_for('admin.list_products'))


@admin.route('/edit-category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """
    Editing a category
    """
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        """
        Update category details from the form
        """
        category.name = request.form.get('name')
        category.description = request.form.get('description')

        """Commit updates to the database"""
        try:
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin.list_categories'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating the category. Please try again', 'danger')
    return render_template('admin/edit_category.html', category=category)

@admin.route('/delete-category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    """
    Deletes a category
    """
    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        flash('Category successfully deleted', 'success')
    else:
        flash('Could not find the category', 'danger')
    return redirect(url_for('admin.list_categories'))


@admin.route('/categories')
@login_required
def list_categories():
    """
    Lists the categories lists
    """
    categories = Category.query.all()
    return render_template('admin/categories_list.html', categories=categories)

# Route to view user wishlists
@admin.route('/view_wishlists')
@login_required
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
