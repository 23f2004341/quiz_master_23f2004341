from app import app
from extensions import db, bcrypt
from models import User
from datetime import date

with app.app_context():
    db.create_all()
    # predefined admin account
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
        admin = User(
            email="admin@123.com",
            password=hashed_password,
            full_name="Quiz Master",
            role="admin",
            qualification="N/A",
            dob=date(1990, 1, 1)
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin account created: gmail:admin@gmail.com and password:admin123")
    else:
        print("Admin account already exists.")
    print("Database created successfully!")
"""this  creates the database and the admin account if it does not exist. and also hassed the password for the admin account and others when created as well"""