import time
import zmq

def message_receiver():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.bind("tcp://*:5556")

    while(True):
        message = socket.recv_json()
        print("Received message : ", message)

if __name__ == "__main__":
    message_receiver()