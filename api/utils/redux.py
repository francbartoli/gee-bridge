from ee import Reducer, EEException


def createImageMeanDictByRegion(img_inst, geom):

    try:
        stat = img_inst.reduceRegion(
            reducer=Reducer.mean(),
            geometry=geom,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise


def createImageSumDictByRegion(img_inst, geom):

    try:
        stat = img_inst.reduceRegion(
            reducer=Reducer.sum(),
            geometry=geom,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise


def createImageMinMaxDictByRegion(img_inst, geom):

    try:
        stat = img_inst.reduceRegion(
            reducer=Reducer.minMax(),
            geometry=geom,
            scale=30,
            maxPixels=1e9
        )
        return stat.getInfo()
    except EEException as e:
        raise
