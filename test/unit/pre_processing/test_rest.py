from json import JSONDecodeError

import pytest
from pdf_generator.pre_processing.rest import DEFAULT_URL, create_request_url, request_firmware_data


class MockResponse:
    def __init__(self, response, raises=False):
        self._response = response
        self._raises = raises

    def json(self):
        if self._raises:
            raise JSONDecodeError('non json response', '', 0)
        return self._response


def test_request_firmware_data(monkeypatch):
    monkeypatch.setattr('pdf_generator.pre_processing.rest.requests.get', lambda x: MockResponse({'firmware': {'analysis': 'A', 'meta_data': 'B'}}))
    assert request_firmware_data(None) == ('A', 'B')


def test_request_firmware_data_no_connection(monkeypatch):  # pylint: disable=invalid-name
    monkeypatch.setattr('pdf_generator.pre_processing.rest.requests.get', lambda x: MockResponse(None, True))
    with pytest.raises(RuntimeError):
        request_firmware_data(None)


def test_request_firmware_data_bad_response(monkeypatch):  # pylint: disable=invalid-name
    monkeypatch.setattr('pdf_generator.pre_processing.rest.requests.get', lambda x: MockResponse({'unknown': 'message'}))
    with pytest.raises(RuntimeError):
        request_firmware_data(None)


def test_create_request_url():
    assert create_request_url('X', None) == '{}/rest/firmware/X'.format(DEFAULT_URL)
    assert create_request_url('X', 'Y') == 'Y/rest/firmware/X'
