from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % ("yujin", "dnlab2022"))
best_block_hash = rpc_connection.getbestblockhash()
block = rpc_connection.getblock(best_block_hash)
print(best_block_hash)
print(block['height'])