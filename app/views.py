from app import app, db, bcrypt
import secrets
import os
import json
from PIL import Image
from app.models import Users, addresses, payment_details, items, orders, cart_items
from flask import render_template, url_for, redirect, flash, request
from app.forms import loginForm, registerForm, sellItemForm, editAccountForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    # Get all items from the database
    items_list = items.query.all()
    items_seller_list = []

    # Get the seller for each item
    for item in items_list:
        items_seller_list.append((Users.query.get(item.seller_id)))

    # Get the current user if they are logged in
    if current_user.is_authenticated:
        user = Users.query.get(current_user.id)
    else:
        user = None

    return render_template('home_template.html', title='Home', items=zip(items_list, items_seller_list), current_user=current_user, user_logged_in=current_user.is_authenticated, user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()
    if current_user.is_authenticated:
        return redirect(url_for('my_account'))
    else:
        if form.validate_on_submit():
            user = Users.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                flash('You have been logged in!', 'success')

                # If the user was redirected to the login page, redirect them back to where they were
                next = request.args.get('next')

                return redirect(next) if next else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
                return redirect(url_for('login'))
        return render_template('login_template.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = editAccountForm()
    if form.validate_on_submit():
        # Update the user's information
        # Sorry this is so ugly
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.addresses.street_address1 = form.street.data
        current_user.addresses.street_address2 = form.street2.data
        current_user.addresses.city = form.city.data
        current_user.addresses.zip_code = form.zip.data
        current_user.addresses.country = form.country.data
        current_user.payments.card_number = form.card_number.data
        current_user.payments.card_name = form.card_name.data
        current_user.payments.card_exp = form.card_exp.data
        current_user.payments.card_cvv = form.card_cvv.data
        db.session.commit()
        flash(f'Account updated successfully', 'success')
        return redirect(url_for('my_account'))
    elif request.method == 'GET':
        # Populate the form with the user's current information
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.street.data = current_user.addresses.street_address1
        form.street2.data = current_user.addresses.street_address2
        form.city.data = current_user.addresses.city
        form.zip.data = current_user.addresses.zip_code
        form.country.data = current_user.addresses.country
        form.card_number.data = current_user.payments.card_number
        form.card_name.data = current_user.payments.card_name
        form.card_exp.data = current_user.payments.card_exp
        form.card_cvv.data = current_user.payments.card_cvv

    return render_template('account_template.html', title='My Account', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = registerForm()
    if current_user.is_authenticated:
        return redirect(url_for('my_account'))
    else:
        if form.validate_on_submit():
            # Hash the password
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            
            # Create the user
            user = Users(username=form.username.data, first_name=form.first_name.data,
                         last_name=form.last_name.data, password_hash=hashed_password)
            db.session.add(user)

            # Commit the user to the database so that we can get their id
            db.session.commit()

            # Create the user's address and payment details
            address = addresses(owner_id=user.id, street_address1=form.street.data, street_address2=form.street2.data,
                                city=form.city.data, zip_code=form.zip.data, country=form.country.data, active=True)
            db.session.add(address)
            payment = payment_details(owner_id=user.id, card_number=form.card_number.data, card_name=form.card_name.data,
                                      card_exp=form.card_exp.data, card_cvv=form.card_cvv.data, active=True)
            db.session.add(payment)
            db.session.commit()
            flash(
                f'Account created for {form.username.data}! You may now login', 'success')
            return redirect(url_for('home'))
        return render_template('register_template.html', title='Register', form=form)


# This is a function to save the picture to the filesystem
# Uses the secrets module to generate a random hex for the filename
# to prevent filename collisions
def process_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    new_picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', new_picture_fn)

    # Resize the image before saving
    image_resized = Image.open(form_picture)

    # Crop the image to a square from the center
    width, height = image_resized.size
    if width > height:
        image_resized = image_resized.crop(
            ((width - height) / 2, 0, (width + height) / 2, height))
    elif height > width:
        image_resized = image_resized.crop(
            (0, (height - width) / 2, width, (height + width) / 2))

    output_size = (500, 500)
    image_resized.thumbnail(output_size)
    image_resized.save(picture_path)

    return new_picture_fn


@app.route('/sell_item', methods=['GET', 'POST'])
@login_required
def sell_item():
    form = sellItemForm()
    if form.validate_on_submit():
        # Check if the user uploaded a picture
        if form.image.data:
            picture_file = process_picture(form.image.data)
            item = items(seller_id=current_user.id, name=form.name.data, price=form.price.data, description=form.description.data, category=form.category.data, location=form.location.data,
                         stock_quantity=form.stock_quantity.data, shipping_method=form.shipping_method.data, shipping_price=form.shipping_price.data, image=picture_file, active=True)
        else:
            # If the user didn't upload a picture, use the default
            item = items(seller_id=current_user.id, name=form.name.data, price=form.price.data, description=form.description.data, category=form.category.data,
                         location=form.location.data, stock_quantity=form.stock_quantity.data, shipping_method=form.shipping_method.data, shipping_price=form.shipping_price.data, active=True)
        db.session.add(item)
        db.session.commit()
        flash(f'Item created for {form.name.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('sell_item_template.html', title='Sell Item', form=form)


@app.route('/my_cart')
@login_required
def my_cart():
    user_id = current_user.id
    items_in_cart = cart_items.query.filter_by(owner_id=user_id).all()
    products = []

    # Get the products in the user's cart for display
    for item in items_in_cart:
        products.append(items.query.get(item.item_id))
    user = Users.query.filter_by(id=user_id).first()

    # Get the sub total for each item in the cart (price * quantity + shipping price)
    sub_total = []
    for item in products:
        sub_total.append(item.price * cart_items.query.filter_by(owner_id=user_id,
                         item_id=item.id).first().quantity + item.shipping_price)
        
    # Get the number of products in the cart so we know if we should have a checkout button
    products_len = len(products)

    return render_template('cart_template.html', title='My Cart', user=user, items_in_cart=zip(items_in_cart, products, sub_total), total=sum(sub_total), products_len=products_len)


@app.route('/add_to_basket', methods=['POST', 'GET'])
@login_required
def add_to_cart():
    if request.is_json:
        item_id = json.loads(request.data).get("item_id")
        user_id = json.loads(request.data).get("user_id")

        # Check that the item exists
        item = items.query.get(item_id)
        if not item:
            return {'success': False}

        # Check that the item is not out of stock
        if item.stock_quantity <= 0:
            return {'success': False}

        # Check if the user has already added this item to their cart
        cart_item = cart_items.query.filter_by(
            owner_id=user_id, item_id=item_id).first()
        if cart_item:
            # If the user has already added this item to their cart, increment the quantity
            # Prevent the user from adding more than the stock quantity of the item
            if cart_item.quantity < item.stock_quantity:
                cart_item.quantity += 1
                db.session.commit()

            cart_item = cart_items.query.filter_by(
                owner_id=user_id, item_id=item_id).first()

            return {"success": True, "item_id": item_id, "quantity": cart_item.quantity}
        else:
            # If the user hasn't added this item to their cart, add it
            cart_item = cart_items(
                owner_id=user_id, item_id=item_id, quantity=1, active=True)
            db.session.add(cart_item)
            db.session.commit()
            cart_item = cart_items.query.filter_by(
                owner_id=user_id, item_id=item_id).first()
            return {"success": True, "item_id": item_id, "quantity": cart_item.quantity}

    else:
        return {'success': False}


@app.route('/remove_from_basket/<int:item_id>', methods=['POST', 'GET'])
@login_required
def remove_from_basket(item_id):
    user_id = current_user.id
    cart_item = cart_items.query.filter_by(
        owner_id=user_id, item_id=item_id).first()
    db.session.delete(cart_item)
    db.session.commit()

    return redirect(url_for('my_cart'))


@app.route('/checkout', methods=['POST', 'GET'])
@login_required
def checkout():
    user_id = current_user.id
    items_in_cart = cart_items.query.filter_by(owner_id=user_id).all()
    products = []

    # Get the products in the user's cart for display
    for cart_item in items_in_cart:
        products.append(items.query.get(cart_item.item_id))

    # Get the sub total for each item in the cart (price * quantity + shipping price)
    sub_total = []
    for product in products:
        sub_total.append(product.price * cart_items.query.filter_by(owner_id=user_id,
                         item_id=product.id).first().quantity + product.shipping_price)

    # Loop through every item in the cart
    for item in items_in_cart:
        # Loop through every item in the cart
        # Get the product
        # Subtract the stock quantity by the quantity in the cart
        product = items.query.get(item.item_id)
        product.stock_quantity -= item.quantity
        db.session.commit()

        # Create an order for the user
        order = orders(buyer_id=user_id, item_id=item.item_id,
                       quantity=item.quantity)
        db.session.add(order)
        db.session.commit()

        # Delete the item from the cart
        db.session.delete(item)
        db.session.commit()

    flash(f'Order placed successfully!', 'success')

    return redirect(url_for('home'))


@app.route('/my_orders')
@login_required
def view_orders():
    user_id = current_user.id
    orders_list = orders.query.filter_by(buyer_id=user_id).all()
    products = []

    # Get the products that the user has ordered
    for order in orders_list:
        products.append(items.query.get(order.item_id))

    # Get the seller for each product
    seller = []
    for product in products:
        seller.append(Users.query.get(product.seller_id))

    return render_template('view_orders_template.html', title='My Orders', items=zip(products, seller, orders_list))


@app.route('/my_products')
@login_required
def view_selling():
    user_id = current_user.id
    products = items.query.filter_by(seller_id=user_id).all()
    return render_template('view_selling_template.html', title='My Products', products=products)
