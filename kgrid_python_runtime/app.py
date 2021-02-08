from datetime import datetime
from os import getenv, makedirs, path
import json
import threading
import time
import shutil
import sys
import importlib
import subprocess
import requests
import logging
from flask import Flask, request, jsonify
from flask_api import status
from flask_script import Manager
import pyshelf  # must be imported to activate and execute KOs
from kgrid_python_runtime.context import Context
from kgrid_python_runtime.exceptions import error_handlers

PYSHELF_DIRECTORY = 'pyshelf'
PYTHON = 'python'

werkzueg_logger = logging.getLogger('werkzeug')
werkzueg_logger.setLevel(logging.ERROR)
is_debug_mode = getenv('DEBUG', False)
log = logging.getLogger('logger')
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
if is_debug_mode:
    log.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)

this_dir = path.dirname(path.realpath(__file__))
with open(path.join(this_dir, 'VERSION')) as version_file:
    version = version_file.read().strip()

endpoint_context = Context()

app = Flask(__name__)
app.register_blueprint(error_handlers)
app_port = getenv('KGRID_PYTHON_ENV_PORT', 5000)
if getenv('PORT') is not None:
    app_port = int(getenv('PORT'))
activator_url = getenv('KGRID_PROXY_ADAPTER_URL', 'http://localhost:8080')
python_runtime_url = getenv('KGRID_PYTHON_ENV_URL', f'http://localhost:{app_port}')


def setup_app():
    time.sleep(3)
    log.debug(f'Kgrid Activator URL is: {activator_url}')
    log.debug(f'Python Runtime URL is: {python_runtime_url}')
    if path.isfile('context.json'):
        with open('context.json') as context_json:
            endpoint_context.endpoints = json.load(context_json)
        for key, endpoint in endpoint_context.endpoints.items():
            hash_key = key
            entry_name = endpoint['entry']
            function_name = endpoint['function_name']
            checksum = endpoint['checksum']
            uri = endpoint['id']
            package_name = f'{PYSHELF_DIRECTORY}.{hash_key}.{entry_name}'
            activate_endpoint(package_name, hash_key, entry_name, function_name, uri, checksum)

    register_with_activator(True)


def register_with_activator(request_refresh):
    registration_body = {
        'engine': PYTHON,
        'version': version,
        'url': python_runtime_url,
        'forceUpdate': request_refresh
    }
    global activator_url
    try:
        if activator_url.endswith('/'):
            activator_url = activator_url[:-1]
        response = requests.post(activator_url + '/proxy/environments', data=json.dumps(registration_body),
                                 headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            log.warning(f'Could not register this runtime at the url {activator_url} '
                            f'Check that the activator is running at that address.')
    except requests.ConnectionError as err:
        log.warning(f'Could not connect to remote activator at {activator_url} Error: {err}')


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
    app_name = 'kgrid-python-runtime'
    return {
        'app': app_name,
        'version': version,
        'status': 'up',
        'url': python_runtime_url,
        'engine': PYTHON,
        'activatorUrl': activator_url
    }


@app.route('/endpoints', methods=['POST'])
def deployments():
    return activate_from_request(request)


@app.route('/endpoints', methods=['GET'])
def endpoint_list():
    writeable_endpoints = []
    endpoints = endpoint_context.endpoints.items()
    for element in endpoints:
        endpoint = make_serializable_endpoint(element[1])
        writeable_endpoints.append(endpoint)
    return jsonify(writeable_endpoints)


@app.route('/endpoints/<naan>/<name>/<version>/<endpoint>', methods=['GET'])
def get_endpoint(naan, name, version, endpoint):
    hash_key = endpoint_context.hash_uri(f'{naan}/{name}/{version}/{endpoint}')
    element = endpoint_context.endpoints[hash_key]
    endpoint = make_serializable_endpoint(element)
    return jsonify(endpoint)


@app.route('/register', methods=['GET'])
def register():
    register_with_activator(True)
    return {"Registered with": activator_url}


def make_serializable_endpoint(element):
    serializable_endpoint = dict(element)
    if serializable_endpoint['url'] is None:
        del serializable_endpoint['url']
    del serializable_endpoint['function']
    del serializable_endpoint['path']
    del serializable_endpoint['entry']
    return serializable_endpoint


@app.route('/<endpoint_key>', methods=['POST'])
def execute_endpoint(endpoint_key):
    data = request.get_data()
    if request.content_type == 'application/json':
        try:
            result = endpoint_context.endpoints[endpoint_key]['function'](request.json)
        except KeyError:
            raise KeyError(f'Could not find endpoint {endpoint_key} in python runtime.')
    else:
        try:
            result = endpoint_context.endpoints[endpoint_key]['function'](data.decode("UTF-8"))
        except KeyError:
            raise KeyError(f'Could not find endpoint {endpoint_key} in python runtime.')

    return {'result': result}


def activate_from_request(activation_request):
    request_json = activation_request.json
    log.debug(f'activator sent over json in activation request {request_json}')
    hash_key = get_hash_key(activation_request)
    entry_name = request_json['entry'].rsplit('.', 2)[0].replace('/', '.')
    package_name = f'{PYSHELF_DIRECTORY}.{hash_key}.{entry_name}'
    function_name = request_json['function']
    uri = request_json['uri']
    if 'checksum' in request_json:
        checksum = request_json['checksum']
    else:
        checksum = None
    if hash_key not in endpoint_context.endpoints:
        endpoint_context.endpoints[hash_key] = {'is_processing': True}
        copy_artifacts_to_shelf(activation_request)
        return activate_endpoint(package_name, hash_key, entry_name, function_name, uri, checksum)
    if getenv('KGRID_PYTHON_CACHE_STRATEGY') == 'always' and hash_key in endpoint_context.endpoints:
        return {'baseUrl': python_runtime_url, 'url': endpoint_context.endpoints[hash_key]['url'],
                "activated": endpoint_context.endpoints[hash_key]['activated'],
                "status": endpoint_context.endpoints[hash_key]['status'], "id": uri, 'uri': hash_key}
    elif getenv('KGRID_PYTHON_CACHE_STRATEGY') == 'use_checksum' and hash_key in endpoint_context.endpoints and \
            'checksum' in request_json and \
            checksum == endpoint_context.endpoints[hash_key]['checksum']:
        return {'baseUrl': python_runtime_url, 'url': endpoint_context.endpoints[hash_key]['url'],
                "activated": endpoint_context.endpoints[hash_key]['activated'],
                "status": endpoint_context.endpoints[hash_key]['status'], "id": uri, 'uri': hash_key}
    elif endpoint_context.endpoints[hash_key]['is_processing']:
        log.debug(f'Endpoint {hash_key} is being processed already, try again later.')
        return ({'baseUrl': python_runtime_url, 'url': endpoint_context.endpoints[hash_key]['url'],
                 "activated": endpoint_context.endpoints[hash_key]['activated'],
                 "status": 'Endpoint is in processing, try again later.', "id": uri, 'uri': hash_key},
                status.HTTP_503_SERVICE_UNAVAILABLE)
    else:
        log.debug(f'processing endpoint: {hash_key}.')
        copy_artifacts_to_shelf(activation_request)
        endpoint_context.endpoints[hash_key]['is_processing'] = True
        return activate_endpoint(package_name, hash_key, entry_name, function_name, uri, checksum)


def activate_endpoint(package_name, hash_key, entry_name, function_name, uri, checksum):
    log.debug(f'Activating endpoint: {uri}')
    if package_name in sys.modules:
        for module in list(sys.modules):
            if module.startswith(f'{PYSHELF_DIRECTORY}.{hash_key}'):
                importlib.reload(sys.modules[module])
    else:
        import_package(hash_key, package_name)

    function = eval(f'{package_name}.{function_name}')
    activated_time = datetime.now()
    status = "Activated"
    if python_runtime_url.endswith("/"):
        url = python_runtime_url + hash_key
    else:
        url = python_runtime_url + "/" + hash_key
    insert_endpoint_into_context(hash_key, activated_time, entry_name, function, function_name, url, package_name, uri,
                                 status, checksum)
    response = {'baseUrl': python_runtime_url, 'url': url, "activated": activated_time, "status": status,
                "id": uri, 'uri': hash_key}
    endpoint_context.endpoints[hash_key]['is_processing'] = False
    return response


def insert_endpoint_into_context(hash_key, activated_time, entry_name, function, function_name, url, package_name, uri,
                                 endpoint_status, checksum):
    endpoint_context.endpoints[hash_key] = {
        'url': url,
        'path': package_name,
        'function': function,
        'function_name': function_name,
        'entry': entry_name,
        'id': uri,
        'activated': activated_time,
        'status': endpoint_status,
        'checksum': checksum,
        'is_processing': True
    }

    if 'TEST_CONTEXT' in app.config:
        context_file = app.config['TEST_CONTEXT']
    else:
        context_file = 'context.json'
    with open(context_file, 'w') as outfile:
        outfile.write(json.dumps(endpoint_context.endpoints, indent=4, sort_keys=True, default=str))


def import_package(hash_key, package_name):
    dependency_requirements = f'{PYSHELF_DIRECTORY}/{hash_key}/requirements.txt'
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
    except SyntaxError as e:
        insert_endpoint_into_context(hash_key, datetime.now(), None, None, None, None, {'uri': hash_key}, str(e))
        shutil.rmtree(f'{PYSHELF_DIRECTORY}/{hash_key}')
        raise e


def get_hash_key(req):
    return endpoint_context.hash_uri(req.json['uri'])


def copy_artifacts_to_shelf(activation_request):
    request_json = activation_request.json
    hash_key = get_hash_key(activation_request)

    endpoint_directory = f'{PYSHELF_DIRECTORY}/{hash_key}'
    if path.exists(endpoint_directory):
        shutil.rmtree(endpoint_directory)
    for artifact in request_json['artifact']:
        artifact_path = f'{endpoint_directory}/{artifact}'
        dir_name = artifact_path.rsplit('/', 1)[0]
        if not path.isdir(dir_name):
            makedirs(dir_name)
        artifact_binary = requests.get(request_json['baseUrl'] + artifact, stream=True)
        with open(artifact_path, 'wb') as handle:
            for data in artifact_binary.iter_content():
                handle.write(data)


manager = Manager(app)


def heart_beat():
    log.debug(f'The heart hath beaten, registering with activator')
    register_with_activator(False)


def start_heart():
    heart_rate = int(getenv('KGRID_PROXY_HEARTBEAT_INTERVAL', 30))
    log.debug(f'Starting heart beat at every {heart_rate} seconds')
    if heart_rate >= 5:
        ticker = threading.Event()
        while not ticker.wait(heart_rate):
            heart_beat()


@manager.command
def runserver():
    app_thread = threading.Thread(target=setup_app)
    heartbeat_thread = threading.Thread(target=start_heart)
    app_thread.start()
    heartbeat_thread.start()
    app.run(port=app_port, host='0.0.0.0', debug=is_debug_mode)


if __name__ == '__main__':
    manager.run()
