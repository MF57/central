from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/trace/<src>/<dst>')
def trace(src, dst):
    print src
    print dst
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
