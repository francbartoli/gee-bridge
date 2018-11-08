import pytest
import json
from tests.api.factories import ProcessFactory, seq_inputdata


@pytest.mark.django_db
def test_process_model():
    """ Test process model """
    # create process model instance
    process = ProcessFactory(input_data=seq_inputdata())
    assert process.type["mode"] == "sync"
    assert 'wapor' in process.type
    assert 'inputs' and 'outputs' in process.input_data
    assert 'inputs' and 'outputs' in process.output_data
    assert isinstance(json.loads(process.output_data['outputs'])[0], dict)
    assert 'maps' and 'stats' and 'tasks' and 'errors' in json.loads(
        process.output_data['outputs']
    )[0]
