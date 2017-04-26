from flask import Flask
import json

app = Flask(__name__)



@app.route('/lol')
def trace2():
    result = {}
    result['timestamp'] = 1492457001111
    result['sample_id'] = "asdsadasds"
    return json.dumps(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)
