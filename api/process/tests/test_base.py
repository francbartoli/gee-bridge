import pytest
from api.process.base import Base

class TestBase(object):
    cls = Base

    def test_name(self):
        assert self.cls.name
    def test_inputs(self):
        assert self.cls.inputs
    def test_options(self):
        assert self.cls.options
    def test_outputs(self):
        assert self.cls.outputs
    def test_state(self):
        assert self.cls.state