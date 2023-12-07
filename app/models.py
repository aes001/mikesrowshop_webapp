from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    orders = db.relationship('orders', backref='buyer',
                             lazy=True, uselist=False)
    items = db.relationship('items', backref='seller',
                            lazy=True, uselist=False)
    addresses = db.relationship(
        'addresses', backref='owner', lazy=True, uselist=False)
    payments = db.relationship(
        'payment_details', backref='owner', lazy=True, uselist=False)

    def __repr__(self):
        return f"users('{self.username}', '{self.first_name}', '{self.last_name}')"


class addresses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    street_address1 = db.Column(db.String(20), nullable=False)
    street_address2 = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"addresses('{self.id}', '{self.owner_id}', '{self.street_address1}', '{self.street_address2}', '{self.city}', '{self.zip_code}', '{self.country}', '{self.active}')"


class payment_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_number = db.Column(db.String(20), nullable=False)
    card_name = db.Column(db.String(20), nullable=False)
    card_exp = db.Column(db.String(20), nullable=False)
    card_cvv = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"payment_details('{self.id}', '{self.owner_id}', '{self.card_number}', '{self.card_name}', '{self.card_exp}', '{self.card_cvv}', '{self.active}')"


class items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(50), nullable=False)
    shipping_method = db.Column(db.String(20), nullable=False)
    shipping_price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    active = db.Column(db.Boolean)

    def __repr__(self):
        return f"items('{self.id}', '{self.seller_id}', '{self.name}', '{self.price}', '{self.description}', '{self.image}', '{self.category}', '{self.stock_quantity}', '{self.shipping_method}', '{self.active}')"


class cart_items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"cart_items('{self.id}', '{self.owner_id}', '{self.item_id}', '{self.quantity}', '{self.active}')"

# Many to Many relationship between items and users
# This is the join table
# A user can purchase many items
# An item can be purchased by many users


class orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quantity = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"orders('{self.id}', '{self.item_id}', '{self.buyer_id}', '{self.quantity}', '{self.date}')"
