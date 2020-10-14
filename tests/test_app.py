import json
import unittest
from unittest.mock import MagicMock, patch
import requests
import runtime.app as app

activator_url = 'http://localhost:8080'
python_runtime_url = 'http://localhost:5000'
proxy_env_endpoint = '/proxy/environments'
activate_endpoint = '/activate/python'
mock_post_request = MagicMock(requests.post)
mock_get_request = MagicMock(requests.get)
mock_flask_request = {
    'json': json.dumps({'entry': 'src/index.py', 'function': 'doThings', 'uri': 'naan/name/version/endpoint'})}


@patch('requests.post', mock_post_request)
@patch('requests.get', mock_get_request)
class Test(unittest.TestCase):
    def test_setup_app_sends_post_to_activator(self):
        registration_body = json.dumps({"type": "python", "url": python_runtime_url})
        headers = {'Content-Type': 'application/json'}
        app.setup_app()

        mock_post_request.assert_called_with(
            activator_url + proxy_env_endpoint,
            data=registration_body,
            headers=headers)

    def test_setup_app_tells_activator_to_activate(self):
        app.setup_app()

        mock_get_request.assert_called_with(
            activator_url + activate_endpoint)

    def test_info_returns_status_up(self):
        info = app.info()
        self.assertEqual({'Status': 'Up'}, info)

