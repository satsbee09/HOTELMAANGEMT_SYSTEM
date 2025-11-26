from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Secret Key for Sessions
app.secret_key = "supersecretkey"  # change before deploying!

# Database Connection
def get_db_connection():
    db_path = os.getenv('DATABASE_PATH', 'hotel_management.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number VARCHAR(10) UNIQUE NOT NULL,
            room_type VARCHAR(50) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'Available',
            capacity INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(15) NOT NULL,
            address TEXT,
            id_proof VARCHAR(50) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            total_amount DECIMAL(10,2),
            booking_status VARCHAR(20) DEFAULT 'Confirmed',
            FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            position VARCHAR(50) NOT NULL,
            phone VARCHAR(15) NOT NULL,
            salary DECIMAL(10,2),
            hire_date DATE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_method VARCHAR(20) NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
        )
    ''')

    conn.commit()
    conn.close()


# Login Required Decorator
def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# --------------------- AUTH ROUTES ---------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            flash("Login Successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


# --------------------- DASHBOARD ---------------------

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()
    total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    occupied_rooms = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Occupied'").fetchone()[0]
    total_guests = conn.execute("SELECT COUNT(*) FROM guests").fetchone()[0]
    total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    revenue = conn.execute("SELECT SUM(amount) FROM payments").fetchone()[0] or 0
    conn.close()

    return render_template("dashboard.html",
                           total_rooms=total_rooms,
                           occupied_rooms=occupied_rooms,
                           available_rooms=total_rooms - occupied_rooms,
                           total_guests=total_guests,
                           total_bookings=total_bookings,
                           total_revenue=revenue)


# --------------------- ROOMS ---------------------

@app.route("/rooms")
@login_required
def rooms():
    conn = get_db_connection()
    rooms = conn.execute("SELECT * FROM rooms").fetchall()
    conn.close()
    return render_template("rooms.html", rooms=rooms)


@app.route("/rooms/add", methods=["GET", "POST"])
@login_required
def add_room():
    if request.method == "POST":
        conn = get_db_connection()
        conn.execute("INSERT INTO rooms (room_number, room_type, price, capacity) VALUES (?, ?, ?, ?)",
                     (request.form["room_number"], request.form["room_type"],
                      request.form["price"], request.form["capacity"]))
        conn.commit()
        conn.close()
        return redirect(url_for("rooms"))

    return render_template("add_room.html")


@app.route("/rooms/delete/<int:room_id>", methods=["POST"])
@login_required
def delete_room(room_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("rooms"))


# --------------------- GUESTS ---------------------

@app.route("/guests")
@login_required
def guests():
    conn = get_db_connection()
    guests = conn.execute("SELECT * FROM guests").fetchall()
    conn.close()
    return render_template("guests.html", guests=guests)


@app.route("/guests/add", methods=["GET", "POST"])
@login_required
def add_guest():
    if request.method == "POST":
        conn = get_db_connection()
        conn.execute("INSERT INTO guests (name, email, phone, address, id_proof) VALUES (?, ?, ?, ?, ?)",
                     (request.form["name"], request.form["email"], request.form["phone"],
                      request.form["address"], request.form["id_proof"]))
        conn.commit()
        conn.close()
        return redirect(url_for("guests"))

    return render_template("add_guest.html")


@app.route("/guests/search")
@login_required
def search_guest():
    query = request.args.get("q", "")
    conn = get_db_connection()
    guests = conn.execute("SELECT * FROM guests WHERE name LIKE ? OR phone LIKE ?",
                          (f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return render_template("guests.html", guests=guests, search_query=query)


# --------------------- BOOKINGS ---------------------

@app.route("/bookings")
@login_required
def bookings():
    conn = get_db_connection()
    bookings = conn.execute('''
        SELECT b.booking_id, g.name, r.room_number, b.check_in_date, 
               b.check_out_date, b.total_amount, b.booking_status
        FROM bookings b
        JOIN guests g ON b.guest_id = g.guest_id
        JOIN rooms r ON b.room_id = r.room_id
        ORDER BY b.booking_id DESC
    ''').fetchall()
    conn.close()
    return render_template("bookings.html", bookings=bookings)


@app.route("/bookings/add", methods=["GET", "POST"])
@login_required
def add_booking():
    conn = get_db_connection()

    if request.method == "POST":
        guest_id = request.form["guest_id"]
        room_id = request.form["room_id"]
        check_in = request.form["check_in_date"]
        check_out = request.form["check_out_date"]

        price = conn.execute("SELECT price FROM rooms WHERE room_id=?", (room_id,)).fetchone()[0]

        d1 = datetime.strptime(check_in, "%Y-%m-%d")
        d2 = datetime.strptime(check_out, "%Y-%m-%d")
        days = (d2 - d1).days
        total_amount = days * price

        conn.execute("INSERT INTO bookings (guest_id, room_id, check_in_date, check_out_date, total_amount)"
                     " VALUES (?, ?, ?, ?, ?)", (guest_id, room_id, check_in, check_out, total_amount))
        conn.execute("UPDATE rooms SET status='Occupied' WHERE room_id=?", (room_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("bookings"))

    guests = conn.execute("SELECT * FROM guests").fetchall()
    rooms = conn.execute("SELECT * FROM rooms WHERE status='Available'").fetchall()
    conn.close()
    return render_template("add_booking.html", guests=guests, rooms=rooms)


@app.route("/bookings/checkout/<int:booking_id>", methods=["GET", "POST"])
@login_required
def checkout(booking_id):
    conn = get_db_connection()

    if request.method == "POST":
        booking = conn.execute("SELECT * FROM bookings WHERE booking_id=?", (booking_id,)).fetchone()
        conn.execute("INSERT INTO payments (booking_id, amount, payment_method) VALUES (?, ?, ?)",
                     (booking["booking_id"], booking["total_amount"], request.form["payment_method"]))
        conn.execute("UPDATE bookings SET booking_status='Completed' WHERE booking_id=?", (booking_id,))
        conn.execute("UPDATE rooms SET status='Available' WHERE room_id=?", (booking["room_id"],))
        conn.commit()
        conn.close()
        return redirect(url_for("bookings"))

    booking = conn.execute('''
        SELECT b.*, g.name AS guest_name, r.room_number
        FROM bookings b
        JOIN guests g ON b.guest_id=g.guest_id
        JOIN rooms r ON b.room_id=r.room_id
        WHERE b.booking_id=?
    ''', (booking_id,)).fetchone()
    conn.close()
    return render_template("checkout.html", booking=booking)


# --------------------- STAFF ---------------------

@app.route("/staff")
@login_required
def staff():
    conn = get_db_connection()
    staff = conn.execute("SELECT * FROM staff").fetchall()
    conn.close()
    return render_template("staff.html", staff=staff)


@app.route("/staff/add", methods=["GET", "POST"])
@login_required
def add_staff():
    if request.method == "POST":
        conn = get_db_connection()
        conn.execute("INSERT INTO staff (name, position, phone, salary, hire_date) VALUES (?, ?, ?, ?, ?)",
                     (request.form["name"], request.form["position"], request.form["phone"],
                      request.form["salary"], request.form["hire_date"]))
        conn.commit()
        conn.close()
        return redirect(url_for("staff"))

    return render_template("add_staff.html")


# --------------------- REPORTS ---------------------

@app.route("/reports")
@login_required
def reports():
    conn = get_db_connection()
    revenue = conn.execute("SELECT SUM(amount) FROM payments").fetchone()[0] or 0
    monthly = conn.execute('''
        SELECT strftime('%Y-%m', payment_date) AS month, SUM(amount) AS revenue
        FROM payments GROUP BY month ORDER BY month DESC LIMIT 6
    ''').fetchall()
    total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    occupied = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Occupied'").fetchone()[0]
    rate = (occupied / total_rooms * 100) if total_rooms else 0
    conn.close()

    return render_template("reports.html",
                           total_revenue=revenue,
                           monthly=monthly,
                           occupied_rooms=occupied,
                           available_rooms=total_rooms - occupied,
                           occupancy_rate=rate)


# --------------------- RUN APP ---------------------

if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
