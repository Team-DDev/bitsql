import argparse
import time
import zmq

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import secret

FLAGS = _ = None
DEBUG = False


def monitor():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (secret.rpcuser, secret.rpcpassword))
    best_block_hash = rpc_connection.getbestblockhash()

    return best_block_hash


def monitor_message(best_block_hash):
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (secret.rpcuser, secret.rpcpassword))
    block = rpc_connection.getblock(monitor())
    message = {'hash': monitor(), 'height': block['height']}

    return message


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    try:
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.connect("tcp://127.0.0.1:5556")

        while True:
            value = monitor()
            time.sleep(3)
            best_block_hash = monitor()

            if value != best_block_hash:
                message = monitor_message(best_block_hash)
                socket.send_json(message)
                print('New Block : ', message)
    except KeyboardInterrupt:
        print("keyboradinterrupt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    FLAGS, _=parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
