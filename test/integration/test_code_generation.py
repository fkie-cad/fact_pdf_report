import pytest
from pdf_generator.pre_processing.rest import request_firmware_data
from pdf_generator.tex_generation.template_engine import Engine
from test.data.test_dict import TEST_DICT

# pylint: disable=redefined-outer-name


class MockResponse:
    @staticmethod
    def json():
        return {'firmware': {'analysis': {}, 'meta_data': {}}}


@pytest.fixture(scope='function')
def stub_engine():
    return Engine()


def test_anything_mocked(monkeypatch):
    monkeypatch.setattr('pdf_generator.pre_processing.rest.requests.get', lambda x: MockResponse())

    anything = request_firmware_data('anything')
    assert anything


def test_latex_code_generation(stub_engine: Engine):
    result = stub_engine.render_meta_template(TEST_DICT)
    assert result
