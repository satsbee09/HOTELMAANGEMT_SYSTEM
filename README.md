🏨 Hotel Management System – Flask Web Application

A complete Hotel Management System built using Flask, SQLite, HTML/CSS, and Bootstrap.
This project allows hotel staff to manage rooms, guests, bookings, payments, staff, and reports.

🚀 Live Demo
https://hotelmaangemt-system-1.onrender.com

📌 Features

🛏️ Rooms Management
• Add, view and delete rooms
• Track room availability
• Auto-update room status

👤 Guest Management
• Add guest details
• Search by name or phone
• Store address + ID proof

📅 Booking Management
• New booking creation
• Auto price calculation
• Checkout + payment record
• Update room occupancy

💳 Payments
• Store payment history
• View total revenue
• Track date and method

🧑‍💼 Staff Management
• Add / view staff
• Manage salary & positions

📊 Reports Dashboard
• Monthly revenue chart
• Rooms occupancy status
• Total customers & bookings

🛠️ Tech Stack

Backend → Python Flask
Database → SQLite
Frontend → HTML, CSS, Bootstrap, Jinja2
Server Deployment → Render + Gunicorn

📂 Project Structure

HOTEL_MANAGEMENT_SYSTEM/
│── app.py
│── requirements.txt
│── templates/
│ ├── login.html
│ ├── dashboard.html
│ ├── rooms.html
│ ├── add_room.html
│ ├── guests.html
│ ├── add_guest.html
│ ├── bookings.html
│ ├── add_booking.html
│ ├── checkout.html
│ ├── staff.html
│ ├── add_staff.html
│ └── reports.html
│── static/
│ ├── css
│ ├── js
│ └── images
└── hotel_management.db

🔐 Login Details

Username: admin
Password: admin123

⚙️ Installation & Setup

1️⃣ Clone the repo:
git clone https://github.com/satsbee09/HOTEL_MANAGEMENT_SYSTEM.git

cd HOTEL_MANAGEMENT_SYSTEM

2️⃣ Install dependencies:
pip install -r requirements.txt

3️⃣ Start the server:
python app.py

4️⃣ Open:
http://127.0.0.1:5000

🚀 Render Deployment

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

requirements.txt must include:
flask
werkzeug
gunicorn

🗄 Database Auto-Creation
Tables included: Rooms, Guests, Bookings, Staff, Payments

📸 Screenshots
(Add dashboard and forms screenshots here)

🤝 Contribution
Pull requests & improvements are welcome!

📜 License
This project is free & open-source for educational use.

⭐ If you find this useful — please Star the GitHub repo! 😊