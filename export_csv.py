import sqlite3
import pandas as pd


def main():
    conn = sqlite3.connect("dbv3-core.db") # location of dbv3-core.db
    cur = conn.cursor()

    attachDB = "dbv3-index.db" # location of dbv3-index.db

    cur.execute("ATTACH DATABASE ? AS db", [attachDB])

    df = pd.read_sql_query('''SELECT A.blk blkid, B.blkhash, A.unixtime miningtime 
                              FROM BlkTime 
                              A INNER JOIN db.BlkID B 
                              ON A.blk = B.id''',conn)
    df.to_csv(r'blkinfo.csv', index=False)

    df = pd.read_sql_query('''SELECT A.tx txid, B.txid txhash, A.blk blkid 
                              FROM BlkTx 
                              A INNER JOIN db.TxID B 
                              ON A.tx = B.id''', conn)
    df.to_csv(r'txinfo.csv', index=False)

    df = pd.read_sql_query('''SELECT A.id addrtypeid, A.addrtype 
                              FROM db.AddrTypeID A ''', conn)
    df.to_csv(r'addrtype.csv', index=False)

    df = pd.read_sql_query('''SELECT id addrid, addr, 
                              CASE SUBSTR(addr, 1, 1) 
                              WHEN '1' THEN 1 
                              WHEN '3' THEN 2 
                              ELSE 3 
                              END addrtypeid, 
                              (SELECT db.BlkID.id 
                               FROM db.BlkID INNER JOIN BlkTx 
                               ON BlkTx.blk = db.BlkID.id 
                               WHERE BlkTx.tx = (
                                    SELECT MIN(TxOut.tx) 
                                    FROM TxOut 
                                    WHERE TxOut.addr IN (
                                        SELECT db.AddrID.id 
                                        FROM db.AddrID 
                                        WHERE db.AddrID.id = T.id))) blkid 
                               FROM db.AddrID T''',conn)
    df.to_csv(r'addrinfo.csv', index=False)

    df = pd.read_sql_query('''SELECT tx txid, n, ptx ptxid, pn FROM TxIn''', conn)
    df.to_csv(r'txin.csv', index=False)

    df = pd.read_sql_query('''SELECT tx txid, n, addr addrid, btc FROM TxOut''', conn)
    df.to_csv(r'txout.csv', index=False)

    conn.close()


if __name__ == "__main__":
    main()
