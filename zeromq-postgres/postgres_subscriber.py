import psycopg2 as pg
import os
import zmq

# TODO:
# - handle invalid messages
# - handle database connection drops

def prepare_zmq(port=5556):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    # accept all topics (prefixed) - default is none
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.bind("tcp://*:{}".format(port))
    return context, socket


def connect_to_db():
    host = os.getenv('DB_HOST', 'localhost')
    database = os.getenv('DB_DATABASE', 'dump1090')
    user = os.getenv('DB_USER', 'dump1090')
    password = os.getenv('DB_PASSWORD', 'dump1090')
    print(host, database, user, password)
    db = pg.connect(host=host, database=database, user=user, password=password)
    cursor = db.cursor()
    return db, cursor


def insert_message(cursor, db, message):
    # MessageType, TransmissionType, SessionID, AircraftID, HexIdent, FlightID,
    # DateMessageGenerated, TimeMessageGenerated, DateMessageLogged,
    # TimeMessageLogged, Callsign, Altitude, GroundSpeed, Track, Latitude,
    # Longitude, VerticalRate, Squawk, Alert, Emergency, SPI, IsOnGround
    fields = message.split(',')

    def empty_to_none(value):
        return value if value != '' else None

    fields = [empty_to_none(field) for field in fields]

    # Insert the message into the database
    query = """
    INSERT INTO messages
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s);
    """
    cursor.execute(query, fields)
    db.commit()

if __name__ == '__main__':
    zmq_context, zmq_socket = prepare_zmq()
    pg_db, pg_cursor = connect_to_db()

    while True:
        message = zmq_socket.recv_string()
        insert_message(pg_cursor, pg_db, message)
