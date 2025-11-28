from celery import Celery
from celery.schedules import crontab
import config

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=config.CELERY_BROKER_URL,
        backend=config.CELERY_RESULT_BACKEND
    )
    celery.conf.update(
        task_serializer=config.CELERY_TASK_SERIALIZER,
        result_serializer=config.CELERY_RESULT_SERIALIZER,
        accept_content=config.CELERY_ACCEPT_CONTENT,
        timezone=config.CELERY_TIMEZONE,
        enable_utc=config.CELERY_ENABLE_UTC,
        beat_schedule={
            'send-daily-reminders': {
                'task': 'tasks.send_daily_reminders',
                'schedule': crontab(hour=9, minute=0),  
            },
            'send-monthly-reports': {
                'task': 'tasks.send_monthly_reports',
                'schedule': crontab(day_of_month=1, hour=8, minute=0), 
            },
        }
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
