# celery_worker.py
from celery import Celery
from app import app
 #n app factory pattern
from model import Booking, Trek, User
import csv
import os
from celery.schedules import crontab



# Configure Celery
celery = Celery(
    app.import_name,
    backend='redis://localhost:7000/0', # Redis stores the task result
    broker='redis://localhost:7000/0',   # Redis acts as the message queue
    include=['tasks']
)
celery.conf.update(app.config)
# celery_worker.py (temporary edit for testing)
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
# 3. THE FIX: Create a custom Task class that safely manages the app context
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

# 4. Apply the custom Task class to Celery
celery.Task = ContextTask