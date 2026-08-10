# celery_worker.py
from celery import Celery
from app import app
from celery.schedules import crontab



# Configure Celery
celery = Celery(
    app.import_name,
    backend='redis://localhost:7000/0', 
    broker='redis://localhost:7000/0',   
    include=['tasks']
)
celery.conf.update(app.config)

celery.conf.timezone = 'Asia/Kolkata'
celery.conf.beat_schedule = {
    'daily-trek-reminders': {
        'task': 'tasks.send_daily_reminders',
        # 'schedule': crontab(minute="*"), # Daily at 8:00 AM
        'schedule': crontab(minute="*"), # Daily at 8:00 AM
    },
    'monthly-admin-report': {
        'task': 'tasks.send_monthly_report',
        # 'schedule': crontab(day_of_month='1', hour=9, minute=0), # 1st of month at 9:00 AM
        'schedule': crontab(minute="*"), # 1st of month at 9:00 AM
    }
}

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask