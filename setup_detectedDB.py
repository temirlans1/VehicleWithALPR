import psycopg2
import sys
import cv2
from moviepy.editor import VideoFileClip
import Main

try:
    conn = psycopg2.connect(
        host="localhost", database="postgres", user="dbuser", password = "password")
    conn.autocommit = True
    command = "CREATE DATABASE detected_plates;"
    cur = conn.cursor()
    cur.execute(command)
    cur.close()
except psycopg2.DatabaseError as e:
    print(e)
except Exception as e:
    print(e)
    sys.exit(1)
finally:
    conn.close()

def table_exists(c, tn):
    query = """SELECT EXISTS(SELECT relname FROM pg_class WHERE relname= '{}')""".format(
        tn)
    resp = c.execute(query)
    rows = c.fetchone()
    print(rows[0])
    return rows[0]

try:
    conn = psycopg2.connect(
        host="localhost", database="detected_plates", user="dbuser", password = "password")
    conn.autocommit = True
    cur = conn.cursor()
    table_name = 'detected_plates'
    if not table_exists(cur, table_name):
        commands = [
            """CREATE TABLE {} (
            id SERIAL PRIMARY KEY,
            time TEXT NOT NULL,
            date TEXT NOT NULL,
            carnum TEXT NOT NULL,
            full_name TEXT NOT NULL,
            penalties_info TEXT
        );""".format(table_name),
            """
            CREATE FUNCTION notify_trigger() RETURNS trigger AS $$
            DECLARE
            BEGIN
            PERFORM pg_notify('items_watchers',
                '{"time":' || '"' || NEW.time || '",' ||
                '"date":' || '"' || NEW.date || '",' ||
                '"carnum":' || '"' || NEW.carnum || '",' ||
                '"full_name":' || '"' || NEW.full_name || '",' ||
                '"penalties":' || '"' || NEW.penalties_info || '"' ||
                '}');
            RETURN new;
            END;
            $$ LANGUAGE plpgsql;
        """,
            """
            CREATE TRIGGER watched_table_trigger AFTER INSERT ON {}
            FOR EACH ROW EXECUTE PROCEDURE notify_trigger();
        """.format(table_name)
        ]

        for c in commands:
            cur.execute(c)

    conn2 = psycopg2.connect(host = "localhost", database = "penalties", user = "dbuser", password = "password")
    cur2 = conn2.cursor()

    cap = cv2.VideoCapture("VIDEO3.avi")
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = 0
    clip = VideoFileClip("VIDEO3.avi")
    
    while (n != length):
        
        ret, frame = cap.read()
        frame1 = frame[100:]
        result = str(Main.main(frame1))

        cur2.execute("""SELECT carnum FROM penalties;""")
        carnums = cur2.fetchall() 

        video_time = n * clip.duration / length
        video_time = round(video_time, 4)

        j = 1 
        found = False

        if len(result) != 0:

            for i in carnums:
                if result == i[0]:
                    found = True
                    cur2.execute("SELECT * FROM penalties WHERE id = %s", (j,))
                    resultRow = cur2.fetchone()
                    cur.execute("""INSERT INTO detected_plates(time, date, carnum, full_name, penalties_info) 
                                VALUES (%s, %s, %s, %s, %s);""", ("{}:{}".format((int(video_time / 60)), (int(video_time) % 60)), "11-12-2018", result, resultRow[2], resultRow[3]))
                    cur.execute("SELECT * FROM detected_plates")
                    resultTable = cur.fetchall()
                    print(str(resultTable))
                    break
                j += 1

            if not found:
                cur.execute("""INSERT INTO detected_plates(time, date, carnum, full_name, penalties_info) 
                            VALUES (%s, %s, %s, %s, %s);""", ("{}:{}".format((int(video_time / 60)), (int(video_time) % 60)), "11-12-2018", result, "Unknown", "None"))
                cur.execute("SELECT * FROM detected_plates")
                resultTable = cur.fetchall()
                print(str(resultTable))

        n += 1

    print("Finished.")
    cap.release()

    cur.close()
    cur2.close()
finally:
    conn.close()
    conn2.close()
