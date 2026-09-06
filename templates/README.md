# Trekking Management System

## Project Description

The Trekking Management System is a Flask-based web application developed for the MAD-I project. It allows administrators to manage trekking activities, staff to manage assigned treks, and users to book trekking events.

---

## Technologies Used

- Python
- Flask
- SQLAlchemy
- SQLite
- HTML
- CSS
- Jinja2

---

## Features

### Admin
- Login
- Dashboard
- Create Trek
- Edit Trek
- Delete Trek
- View Users
- View Staff
- Approve Staff
- Blacklist Staff
- Blacklist Users
- Assign Staff
- View Bookings
- Search Users and Treks

### Staff
- Login
- Dashboard
- View Assigned Treks
- Update Trek Status

### User
- Register
- Login
- View Available Treks
- Book Trek
- View My Bookings
- Cancel Booking

---

## Project Structure

```
mad1-project/
│
├── app.py
├── models.py
├── extensions.py
├── templates/
│   ├── admin/
│   ├── staff/
│   ├── user/
│   ├── base.html
│   ├── login.html
│   └── register.html
│
├── static/
└── instance/
```

---

## How to Run

1. Clone the repository.

2. Create a virtual environment.

3. Install dependencies.

```
pip install -r requirements.txt
```

4. Run the application.

```
python app.py
```

5. Open the browser.

```
http://127.0.0.1:5000
```

---

## Author

Tanishka Singh

MAD-I Project