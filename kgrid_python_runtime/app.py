from os import getenv, makedirs, path
import os
import threading
from flask import Flask, request
import json
from flask_script import Manager
import time
from werkzeug.exceptions import HTTPException
import shutil
import sys
import importlib
import subprocess
import pyshelf  # must be imported to activate and execute KOs
import requests

endpoints = {}

app = Flask(__name__)
app_port = getenv('KGRID_PYTHON_ENV_PORT', 5000)
activator_url = getenv('KGRID_PROXY_ADAPTER_URL', 'http://localhost:8080')
python_runtime_url = getenv('KGRID_PYTHON_ENV_URL', f'http://localhost:{app_port}')
pyshelf_folder = 'pyshelf/'


def setup_app():
    time.sleep(3)
    print(f'Kgrid Activator URL is: {activator_url}')
    print(f'Python Runtime URL is: {python_runtime_url}')
    registration_body = {'type': 'python', 'url': python_runtime_url}
    try:
        response = requests.post(activator_url + '/proxy/environments', data=json.dumps(registration_body),
                                 headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            print(f'Could not register this runtime at the url {activator_url} '
                  f'Check that the activator is running at that address.')
            os._exit(-1)
        else:
            requests.get(activator_url + '/activate/python')
    except requests.ConnectionError as err:
        print(f'Could not connect to remote activator at {activator_url} Error: {err}')
        os._exit(-1)


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
    print('Error: ' + str(e))
    resp = {'Error': str(e)}
    return resp, 400


@app.errorhandler(Exception)
def handle_exception(e):
    print('Exception: ' + str(e))
    resp = {'Exception': str(e)}
    return resp, 400


def activate_endpoint(activation_request, python_runtime_url, endpoints):
    request_json = activation_request.json
    print(f'activator sent over json in activation request {request_json}')
    hash_key = copy_artifacts_to_shelf(activation_request)
    entry_name = request_json['entry'].rsplit('.', 2)[0].replace('/', '.')
    package_name = 'pyshelf.' + hash_key + '.' + entry_name
    if package_name in sys.modules:
        for module in list(sys.modules):
            if module.startswith('pyshelf.' + hash_key):
                importlib.reload(sys.modules[module])
    else:
        import_package(hash_key, package_name)
    function = eval(f'{package_name}.{request_json["function"]}')
    endpoints[hash_key] = {'uri': request_json['uri'], 'path': package_name, 'function': function}
    response = {'baseUrl': python_runtime_url, 'endpointUrl': hash_key}
    return response


def import_package(hash_key, package_name):
    dependency_requirements = pyshelf_folder + hash_key + '/requirements.txt'
    if path.exists(dependency_requirements):
        subprocess.check_call([
            sys.executable,
            '-m',
            'pip',
            'install',
            '-r',
            dependency_requirements])
    importlib.import_module(package_name)


def copy_artifacts_to_shelf(activation_request):
    request_json = activation_request.json
    hash_key = request_json['uri'].replace('/', '_').replace('.', '_')

    if path.exists(pyshelf_folder + hash_key):
        shutil.rmtree(pyshelf_folder + hash_key)
    for artifact in request_json['artifact']:
        artifact_path = pyshelf_folder + hash_key + '/' + artifact
        dir_name = artifact_path.rsplit('/', 1)[0]
        if not path.isdir(dir_name):
            makedirs(dir_name)
        artifact_binary = requests.get(request_json['baseUrl'] + artifact, stream=True)
        with open(artifact_path, 'wb') as handle:
            for data in artifact_binary.iter_content():
                handle.write(data)

    return hash_key


manager = Manager(app)


@manager.command
def runserver():
    thread = threading.Thread(target=setup_app)
    thread.start()
    app.run(port=app_port)


if __name__ == '__main__':
    manager.run()
