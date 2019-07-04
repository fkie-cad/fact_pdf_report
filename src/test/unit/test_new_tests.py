from pathlib import Path

import pytest

from latex_code_generation.code_generation import generate_meta_data_code

from rest_import.rest import create_request_url, request_firmware_data
from jinja2 import Environment, FileSystemLoader


class MockResponse:
    @staticmethod
    def json():
        return dict()


@pytest.fixture(scope='function')
def mock_environment():
    env = Environment(
        block_start_string="\BLOCK{",
        block_end_string="}",
        variable_start_string="\VAR{",
        variable_end_string="}",
        comment_start_string="\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        loader=FileSystemLoader(str(Path(Path(__file__).parent.parent.parent, "templates", 'default'))),
    )
    return env


def test_anything_mocked(monkeypatch):
    monkeypatch.setattr('rest_import.rest.requests.get', lambda x: MockResponse())

    anything = request_firmware_data('anything')
    assert anything


def test_generate_meta_code(mock_environment):
    result = generate_meta_data_code(mock_environment, {})
    assert result
