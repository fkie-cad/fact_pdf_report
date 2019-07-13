from json import JSONDecodeError

import requests

DEFAULT_URL = 'http://localhost:5000'


def create_request_url(firmware_uid, server_url):
    return '{}/rest/firmware/{}?summary=true'.format(server_url if server_url else DEFAULT_URL, firmware_uid)


def request_firmware_data(request_url):
    try:
        response = requests.get(request_url)
        firmware_data = response.json()
        return firmware_data['firmware']['analysis'], firmware_data['firmware']['meta_data']
    except (JSONDecodeError, requests.ConnectionError):
        raise RuntimeError('FACT server is not reachable') from None
    except KeyError:
        raise RuntimeError('Response did not contain a valid firmware') from None
