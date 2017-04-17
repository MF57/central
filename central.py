import requests
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/trace/<src>/<dst>')
def trace(src, dst):
    print 'http://' + src + "/trac/" + dst
    r = requests.get('http://' + src + "/trac/" + dst)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
