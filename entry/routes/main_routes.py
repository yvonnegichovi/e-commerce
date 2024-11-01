from flask import Blueprint, render_template, flash, redirect, url_for, jsonify

from entry.models import Product


main = Blueprint('main', __name__)

@main.route('/')
def home():
    products = Product.query.all()
    starred_products = Product.query.filter_by(is_starred=True).all()

    return render_template('home.html', title=home, products=products, starred_products=starred_products)
