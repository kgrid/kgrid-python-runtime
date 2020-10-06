from flask import Flask
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './shelf/hashid')
import hello

app = Flask(__name__)

@app.route("/hashid")
def welcome():
    # if request.method == 'POST':
    return hello.hello()
    # else:
        # return "hashid"
