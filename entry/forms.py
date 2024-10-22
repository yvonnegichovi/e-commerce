from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateTimeField, FloatField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, Optional, ValidationError, NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Full Names', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Contact Number', validators=[DataRequired(),
                                 Regexp(r'^[0-9]{10}$',
                                 message='Please enter a valid 10-digit phone number')])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class AdminRegisterForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class ProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[('electronics', 'Electronics'), ('beauty', 'Beauty'), ('clothing', 'Clothing')], validators=[DataRequired()])
    price = DecimalField('Price (KES)', validators=[DataRequired()])
    description = TextAreaField('Description')
    stock = IntegerField('Stock', validators=[DataRequired()])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    is_starred = BooleanField('Starred Product')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
