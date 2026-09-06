from datetime import date
from flask import Flask, render_template, request, redirect, url_for
from config import Config
from flask import session
from extensions import db
from functools import wraps
from flask import session, redirect

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

import models

def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        user = models.User.query.get(session["user_id"])

        if user.role != "admin":
            return redirect("/login")

        return f(*args, **kwargs)

    return wrapper

def staff_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        user = models.User.query.get(session["user_id"])

        if user.role != "staff":
            return redirect("/login")

        return f(*args, **kwargs)

    return wrapper


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        if session.get("role") != "user":
            return "Access Denied"

        return f(*args, **kwargs)

    return decorated_function

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin/view_bookings")
@admin_required
def view_bookings():

    bookings = models.Booking.query.all()

    return render_template(
        "admin/view_bookings.html",
        bookings=bookings
    )

@app.route("/admin/search", methods=["GET"])
@admin_required
def admin_search():

    query = request.args.get("query", "")

    users = models.User.query.filter(
        models.User.name.ilike(f"%{query}%")
    ).all()

    treks = models.Trek.query.filter(
        models.Trek.trek_name.ilike(f"%{query}%")
    ).all()

    return render_template(
        "admin/search.html",
        query=query,
        users=users,
        treks=treks
    )



@app.route("/staff/update_status/<int:trek_id>", methods=["GET", "POST"])
@staff_required
def update_trek_status(trek_id):

    trek = models.Trek.query.get_or_404(trek_id)

    # Ensure only the assigned staff can update this trek
    if trek.assigned_staff != session["user_id"]:
        return "Unauthorized", 403

    if request.method == "POST":
        trek.status = request.form["status"]
        db.session.commit()
        return redirect("/staff/dashboard")

    return render_template(
        "staff/update_status.html",
        trek=trek
    )



@app.route("/register", methods=["GET", "POST"])
def register():



    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        approved = False if role == "staff" else True

        new_user = models.User(
    name=name,
    email=email,
    password=password,
    role=role,
    approved=approved,
    blacklisted=False
)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

@app.route("/staff/my_treks")
def my_treks():

    staff = models.User.query.filter_by(role="staff", approved=True).first()

    treks = models.Trek.query.filter_by(assigned_staff=staff.id).all()

    return render_template(
        "staff/my_treks.html",
        treks=treks
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = models.User.query.filter_by(email=email).first()

        # Check email and password
        if not user or user.password != password:
            return "Invalid Email or Password"

        # Check if user is blacklisted
        if user.blacklisted:
            return "Your account has been blacklisted."

        # Staff must be approved before login
        if user.role == "staff" and not user.approved:
            return "Waiting for Admin Approval"

        # Create login session
        session["user_id"] = user.id
        session["role"] = user.role

        # Redirect according to role
        if user.role == "admin":
            return redirect("/admin/dashboard")

        elif user.role == "staff":
            return redirect("/staff/dashboard")

        elif user.role == "user":
            return redirect("/user/dashboard")

    return render_template("login.html")
@app.route("/admin/view_users")
@admin_required
def view_users():

    users = models.User.query.all()

    return render_template(
        "admin/view_users.html",
        users=users
    )

@app.route("/admin/blacklist/<int:user_id>")
@admin_required
def blacklist_user(user_id):

    user = models.User.query.get_or_404(user_id)

    # Prevent blacklisting the admin
    if user.role != "admin":
        user.blacklisted = True
        db.session.commit()

    return redirect("/admin/view_users")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    total_users = models.User.query.filter_by(role="user").count()

    total_staff = models.User.query.filter_by(role="staff").count()

    total_treks = models.Trek.query.count()

    total_bookings = models.Booking.query.count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings
    )


@app.route("/staff/dashboard")
@staff_required
def staff_dashboard():

    staff = models.User.query.get(session["user_id"])

    assigned_treks = models.Trek.query.filter_by(
        assigned_staff=staff.id
    ).all()

    return render_template(
        "staff/dashboard.html",
        staff=staff,
        assigned_treks=assigned_treks
    )

@app.route("/user/dashboard")
def user_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user = models.User.query.get(session["user_id"])

    bookings = models.Booking.query.filter_by(
        user_id=user.id
    ).all()

    return render_template(
        "user/dashboard.html",
        user=user,
        bookings=bookings
    )


@app.route("/user/view_treks", methods=["GET", "POST"])
def user_view_treks():

    if request.method == "POST":

        trek_id = request.form["trek_id"]

        trek = models.Trek.query.get(trek_id)

        if trek.available_slots <= 0:
            return "No Slots Available"

        existing_booking = models.Booking.query.filter_by(
            user_id=session["user_id"],
            trek_id=trek.id
        ).first()

        if existing_booking:
            return "You have already booked this trek."

        trek.available_slots -= 1

        booking = models.Booking(
    user_id=session["user_id"],
    trek_id=trek.id,
    booking_date=date.today(),
    status="Booked"
)

        db.session.add(booking)
        db.session.commit()

        return "Trek Booked Successfully!"

    treks = models.Trek.query.filter_by(status="Open").all()

    return render_template(
        "user/view_treks.html",
        treks=treks
    )

@app.route("/user/my_bookings")
@user_required
def my_bookings():

    bookings = models.Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "user/my_bookings.html",
        bookings=bookings
    )

@app.route("/user/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):

    booking = models.Booking.query.get(booking_id)

    if booking:

        trek = models.Trek.query.get(booking.trek_id)

        trek.available_slots += 1

        booking.status = "Cancelled"

        db.session.commit()

    return redirect("/user/my_bookings")




@app.route("/admin/approve/<int:user_id>")
@admin_required
def approve_staff(user_id):

    staff = models.User.query.get(user_id)

    if staff:
        staff.approved = True
        db.session.commit()

    return redirect("/admin/staff")



@app.route("/admin/create_trek", methods=["GET", "POST"])
@admin_required
def create_trek():

    if request.method == "POST":

        trek_name = request.form["trek_name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = request.form["duration"]
        slots = request.form["slots"]

        new_trek = models.Trek(
            trek_name=trek_name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=slots
        )

        db.session.add(new_trek)
        db.session.commit()

        return "Trek Created Successfully!"

    return render_template("admin/create_trek.html")

@app.route("/admin/view_treks")
@admin_required
def view_treks():

    treks = models.Trek.query.all()

    return render_template(
        "admin/view_treks.html",
        treks=treks
    )

@app.route("/admin/edit_trek/<int:trek_id>", methods=["GET", "POST"])
@admin_required
def edit_trek(trek_id):

    trek = models.Trek.query.get(trek_id)

    if request.method == "POST":

        trek.trek_name = request.form["trek_name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = request.form["duration"]
        trek.available_slots = request.form["slots"]

        db.session.commit()

        return redirect("/admin/view_treks")

    return render_template(
        "admin/edit_trek.html",
        trek=trek
    )

@app.route("/admin/delete_trek/<int:trek_id>")
@admin_required
def delete_trek(trek_id):

    trek = models.Trek.query.get(trek_id)

    if trek:
        db.session.delete(trek)
        db.session.commit()

    return redirect("/admin/view_treks")

@app.route("/admin/assign_staff", methods=["GET", "POST"])
@admin_required
def assign_staff():

    if request.method == "POST":

        trek_id = request.form["trek_id"]
        staff_id = request.form["staff_id"]

        trek = models.Trek.query.get(trek_id)

        trek.assigned_staff = staff_id

        db.session.commit()

        return "Staff Assigned Successfully!"

    treks = models.Trek.query.all()

    staffs = models.User.query.filter_by(
        role="staff",
        approved=True
    ).all()

    return render_template(
        "admin/assign_staff.html",
        treks=treks,
        staffs=staffs
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/admin/staff")
@admin_required
def view_staff():

    staff_members = models.User.query.filter_by(role="staff").all()

    return render_template(
        "admin/view_staff.html",
        staff_members=staff_members
    )

@app.route("/admin/blacklist_staff/<int:user_id>")
@admin_required
def blacklist_staff(user_id):

    staff = models.User.query.get_or_404(user_id)

    staff.blacklisted = True

    db.session.commit()

    return redirect("/admin/staff")

if __name__ == "__main__":
    app.run(debug=True)