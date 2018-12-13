import dramatiq
from api.process.wapor.wapor import Wapor
from api import models
from gee_bridge.settings import (
    DRAMATIQ_BROKER,
    DRAMATIQ_RESULT_BACKEND,
    DRAMATIQ_TASKS_DATABASE
)
from dramatiq.results.backends import RedisBackend
from dramatiq.results import Results
from dramatiq.brokers.rabbitmq import URLRabbitmqBroker

result_backend_url = DRAMATIQ_RESULT_BACKEND["BACKED_OPTIONS"]["url"]
result_backend = RedisBackend(url=result_backend_url)
broker_url = DRAMATIQ_BROKER["OPTIONS"]["url"]
broker = URLRabbitmqBroker(broker_url)
broker.add_middleware(Results(backend=result_backend))

dramatiq.set_broker(broker)


@dramatiq.actor
def generate_process(pk, process, alg):
    proc = models.Process.objects.get(pk=pk)

    try:
        if isinstance(process, Wapor):
            proc.output_data = [process.run(alg)]
            proc.status = models.Process.STATUS_DONE
    except Exception:
        proc.status = models.Process.STATUS_FAILED

    proc.save()
