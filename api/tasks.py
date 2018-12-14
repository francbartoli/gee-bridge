import dramatiq
from dramatiq import actor
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


@actor
def generate_process(pk):

    process = models.Process.objects.get(pk=pk)

    try:
        type = process.type
        aois = process.aoi
        tois = process.toi
        input_data = process.input_data
        algorithm = type["wapor"].get("template")
        aoi = aois[0]
        toi = tois[0]
        inputs = input_data.get("inputs")
        kwargs = dict(
            wapor_name=process.name,
            wapor_inputs=inputs,
            wapor_options=dict(spatial_extent=aoi, temporal_extent=toi)
        )
        gee_processing = Wapor(**kwargs)
        process.output_data = [gee_processing.run(algorithm)]
        process.status = models.Process.STATUS_DONE
    except Exception:
        process.status = models.Process.STATUS_FAILED

    process.save()
