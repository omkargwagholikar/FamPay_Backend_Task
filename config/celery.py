import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('FamPay_Backend_Task')

# Use string as config key in settings because celery can't serialize objects
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.enable_utc = False
app.conf.update(timezone="Asia/Kolkata")

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')