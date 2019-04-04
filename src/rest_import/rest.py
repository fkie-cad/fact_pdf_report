import json
import requests


def create_request_url():
    host = "http://127.0.0.1:5000"
    path = "/rest/firmware/"
    # firmware_uid = cmd_arg
    firmware_uid = "bab8d95fc42176abc9126393b6035e4012ebccc82c91e521b91d3bcba4832756_3801088"
    rest_url = host + path + firmware_uid
    return rest_url


def get_firmware(request_url):
    response = requests.get(request_url)
    firmware_data = response.text
    firmware_dict = json.loads(firmware_data)
    return firmware_dict['firmware']


def get_firmware_analyses(firmware_dict):
    return firmware_dict['analysis']


def get_firmware_meta_data(firmware_dict):
    return firmware_dict['meta_data']