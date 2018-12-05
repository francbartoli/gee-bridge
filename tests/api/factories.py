import factory
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from rest_auth.models import TokenModel
from api.models import Process
from collections import namedtuple


def seq_type():
    """
    Sequence for type json field
    """
    return {
        "mode": "sync",
        "wapor": {
            "template": "ALG"
        }
    }


def seq_aoi(toomany=False):
    """
    Sequence for aoi json field
    """
    Coords = namedtuple('Coords', ['too_many_pixels', 'valid_pixels'])
    too_many_pixels = [[
        [17.578125, 19.31114335506464],
        [32.6953125, -3.513421045640032],
        [34.453125, 19.31114335506464],
        [17.578125, 19.31114335506464]
    ]]
    valid_pixels = [[
        [26.6, 26.6],
        [26.7, 26.6],
        [26.7, 26.7],
        [26.6, 26.7],
        [26.6, 26.6]
    ]]
    coords = Coords(too_many_pixels, valid_pixels)
    if toomany:
        coordinates = coords.too_many_pixels
    else:
        coordinates = coords.valid_pixels
    AOI = namedtuple('AOI', ['fc', 'ft', 'poly'])
    fc = [{
        "type": "FeatureCollection",
        "features": [{
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            },
            "type": "Feature",
            "properties": {}
        }]
    }]
    ft = [{
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates
        },
        "type": "Feature",
        "properties": {}
    }]
    poly = [{
        "type": "Polygon",
        "coordinates": coordinates
    }]
    aoi = AOI(fc, ft, poly)
    return aoi


def seq_toi():
    """
    Sequence for toi json field
    """
    return [{"enddate": "2015-12-31", "startdate": "2015-1-1"}]


def seq_inputdata(level):
    """
    Sequence for input_data json field
    """
    return {
        "inputs": [
            {
                "dataset": "projects/fao-wapor/{lev}/{lev}_AETI_D".format(
                    lev=level
                ),
                "metadata": "",
                "bands": [""]
            },
            {
                "dataset": "projects/fao-wapor/{lev}/{lev}_NPP_D".format(
                    lev=level
                ),
                "metadata": "",
                "bands": [""]
            }
        ],
        "outputs": {}
    }


def seq_outputdata():
    """
    Sequence for output_data json field
    """
    return {}


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: u'marmee_{}'.format(n))
    password = factory.LazyAttribute(lambda n: make_password("password"))
    email = factory.Sequence(lambda n: u'marmee_{}@test.com'.format(n))


class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TokenModel

    key = factory.LazyFunction(get_random_string)
    user = factory.SubFactory(UserFactory)


class ProcessFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Process

    id = factory.Faker('uuid4')
    name = factory.Sequence(lambda n: u'process_{}'.format(n))
    type = factory.LazyFunction(seq_type)
    owner = factory.SubFactory(UserFactory)
    # FIXME: force aoi to be just polygon with not too many pixels
    aoi = factory.LazyFunction(lambda: seq_aoi(toomany=False).poly)
    toi = factory.LazyFunction(seq_toi)
    input_data = factory.LazyFunction(lambda: seq_inputdata("L1"))
    output_data = factory.LazyFunction(seq_outputdata)
