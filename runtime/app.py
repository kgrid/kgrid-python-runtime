from os import getenv
import threading
from flask import Flask, request
import requests
import json
from flask_script import Manager
import time
from werkzeug.exceptions import HTTPException
from runtime.activation_utils import activate_endpoint

endpoints = {}

app = Flask(__name__)
activator_url = getenv('KGRID_ADAPTER_PROXY_URL', 'http://localhost:8080')
python_runtime_url = getenv('ENVIRONMENT_SELF_URL', 'http://localhost:5000')


def setup_app():
    time.sleep(3)
    print(f'Kgrid Activator URL is: {activator_url}')
    print(f'Python Runtime URL is: {python_runtime_url}')
    registration_body = {'type': 'python', 'url': python_runtime_url}
    requests.post(activator_url + '/proxy/environments', data=json.dumps(registration_body),
                  headers={'Content-Type': 'application/json'})
    requests.get(activator_url + '/activate/python')


@app.route('/info', methods=['GET'])
def info():
    info_up = {'Status': 'Up'}
    return info_up


@app.route('/deployments', methods=['POST'])
def deployments():
    return activate_endpoint(request, python_runtime_url, endpoints)


@app.route('/endpoints', methods=['GET'])
def endpoint_list():
    writeable_endpoints = {}
    for element in endpoints.items():
        element_uri = element[1]['uri']
        writeable_endpoints[element_uri] = element[1]
        del writeable_endpoints[element_uri]['function']
    return writeable_endpoints


@app.route('/<endpoint_key>', methods=['POST'])
def execute_endpoint(endpoint_key):
    print(f'activator sent over json in execute request {request.json}')
    result = endpoints[endpoint_key]['function'](request.json)
    return {'result': result}


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        'code': e.code,
        'name': e.name,
        'description': e.description,
    })
    response.content_type = 'application/json'
    return response


@app.errorhandler(SyntaxError)
def handle_syntax_error(e):
    resp = {'Error': str(e)}
    return resp, 400


@app.errorhandler(Exception)
def handle_exception(e):
    resp = {'Exception': str(e)}
    return resp, 400


manager = Manager(app)


@manager.command
def runserver():
    thread = threading.Thread(target=setup_app)
    thread.start()
    app.run()


if __name__ == '__main__':
    manager.run()
