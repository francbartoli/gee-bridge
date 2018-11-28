import factory
import json
from django.contrib.auth.models import User
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


def seq_aoi():
    """
    Sequence for aoi json field
    """
    AOI = namedtuple('AOI', ['fc', 'ft', 'poly'])
    fc = [{
        "type": "FeatureCollection",
        "features": [{
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [17.578125, 19.31114335506464],
                        [32.6953125, -3.513421045640032],
                        [34.453125, 19.31114335506464],
                        [17.578125, 19.31114335506464]
                    ]
                ]
            },
            "type": "Feature",
            "properties": {}
        }]
    }]
    ft = [{
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [17.578125, 19.31114335506464],
                    [32.6953125, -3.513421045640032],
                    [34.453125, 19.31114335506464],
                    [17.578125, 19.31114335506464]
                ]
            ]
        },
        "type": "Feature",
        "properties": {}
    }]
    poly = [{
        "type": "Polygon",
        "coordinates": [
            [
                [17.578125, 19.31114335506464],
                [32.6953125, -3.513421045640032],
                [34.453125, 19.31114335506464],
                [17.578125, 19.31114335506464]
            ]
        ]
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


class ProcessFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Process

    id = factory.Faker('uuid4')
    name = factory.Sequence(lambda n: u'process_{}'.format(n))
    type = factory.LazyFunction(seq_type)
    owner = factory.SubFactory(UserFactory)
    # FIXME: force aoi to be just polygon
    aoi = factory.LazyFunction(lambda: seq_aoi().poly)
    toi = factory.LazyFunction(seq_toi)
    input_data = factory.LazyFunction(lambda: seq_inputdata("L1"))
    output_data = factory.LazyFunction(seq_outputdata)

    # simulate algorithm execution by changing input/output data
    # @factory.post_generation
    # def input_data(self, create, extracted, **kwargs):
    #     empty_output = [
    #         {
    #             "maps": {},
    #             "stats": {},
    #             "tasks": {},
    #             "errors": {}
    #         }
    #     ]
    #     output = json.dumps(empty_output)

    #     if not create:
    #         return

    #     if extracted and isinstance(extracted, dict):
    #         self.input_data = extracted
    #         output_data = extracted
    #         output_data.update(outputs=output)
    #         self.output_data = output_data
