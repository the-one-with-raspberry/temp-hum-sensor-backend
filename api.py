from flask import render_template, Flask, request, jsonify
import sht21
from sht21 import SHT21

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/docs', methods=['GET'])
def apidocs():
    return render_template('docs.html')
@app.route('/api/v1/current/getInfo', methods=['GET'])
def api_getInfo():
    with SHT21(1) as sht21:
        response = jsonify({'status': 200, 'content': {'humidity': {'value': round(sht21.read_humidity(), 1)}, 'farenheit': {'value': round(sht21.read_temperature(), 1) * (9/5) + 32, 'unit': 'farenheit'}, 'celsius': {'value': round(sht21.read_temperature(), 1), 'unit': 'celsius'}}})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response, 200
if __name__ == '__main__':
    app.run('0.0.0.0', 5000, True)
