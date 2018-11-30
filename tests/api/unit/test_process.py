import pytest
from ee import EEException
from tests.api.factories import (
    ProcessFactory,
    seq_inputdata,
    seq_outputdata,
    seq_aoi,
    seq_toi,
    seq_type
)


@pytest.mark.django_db
def test_create_process_model_valid_aoi():
    """ Test process model with valid aoi"""
    # create process model instance with valid aoi
    process = ProcessFactory()

    assert process.type["mode"] == "sync"
    assert 'wapor' in process.type
    assert 'inputs' and 'outputs' in process.input_data
    assert not process.output_data


@pytest.mark.django_db
def test_create_process_model_not_valid_aoi():
    """ Test process model with too many pixels"""
    # create process model instance with too many pixels aoi
    with pytest.raises(EEException):
        ProcessFactory(aoi=seq_aoi(toomany=True).poly)
