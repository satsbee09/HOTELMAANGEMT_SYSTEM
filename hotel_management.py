import sqlite3
from datetime import datetime
import os
import hashlib

class HotelManagementSystem:
    def __init__(self, db_name="hotel_management.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect_db()
        self.create_tables()
    
    def connect_db(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print(f"✓ Connected to database: {self.db_name}")
    
    def create_tables(self):
        """Create all necessary tables"""
        
        # Rooms Table
        self.cursor.execute('''
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS guests (
                guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(15) UNIQUE NOT NULL,
                address TEXT,
                id_proof VARCHAR(50) UNIQUE NOT NULL
            )
        ''')
        
        # Bookings Table
        self.cursor.execute('''
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
        self.cursor.execute('''
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_method VARCHAR(20) NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
            )
        ''')

        # Admin Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            )
        ''')

        # Insert default admin if not exists
        self.cursor.execute("SELECT COUNT(*) FROM admin")
        if self.cursor.fetchone()[0] == 0:
            default_user = "admin"
            default_pass = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)",
                                (default_user, default_pass))

        self.conn.commit()
        print("✓ All tables created successfully")

    # ---------------- ADMIN LOGIN ----------------
    def admin_login(self):
        print("\n===== ADMIN LOGIN =====")
        username = input("Username: ")
        password = input("Password: ")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        self.cursor.execute(
            "SELECT * FROM admin WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        result = self.cursor.fetchone()

        if result:
            print("✓ Login Successful! Welcome Admin.")
            return True
        else:
            print("✗ Incorrect Username or Password!")
            return False

    # ---------------- ROOM MANAGEMENT ----------------
    def add_room(self):
        print("\n--- Add New Room ---")
        room_number = input("Room Number: ")
        room_type = input("Room Type (Single/Double/Suite/Deluxe): ")
        price = float(input("Price per night: "))
        capacity = int(input("Capacity (number of guests): "))

        try:
            self.cursor.execute(
                "INSERT INTO rooms (room_number, room_type, price, capacity) VALUES (?, ?, ?, ?)",
                (room_number, room_type, price, capacity))
            self.conn.commit()
            print(f"✓ Room {room_number} added successfully!")
        except sqlite3.IntegrityError:
            print("✗ Error: Room number already exists!")

    def view_all_rooms(self):
        self.cursor.execute("SELECT * FROM rooms")
        rooms = self.cursor.fetchall()

        if rooms:
            print("\n" + "="*80)
            print("ID  Room No   Type            Price      Status        Capacity")
            print("="*80)
            for room in rooms:
                print(f"{room[0]:<5} {room[1]:<10} {room[2]:<15} ${room[3]:<9.2f} {room[4]:<15} {room[5]:<10}")
        else:
            print("No rooms found!")

    def view_available_rooms(self):
        self.cursor.execute("SELECT * FROM rooms WHERE status = 'Available'")
        rooms = self.cursor.fetchall()

        if rooms:
            print("\n" + "="*80)
            print("ID  Room No   Type            Price      Capacity")
            print("="*80)
            for room in rooms:
                print(f"{room[0]:<5} {room[1]:<10} {room[2]:<15} ${room[3]:<9.2f} {room[5]:<10}")
        else:
            print("No available rooms!")
        return rooms

    # ---------------- GUEST MANAGEMENT ----------------
    def add_guest(self):
        import re
        print("\n--- Add New Guest ---")

        name = input("Guest Name: ")
        email = input("Email: ")
        phone = input("Phone (10-digit): ")
        address = input("Address: ")
        id_proof = input("Aadhaar Number (12-digit): ")

        if not re.fullmatch(r"[6-9]\d{9}", phone):
            print("✗ Invalid Mobile Number!")
            return None

        if not re.fullmatch(r"\d{12}", id_proof):
            print("✗ Invalid Aadhaar!")
            return None

        try:
            self.cursor.execute(
                "INSERT INTO guests (name, email, phone, address, id_proof) VALUES (?, ?, ?, ?, ?)",
                (name, email, phone, address, id_proof)
            )
            self.conn.commit()
            guest_id = self.cursor.lastrowid
            print(f"✓ Guest added successfully! Guest ID: {guest_id}")
            return guest_id

        except sqlite3.IntegrityError:
            print("✗ Duplicate Email/Phone/Aadhaar!")
            return None

    # ---------------- BOOKING ----------------
    def create_booking(self):
        print("\n--- Create New Booking ---")
        available = self.view_available_rooms()
        if not available: return

        choice = input("\n1. Existing Guest\n2. New Guest\nChoice: ")
        if choice == '1':
            self.cursor.execute("SELECT * FROM guests")
            guests = self.cursor.fetchall()
            if guests:
                print("\nGuest List:")
                for g in guests:
                    print(f"ID:{g[0]} Name:{g[1]} Phone:{g[3]}")
            guest_id = int(input("Enter Guest ID: "))
        else:
            guest_id = self.add_guest()
            if guest_id is None:
                return

        room_id = int(input("Enter Room ID: "))
        self.cursor.execute("SELECT price,status FROM rooms WHERE room_id=?", (room_id,))
        room_data = self.cursor.fetchone()
        if not room_data or room_data[1] != 'Available':
            print("✗ Room not available!")
            return

        price = room_data[0]
        check_in = input("Check-in (YYYY-MM-DD): ")
        check_out = input("Check-out (YYYY-MM-DD): ")
        days = (datetime.strptime(check_out, '%Y-%m-%d') - datetime.strptime(check_in, '%Y-%m-%d')).days
        total_amount = days * price

        self.cursor.execute(
            "INSERT INTO bookings (guest_id, room_id, check_in_date, check_out_date, total_amount) "
            "VALUES (?, ?, ?, ?, ?)",
            (guest_id, room_id, check_in, check_out, total_amount)
        )
        self.cursor.execute("UPDATE rooms SET status='Occupied' WHERE room_id=?", (room_id,))
        self.conn.commit()

        print("✓ Booking Successful!")

    # ---------------- CHECKOUT ----------------
    def checkout(self):
        booking_id = int(input("\nEnter Booking ID: "))

        self.cursor.execute(
            "SELECT b.total_amount,b.room_id,r.room_number FROM bookings b JOIN rooms r "
            "ON b.room_id=r.room_id WHERE b.booking_id=?",
            (booking_id,))
        result = self.cursor.fetchone()

        if not result:
            print("✗ Booking not found!")
            return

        total_amount, room_id, room_no = result
        print(f"Total Amount Due: ${total_amount:.2f}")
        method = input("Payment Method (Cash/Card/UPI): ")

        self.cursor.execute("INSERT INTO payments (booking_id,amount,payment_method) VALUES (?,?,?)",
                            (booking_id, total_amount, method))
        self.cursor.execute("UPDATE bookings SET booking_status='Completed' WHERE booking_id=?", (booking_id,))
        self.cursor.execute("UPDATE rooms SET status='Available' WHERE room_id=?", (room_id,))
        self.conn.commit()
        print(f"✓ Checkout Done! Room {room_no} Available.")

    # ---------------- EXIT ----------------
    def close(self):
        if self.conn:
            self.conn.close()
            print("✓ Database Closed")


def main():
    hms = HotelManagementSystem()

    # Require Admin Login
    if not hms.admin_login():
        print("Access Denied. Exiting...")
        return

    while True:
        print("\n====== HOTEL MANAGEMENT SYSTEM ======")
        print("1. Add Room")
        print("2. View Rooms")
        print("3. View Available Rooms")
        print("4. Add Guest")
        print("5. Create Booking")
        print("6. Checkout")
        print("0. Exit")
        print("=====================================")

        ch = input("Enter Choice: ")

        if ch == '1': hms.add_room()
        elif ch == '2': hms.view_all_rooms()
        elif ch == '3': hms.view_available_rooms()
        elif ch == '4': hms.add_guest()
        elif ch == '5': hms.create_booking()
        elif ch == '6': hms.checkout()
        elif ch == '0':
            hms.close()
            print("Thank you for using system!")
            break
        else:
            print("Invalid Choice!")


if __name__ == "__main__":
    main()
