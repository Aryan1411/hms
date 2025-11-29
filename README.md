# Hospital Management System (HMS)

A complete Hospital Management System built with Flask (Backend) and Vue.js (Frontend).

## Prerequisites

- **Python 3.10+**
- **Node.js 16+**
- **Redis** (for background tasks)

## Project Structure

```
hms/
├── backend/          # Flask API, Database, Celery
│   ├── application/  # App logic (routes, models)
│   ├── instance/     # SQLite database
│   ├── exports/      # Generated CSV files
│   └── app.py        # Entry point
└── frontend/         # Vue.js Application
    ├── src/          # Vue components & views
    └── public/       # Static assets
```

## 🚀 Quick Start Guide

Follow these steps exactly to set up the project from scratch.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hms
```

### 2. Backend Setup

Open a terminal and navigate to the backend directory:

```bash
cd backend
```

**Create and Activate Virtual Environment:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

**Install Dependencies:**

```bash
pip install -r requirements.txt
```

**Configure Environment Variables:**

Create a `.env` file in the `backend/` directory:

```bash
touch .env
```

Add the following content to `.env` (update with your email credentials):

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
secret=your-secret-key-here
```

> **Note:** For Gmail, you must use an **App Password**, not your regular password.

### 3. Frontend Setup

Open a **new terminal** and navigate to the frontend directory:

```bash
cd frontend
```

**Install Dependencies:**

```bash
npm install
```

### 4. Running the Application

You need to run 4 separate processes. Use separate terminal tabs for each.

**Terminal 1: Redis Server**
```bash
redis-server
```

**Terminal 2: Backend API**
```bash
cd backend
source venv/bin/activate
python app.py
```
*Server will start at http://localhost:5000*

**Terminal 3: Celery Worker (Background Tasks)**
```bash
cd backend
source venv/bin/activate
celery -A app.celery worker --loglevel=info
```

**Terminal 4: Celery Beat (Scheduled Tasks)**
```bash
cd backend
source venv/bin/activate
celery -A app.celery beat --loglevel=info
```

**Terminal 5: Frontend**
```bash
cd frontend
npm run dev
```
*App will be available at http://localhost:5173*

## 🔑 Default Credentials

The system automatically creates an admin account on first run.

**Admin**
- **Username:** `admin`
- **Password:** `admin123`
- **Login:** Select "Login as Admin"

**Patient**
- Register a new account or use the admin dashboard to create one.

## ✨ Features

- **Admin Dashboard:** Manage doctors, patients, and view statistics.
- **Doctor Dashboard:** Manage appointments and availability.
- **Patient Dashboard:** Book appointments, view history, and update profile.
- **Export Data:** Patients can export their treatment history as CSV (processed in background).
- **Email Notifications:** Automated emails for appointment bookings and reminders.

## 🛠 Troubleshooting

**CORS Errors?**
- Ensure backend is running on port 5000.
- Clear browser cache/cookies.
- Try Incognito mode.

**Database Issues?**
- The database is located at `backend/instance/hms.db`.
- To reset: Stop backend, delete `backend/instance` folder, and restart backend.

**Email Not Sending?**
- Check your internet connection.
- Verify `.env` credentials.
- Ensure "Less secure app access" is enabled or use App Password.
