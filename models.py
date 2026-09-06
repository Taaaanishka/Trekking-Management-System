from extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    approved = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)

    bookings = db.relationship("Booking", backref="user", lazy=True)
    treks = db.relationship("Trek", backref="staff", lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    duration = db.Column(db.Integer)

    available_slots = db.Column(db.Integer)

    status = db.Column(db.String(20), default="Pending")

    start_date = db.Column(db.Date)

    end_date = db.Column(db.Date)

    assigned_staff = db.Column(db.Integer,
                               db.ForeignKey("users.id"))

    bookings = db.relationship("Booking",
                               backref="trek",
                               lazy=True)


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    booking_date = db.Column(db.Date)

    status = db.Column(db.String(20), default="Booked")

    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.id"))

    trek_id = db.Column(db.Integer,
                        db.ForeignKey("treks.id"))


class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)

    phone = db.Column(db.String(15))

    address = db.Column(db.String(200))

    experience = db.Column(db.Integer)

    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.id"),
                        unique=True)