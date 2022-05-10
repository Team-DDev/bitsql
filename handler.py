import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt_string(zmq.SUBSCRIBE, "")
socket.bind("tcp://*:5556")

while(True):
    message = socket.recv()
    print("Received requst: %s" % message)
    time.sleep(1)
