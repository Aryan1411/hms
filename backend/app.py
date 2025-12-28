from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()
from flask_cors import CORS
from flask_mail import Mail
from application.database import db
from celery import Celery
import application.config as config

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__)
    
    # Secret key for sessions and JWT
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration - use PostgreSQL on Render, SQLite locally
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Render uses postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CELERY_BROKER_URL'] = config.CELERY_BROKER_URL
    app.config['CELERY_RESULT_BACKEND'] = config.CELERY_RESULT_BACKEND
    
    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = config.MAIL_SERVER
    app.config['MAIL_PORT'] = config.MAIL_PORT
    app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    db.init_app(app)
    
    # Initialize Flask-Mail
    mail = Mail(app)
    
    # Initialize mail in tasks module
    import application.tasks as tasks
    tasks.init_mail(app)

    celery = make_celery(app)

    with app.app_context():
        # Import models to ensure they are registered
        from application.models import User, Doctor, Patient, Appointment, Treatment
        db.create_all()

        # Create admin user if not exists
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', role='admin', email='admin@hms.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")

    # Register Blueprints
    from application.routes.auth import auth_bp
    from application.routes.admin import admin_bp
    from application.routes.doctor import doctor_bp
    from application.routes.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp, url_prefix='/patient')

    return app, celery

app, celery = create_app()

if __name__ == '__main__':
    app.run(debug=False)
