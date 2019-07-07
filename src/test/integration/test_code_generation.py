from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader
from latex_code_generation.code_generation import _add_filters_to_jinja, generate_meta_data_code
from rest_import.rest import request_firmware_data

from ..data.test_dict import test_dict

# pylint: disable=redefined-outer-name


class MockResponse:
    @staticmethod
    def json():
        return {'firmware': {'analysis': {}, 'meta_data': {}}}


@pytest.fixture(scope='function')
def mock_environment():
    env = Environment(
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=FileSystemLoader(str(Path(Path(__file__).parent.parent.parent, 'templates', 'default'))),
    )
    _add_filters_to_jinja(env)
    return env


def test_anything_mocked(monkeypatch):
    monkeypatch.setattr('rest_import.rest.requests.get', lambda x: MockResponse())

    anything = request_firmware_data('anything')
    assert anything


def test_latex_code_generation(mock_environment):
    result = generate_meta_data_code(mock_environment, test_dict)
    assert result
