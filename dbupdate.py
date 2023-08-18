import datetime, psycopg2, schedule, time
from sht21 import SHT21

def pushDB():
    conn = psycopg2.connect(database="pimyhouse", user="pi", password="123456", host="192.168.68.70", port=5432)
    c = conn.cursor()

    with SHT21(1) as s:
        t = s.read_temperature()
        h = s.read_humidity()
    
    q = "INSERT INTO th (temp, hum, timestamp) VALUES (%s, %s, %s);"
    d = (t, h, datetime.datetime.now())

    c.execute(q, d)
    conn.commit()
    conn.close()

schedule.every(1).minutes.do(pushDB)

while True:
    schedule.run_pending()
    time.sleep(1)
