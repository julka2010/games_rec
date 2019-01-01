import os

from celery import Celery

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'game_recommendations.settings'
    )

app = Celery('games_recommendation')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
