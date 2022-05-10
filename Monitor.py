import time
import zmq

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def monitor():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % ("yujin", "dnlab2022"))
    best_block_hash = rpc_connection.getbestblockhash()
    return best_block_hash

if __name__ == "__main__":

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://127.0.0.1:5556")

    while(True):
        value = monitor()
        time.sleep(3)
        if(value != monitor()):
            #zeroMQ 핸들러에게 날리기
            socket.send_string(value)
            print('send')







