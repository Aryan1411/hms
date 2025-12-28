import os

# Email Configuration
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '22f3001834@ds.study.iitm.ac.in')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', os.getenv('app_pass'))
MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', '22f3001834@ds.study.iitm.ac.in')

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_ENABLE_UTC = False

# Export Configuration
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
EXPORT_FOLDER = os.path.join(basedir, 'exports')
EXPORT_FILE_RETENTION_HOURS = 24
