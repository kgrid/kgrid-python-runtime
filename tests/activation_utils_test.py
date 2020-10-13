import json
import unittest
from unittest.mock import MagicMock, patch
import requests
import runtime.activation_utils as au

activator_url = 'http://localhost:8080'
python_runtime_url = 'http://localhost:5000'
proxy_env_endpoint = '/proxy/environments'
activate_endpoint = '/activate/python'
mock_post_request = MagicMock(requests.post)
mock_get_request = MagicMock(requests.get)
mock_flask_request = {
    'baseUrl': 'some-url.com',
    'json': json.dumps({'entry': 'src/index.py', 'function': 'doThings', 'uri': 'naan/name/version/endpoint'})}
endpoint_map = {}


class Test(unittest.TestCase):
    def test_activate_endpoint_gets_binaries(self):
        result = au.activate_endpoint(mock_flask_request, python_runtime_url, endpoint_map)
        assert result == 'fewafewafewa'
