from os import getenv, makedirs, path
import os
import json
import threading
import time
import shutil
import sys
import importlib
import subprocess
import requests
import pkg_resources
from flask import Flask, request
from flask_script import Manager
import pyshelf  # must be imported to activate and execute KOs
from kgrid_python_runtime.context import Context
from kgrid_python_runtime.exceptions import error_handlers

version = pkg_resources.require("kgrid-python-runtime")[0].version

endpoint_context = Context()

app = Flask(__name__)
app.register_blueprint(error_handlers)
app_port = getenv('KGRID_PYTHON_ENV_PORT', 5000)
if getenv('PORT') is not None:
    app_port = int(getenv('PORT'))
activator_url = getenv('KGRID_PROXY_ADAPTER_URL', 'http://localhost:8080')
python_runtime_url = getenv('KGRID_PYTHON_ENV_URL', f'http://localhost:{app_port}')


def get_pyshelf_dir():
    if 'TEST_SHELF_PARENT' in app.config:
        return f'{app.config["TEST_SHELF_PARENT"]}pyshelf/'
    else:
        return 'pyshelf/'


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


@app.route('/', methods=['GET'])
def root():
    return {
        'Name': 'Kgrid Python Runtime',
        'Description': 'Running Knowledge Objects written in Python',
        'Version': version,
        'Info': f'http://localhost:{app_port}/info',
        'Endpoints': f'http://localhost:{app_port}/endpoints'
    }


@app.route('/info', methods=['GET'])
def info():
    return {
        'Status': 'Up',
        'Activator': activator_url,
        'Python Runtime': python_runtime_url
    }


@app.route('/deployments', methods=['POST'])
def deployments():
    return activate_endpoint(request)


@app.route('/endpoints', methods=['GET'])
def endpoint_list():
    writeable_endpoints = {}
    endpoints = endpoint_context.endpoints.items()
    for element in endpoints:
        element_uri = endpoint_context.hash_uri(element[1]['uri'])
        writeable_endpoints[element_uri] = dict(element[1])
        del writeable_endpoints[element_uri]['function']
    return writeable_endpoints


@app.route('/<endpoint_key>', methods=['POST'])
def execute_endpoint(endpoint_key):
    data = request.get_data()
    print(f'activator sent over data in execute request {data}')
    if request.content_type == 'application/json':
        try:
            result = endpoint_context.endpoints[endpoint_key]['function'](request.json)
        except KeyError as e:
            raise KeyError(f'Could not find endpoint {endpoint_key} in python runtime.')
    else:
        try:
            result = endpoint_context.endpoints[endpoint_key]['function'](data.decode("UTF-8"))
        except KeyError as e:
            raise KeyError(f'Could not find endpoint {endpoint_key} in python runtime.')

    return {'result': result}


def activate_endpoint(activation_request):
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
    endpoint_context.endpoints[hash_key] = {'uri': request_json['uri'], 'path': package_name, 'function': function,
                                            'entry': entry_name}
    response = {'baseUrl': python_runtime_url, 'endpointUrl': hash_key}
    return response


def import_package(hash_key, package_name):
    dependency_requirements = get_pyshelf_dir() + hash_key + '/requirements.txt'
    if path.exists(dependency_requirements):
        subprocess.check_call([
            sys.executable,
            '-m',
            'pip',
            'install',
            '-r',
            dependency_requirements])
    try:
        importlib.import_module(package_name)
    except Exception as e:
        shutil.rmtree(f'{get_pyshelf_dir()}/{hash_key}')
        raise SyntaxError(f'Error importing package: {package_name} in python runtime. Error: {e.msg}')


def copy_artifacts_to_shelf(activation_request):
    pyshelf_folder = get_pyshelf_dir()
    request_json = activation_request.json
    hash_key = endpoint_context.hash_uri(request_json['uri'])

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
    app.run(port=app_port, host='0.0.0.0')


if __name__ == '__main__':
    manager.run()
