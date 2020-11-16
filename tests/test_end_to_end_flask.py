import json
import os
import shutil
import unittest
import responses
from kgrid_python_runtime.app import app

naan = 'naan'
name = 'name'
version = 'version'
endpoint = 'endpoint'
activator_url = 'http://localhost:8080'
python_runtime_url = 'http://localhost:5000'
proxy_env_endpoint = '/proxy/environments'

payload_return_value = b'def welcome(json_input):\n    return f\'Welcome to the Knowledge Grid, {json_input["name"]}\''
flask_request_json = {
    'entry': 'src/index.py',
    'function': 'welcome',
    'uri': f'{naan}/{name}/{version}/{endpoint}',
    'artifact': ['src/index.py'],
    'baseUrl': f'{activator_url}/proxy/{naan}/{name}/{version}/'
}


class Tests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['TEST_SHELF_PARENT'] = ""
        responses.add(responses.GET, f'{activator_url}{proxy_env_endpoint}',
                      body={"registered"}, status=200)
        self.app = app.test_client()

    def tearDown(self):
        if os.path.exists(f'pyshelf/{naan}_{name}_{version}_{endpoint}'):
            shutil.rmtree(f'pyshelf/{naan}_{name}_{version}_{endpoint}')

    def test_info(self):
        response = self.app.get('/info')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'{"activatorUrl":"http://localhost:8080",'
                         b'"app":"kgrid-python-runtime",'
                         b'"engine":"python",'
                         b'"status":"up",'
                         b'"url":"http://localhost:5000",'
                         b'"version":"0.0.12"}\n', response.data)

    @responses.activate
    def test_activate(self):
        responses.add(responses.GET, f'{activator_url}/proxy/{naan}/{name}/{version}/src/index.py',
                      body=payload_return_value, status=200)

        response = self.app.post('/endpoints', json=flask_request_json)
        response_json = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response_json['activated'])
        self.assertEqual(python_runtime_url, response_json['baseUrl'])
        self.assertEqual(f'{naan}/{name}/{version}/{endpoint}', response_json['id'])
        self.assertEqual('Activated', response_json['status'])
        self.assertEqual(f'{naan}_{name}_{version}_{endpoint}', response_json['uri'])

    @responses.activate
    def test_execute(self):
        endpoint_location = f'{naan}_{name}_{version}_{endpoint}'

        responses.add(responses.GET, f'{activator_url}/proxy/{naan}/{name}/{version}/src/index.py',
                      body=payload_return_value, status=200)
        self.app.post('/endpoints', json=flask_request_json)
        response = self.app.post(f'/{endpoint_location}', json=dict(name='Hank'))
        self.assertEqual(response.status_code, 200)
        json_string = '{"result":"Welcome to the Knowledge Grid, Hank"}\n'
        self.assertEqual(response.data.decode('utf-8'), json_string)
