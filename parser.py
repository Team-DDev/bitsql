from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import secret

RPCM = None


def get_vin_list(txid):
    vin_list = []
    tx = rpc.getrawtransaction(txid, 1)
    tx_vin = tx['vin']
    number_of_tx_vin = len(tx['vin'])

    for i in range(number_of_tx_vin):
        temp_list = {}
        tx_vin_txid = tx_vin[i]['txid']
        temp_list['in_n'] = i

        prev_tx = rpc.getrawtransaction(tx_vin_txid, 1)
        number_of_prev_tx_vout = len(prev_tx['vout'])

        for j in range(number_of_prev_tx_vout):
            if tx_vin[i]['vout'] == prev_tx['vout'][j]['n']:
                temp_list['address'] = prev_tx['vout'][j]['scriptPubKey']['address']
                temp_list['value'] = prev_tx['vout'][j]['value']
                vin_list.append(temp_list)

    return vin_list


def get_vout_list(txid):
    vout_list = []
    tx = rpc.getrawtransaction(txid, 1)
    tx_vout = tx['vout']
    number_of_tx_vout = len(tx['vout'])

    for i in range(number_of_tx_vout):
        temp_list = {}
        temp_list['out_n'] = i
        temp_list['address'] = tx_vout[i]['scriptPubKey']['address']
        temp_list['value'] = tx_vout[i]['value']

        vout_list.append(temp_list)

    return vout_list


def showtable(block, txid, vin_list, vout_list):
    result_table = []
    number_of_vin_list = len(vin_list)
    number_of_vout_list = len(vout_list)

    for i in range(number_of_vin_list):
        for j in range(number_of_vout_list):
            temp_list = {}
            temp_list['block height'] = block['height']
            temp_list['block hash'] = block['hash']
            temp_list['transaction hash(id)'] = txid
            temp_list['vin'] = vin_list[i]
            temp_list['vout'] = vout_list[j]

            result_table.append(temp_list)

    return result_table


def main():
    rpc = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (secret.rpc_username, secret.rpc_password))

    bestblockhash = rpc.getbestblockhash()
    block = rpc.getblock(bestblockhash)  # 최근에 들어온 블록
    txid = block['tx'][7]  # 특정 트랜잭션 선정

    vin_list = get_vin_list(txid)
    vout_list = get_vout_list(txid)
    result = showtable(block, txid, vin_list, vout_list)

    print(result)


if __name__ == "__main__":
    RPCM = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (secret.rpc_username, secret.rpc_password))
    rpc = RPCM

    main()
