#!/usr/bin/python
from flask import render_template, Flask, request, jsonify
import psycopg2
from sht21 import SHT21

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/docs", methods=["GET"])
def apidocs():
    return render_template("docs.html")


@app.route("/api/v1/current/getInfo", methods=["GET"])
def api_getInfo():
    with SHT21(1) as sht21:
        if sht21:
            response = jsonify({"status": 200, "content": {"humidity": {"value": round(sht21.read_humidity(), 1)}, "farenheit": {"value": round(sht21.read_temperature(), 1) * (9 / 5) + 32, "unit": "farenheit"}, "celsius": {"value": round(sht21.read_temperature(), 1), "unit": "celsius"}}})  # type: ignore
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
    response = jsonify({})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    histTemp = ""
    histHum = ""
    histFaren = ""
    def sV(t):
        histTemp = hist("temp", t)
        histHum = hist("hum", t)
        histFaren = hist("tempfaren", t)
    time = request.args.get("time")
    if time == "1d":
        sV('1 day')
    elif time == "1w":
        sV('1 week')
    elif time == "1m":
        sV('1 month')
    elif time == "1y":
        sV('1 year')
    elif time == "all":
        sV('all')
    else:
        response = jsonify({'status': 400, 'error': 'The client sent an invalid time range.'})
        return response, 400
    for i in range(len(histTemp)):
        histTemp[i] = round(int(histTemp[i]), 1) # type: ignore
    for i in range(len(histHum)):
        histHum[i] = round(int(histHum[i]), 1) # type: ignore
    for i in range(len(histFaren)):
        histFaren[i] = round(int(histFaren[i]), 1) # type: ignore
    response = jsonify({'status': 200, 'content': {'humidity': {'value': histHum}, 'celsius': {'value': histTemp, 'unit': 'celsius'}, 'farenheit': {'value': histFaren, 'unit': 'farenheit'}}})
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
        print(error)
        return error
    finally:
        if connection is not None:
            connection.close()
            print("Connection closed, returning data.")
            return hData  # type: ignore


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, True)
