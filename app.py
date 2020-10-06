from flask import Flask, request
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './shelf/hashid')
import hello
import writeToFile

app = Flask(__name__)

@app.route("/hello", methods=['POST'])
def sayHello():
    print(f'received json: {request.json}')
    return hello.hello(request.json)
    
@app.route("/write", methods=['POST'])
def write():
    print(f'received json: {request.json}')
    return writeToFile.writeToFile(request.json)
    
@app.route("/display", methods=['POST'])
def printFromUrl():
    print(f'received json: {request.json}')
    
