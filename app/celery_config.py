from celery import Celery

from app.config import CELERY_BROKER_URL, CELERY_BACKEND

celery_app = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_BACKEND)
celery_app.conf.update(
    imports=[
        'app.tasks.clone',
        'app.tasks.calculate_metrics',
        'app.tasks.co_evolution_analysis',
        'app.tasks.extract_commits',
        'app.tasks.generate_time_series',
    ],
    broker_connection_retry_on_startup= True,
    task_track_started= True
 )