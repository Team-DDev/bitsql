import argparse
import zmq

FLAGS = _ = None
DEBUG = False


def message_receiver():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.bind("tcp://*:5556")

    while True:
        message = socket.recv_json()
        print("Received message : ", message)


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    try:
        message_receiver()
    except KeyboardInterrupt:
        print("keyboradinterrupt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
