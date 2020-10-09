import threading
from flask import Flask, request
from os import getenv, makedirs
import requests
import json
from flask_script import Manager
import importlib
import shelf

artifacts = {}

app = Flask(__name__)
activator_url = getenv("KGRID_ADAPTER_PROXY_URL", "http://localhost:8083")
python_runtime_url = getenv("ENVIRONMENT_SELF_URL", "http://localhost:5000")


def setup_app():
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
    artifact = requests.get(request.json['baseUrl'] + request.json['entry'], stream=True)
    hash_key = hash(request.json['uri']).__abs__().__str__()
    hash_key = 'ko' + hash_key
    artifact_path = 'shelf/' + hash_key + '/' + request.json['entry']
    package_name = artifact_path.rsplit('.', 1)[0].replace('/', '.')
    dir_name = artifact_path.rsplit('/', 1)[0]
    makedirs(dir_name)
    with open(artifact_path, "wb") as handle:
        for data in artifact.iter_content():
            handle.write(data)
    # install any dependencies?
    artifacts[hash_key] = {'path': package_name, 'function': request.json['function']}
    importlib.import_module(package_name)
    response = {'baseUrl': python_runtime_url, 'endpointUrl': hash_key}
    return response


@app.route("/<endpoint_key>", methods=['POST'])
def execute_endpoint(endpoint_key):
    print(f"activator sent over json in execute request {request.json}")
    result = eval(artifacts[endpoint_key]['path'] + "." + artifacts[endpoint_key]['function'] + "(request.json)")
    return {'result': result}


manager = Manager(app)


@manager.command
def runserver():
    thread = threading.Thread(target=setup_app)
    thread.start()
    app.run()


if __name__ == '__main__':
    manager.run()
