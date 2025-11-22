🏨 Hotel Management System – Flask Web Application

A complete Hotel Management System built using Flask, SQLite, HTML/CSS, and Bootstrap.
This project allows hotel staff to manage rooms, guests, bookings, payments, staff, and generate reports.

🚀 Live Demo

(Add your Render deployed link here)

📌 Features
🛏️ Rooms Management

Add, view, and delete rooms

Track room availability

Auto-update room status during booking

👤 Guest Management

Add guest details

Search guests by name or phone

Store address and ID proof

📅 Booking Management

Create bookings

Auto-calculate total amount based on stay duration

Checkout functionality with payment entry

Change room status (Available/Occupied)

💳 Payments

Store payments

View total revenue

Track payment method and date

🧑‍💼 Staff Management

Add staff

View staff details

Manage salary, position, and hire date

📊 Reports Dashboard

Total revenue

Total bookings

Monthly revenue

Occupancy rate

Total guests and rooms overview

🛠️ Tech Stack

Backend: Python, Flask, SQLite
Frontend: HTML, CSS, Bootstrap, Jinja2
Deployment: Render (Web Service), Gunicorn

📂 Project Structure
HOTELMAANGEMT_SYSTEM/
│── app.py
│── requirements.txt
│── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── rooms.html
│   ├── add_room.html
│   ├── guests.html
│   ├── add_guest.html
│   ├── bookings.html
│   ├── add_booking.html
│   ├── checkout.html
│   ├── staff.html
│   ├── add_staff.html
│   └── reports.html
│── static/
│   ├── css/
│   ├── js/
│   └── images/
└── hotel_management.db

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/satsbee09/HOTELMAANGEMT_SYSTEM.git
cd HOTELMAANGEMT_SYSTEM

2️⃣ Install Requirements
pip install -r requirements.txt

3️⃣ Run the Project
python app.py

4️⃣ Open in Browser
http://127.0.0.1:5000

🚀 Deploy on Render
Build Command
pip install -r requirements.txt

Start Command
gunicorn app:app

requirements.txt Must Include
flask
gunicorn
python-dotenv

🗄 Database

SQLite database (hotel_management.db) is auto-created with tables:

rooms

guests

bookings

staff

payments

🤝 Contributing

Pull requests and feature improvements are welcome.

📜 License

This project is open-source and free to use.