from celery import Celery
from celery.schedules import crontab

from twittersupervisor import create_app


def create_celery_app(app=None):
    app = app or create_app()
    celery_app = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        include=['twittersupervisor.tasks']
    )
    celery_app.conf.update(app.config)
    celery_app.conf.beat_schedule = {
        'check_followers': {
            'task': 'twittersupervisor.tasks.check_app_users_followers',
            'schedule': crontab(minute='*/15'),
            'args': (),
        },
        'update_users_data': {
            'task': 'twittersupervisor.tasks.update_users_data',
            'schedule': crontab(minute='*/15'),
            'args': (),
        }
    }

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app


celery = create_celery_app()
