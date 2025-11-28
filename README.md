# Hospital Management System (HMS)

A comprehensive web-based Hospital Management System built with Flask (Backend) and Vue.js (Frontend). This system provides role-based access for Admins, Doctors, and Patients with features including appointment scheduling, treatment management, automated reminders, and administrative dashboards.

## 🌟 Features

### Admin Dashboard
- **User Management**: Create, view, and manage doctors and patients
- **Blacklist Management**: Blacklist/unblacklist users
- **Appointment Overview**: View pending and previous appointments
- **Statistics Dashboard**: Real-time stats including total users, appointments, and pending appointments
- **Data Export**: Export patient treatment history as CSV
- **Search Functionality**: Search by patient/doctor IDs and contact numbers

### Doctor Portal
- **Availability Management**: Set and manage consultation time slots
- **Appointment Management**: View and manage patient appointments
- **Treatment Records**: Add diagnosis, prescriptions, and notes for appointments
- **Activity Reports**: Receive monthly activity reports via email

### Patient Portal
- **Doctor Discovery**: Browse available doctors by specialization and department
- **Appointment Booking**: Book appointments with available doctors
- **Appointment History**: View past and upcoming appointments
- **Treatment Records**: Access treatment history and prescriptions
- **Appointment Reminders**: Receive automated email reminders

### Automated Backend Jobs (Celery)
- **Daily Appointment Reminders**: Automated email reminders sent to patients 24 hours before appointments
- **Monthly Doctor Reports**: Monthly activity reports sent to doctors
- **CSV Export**: User-triggered export of patient treatment history

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens) with PyJWT
- **Task Queue**: Celery 5.3.4 with Redis
- **Email**: Flask-Mail
- **Security**: Flask-Bcrypt for password hashing
- **CORS**: Flask-CORS for cross-origin requests

### Frontend
- **Framework**: Vue.js 3.5.24
- **Routing**: Vue Router 4.6.3
- **Build Tool**: Vite 7.2.4
- **UI Framework**: Bootstrap 5.3.8
- **HTTP Client**: Fetch API

### Infrastructure
- **Message Broker**: Redis 5.0.1
- **Task Scheduler**: Celery Beat

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** and npm - [Download Node.js](https://nodejs.org/)
- **Redis Server** - [Download Redis](https://redis.io/download/)
  - Windows: Use [Memurai](https://www.memurai.com/) or [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
  - Linux/Mac: `sudo apt-get install redis-server` or `brew install redis`
- **Git** - [Download Git](https://git-scm.com/downloads)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Aryan1411/hms.git
cd hms
```

### 2. Backend Setup

#### Step 2.1: Navigate to Backend Directory
```bash
cd backend
```

#### Step 2.2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Step 2.3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2.4: Configure Environment Variables
Create a `.env` file in the `backend` directory (or copy from `.env.example`):

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit the `.env` file with your settings:
```env
# Email Settings (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Redis/Celery
REDIS_URL=redis://localhost:6379/0
```

> **Note**: For Gmail, you need to create an [App Password](https://support.google.com/accounts/answer/185833) instead of using your regular password.

#### Step 2.5: Update config.py
Edit `backend/config.py` and update the email credentials:
```python
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'
MAIL_DEFAULT_SENDER = 'your-email@gmail.com'
```

#### Step 2.6: Initialize Database
```bash
python app.py
```
This will:
- Create the SQLite database (`hms.db`)
- Create all necessary tables
- Create a default admin user (username: `admin`, password: `adminpassword`)

Press `Ctrl+C` to stop the server after initialization.

### 3. Frontend Setup

#### Step 3.1: Navigate to Frontend Directory
```bash
# From project root
cd frontend
```

#### Step 3.2: Install Node Dependencies
```bash
npm install
```

### 4. Redis Setup

#### Step 4.1: Start Redis Server

**Windows (using Memurai):**
```bash
# Start Memurai service from Start Menu or
memurai
```

**Linux:**
```bash
sudo service redis-server start
# or
redis-server
```

**Mac:**
```bash
brew services start redis
# or
redis-server
```

#### Step 4.2: Verify Redis is Running
```bash
redis-cli ping
# Should return: PONG
```

## 🎯 Running the Application

You need to run **three separate processes** simultaneously:

### Terminal 1: Backend Server

```bash
cd backend
# Activate virtual environment if not already activated
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python app.py
```
Backend will run on: `http://localhost:5000`

### Terminal 2: Celery Worker

```bash
cd backend
# Activate virtual environment if not already activated

# Windows
celery -A celery_config.celery worker --loglevel=info --pool=solo

# Linux/Mac
celery -A celery_config.celery worker --loglevel=info
```

### Terminal 3: Celery Beat (Task Scheduler)

```bash
cd backend
# Activate virtual environment if not already activated

celery -A celery_config.celery beat --loglevel=info
```

### Terminal 4: Frontend Development Server

```bash
cd frontend
npm run dev
```
Frontend will run on: `http://localhost:5173` (or another port if 5173 is busy)

## 🔑 Default Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `adminpassword`

> **Important**: Change the admin password after first login!

### Creating Additional Users
- **Doctors and Patients**: Can be created by the admin through the Admin Dashboard
- Each user type has different access levels and features

## 📁 Project Structure

```
hospital-management-system/
├── backend/
│   ├── routes/              # API route blueprints
│   │   ├── auth.py         # Authentication routes
│   │   ├── admin.py        # Admin dashboard routes
│   │   ├── doctor.py       # Doctor portal routes
│   │   └── patient.py      # Patient portal routes
│   ├── templates/          # Email templates
│   ├── exports/            # CSV export storage
│   ├── instance/           # SQLite database location
│   ├── app.py             # Flask application factory
│   ├── models.py          # Database models
│   ├── tasks.py           # Celery tasks
│   ├── config.py          # Configuration settings
│   ├── celery_config.py   # Celery configuration
│   ├── extensions.py      # Flask extensions
│   ├── auth_decorator.py  # JWT authentication decorator
│   └── requirements.txt   # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── views/         # Vue components for each page
│   │   ├── router/        # Vue Router configuration
│   │   ├── components/    # Reusable Vue components
│   │   ├── App.vue        # Root Vue component
│   │   └── main.js        # Vue app entry point
│   ├── public/            # Static assets
│   ├── index.html         # HTML entry point
│   ├── vite.config.js     # Vite configuration
│   └── package.json       # Node dependencies
│
└── README.md              # This file
```

## 🔧 API Documentation

Detailed API documentation is available in `backend/API.md`. Key endpoints include:

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Admin Routes
- `GET /admin/dashboard` - Dashboard statistics
- `POST /admin/create-user` - Create doctor/patient
- `GET /admin/users` - List all users
- `POST /admin/blacklist/:id` - Blacklist user
- `GET /admin/export-treatments/:patient_id` - Export patient data

### Doctor Routes
- `GET /doctor/appointments` - View appointments
- `POST /doctor/availability` - Set availability
- `POST /doctor/treatment` - Add treatment record

### Patient Routes
- `GET /patient/doctors` - Browse doctors
- `POST /patient/book-appointment` - Book appointment
- `GET /patient/appointments` - View appointments
- `GET /patient/treatments` - View treatment history

## 📧 Automated Jobs

### Daily Appointment Reminders
- **Schedule**: Runs daily at 9:00 AM
- **Function**: Sends email reminders to patients with appointments in the next 24 hours

### Monthly Doctor Reports
- **Schedule**: Runs on the 1st of each month at 8:00 AM
- **Function**: Sends activity reports to all active doctors

### CSV Export
- **Trigger**: User-initiated from Admin Dashboard
- **Function**: Exports patient treatment history as CSV
- **Retention**: Files are automatically deleted after 24 hours

For more details, see `backend/JOBS_README.md` and `backend/CELERY_GUIDE.md`.

## 🧪 Testing

### Backend Testing
```bash
cd backend
python test_jwt_auth.py
```

### Check Database
```bash
cd backend
python check_db.py
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Redis Connection Error
**Error**: `Error 10061: No connection could be made`

**Solution**:
- Ensure Redis server is running
- Check if Redis is listening on port 6379: `redis-cli ping`
- Windows users: Install and start Memurai

#### 2. Email Not Sending
**Error**: Emails not being sent

**Solution**:
- Verify email credentials in `config.py`
- For Gmail, use an App Password, not your regular password
- Check if Celery worker is running
- Check Celery worker logs for errors

#### 3. Database Errors
**Error**: Database locked or table doesn't exist

**Solution**:
```bash
cd backend
# Delete existing database
rm instance/hms.db
# Reinitialize
python app.py
```

#### 4. Frontend Can't Connect to Backend
**Error**: CORS or network errors

**Solution**:
- Ensure backend is running on port 5000
- Check CORS configuration in `backend/app.py`
- Verify API URLs in frontend code

#### 5. Celery Tasks Not Running
**Error**: Scheduled tasks not executing

**Solution**:
- Ensure Celery Beat is running
- Check Celery Beat logs
- Verify timezone settings in `config.py`

## 🔒 Security Considerations

- **Change Default Credentials**: Update admin password immediately
- **Environment Variables**: Never commit `.env` file to version control
- **JWT Secret**: Use a strong secret key in production
- **HTTPS**: Use HTTPS in production environments
- **Database**: Use PostgreSQL or MySQL in production instead of SQLite
- **Email Credentials**: Use environment variables for sensitive data

## 📝 Development Notes

### Adding New Features
1. Backend: Add routes in `backend/routes/`
2. Frontend: Add views in `frontend/src/views/`
3. Database: Update models in `backend/models.py`
4. Tasks: Add Celery tasks in `backend/tasks.py`

### Database Migrations
Currently using `db.create_all()`. For production, consider using Flask-Migrate:
```bash
pip install Flask-Migrate
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Aryan Mishra

## 🙏 Acknowledgments

- Flask documentation
- Vue.js documentation
- Bootstrap team
- Celery documentation


---

**Made with ❤️ for better healthcare management**
