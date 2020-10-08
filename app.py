from flask import Flask, request
from shelf.hashid import hello, writeToFile
from os import getenv

app = Flask(__name__)
activator_url = getenv("KGRID_ADAPTER_PROXY_URL", "localhost:8080")
python_runtime_url = getenv("ENVIRONMENT_SELF_URL", "localhost:5000")


def setup_app():
    print(f"Kgrid Activator URL IS: {activator_url}")
    print(f"Python Runtime URL IS: {python_runtime_url}")


setup_app()

if __name__ == '__main__':
    app.run()


@app.route("/hello", methods=['POST'])
def say_hello():
    print(f'received json: {request.json}')
    return hello.hello(request.json)


@app.route("/write", methods=['POST'])
def write():
    print(f'received json: {request.json}')
    return writeToFile.write_to_file(request.json)
