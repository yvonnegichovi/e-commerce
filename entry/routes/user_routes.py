from flask import Blueprint, render_template, flash, redirect, url_for, request
from entry.forms import RegistrationForm, LoginForm
from entry.models import User
from entry import app, db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import logging
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password_hash=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        )
        print('new account created')
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            print("Login successful")
            flash('Logged in successfully', 'success')
            return redirect(url_for('product.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', title='Login', form=form)

# User logout route
@login_required
@auth.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('auth.login'))
