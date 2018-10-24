import pytest
from tests.api.factories import ProcessFactory


@pytest.mark.django_db
def test_process_model():
    """ Test process model """
    # create process model instance
    process = ProcessFactory()
    assert process.type["mode"] == "sync"
    assert 'wapor' in process.type
    assert 'inputs' and 'outputs' in process.input_data
