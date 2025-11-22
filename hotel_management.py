import sqlite3
from datetime import datetime
import os

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
                email VARCHAR(100),
                phone VARCHAR(15) NOT NULL,
                address TEXT,
                id_proof VARCHAR(50) NOT NULL
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
        
        self.conn.commit()
        print("✓ All tables created successfully")
    
    # =============== ROOM MANAGEMENT ===============
    
    def add_room(self):
        """Add a new room"""
        print("\n--- Add New Room ---")
        room_number = input("Room Number: ")
        room_type = input("Room Type (Single/Double/Suite/Deluxe): ")
        price = float(input("Price per night: "))
        capacity = int(input("Capacity (number of guests): "))
        
        try:
            self.cursor.execute('''
                INSERT INTO rooms (room_number, room_type, price, capacity)
                VALUES (?, ?, ?, ?)
            ''', (room_number, room_type, price, capacity))
            self.conn.commit()
            print(f"✓ Room {room_number} added successfully!")
        except sqlite3.IntegrityError:
            print("✗ Error: Room number already exists!")
    
    def view_all_rooms(self):
        """View all rooms"""
        self.cursor.execute('SELECT * FROM rooms')
        rooms = self.cursor.fetchall()
        
        if rooms:
            print("\n" + "="*80)
            print(f"{'ID':<5} {'Room No':<10} {'Type':<15} {'Price':<10} {'Status':<15} {'Capacity':<10}")
            print("="*80)
            for room in rooms:
                print(f"{room[0]:<5} {room[1]:<10} {room[2]:<15} ${room[3]:<9.2f} {room[4]:<15} {room[5]:<10}")
        else:
            print("No rooms found!")
    
    def view_available_rooms(self):
        """View available rooms"""
        self.cursor.execute("SELECT * FROM rooms WHERE status = 'Available'")
        rooms = self.cursor.fetchall()
        
        if rooms:
            print("\n" + "="*80)
            print(f"{'ID':<5} {'Room No':<10} {'Type':<15} {'Price':<10} {'Capacity':<10}")
            print("="*80)
            for room in rooms:
                print(f"{room[0]:<5} {room[1]:<10} {room[2]:<15} ${room[3]:<9.2f} {room[5]:<10}")
        else:
            print("No available rooms!")
        return rooms
    
    # =============== GUEST MANAGEMENT ===============
    
    def add_guest(self):
        """Add a new guest"""
        print("\n--- Add New Guest ---")
        name = input("Guest Name: ")
        email = input("Email: ")
        phone = input("Phone: ")
        address = input("Address: ")
        id_proof = input("ID Proof (Aadhaar/Passport/License): ")
        
        self.cursor.execute('''
            INSERT INTO guests (name, email, phone, address, id_proof)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, address, id_proof))
        self.conn.commit()
        
        guest_id = self.cursor.lastrowid
        print(f"✓ Guest added successfully! Guest ID: {guest_id}")
        return guest_id
    
    def view_all_guests(self):
        """View all guests"""
        self.cursor.execute('SELECT * FROM guests')
        guests = self.cursor.fetchall()
        
        if guests:
            print("\n" + "="*90)
            print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Phone':<15} {'ID Proof':<20}")
            print("="*90)
            for guest in guests:
                print(f"{guest[0]:<5} {guest[1]:<20} {guest[2]:<25} {guest[3]:<15} {guest[5]:<20}")
        else:
            print("No guests found!")
    
    # =============== BOOKING MANAGEMENT ===============
    
    def create_booking(self):
        """Create a new booking"""
        print("\n--- Create New Booking ---")
        
        # Show available rooms
        available = self.view_available_rooms()
        if not available:
            return
        
        # Get or create guest
        choice = input("\n1. Existing Guest\n2. New Guest\nChoice: ")
        
        if choice == '1':
            self.view_all_guests()
            try:
                guest_id = int(input("\nEnter Guest ID: "))
                # Verify guest exists
                self.cursor.execute('SELECT guest_id FROM guests WHERE guest_id = ?', (guest_id,))
                if not self.cursor.fetchone():
                    print("✗ Error: Guest ID not found!")
                    return
            except ValueError:
                print("✗ Error: Invalid Guest ID!")
                return
        else:
            guest_id = self.add_guest()
        
        # Get booking details
        try:
            room_id = int(input("Enter Room ID: "))
        except ValueError:
            print("✗ Error: Invalid Room ID!")
            return
        
        # Verify room exists and is available
        self.cursor.execute('SELECT price, status FROM rooms WHERE room_id = ?', (room_id,))
        room_data = self.cursor.fetchone()
        
        if not room_data:
            print("✗ Error: Room ID not found!")
            return
        
        price, status = room_data
        
        if status != 'Available':
            print(f"✗ Error: Room is currently {status}!")
            return
        
        check_in = input("Check-in Date (YYYY-MM-DD): ")
        check_out = input("Check-out Date (YYYY-MM-DD): ")
        
        # Calculate days
        from datetime import datetime
        d1 = datetime.strptime(check_in, '%Y-%m-%d')
        d2 = datetime.strptime(check_out, '%Y-%m-%d')
        days = (d2 - d1).days
        total_amount = days * price
        
        # Create booking
        self.cursor.execute('''
            INSERT INTO bookings (guest_id, room_id, check_in_date, check_out_date, total_amount)
            VALUES (?, ?, ?, ?, ?)
        ''', (guest_id, room_id, check_in, check_out, total_amount))
        
        # Update room status
        self.cursor.execute('''
            UPDATE rooms SET status = 'Occupied' WHERE room_id = ?
        ''', (room_id,))
        
        self.conn.commit()
        
        booking_id = self.cursor.lastrowid
        print(f"\n✓ Booking created successfully!")
        print(f"Booking ID: {booking_id}")
        print(f"Total Amount: ${total_amount:.2f} for {days} days")
    
    def view_all_bookings(self):
        """View all bookings"""
        self.cursor.execute('''
            SELECT b.booking_id, g.name, r.room_number, b.check_in_date, 
                   b.check_out_date, b.total_amount, b.booking_status
            FROM bookings b
            JOIN guests g ON b.guest_id = g.guest_id
            JOIN rooms r ON b.room_id = r.room_id
        ''')
        bookings = self.cursor.fetchall()
        
        if bookings:
            print("\n" + "="*100)
            print(f"{'ID':<5} {'Guest':<20} {'Room':<10} {'Check-in':<12} {'Check-out':<12} {'Amount':<10} {'Status':<15}")
            print("="*100)
            for booking in bookings:
                print(f"{booking[0]:<5} {booking[1]:<20} {booking[2]:<10} {booking[3]:<12} {booking[4]:<12} ${booking[5]:<9.2f} {booking[6]:<15}")
        else:
            print("No bookings found!")
    
    def checkout(self):
        """Checkout and make payment"""
        print("\n--- Checkout ---")
        booking_id = int(input("Enter Booking ID: "))
        
        # Get booking details
        self.cursor.execute('''
            SELECT b.total_amount, b.room_id, r.room_number
            FROM bookings b
            JOIN rooms r ON b.room_id = r.room_id
            WHERE b.booking_id = ?
        ''', (booking_id,))
        
        result = self.cursor.fetchone()
        if not result:
            print("✗ Booking not found!")
            return
        
        total_amount, room_id, room_number = result
        print(f"Total Amount: ${total_amount:.2f}")
        
        payment_method = input("Payment Method (Cash/Card/UPI): ")
        
        # Record payment
        self.cursor.execute('''
            INSERT INTO payments (booking_id, amount, payment_method)
            VALUES (?, ?, ?)
        ''', (booking_id, total_amount, payment_method))
        
        # Update booking status
        self.cursor.execute('''
            UPDATE bookings SET booking_status = 'Completed' WHERE booking_id = ?
        ''', (booking_id,))
        
        # Update room status
        self.cursor.execute('''
            UPDATE rooms SET status = 'Available' WHERE room_id = ?
        ''', (room_id,))
        
        self.conn.commit()
        print(f"✓ Checkout completed! Room {room_number} is now available.")
    
    # =============== STAFF MANAGEMENT ===============
    
    def add_staff(self):
        """Add new staff member"""
        print("\n--- Add New Staff ---")
        name = input("Staff Name: ")
        position = input("Position (Manager/Receptionist/Housekeeping/Chef): ")
        phone = input("Phone: ")
        salary = float(input("Salary: "))
        hire_date = input("Hire Date (YYYY-MM-DD): ")
        
        self.cursor.execute('''
            INSERT INTO staff (name, position, phone, salary, hire_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, position, phone, salary, hire_date))
        self.conn.commit()
        print("✓ Staff member added successfully!")
    
    def view_all_staff(self):
        """View all staff members"""
        self.cursor.execute('SELECT * FROM staff')
        staff = self.cursor.fetchall()
        
        if staff:
            print("\n" + "="*85)
            print(f"{'ID':<5} {'Name':<20} {'Position':<20} {'Phone':<15} {'Salary':<12} {'Hire Date':<12}")
            print("="*85)
            for member in staff:
                print(f"{member[0]:<5} {member[1]:<20} {member[2]:<20} {member[3]:<15} ${member[4]:<11.2f} {member[5]:<12}")
        else:
            print("No staff found!")
    
    # =============== REPORTS ===============
    
    def generate_revenue_report(self):
        """Generate revenue report"""
        self.cursor.execute('''
            SELECT SUM(amount) as total_revenue, COUNT(*) as total_payments
            FROM payments
        ''')
        result = self.cursor.fetchone()
        
        print("\n--- Revenue Report ---")
        if result[0] is not None:
            total_revenue = float(result[0])
        else:
            total_revenue = 0.0
        print(f"Total Revenue: ${total_revenue:.2f}")
        print(f"Total Transactions: {result[1]}")
        
        # Monthly revenue
        self.cursor.execute('''
            SELECT strftime('%Y-%m', payment_date) as month, SUM(amount) as revenue
            FROM payments
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
        ''')
        monthly = self.cursor.fetchall()
        
        if monthly:
            print("\nMonthly Revenue:")
            for month in monthly:
                print(f"{month[0]}: ${month[1]:.2f}")
    
    # =============== SEARCH & FILTER ===============
    
    def search_guest(self):
        """Search guest by name or phone"""
        print("\n--- Search Guest ---")
        search_term = input("Enter guest name or phone: ")
        
        self.cursor.execute('''
            SELECT * FROM guests 
            WHERE name LIKE ? OR phone LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        guests = self.cursor.fetchall()
        
        if guests:
            print("\n" + "="*90)
            print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Phone':<15} {'ID Proof':<20}")
            print("="*90)
            for guest in guests:
                print(f"{guest[0]:<5} {guest[1]:<20} {guest[2]:<25} {guest[3]:<15} {guest[5]:<20}")
        else:
            print("No guests found!")
    
    def search_booking(self):
        """Search booking by guest name or booking ID"""
        print("\n--- Search Booking ---")
        print("1. Search by Booking ID")
        print("2. Search by Guest Name")
        choice = input("Choice: ")
        
        if choice == '1':
            booking_id = int(input("Enter Booking ID: "))
            self.cursor.execute('''
                SELECT b.booking_id, g.name, g.phone, r.room_number, r.room_type,
                       b.check_in_date, b.check_out_date, b.total_amount, b.booking_status
                FROM bookings b
                JOIN guests g ON b.guest_id = g.guest_id
                JOIN rooms r ON b.room_id = r.room_id
                WHERE b.booking_id = ?
            ''', (booking_id,))
        else:
            guest_name = input("Enter Guest Name: ")
            self.cursor.execute('''
                SELECT b.booking_id, g.name, g.phone, r.room_number, r.room_type,
                       b.check_in_date, b.check_out_date, b.total_amount, b.booking_status
                FROM bookings b
                JOIN guests g ON b.guest_id = g.guest_id
                JOIN rooms r ON b.room_id = r.room_id
                WHERE g.name LIKE ?
            ''', (f'%{guest_name}%',))
        
        bookings = self.cursor.fetchall()
        
        if bookings:
            print("\n" + "="*110)
            print(f"{'ID':<5} {'Guest':<20} {'Phone':<15} {'Room':<8} {'Type':<12} {'Check-in':<12} {'Check-out':<12} {'Amount':<10} {'Status':<10}")
            print("="*110)
            for booking in bookings:
                print(f"{booking[0]:<5} {booking[1]:<20} {booking[2]:<15} {booking[3]:<8} {booking[4]:<12} {booking[5]:<12} {booking[6]:<12} ${booking[7]:<9.2f} {booking[8]:<10}")
        else:
            print("No bookings found!")
    
    def filter_rooms_by_type(self):
        """Filter rooms by type"""
        print("\n--- Filter Rooms by Type ---")
        room_type = input("Enter Room Type (Single/Double/Suite/Deluxe): ")
        
        self.cursor.execute('''
            SELECT * FROM rooms WHERE room_type LIKE ?
        ''', (f'%{room_type}%',))
        
        rooms = self.cursor.fetchall()
        
        if rooms:
            print("\n" + "="*80)
            print(f"{'ID':<5} {'Room No':<10} {'Type':<15} {'Price':<10} {'Status':<15} {'Capacity':<10}")
            print("="*80)
            for room in rooms:
                print(f"{room[0]:<5} {room[1]:<10} {room[2]:<15} ${room[3]:<9.2f} {room[4]:<15} {room[5]:<10}")
        else:
            print("No rooms found!")
    
    def filter_rooms_by_price(self):
        """Filter rooms by price range"""
        print("\n--- Filter Rooms by Price ---")
        min_price = float(input("Minimum Price: "))
        max_price = float(input("Maximum Price: "))
        
        self.cursor.execute('''
            SELECT * FROM rooms WHERE price BETWEEN ? AND ?
        ''', (min_price, max_price))
        
        rooms = self.cursor.fetchall()
        
        if rooms:
            print("\n" + "="*80)
            print(f"{'ID':<5} {'Room No':<10} {'Type':<15} {'Price':<10} {'Status':<15} {'Capacity':<10}")
            print("="*80)
            for room in rooms:
                print(f"{room[0]:<5} {room[1]:<10} {room[2]:<15} ${room[3]:<9.2f} {room[4]:<15} {room[5]:<10}")
        else:
            print("No rooms found in this price range!")
    
    # =============== UPDATE & DELETE ===============
    
    def update_room_price(self):
        """Update room price"""
        print("\n--- Update Room Price ---")
        room_id = int(input("Enter Room ID: "))
        new_price = float(input("Enter New Price: "))
        
        self.cursor.execute('''
            UPDATE rooms SET price = ? WHERE room_id = ?
        ''', (new_price, room_id))
        self.conn.commit()
        
        if self.cursor.rowcount > 0:
            print("✓ Room price updated successfully!")
        else:
            print("✗ Room not found!")
    
    def cancel_booking(self):
        """Cancel a booking"""
        print("\n--- Cancel Booking ---")
        booking_id = int(input("Enter Booking ID: "))
        
        # Get room ID before canceling
        self.cursor.execute('''
            SELECT room_id FROM bookings WHERE booking_id = ?
        ''', (booking_id,))
        result = self.cursor.fetchone()
        
        if not result:
            print("✗ Booking not found!")
            return
        
        room_id = result[0]
        
        # Update booking status
        self.cursor.execute('''
            UPDATE bookings SET booking_status = 'Cancelled' WHERE booking_id = ?
        ''', (booking_id,))
        
        # Free up the room
        self.cursor.execute('''
            UPDATE rooms SET status = 'Available' WHERE room_id = ?
        ''', (room_id,))
        
        self.conn.commit()
        print("✓ Booking cancelled successfully! Room is now available.")
    
    def delete_guest(self):
        """Delete a guest (only if no active bookings)"""
        print("\n--- Delete Guest ---")
        guest_id = int(input("Enter Guest ID: "))
        
        # Check for active bookings
        self.cursor.execute('''
            SELECT COUNT(*) FROM bookings 
            WHERE guest_id = ? AND booking_status != 'Cancelled' AND booking_status != 'Completed'
        ''', (guest_id,))
        
        active_bookings = self.cursor.fetchone()[0]
        
        if active_bookings > 0:
            print("✗ Cannot delete guest with active bookings!")
            return
        
        self.cursor.execute('DELETE FROM guests WHERE guest_id = ?', (guest_id,))
        self.conn.commit()
        
        if self.cursor.rowcount > 0:
            print("✓ Guest deleted successfully!")
        else:
            print("✗ Guest not found!")
    
    # =============== ADVANCED REPORTS ===============
    
    def occupancy_report(self):
        """Show room occupancy statistics"""
        print("\n--- Occupancy Report ---")
        
        self.cursor.execute('SELECT COUNT(*) FROM rooms')
        total_rooms = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Occupied'")
        occupied_rooms = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Available'")
        available_rooms = self.cursor.fetchone()[0]
        
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
        print(f"Total Rooms: {total_rooms}")
        print(f"Occupied Rooms: {occupied_rooms}")
        print(f"Available Rooms: {available_rooms}")
        print(f"Occupancy Rate: {occupancy_rate:.2f}%")
        
        # Room type distribution
        self.cursor.execute('''
            SELECT room_type, COUNT(*), SUM(CASE WHEN status='Occupied' THEN 1 ELSE 0 END) as occupied
            FROM rooms
            GROUP BY room_type
        ''')
        types = self.cursor.fetchall()
        
        if types:
            print("\nRoom Type Distribution:")
            print(f"{'Type':<15} {'Total':<10} {'Occupied':<10}")
            print("-" * 35)
            for room_type in types:
                print(f"{room_type[0]:<15} {room_type[1]:<10} {room_type[2]:<10}")
    
    def guest_history(self):
        """View guest booking history"""
        print("\n--- Guest History ---")
        guest_id = int(input("Enter Guest ID: "))
        
        self.cursor.execute('''
            SELECT g.name, g.phone, b.booking_id, r.room_number, 
                   b.check_in_date, b.check_out_date, b.total_amount, b.booking_status
            FROM bookings b
            JOIN guests g ON b.guest_id = g.guest_id
            JOIN rooms r ON b.room_id = r.room_id
            WHERE g.guest_id = ?
            ORDER BY b.check_in_date DESC
        ''', (guest_id,))
        
        history = self.cursor.fetchall()
        
        if history:
            guest_name = history[0][0]
            guest_phone = history[0][1]
            print(f"\nGuest: {guest_name} | Phone: {guest_phone}")
            print("\n" + "="*100)
            print(f"{'Booking ID':<12} {'Room':<10} {'Check-in':<12} {'Check-out':<12} {'Amount':<12} {'Status':<15}")
            print("="*100)
            for record in history:
                print(f"{record[2]:<12} {record[3]:<10} {record[4]:<12} {record[5]:<12} ${record[6]:<11.2f} {record[7]:<15}")
        else:
            print("No booking history found!")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("\n✓ Database connection closed")


def main():
    """Main menu"""
    hms = HotelManagementSystem()
    
    while True:
        print("\n" + "="*60)
        print("           HOTEL MANAGEMENT SYSTEM")
        print("="*60)
        print("\n📋 ROOM MANAGEMENT")
        print("1.  Add Room")
        print("2.  View All Rooms")
        print("3.  View Available Rooms")
        print("4.  Update Room Price")
        print("5.  Filter Rooms by Type")
        print("6.  Filter Rooms by Price Range")
        
        print("\n👤 GUEST MANAGEMENT")
        print("7.  Add Guest")
        print("8.  View All Guests")
        print("9.  Search Guest")
        print("10. Guest Booking History")
        print("11. Delete Guest")
        
        print("\n📅 BOOKING MANAGEMENT")
        print("12. Create Booking")
        print("13. View All Bookings")
        print("14. Search Booking")
        print("15. Cancel Booking")
        print("16. Checkout")
        
        print("\n👥 STAFF MANAGEMENT")
        print("17. Add Staff")
        print("18. View All Staff")
        
        print("\n📊 REPORTS")
        print("19. Revenue Report")
        print("20. Occupancy Report")
        
        print("\n0.  Exit")
        print("="*60)
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            hms.add_room()
        elif choice == '2':
            hms.view_all_rooms()
        elif choice == '3':
            hms.view_available_rooms()
        elif choice == '4':
            hms.update_room_price()
        elif choice == '5':
            hms.filter_rooms_by_type()
        elif choice == '6':
            hms.filter_rooms_by_price()
        elif choice == '7':
            hms.add_guest()
        elif choice == '8':
            hms.view_all_guests()
        elif choice == '9':
            hms.search_guest()
        elif choice == '10':
            hms.guest_history()
        elif choice == '11':
            hms.delete_guest()
        elif choice == '12':
            hms.create_booking()
        elif choice == '13':
            hms.view_all_bookings()
        elif choice == '14':
            hms.search_booking()
        elif choice == '15':
            hms.cancel_booking()
        elif choice == '16':
            hms.checkout()
        elif choice == '17':
            hms.add_staff()
        elif choice == '18':
            hms.view_all_staff()
        elif choice == '19':
            hms.generate_revenue_report()
        elif choice == '20':
            hms.occupancy_report()
        elif choice == '0':
            hms.close()
            print("Thank you for using Hotel Management System!")
            break
        else:
            print("Invalid choice! Please try again.")


if __name__ == "__main__":
    main()