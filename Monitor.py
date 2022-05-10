import time
import zmq

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

#가장 최근 블록의 해시값 리턴
def monitor():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % ("yujin", "dnlab2022"))
    best_block_hash = rpc_connection.getbestblockhash()

    return best_block_hash

#가장 최근 블록의 hash값과 height값으로 message만들어서 리턴
def monitor_message(best_block_hash):
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % ("yujin", "dnlab2022"))
    block = rpc_connection.getblock(monitor())
    message = {'hash': monitor(), 'height': block['height']}
    return message

if __name__ == "__main__":

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://127.0.0.1:5556")

    while(True):
        value = monitor()
        time.sleep(3)
        best_block_hash = monitor()
        if(value != best_block_hash):
            message = monitor_message(best_block_hash)
            socket.send_json(message)
            print('New Block : ', message)







