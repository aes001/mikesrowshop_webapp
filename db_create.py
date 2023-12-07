from config import SQLALCHEMY_DATABASE_URI
from app import db
import os.path

db.create_all()

CREATE_ADMIN = True
# Create a default user
if CREATE_ADMIN:
    from app.models import Users, addresses, payment_details
    from app import bcrypt
    user = Users(username='admin', first_name='admin', last_name='admin', password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'))
    db.session.add(user)
    db.session.commit()
    address = addresses(owner_id=user.id, street_address1='123 Main St', street_address2='Apt 1', city='New York', zip_code='12345', country='USA', active=True)
    db.session.add(address)
    payment = payment_details(owner_id=user.id, card_number='1234567890', card_name='John Doe', card_exp='01/01', card_cvv='123', active=True)
    db.session.add(payment)
    db.session.commit()