import dramatiq
from dramatiq import actor
from api.process.wapor.wapor import Wapor
from api import models


@actor
def geeprocess(pk):
    """Execute background processing on GEE

    Parameters
    ----------
    pk : str
        Primary key of the process created

    """

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
