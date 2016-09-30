import os
import zmq
import time
import socket

zmq_host = os.getenv('ZMQ_HOST', 'localhost')
zmq_port = os.getenv('ZMQ_PORT', '5556')
context = zmq.Context()
zmq_socket = context.socket(zmq.PUB)
zmq_socket.connect("tcp://{}:{}".format(zmq_host, zmq_port))

# Sleep a bit of time until the connection is properly established,
# otherwise some messages may be lost.
# http://stackoverflow.com/questions/7470472/lost-messages-on-zeromq-pub-sub
time.sleep(1)

def netcat(hostname, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, int(port)))
    socket_file = s.makefile()
    for line in socket_file:
        yield line.strip()
    s.close()

dump1090_host = os.getenv('DUMP1090_HOST', 'localhost')
# BaseStation CSV format
dump1090_port = os.getenv('DUMP1090_PORT', '30003')

# we add the receiver identifier (eg. MAC address) as the first CSV column
receiver_id = os.getenv('RECEIVER_ID', '').strip()

def add_receiver_id(message):
    return receiver_id + ',' + message

for message in netcat(dump1090_host, dump1090_port):
    zmq_socket.send_string(add_receiver_id(message))
