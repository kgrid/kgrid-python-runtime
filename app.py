import os
import sys
import threading
from flask import Flask, request
from os import getenv, makedirs
import requests
import json
from flask_script import Manager
import importlib
import shelf
import time
import subprocess
import traceback
from werkzeug.exceptions import HTTPException

endpoints = {}

app = Flask(__name__)
activator_url = getenv("KGRID_ADAPTER_PROXY_URL", "http://localhost:8080")
python_runtime_url = getenv("ENVIRONMENT_SELF_URL", "http://localhost:5000")


@app.errorhandler(HTTPException)
def handle_httpexception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.errorhandler(SyntaxError)
def handle_syntaxerror(e):
    resp = {"Error":str(e)}
    return resp, 400

@app.errorhandler(Exception)
def handle_exception(e):
    resp = {"Exception":str(e)}
    return resp, 400


def setup_app():
    time.sleep(3)
    print(f"Kgrid Activator URL is: {activator_url}")
    print(f"Python Runtime URL is: {python_runtime_url}")
    registration_body = {'type': 'python', 'url': python_runtime_url}
    requests.post(activator_url + "/proxy/environments", data=json.dumps(registration_body),
                  headers={'Content-Type': "application/json"})
    requests.get(activator_url + "/activate/python")


@app.route("/info", methods=['GET'])
def info():
    info_up = {'Status': 'Up'}
    return info_up


@app.route("/deployments", methods=['POST'])
def deployments():
    print(f"activator sent over json in activation request {request.json}")
    hash_key = copy_artifacts_to_shelf()
    entry_name = request.json['entry'].rsplit('.', 2)[0].replace('/', '.')
    package_name = 'shelf.' + hash_key + '.' + entry_name
    if package_name in sys.modules:
        del(sys.modules[package_name])
    import_package(hash_key, package_name)
    function = eval(package_name + "." + request.json['function'])
    endpoints[hash_key] = {'uri': request.json['uri'], 'path': package_name, 'function': function }
    response = {'baseUrl': python_runtime_url, 'endpointUrl': hash_key}
    return response


def import_package(hash_key, package_name):
    dependency_requirements = 'shelf/' + hash_key + '/requirements.txt'
    if os.path.exists(dependency_requirements):
        print(f'installing dependencies for KO: {package_name}')
        run_result = subprocess.check_call([
            sys.executable,
            '-m',
            'pip',
            'install',
            '-r',
            (dependency_requirements)])
        print(f'dependencies installed. result: {run_result}')
    importlib.import_module(package_name)


def copy_artifacts_to_shelf():
    hash_key = request.json['uri'].replace('/', '_').replace('.', '_')
    for artifact in request.json['artifact']:
        artifact_path = 'shelf/' + hash_key + '/' + artifact
        dir_name = artifact_path.rsplit('/', 1)[0]
        if not os.path.isdir(dir_name):
            makedirs(dir_name)
        artifact_binary = requests.get(request.json['baseUrl'] + artifact, stream=True)
        with open(artifact_path, "wb") as handle:
            for data in artifact_binary.iter_content():
                handle.write(data)

    return hash_key


@app.route("/<endpoint_key>", methods=['POST'])
def execute_endpoint(endpoint_key):
    print(f"activator sent over json in execute request {request.json}")
    result = endpoints[endpoint_key]['function'](request.json)
    return {'result': result}


manager = Manager(app)


@manager.command
def runserver():
    thread = threading.Thread(target=setup_app)
    thread.start()
    app.run()


if __name__ == '__main__':
    manager.run()
