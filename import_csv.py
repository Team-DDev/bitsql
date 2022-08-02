import sqlite3
import pandas as pd
import mariadb
import secret


def main():
    conn = mariadb.connect(user=secret.db_username,
                           password=secret.db_password,
                           host=secret.db_host,
                           port=secret.db_port,
                           database=secret.db_databasename)
    cur = conn.cursor()

    #create table
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS blkinfo(
           blkid INT NOT NULL,
           blkhash CHAR(64) NOT NULL,
           miningtime INT NOT NULL,
           PRIMARY KEY(blkid),
           UNIQUE(blkhash, miningtime));''')

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS txinfo(
           txid INT NOT NULL,
           txhash CHAR(64) NOT NULL,
           blkid INT NOT NULL,
           PRIMARY KEY(txid),
           FOREIGN KEY(blkid) REFERENCES blkinfo(blkid) ON DELETE CASCADE,
           UNIQUE(txhash, blkid));''')

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS addrtype(
           addrtypeid INT NOT NULL,
           addrtype TEXT NOT NULL,
           PRIMARY KEY(addrtypeid),
           UNIQUE(addrtype));''')

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS addrinfo(
           addrid INT NOT NULL,
           addr TEXT NOT NULL,
           addrtypeid INT NOT NULL,
           blkid INT NOT NULL,
           PRIMARY KEY(addrid),
           FOREIGN KEY(blkid) REFERENCES blkinfo(blkid) ON DELETE CASCADE,
           FOREIGN KEY(addrtypeid) REFERENCES addrtype(addrtypeid),
           UNIQUE(addr, addrtypeid, blkid));''')

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS txin(
           txid INT NOT NULL,
           n INT NOT NULL,
           ptxid INT NOT NULL,
           pn INT NOT NULL,
           FOREIGN KEY(txid) REFERENCES txinfo(txid) ON DELETE CASCADE,
           UNIQUE(txid, n));''')

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS txout(
           txid INT NOT NULL,
           n INT NOT NULL,
           addrid INT NOT NULL,
           btc DOUBLE NOT NULL,
           FOREIGN KEY(txid) REFERENCES txinfo(txid) ON DELETE CASCADE,
           UNIQUE(txid, n));''')

    conn.commit()

    # insert csv to mariaDB

    cur.execute('load data local infile "blkinfo.csv" into table blkinfo columns terminated by "," enclosed by "\n" ignore 1 rows;')

    cur.execute('load data local infile "txinfo.csv" into table txinfo columns terminated by "," enclosed by "\n" ignore 1 rows;')

    cur.execute('load data local infile "addrtype.csv" into table addrtype columns terminated by "," enclosed by "\n" ignore 1 rows;')

    cur.execute('load data local infile "addrinfo.csv" into table addrinfo columns terminated by "," enclosed by "\n" ignore 1 rows;')

    cur.execute('load data local infile "txin.csv" into table txin columns terminated by "," enclosed by "\n" ignore 1 rows;')

    cur.execute('load data local infile "txout.csv" into table txout columns terminated by "," enclosed by "\n" ignore 1 rows;')


if __name__ == "__main__":
    main()
