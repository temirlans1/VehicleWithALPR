import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host="localhost", database="postgres", user="dbuser", password = "password")
    conn.autocommit = True
    command = "CREATE DATABASE penalties;"
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
        host="localhost", database="penalties", user="dbuser", password = "password")
    conn.autocommit = True
    cur = conn.cursor()
    table_name = 'penalties'
    if not table_exists(cur, table_name):
        commands = [
            """CREATE TABLE {} (
            id SERIAL PRIMARY KEY,
            carnum TEXT NOT NULL,
            full_name TEXT NOT NULL,
            penalties_info TEXT
        );""".format(table_name),
            """
            CREATE FUNCTION notify_trigger() RETURNS trigger AS $$
            DECLARE
            BEGIN
            PERFORM pg_notify('items_watchers',
                '{"carnum":' || '"' || NEW.carnum || '",' ||
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

        sql = """INSERT INTO penalties(carnum, full_name, penalties_info)
                 VALUES(%s, %s, %s);"""

        data = [
            {"carnum": "382CCZ01", "full_name": 'Tugenov Arman Kumarovich', "penalties_info": 'Over speed: 5 MCI'},
            {"carnum": "209MOA01", "full_name": 'Kuanyshkereyev Farkhad Rinatuly', "penalties_info": 'None'},
            {"carnum": "212KNA03", "full_name": 'Shamelov Tamerlan Erulanuly', "penalties_info": 'Wrong place parking: 3 MCI; Over speed: 5 MCI'},
            {"carnum": "114HXA01", "full_name": 'Kuanyshkereyev Ali Rinatovich', "penalties_info": 'Oncoming lane departure: 10 MCI'},
            #{"carnum": "183TSA01", "full_name": 'Kurmanbek Bakhytzhan Talgatuly', "penalties_info": 'None'},
        ]

        for i in range(0, len(data)):
            d = data[i]
            cur.execute(sql, (d['carnum'], d['full_name'], d['penalties_info']))

    cur.close()
finally:
    conn.close()
