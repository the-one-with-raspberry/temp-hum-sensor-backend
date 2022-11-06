from flask import render_template, Flask, request, jsonify
import sht21
from sht21 import SHT21

def convert_temperature(value, from_unit, to_unit):
    """ Convert and return the temperature value from from_unit to to_unit. """

    # A dictionary of conversion functions from different units *to* K.
    toK = {'K': lambda val: val,
           'C': lambda val: val + 273.15,
           'F': lambda val: (val + 459.67)*5/9,
          }
    # A dictionary of conversion functions *from* K to different units.
    fromK = {'K': lambda val: val,
             'C': lambda val: val - 273.15,
             'F': lambda val: val*9/5 - 459.67,
            }

    # First convert the temperature from from_unit to K.
    try:
        T = toK[from_unit](value)
    except KeyError:
        raise ValueError('Unrecognized temperature unit: {}'.format(from_unit))

    if T < 0:
        raise ValueError('Invalid temperature: {} {} is less than 0 K'
                                .format(value, from_unit))

    if from_unit == to_unit:
       # No conversion needed!
        return value

    # Now convert it from K to to_unit and return its value.
    try:
        return fromK[to_unit](T)
    except KeyError:
        raise ValueError('Unrecognized temperature unit: {}'.format(to_unit))

app = Flask(__name__);
app.config["DEBUG"] = True

@app.route('/docs', methods=['GET'])
def apidocs():
    return render_template('docs.html')
@app.route('/api/v1/current/getTemp', methods=['GET'])
def api_getTemp():
    with SHT21(1) as sht21:
        if 'unit' in request.args:
            if request.args.get('unit') == 'celsius':
                return jsonify({'status': 200, 'content': {'value': round(sht21.read_temperature(), 1), 'unit': 'celsius'}}), 200
            elif request.args.get('unit') == 'farenheit':
                return jsonify({'status': 200, 'content': {'value': convert_temperature(round(sht21.read_temperature(), 1), 'C', 'K'), 'unit': 'celsius'}}), 200
        else:
            return jsonify({'status': 400, 'content': {'error': 'The unit parameter was not specified.'}}), 400
@app.route('/api/v1/current/getHum', methods=['GET'])
def api_getHum():
    with SHT21(1) as sht21:
        return jsonify({'status': 200, 'content': {'value': round(sht21.read_humidity(), 1)}})
if __name__ == '__main__':
    app.run('0.0.0.0', 5000, True)