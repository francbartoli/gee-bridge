import pytest
from api.process.wapor.wapor import Wapor
from api.process.tests.test_base import TestBase


@pytest.fixture
def wapor():
    return Wapor()


class TestWapor(TestBase):
    cls = Wapor

    def test_name(self):
        assert self.cls().name == 'Wapor'

    def test_name_init(wapor):
        import ipdb; ipdb.set_trace()
        assert wapor.name == ""

    def test_inputs_init(wapor):
        assert wapor.inputs == {}

    def test_options_init(wapor):
        assert wapor.options == {}

    def test_outputs_init(wapor):
        assert wapor.outputs == {}

    def test_state_init(wapor):
        assert wapor.state == ""

    def test_namespace_init(wapor):
        assert wapor.namespace == "wapor"

    def test_mode_init(wapor):
        assert wapor.mode == "SYNC"