import argparse
import zmq
import mariadb
import datetime
from time import strftime

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import secret

FLAGS = _ = None
DEBUG = False


def message_receiver():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.bind("tcp://*:6666")

    while True:
        message = socket.recv_json()
        print("Received message : ", message)

        try:
            conn = mariadb.connect(user=secret.db_username,
                                   password=secret.db_password,
                                   host=secret.db_host,
                                   port=secret.db_port,
                                   database=secret.db_databasename)
            cur = conn.cursor()

        except mariadb.Error as e:
            print(f'Error connecting to MariaDB: {e}')
            sys.exit(0)

        rpc = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (secret.rpc_username, secret.rpc_password))
        block = rpc.getblock(message['hash'])

        time = datetime.datetime.utcfromtimestamp(block['time']).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute('''INSERT INTO blk VALUES(?, ?, ?);''', (message['height'], message['hash'], time))

        conn.commit()
        conn.close()


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
