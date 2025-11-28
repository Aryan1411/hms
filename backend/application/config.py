import os
# Email Configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = '22f3001834@ds.study.iitm.ac.in' 
MAIL_PASSWORD = os.getenv('app_pass')   
MAIL_DEFAULT_SENDER = '22f3001834@ds.study.iitm.ac.in'

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_ENABLE_UTC = False

# Export Configuration
EXPORT_FOLDER = 'exports'
EXPORT_FILE_RETENTION_HOURS = 24
