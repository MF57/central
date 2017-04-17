import requests
import time
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/trace/<src>/<dst>')
def trace(src, dst):
    r = requests.post('http://requestb.in/z8yougz8', data={"ts": time.time()})
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
