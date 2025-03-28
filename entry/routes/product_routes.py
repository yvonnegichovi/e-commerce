from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from entry.forms import RegistrationForm, LoginForm
from entry.models import User, Product, Admin, Wishlist, CartList
from entry.forms import ProductForm
from entry import app, db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import quote
import logging


product = Blueprint('product', __name__)

@product.route('/dashboard')
@login_required
def dashboard():
    """ Fetches information for the dashboard """
    products = Product.query.all()
    starred_products = Product.query.filter_by(is_starred=True).all()
    flash("You are now in the dashboard. Yeeeeih!!!", "success")

    return render_template('dashboard.html', products=products, starred_products=starred_products)


@product.route('/product/<int:product_id>')
@login_required
def product_detail(product_id):
    """ Retrieves product details and displays it"""
    product = Product.query.get_or_404(product_id)
    category_products = Product.query.filter_by(category_id=product.category_id).filter(Product.id != product_id).limit(5).all()
    return render_template('products/product_detail.html', category_products=category_products, product=product)


@product.route('/wishlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    """Adds a product to a user wishlist"""
    product = Product.query.get_or_404(product_id)

    # Check if the product is already in the user's wishlist
    existing_entry = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing_entry:
        return {"message": "Product already in your wishlist!", "status": "info"}, 200
    else:
        # Create a new Wishlist entry
        wishlist_entry = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_entry)
        db.session.commit()
        return {"message": "Product added to your wishlist!", "status": "success"}, 200

    return jsonify(response)


@product.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    data = request.get_json()
    cart_id = data.get('cart_id')
    new_quantity = data.get('quantity')

    if not data or 'cart_id' not in data or 'quantity' not in data:
        return jsonify({'success': False, 'error': 'Invalid input data.'}), 400

    if new_quantity <= 0:
        return jsonify({'success': False, 'error': 'Quantity must be greater than 0.'}), 400

    cart_item = CartList.query.get_or_404(cart_id)
    cart_item.quantity = new_quantity
    db.session.commit()

    product_price = cart_item.product.price
    total_price = sum(item.product.price * item.quantity for item in CartList.query.filter_by(user_id=current_user.id).all())

    return jsonify({
        'success': True,
        'product_price': product_price,
        'product_name': cart_item.product.product_name,
        'total_price': total_price
    })


@product.route('/wishlist/<user_id>', methods=['GET', 'POST'])
@login_required
def view_wishlist(user_id):
    """Displays a user's Wishlist page"""
    wishlist_products = Wishlist.query.filter_by(user_id=user_id).all()
    user = User.query.filter_by(id=user_id).first()
    return render_template('/products/view_wishlist.html', wishlist_products=wishlist_products, user=user)


@product.route('/wishlist/remove/<int:wishlist_id>', methods=['POST'])
@login_required
def remove_from_wishlist(wishlist_id):
    try:
        wishlist_item = Wishlist.query.get(wishlist_id)
        if not wishlist_item:
            return jsonify({'status': 'error', 'message': 'Item not found'}), 404

        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Item removed successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to remove item', 'error': str(e)}), 500


@product.route('/cart/add/<int:product_id>', methods=['POST', 'GET'])
@login_required
def add_to_cart(product_id):
    """
    Adds a product into the cart
    """
    product = Product.query.get_or_404(product_id)

    data = request.get_json()
    quantity = int(data.get('quantity', 0))

    if quantity is None or quantity <= 0:
        flash("Please provide a valid quantity!", "danger")

    existing_entry = CartList.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing_entry:
        existing_entry.quantity += quantity
        db.session.commit()
        flash(f"Updated the quantity of '{product.product_name}' in your cart!", "success")
        return redirect(url_for('product.product_detail', product_id=product_id))
    else:
        cart_item=CartList(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
        db.session.commit()
        flash("Product successfully added to your Cart!", "success")
        return redirect(url_for('product.product_detail', product_id=product_id))

    return redirect(url_for('product.product_detail', product_id=product_id))


@product.route('/cart/<user_id>', methods=['GET'])
@login_required
def view_cartlist(user_id):
    cartlist_products = CartList.query.filter_by(user_id=user_id).all()

    # Calculate total price
    total_price = sum(item.product.price * item.quantity for item in cartlist_products)

    user = User.query.filter_by(id=user_id).first()
    return render_template(
        '/products/view_cartlist.html', 
        cartlist_products=cartlist_products, 
        user=user, 
        total_price=total_price
    )

@product.route('/cartlist/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    """
    Removes an item from the cart by its ID
    """
    print("YOU CAN NOW DELETE ITEMS")
    try:
        cart_item = CartList.query.filter_by(id=cart_id).first()
        if not cart_item:
            return jsonify({'status': 'error', 'message': 'Item not found'}), 404
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to remove item', 'error': str(e)}), 500


@product.route('/categories/<int:category_id>')
def list_by_category(category_id):
    """
    Lists products in a specific category.
    """
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category.id).all()
    print(f"FETCHED {category.name} SUCESSFULLY")
    return render_template('product/list_by_category.html', category=category, products=products)
