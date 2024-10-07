from flask import Blueprint, render_template, flash, redirect, url_for, request
from entry.forms import RegistrationForm
from entry.models import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html', title='Register', form=form)
