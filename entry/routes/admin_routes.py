from flask import render_template, redirect, url_for, flash, request, session
from entry import db, app
from entry.models import Admin, Product, Category, User, Wishlist, Cart
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Admin login route
@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verify admin credentials
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            flash('Successfully logged in as admin.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('admin/login.html')

# Admin logout route
@admin.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('admin.admin_login'))

# Admin dashboard route
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
