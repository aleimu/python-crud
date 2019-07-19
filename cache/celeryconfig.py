from kombu import Queue
from app.config import REDIS_URL_REQUEST

BROKER_URL = REDIS_URL_REQUEST  # request queue
CELERY_DEFAULT_QUEUE = 'default'  # default queue and custom queues
CELERY_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('right_manager_dispatcher', routing_key='right_manager_dispatcher'),
)
CELERY_ROUTES = {  # routes
    'devops_srv.tasks.right_manager': {
        'queue': 'right_manager_dispatcher',
        'routing_key': 'right_manager_dispatcher',
    }
}
