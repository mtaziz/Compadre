from __future__ import absolute_import

from celery import Celery

app = Celery('celeryapp',
             broker='amqp://yonatan:yonatan09@localhost:5672/yvhost',
             backend='amqp://',
             include=['celeryapp.tasks'])

# Optional configuration, see the application user guide.
app.config_from_object('celeryconfig')

if __name__ == '__main__':
    app.start()