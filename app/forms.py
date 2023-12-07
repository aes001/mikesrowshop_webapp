from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo, ValidationError, InputRequired
from app.models import Users
from flask_wtf.file import FileField, FileAllowed


class loginForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=1, max=64)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=1, max=64)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class registerForm(FlaskForm):
    # Register Personal
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=1, max=64)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=1, max=64)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), Length(min=1, max=64), EqualTo('password')])
    first_name = StringField('First Name', validators=[
                             DataRequired(), Length(min=1, max=64)])
    last_name = StringField('Last Name', validators=[
                            DataRequired(), Length(min=1, max=64)])

    # Register Address
    street = StringField('Street', validators=[
                         DataRequired(), Length(min=1, max=64)])
    street2 = StringField('Street 2', validators=[
                          DataRequired(), Length(min=1, max=64)])
    city = StringField('City', validators=[
                       DataRequired(), Length(min=1, max=64)])
    zip = StringField('Zip', validators=[
                      DataRequired(), Length(min=1, max=64)])
    country = StringField('Country', validators=[
                          DataRequired(), Length(min=1, max=64)])

    # Register Payment
    card_number = StringField('Card Number', validators=[
                              DataRequired(), Length(min=1, max=64)])
    card_name = StringField('Card Name', validators=[
                            DataRequired(), Length(min=1, max=64)])
    card_exp = StringField('Card Expiration', validators=[
                           DataRequired(), Length(min=1, max=64)])
    card_cvv = StringField('Card CVV', validators=[
                           DataRequired(), Length(min=1, max=64)])

    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')


class sellItemForm(FlaskForm):
    name = StringField('Name', validators=[
                       DataRequired(), Length(min=1, max=64)])
    price = DecimalField('Price', validators=[
                         InputRequired(), NumberRange(min=0, max=1000000000000000)])
    description = StringField('Description', validators=[
                              DataRequired(), Length(min=1, max=64)])
    category = StringField('Category', validators=[
                           DataRequired(), Length(min=1, max=64)])
    location = StringField('Location', validators=[
                           DataRequired(), Length(min=1, max=64)])
    stock_quantity = IntegerField('Stock Quantity', validators=[
                                  DataRequired(), NumberRange(min=0, max=1000000000000000)])
    shipping_method = StringField('Shipping Method', validators=[
                                  DataRequired(), Length(min=1, max=64)])
    shipping_price = DecimalField('Shipping Price', validators=[
                                  InputRequired(), NumberRange(min=0, max=1000000000000000)])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Sell')

    def validate_category(self, category):
        category_d = category.data.lower()
        if category_d != 'boat' and category_d != 'training equipment' and category_d != 'oar' and category_d != 'other':
            raise ValidationError(
                'That is not a valid category. Please choose either "Boat", "Training Equipment", "Oar", or "Other".')


class editAccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[
                             DataRequired(), Length(min=1, max=64)])
    last_name = StringField('Last Name', validators=[
                            DataRequired(), Length(min=1, max=64)])
    street = StringField('Street', validators=[
                         DataRequired(), Length(min=1, max=64)])
    street2 = StringField('Street 2', validators=[
                          DataRequired(), Length(min=1, max=64)])
    city = StringField('City', validators=[
                       DataRequired(), Length(min=1, max=64)])
    zip = StringField('Zip', validators=[
                      DataRequired(), Length(min=1, max=64)])
    country = StringField('Country', validators=[
                          DataRequired(), Length(min=1, max=64)])
    card_number = StringField('Card Number', validators=[
                              DataRequired(), Length(min=1, max=64)])
    card_name = StringField('Card Name', validators=[
                            DataRequired(), Length(min=1, max=64)])
    card_exp = StringField('Card Expiration', validators=[
                           DataRequired(), Length(min=1, max=64)])
    card_cvv = StringField('Card CVV', validators=[
                           DataRequired(), Length(min=1, max=64)])
    submit = SubmitField('Save')
