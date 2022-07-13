import sqlite3
import pandas as pd


def main():
    conn = sqlite3.connect("/media/Data-A/BitcoinAnalysis/BitcoinBlockSampler/dbv3-core.db")
    cur = conn.cursor()

    attachDB = "/media/Data-A/BitcoinAnalysis/BitcoinBlockSampler/dbv3-index.db"

    cur.execute("ATTACH DATABASE ? AS db", [attachDB])

    df = pd.read_sql_query(
        "SELECT A.blk blkid, B.blkhash, A.unixtime miningtime FROM BlkTime A inner join db.BlkID B on A.blk = B.id",
        conn)
    df.to_csv(r'blkinfo.csv', index=False)

    df = pd.read_sql_query(
        "SELECT A.tx txid, B.txid txhash, A.blk blkid FROM BlkTx A inner join db.TxID B on A.tx = B.id", conn)
    df.to_csv(r'txinfo.csv', index=False)

    df = pd.read_sql_query("SELECT tx txid, n, ptx ptxid, pn FROM TxIn", conn)
    df.to_csv(r'txin.csv', index=False)

    df = pd.read_sql_query("SELECT tx txid, n, addr addrid, btc FROM TxOut", conn)
    df.to_csv(r'txout.csv', index=False)

    df = pd.read_sql_query(
        "SELECT B.id addrid, B.addr, case SUBSTR(B.addr, 1, 1) when '1' then 1 when '3' then 2 else 3 end addrtypeid, A.tx txid FROM TxOut A inner join db.AddrID B WHERE A.addr = B.id ",
        conn)
    df.to_csv(r'addrinfo.csv', index=False)

    df = pd.read_sql_query("SELECT A.id addrtypeid, A.addrtype FROM db.AddrTypeID A ", conn)
    df.to_csv(r'addrtype.csv', index=False)


if __name__ == "__main__":
    main()
