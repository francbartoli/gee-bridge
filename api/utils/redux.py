from ee import EEException
import ee


def createImageMeanDictByRegion(img_inst, geom_inst):
    """Create dictionary of sum statistics

    Parameters
    ----------
    img_inst: ee.Image
        Image instance
    geom_inst: ee.Geometry
        Geometry object of the region

    Returns
    -------
    dict
        Dictionary of bands and mean values
    """

    try:
        stat = img_inst.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geom_inst,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise


def createImageSumDictByRegion(img_inst, geom_inst):
    """Create dictionary of sum statistics

    Parameters
    ----------
    img_inst: ee.Image
        Image instance
    geom_inst: ee.Geometry
        Geometry object of the region

    Returns
    -------
    dict
        Dictionary of bands and sum values
    """

    try:
        stat = img_inst.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geom_inst,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise


def createImageMinMaxDictByRegion(img_inst, geom_inst):
    """Create dictionary of sum statistics

    Parameters
    ----------
    img_inst : ee.Image
        Image instance
    geom_inst : ee.Geometry
        Geometry object of the region

    Returns
    -------
    dict
        Dictionary of bands' min/max and their values
    """

    try:
        stat = img_inst.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=geom_inst,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise


def createImageNumPixelsDictByRegion(img_inst, geom_inst):
    """Create dictionary of pixels' number for each band

    Parameters
    ----------
    img_inst : ee.Image
        Image instance
    geom_inst : ee.Geometry
        Geometry object of the region

    Returns
    -------
    dict
        Dictionary of bands' number of pixels and their values
    """

    try:
        pixels = img_inst.reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=geom_inst
        )
        return pixels.getInfo()
    except EEException as e:
        raise
