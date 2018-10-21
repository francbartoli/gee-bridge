import pytest
from api.process.wapor.wapor import Wapor
from api.process.tests.test_base import TestBase


@pytest.fixture(scope="class")
def wapor():
    return Wapor()


class TestWapor(TestBase):

    def test_name(self, wapor):
        assert wapor.__class__.__name__ == 'Wapor'

    def test_name_init(self, wapor):
        assert wapor.name == ""

    def test_inputs_init(self, wapor):
        assert wapor.inputs == {}

    def test_options_init(self, wapor):
        assert wapor.options == {}

    def test_outputs_init(self, wapor):
        assert wapor.outputs == {}

    def test_state_init(self, wapor):
        assert wapor.state == ""

    def test_namespace_init(self, wapor):
        assert wapor.namespace == "wapor"

    def test_mode_init(self, wapor):
        assert wapor.mode == "SYNC"