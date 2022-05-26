import argparse
import sys
import zmq
import mariadb
import datetime

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import secret

FLAGS = _ = None
DEBUG = False
RPCM = None


def convert_time(block_time):
    convert_time = datetime.datetime.utcfromtimestamp(block_time).strftime("%Y-%m-%d %H:%M:%S")

    return convert_time


def check_orphanblock(message):
    global RPCM

    rpc = RPCM

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

    message_height = message['height']
    message_hash = message['hash']

    checkheight = message_height
    while (checkheight != 700000):

        try:
            block = rpc.getblock(message_hash)

        except(BrokenPipeError, JSONRPCException):
            RPCM = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (secret.rpc_username, secret.rpc_password))
            rpc = RPCM

        blockhash = rpc.getblockhash(checkheight)
        temp_block = rpc.getblock(blockhash)

        check_previoushash = temp_block['previousblockhash']

        cur.execute('''SELECT id, blkhash FROM blk WHERE id = %s''', [checkheight - 1])
        temp = cur.fetchall()

        insertedblock_height = temp[0][0]
        insertedblock_hash = temp[0][1]

        if (check_previoushash == insertedblock_hash) is False:
            cur.execute('''DELETE FROM blk WHERE id = %s''', [insertedblock_height])
            conn.commmit()

            insertblock = rpc.getblock(check_previoushash)
            insertheight = checkheight - 1
            inserthash = insertblock['hash']
            inserttime = convert_time(insertblock['time'])

            cur.execute('''INSERT INTO blk VALUES(?, ?, ?);''', (insertheight, inserthash, inserttime))
            conn.commit()

        checkheight -= 1

    conn.close()

def message_receiver():
    global RPCM
    rpc = RPCM

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.bind("tcp://*:5556")

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

        try:
            block = rpc.getblock(message['hash'])

        except(BrokenPipeError, JSONRPCException):

            RPCM = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (secret.rpc_username, secret.rpc_password))
            rpc = RPCM

        cur.execute('''SELECT max(id) FROM blk''')
        temp = cur.fetchall()

        dif = message['height'] - temp[0][0]

        if dif > 1:
            for i in range(dif):
                insert_height = temp[0][0] + i + 1

                temp_block_hash = rpc.getblockhash(insert_height)
                temp_block = rpc.getblock(temp_block_hash)

                insert_hash = temp_block_hash
                insert_time = convert_time(temp_block['time'])

                cur.execute('''INSERT INTO blk VALUES(?, ?, ?);''', (insert_height, insert_hash, insert_time))
                conn.commit()

        else:
            block = rpc.getblock(message['hash'])
            time = convert_time(block['time'])

            cur.execute('''INSERT INTO blk VALUES(?, ?, ?);''', (message['height'], message['hash'], time))
            conn.commit()

        check_orphanblock(message)

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
    RPCM = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (secret.rpc_username, secret.rpc_password))

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
