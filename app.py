from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import json
import os

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database connection helper
def get_db_connection():
    # Use /opt/render/project/src for Render's persistent storage
    db_path = os.getenv('DATABASE_PATH', 'hotel_management.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database (same structure as terminal version)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Rooms Table
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
    
    # Guests Table
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
    
    # Bookings Table
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
    
    # Staff Table
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
    
    # Payments Table
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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    
    # Get statistics
    total_rooms = conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    occupied_rooms = conn.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Occupied'").fetchone()[0]
    total_guests = conn.execute('SELECT COUNT(*) FROM guests').fetchone()[0]
    total_bookings = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
    
    revenue_result = conn.execute('SELECT SUM(amount) FROM payments').fetchone()[0]
    total_revenue = revenue_result if revenue_result else 0
    
    conn.close()
    
    return render_template('dashboard.html', 
                         total_rooms=total_rooms,
                         occupied_rooms=occupied_rooms,
                         available_rooms=total_rooms - occupied_rooms,
                         total_guests=total_guests,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue)

# ============= ROOMS =============
@app.route('/rooms')
def rooms():
    conn = get_db_connection()
    rooms = conn.execute('SELECT * FROM rooms').fetchall()
    conn.close()
    return render_template('rooms.html', rooms=rooms)

@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price = request.form['price']
        capacity = request.form['capacity']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO rooms (room_number, room_type, price, capacity) VALUES (?, ?, ?, ?)',
                        (room_number, room_type, price, capacity))
            conn.commit()
            conn.close()
            return redirect(url_for('rooms'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Room number already exists!", 400
    
    return render_template('add_room.html')

@app.route('/rooms/delete/<int:room_id>', methods=['POST'])
def delete_room(room_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM rooms WHERE room_id = ?', (room_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('rooms'))

# ============= GUESTS =============
@app.route('/guests')
def guests():
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests').fetchall()
    conn.close()
    return render_template('guests.html', guests=guests)

@app.route('/guests/add', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        id_proof = request.form['id_proof']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO guests (name, email, phone, address, id_proof) VALUES (?, ?, ?, ?, ?)',
                    (name, email, phone, address, id_proof))
        conn.commit()
        conn.close()
        return redirect(url_for('guests'))
    
    return render_template('add_guest.html')

@app.route('/guests/search')
def search_guest():
    query = request.args.get('q', '')
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests WHERE name LIKE ? OR phone LIKE ?',
                         (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    return render_template('guests.html', guests=guests, search_query=query)

# ============= BOOKINGS =============
@app.route('/bookings')
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
    return render_template('bookings.html', bookings=bookings)

@app.route('/bookings/add', methods=['GET', 'POST'])
def add_booking():
    if request.method == 'POST':
        guest_id = request.form['guest_id']
        room_id = request.form['room_id']
        check_in = request.form['check_in_date']
        check_out = request.form['check_out_date']
        
        conn = get_db_connection()
        
        # Get room price
        price = conn.execute('SELECT price FROM rooms WHERE room_id = ?', (room_id,)).fetchone()[0]
        
        # Calculate days and total
        d1 = datetime.strptime(check_in, '%Y-%m-%d')
        d2 = datetime.strptime(check_out, '%Y-%m-%d')
        days = (d2 - d1).days
        total_amount = days * price
        
        # Create booking
        conn.execute('''
            INSERT INTO bookings (guest_id, room_id, check_in_date, check_out_date, total_amount)
            VALUES (?, ?, ?, ?, ?)
        ''', (guest_id, room_id, check_in, check_out, total_amount))
        
        # Update room status
        conn.execute('UPDATE rooms SET status = "Occupied" WHERE room_id = ?', (room_id,))
        
        conn.commit()
        conn.close()
        return redirect(url_for('bookings'))
    
    # GET request - show form
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests').fetchall()
    available_rooms = conn.execute('SELECT * FROM rooms WHERE status = "Available"').fetchall()
    conn.close()
    return render_template('add_booking.html', guests=guests, rooms=available_rooms)

@app.route('/bookings/checkout/<int:booking_id>', methods=['GET', 'POST'])
def checkout(booking_id):
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        
        conn = get_db_connection()
        
        # Get booking details
        booking = conn.execute('''
            SELECT total_amount, room_id FROM bookings WHERE booking_id = ?
        ''', (booking_id,)).fetchone()
        
        # Record payment
        conn.execute('INSERT INTO payments (booking_id, amount, payment_method) VALUES (?, ?, ?)',
                    (booking_id, booking['total_amount'], payment_method))
        
        # Update booking status
        conn.execute('UPDATE bookings SET booking_status = "Completed" WHERE booking_id = ?', (booking_id,))
        
        # Update room status
        conn.execute('UPDATE rooms SET status = "Available" WHERE room_id = ?', (booking['room_id'],))
        
        conn.commit()
        conn.close()
        return redirect(url_for('bookings'))
    
    conn = get_db_connection()
    booking = conn.execute('''
        SELECT b.*, g.name as guest_name, r.room_number
        FROM bookings b
        JOIN guests g ON b.guest_id = g.guest_id
        JOIN rooms r ON b.room_id = r.room_id
        WHERE b.booking_id = ?
    ''', (booking_id,)).fetchone()
    conn.close()
    return render_template('checkout.html', booking=booking)

# ============= STAFF =============
@app.route('/staff')
def staff():
    conn = get_db_connection()
    staff = conn.execute('SELECT * FROM staff').fetchall()
    conn.close()
    return render_template('staff.html', staff=staff)

@app.route('/staff/add', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        phone = request.form['phone']
        salary = request.form['salary']
        hire_date = request.form['hire_date']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO staff (name, position, phone, salary, hire_date) VALUES (?, ?, ?, ?, ?)',
                    (name, position, phone, salary, hire_date))
        conn.commit()
        conn.close()
        return redirect(url_for('staff'))
    
    return render_template('add_staff.html')

# ============= REPORTS =============
@app.route('/reports')
def reports():
    conn = get_db_connection()
    
    # Revenue
    revenue_result = conn.execute('SELECT SUM(amount) FROM payments').fetchone()[0]
    total_revenue = revenue_result if revenue_result else 0
    total_payments = conn.execute('SELECT COUNT(*) FROM payments').fetchone()[0]
    
    # Monthly revenue
    monthly = conn.execute('''
        SELECT strftime('%Y-%m', payment_date) as month, SUM(amount) as revenue
        FROM payments
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    ''').fetchall()
    
    # Occupancy
    total_rooms = conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    occupied = conn.execute('SELECT COUNT(*) FROM rooms WHERE status = "Occupied"').fetchone()[0]
    occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0
    
    conn.close()
    
    return render_template('reports.html',
                         total_revenue=total_revenue,
                         total_payments=total_payments,
                         monthly=monthly,
                         total_rooms=total_rooms,
                         occupied_rooms=occupied,
                         available_rooms=total_rooms - occupied,
                         occupancy_rate=occupancy_rate)

if __name__ == '__main__':
    init_db()
    print("🌐 Hotel Management System - Web Interface")
    print("📍 Open your browser and go to: http://127.0.0.1:5000")
    print("💻 Terminal version still works: python hotel_management.py")
    if __name__ == '__main__':
     init_db()
     port = int(os.getenv('PORT', 5000))
     app.run(host='0.0.0.0', port=port, debug=False)