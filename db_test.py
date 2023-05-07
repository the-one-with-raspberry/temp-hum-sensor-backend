import psycopg2
def hist(col, time):
    connection = None
    try:
        print("Attempting connection to database...")
        connection = psycopg2.connect(
            host="192.168.68.70",
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
h = hist("temp", "1 hour")
for i in h: # type: ignore
    for j in i:
        print(j)