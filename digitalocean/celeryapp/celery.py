from __future__ import absolute_import

from celery import Celery

app = Celery('celeryapp',
             broker='amqp://yonatan:yonatan09@localhost:5672/yvhost',
             backend='rpc://',
             include=['celeryapp.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    BROKER_URL = 'amqp://yonatan:yonatan09@localhost:5672/yvhost',
    CELERY_RESULT_BACKEND = 'rpc://',
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TIMEZONE = 'US/Pacific',
    CELERY_ENABLE_UTC = True
)

if __name__ == '__main__':
    app.start()