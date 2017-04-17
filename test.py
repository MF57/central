from flask import Flask

app = Flask(__name__)



@app.route('/trac/<dst>')
def trace2(dst):
    print dst
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
