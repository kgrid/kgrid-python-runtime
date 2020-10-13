import os
import sys
from os import getenv, makedirs
import importlib
import subprocess

import requests


def activate_endpoint(activation_request, python_runtime_url, endpoints):
    request_json = activation_request.json
    print(f'activator sent over json in activation request {request_json}')
    hash_key = copy_artifacts_to_shelf(activation_request)
    entry_name = request_json['entry'].rsplit('.', 2)[0].replace('/', '.')
    package_name = 'shelf.' + hash_key + '.' + entry_name
    if package_name in sys.modules:
        del (sys.modules[package_name])
    import_package(hash_key, package_name)
    function = eval(package_name + '.' + request_json['function'])
    endpoints[hash_key] = {'uri': request_json['uri'], 'path': package_name, 'function': function}
    response = {'baseUrl': python_runtime_url, 'endpointUrl': hash_key}
    return response


def import_package(hash_key, package_name):
    dependency_requirements = 'shelf/' + hash_key + '/requirements.txt'
    if os.path.exists(dependency_requirements):
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
    for artifact in request_json['artifact']:
        artifact_path = 'shelf/' + hash_key + '/' + artifact
        dir_name = artifact_path.rsplit('/', 1)[0]
        if not os.path.isdir(dir_name):
            makedirs(dir_name)
        artifact_binary = requests.get(request_json['baseUrl'] + artifact, stream=True)
        with open(artifact_path, 'wb') as handle:
            for data in artifact_binary.iter_content():
                handle.write(data)

    return hash_key

