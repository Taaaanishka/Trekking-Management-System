from app import app
from extensions import db
from models import User

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(email="admin@trek.com").first()

    if admin is None:
        admin = User(
            name="Admin",
            email="admin@trek.com",
            password="admin123",
            role="admin",
            approved=True,
            blacklisted=False
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully!")

    else:
        print("Admin already exists!")

    print("Database created successfully!")