from ee import EEException
import ee


def createImageMeanDictByRegion(img_inst, geom):
    """Create dictionary of sum statistics

    Parameters
    ----------
    img_inst : ee.Image
        Image instance
    geom : ee.Geometry
        Geometry object of the region

    Returns
    -------
    dict
        Dictionary of bands and mean values
    """

    try:
        stat = img_inst.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geom,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise


def createImageSumDictByRegion(img_inst, geom):
    """Create dictionary of sum statistics

    Parameters
    ----------
    img_inst : ee.Image
        Image instance
    geom : ee.Geometry
        Geometry object of the region

    Returns
    -------
    dict
        Dictionary of bands and sum values
    """

    try:
        stat = img_inst.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geom,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise


def createImageMinMaxDictByRegion(img_inst, geom):
    """Create dictionary of sum statistics

    Parameters
    ----------
    img_inst : ee.Image
        Image instance
    geom : ee.Geometry
        Geometry object of the region

    Returns
    -------
    dict
        Dictionary of bands' min/max and their values
    """

    try:
        stat = img_inst.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=geom,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise
