from __future__ import absolute_import

import os

from celery import Celery
from opbeat.contrib.django.models import client, logger, register_handlers
from opbeat.contrib.celery import register_signal

import dotenv

dotenv.read_dotenv('.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db.settings')

from django.conf import settings  # noqa

RUN_DAILY = 60 * 60 * 24

app = Celery('db')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from db.base.tasks import update_all_tle

    sender.add_periodic_task(RUN_DAILY, update_all_tle.s(),
                             name='update-all-tle')


try:
    register_signal(client)
except Exception as e:
    logger.exception('Failed installing celery hook: %s' % e)

if 'opbeat.contrib.django' in settings.INSTALLED_APPS:
    register_handlers()
