import os
import unittest
from os import makedirs
from unittest.mock import MagicMock, patch
import requests
from requests import Response

import runtime.activation_utils as au
from werkzeug.local import LocalProxy
import importlib

naan = 'naan'
name = 'name'
version = 'version'
endpoint = 'endpoint'
activator_url = 'http://activator-url:1337'
python_runtime_url = 'http://localhost:5000'
proxy_env_endpoint = '/proxy/environments'
mock_eval = MagicMock()
mock_get_request = MagicMock(requests.get)
mock_requests_response = MagicMock(Response)
mock_iter_content = MagicMock(Response.iter_content)
mock_iter_content.return_value(b'def welcome(json_input):\n    return "Welcome to Knowledge Grid,")')
mock_get_request.return_value = mock_requests_response

mock_import = MagicMock(importlib.import_module)
mock_flask_request = MagicMock(LocalProxy)
mock_flask_request.baseUrl = 'some-url.com'
mock_flask_request.json = {
    'entry': 'src/index.py',
    'function': 'doThings',
    'uri': f'{naan}/{name}/{version}/{endpoint}',
    'artifact': ['src/index.py'],
    'baseUrl': f'{activator_url}/proxy/{naan}/{name}/{version}'
}
endpoint_map = {}


@patch('requests.get', mock_get_request)
# @patch('importlib.import_module', mock_import)
class Test(unittest.TestCase):
    def test_activate_endpoint_gets_binaries(self):
        makedirs(f'../shelf/{naan}_{name}_{version}_{endpoint}/src')
        result = au.activate_endpoint(mock_flask_request, python_runtime_url, endpoint_map)
        assert result == 'fewafewafewa'
        os.rmdir(f'../shelf/{naan}_{name}_{version}_{endpoint}')
