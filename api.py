#!/usr/bin/python
from flask import render_template, Flask, request, jsonify
import psycopg2
from datetime import datetime
import time as timemodule
from sht21 import SHT21
TIMEZONE = timemodule.strftime("%z")

app = Flask(__name__)
app.config["DEBUG"] = True


#@app.route("/docs", methods=["GET"])
#def apidocs():
#    return render_template("docs.html")

@app.route("/api/v1/current/getInfo", methods=["GET"])
def api_getInfo():
    with SHT21(1) as sht21:
        if sht21:
            response = jsonify({"status": 200, "content": {"humidity": {"value": round(sht21.read_humidity(), 1)}, "farenheit": {"value": round(sht21.read_temperature(), 1) * (9 / 5) + 32, "unit": "farenheit"}, "celsius": {"value": round(sht21.read_temperature(), 1), "unit": "celsius"}}})
            code = 200
        else:
            response = jsonify({"status": 503})
            code = 503
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response, code

@app.route("/api/v1/hist/getInfo", methods=["GET"])  # type: ignore
def api_getHist():
    histTuple = ""
    time = request.args.get("time")
    if time == "1d":
        histTuple = hist("temp, hum, timestamp", '1 day')
        # histTempTuple = hist("hum", '1 day')
        # histFarenTuple = hist("tempfaren", '1 day')
    elif time == "1w":
        histTuple = hist("temp, hum, timestamp", '1 week')
        # histTempTuple = hist("hum", '1 week')
        # histFarenTuple = hist("tempfaren", '1 week')
    elif time == "1m":
        histTuple = hist("temp, hum, timestamp", '1 month')
        # histTempTuple = hist("hum", '1 month')
        # histFarenTuple = hist("tempfaren", '1 month')
    elif time == "1y":
        histTuple = hist("temp, hum, timestamp", '1 year')
        # histTempTuple = hist("hum", '1 year')
        # histFarenTuple = hist("tempfaren", '1 year')
    elif time == "5y":
        histTuple = hist("temp, hum, timestamp", '5 years')
        # histTempTuple = hist("hum", '5 years')
        # histFarenTuple = hist("tempfaren", '5 years')
    elif time == "all":
        histTuple = hist("temp, hum, timestamp", 'all')
        # # histTempTuple = hist("hum", 'all')
        # histFarenTuple = hist("tempfaren", 'all')
    else:
        response = jsonify({'status': 400, 'error': 'The client sent an invalid time range.'})
        return response, 400
    if histTuple == None or type(histTuple) == str:
        response = jsonify({'status': 500, 'error': 'A column in the database is Unbound. This isn\'t your fault!'})
        return response, 500
    goofy_ahh_response = []
    for entry in histTuple:
        currentTime = entry[2].replace(microsecond=0)
        currentTime = str(currentTime) + f" GMT{TIMEZONE}"
        goofy_ahh_response.append({"humidity": round(entry[1], 1), "celsius": round(entry[0], 1), "fahrenheit": round(entry[0] * 9/5 + 32, 1), "timestamp": currentTime})
    response = jsonify({'status': 200, 'content': goofy_ahh_response})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response, 200
def hist(col, time):
    connection = None
    try:
        print("Attempting connection to database...")
        connection = psycopg2.connect(
            host="localhost",
            database="pimyhouse",
            user="pi",
            password="123456",
            port=5432,
        )
        cursor = connection.cursor()
        if cursor:
            print("Cursor created.")
        if time != "all":
            cursor.execute(f"SELECT {col} FROM th WHERE (timestamp >= date_trunc('{time[2:]}', NOW() - interval '{time}')) ORDER BY timestamp ASC")
        else:
            cursor.execute(f"SELECT {col} FROM th ORDER BY timestamp ASC")
        hData = cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        raise error
    finally:
        if connection is not None:
            connection.close()
            print("Connection closed, returning data.")
            return hData

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, True)
