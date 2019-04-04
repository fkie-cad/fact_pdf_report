import json

import requests


def create_request_url(firmware_uid):
    base_url = 'http://127.0.0.1:5000/rest/firmware/'
    return '{}{}'.format(base_url, firmware_uid)


def request_firmware_data(request_url):
    response = requests.get(request_url)
    firmware_data = response.json()

    return firmware_data['firmware']['analysis'], firmware_data['firmware']['meta_data']
