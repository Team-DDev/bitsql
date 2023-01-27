import os
import sqlite3
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

import secret
import information
import mariadb

conn = cur = None
app = FastAPI(
  title=information.title,
  description=information.description,
  version=information.version,
  contact=information.contact,
  license_info=information.license_info,
  root_path=secret.root_path)


@app.on_event('startup')
async def startup_event():
    global cur
    global conn
    conn = mariadb.connect(user=secret.db_username,
                                password=secret.db_password,
                                host=secret.db_host,
                                port=secret.db_port,
                                database=secret.db_databasename)
    cur = conn.cursor()


@app.on_event('shutdown')
async def shutdown_event():
    global cur
    global conn
    conn.close()


@app.get('/', summary='Say hello to BitSQL API server')
async def read_root():
    global cur
    global conn
    # Get latest block information
    query = '''SELECT MAX(BlkID.id), 
                      BlkID.blkhash,
                      DATE_FORMAT(FROM_UNIXTIME(BlkTime.unixtime), '%Y-%m-%d %H:%M:%S')
               FROM BlkID
               INNER JOIN BlkTime ON 
                 BlkTime.blk = BlkID.id;'''
    
    cur.execute(query)
    row = cur.fetchone()
    return {'Say': 'Hello world!',
            'Latest block height': row[0],
            'Latest block hash': row[1],
            'Latest mining time (UTC)': row[2]}


@app.get('/address/{addr}', summary='Get address information')
async def address_info(addr: str):
    response = []
    global cur
    global conn
    
    # Issue: AddrID table의 addr 컬럼 개행문자 관련 이슈, csv import 관련 구문 수정함, 새로 구축하면 지워도 됨
    addr = addr + "\r"
    
    # Issue: DBUTIL관련 table 구축안되어있음, 구축 후 사용
    # Get transaction
    # txes = []
    # query = '''SELECT DISTINCT TxID.txid AS txid
    #            FROM Edge
    #            INNER JOIN TxID ON TxID.id = Edge.tx
    #            WHERE Edge.src = (
    #              SELECT AddrID.id
    #              FROM AddrID
    #              WHERE AddrID.addr = ?)
    #            OR Edge.dst = (
    #              SELECT AddrID.id
    #              FROM AddrID
    #              WHERE AddrID.addr = ?)
    #            ORDER BY TxID.id DESC;'''
    # for row in cur.execute(query, (addr, addr)):
    #     txes.append(row[0])
    # Get Income
    query = '''SELECT SUM(TxOut.btc) AS value
               FROM TxOut
               WHERE TxOut.addr = (
                 SELECT AddrID.id
                 FROM AddrID
                 WHERE AddrID.addr = ?);'''
    cur.execute(query, (addr,))
    row = cur.fetchone()
    income = row[0]
    # Get Outcome
    query = '''SELECT SUM(TxOut.btc) AS Outcome
               FROM TxIn
               INNER JOIN TxOut ON TxIn.ptx = TxOut.tx 
                 AND TxIn.pn = TxOut.n
               WHERE TxOut.addr = (
                 SELECT AddrID.id
                 FROM AddrID
                 WHERE AddrID.addr = ?);'''
    cur.execute(query, (addr,))
    row = cur.fetchone()

    outcome = row[0]

    if outcome is None:
        outcome = 0

    # Balance
    balance = income - outcome

    return {'Address': addr,
            'TxCount': 'null',
            'Income': income,
            'Outcome': outcome,
            'Balance': balance,
            'Txes': 'null'}


@app.get('/transaction/{txid}', summary='Get transaction information')
async def transaction_info(txid: str):
    response = []
    global cur
    global conn
    # Get block information
    query = '''SELECT TxID.id,
                 BlkID.id, 
                 BlkID.blkhash, 
                 DATE_FORMAT(FROM_UNIXTIME(BlkTime.unixtime), '%Y-%m-%d %H:%M:%S')
               FROM TxID
               INNER JOIN BlkTx 
                 ON BlkTx.tx = TxID.id
               INNER JOIN BlkTime 
                 ON BlkTime.blk = BlkTx.blk
               INNER JOIN BlkID 
                 ON BlkID.id = BlkTx.blk
               WHERE TxID.txid = ?;'''
    cur.execute(query, (txid,))
    row = cur.fetchone()
    tx = row[0] #713936
    blockheight = row[1]
    blockhash = row[2]
    miningtime = row[3]
    # Get input information
    txincnt = 0
    txinbtc = 0
    txin = []
    query = '''SELECT AddrID.addr, TxOut.btc
               FROM TxIn
               INNER JOIN TxOut 
                 ON TxOut.tx = TxIn.ptx 
                 AND TxOut.n = TxIn.pn
               INNER JOIn AddrID 
                 ON AddrID.id = TxOut.addr
               WHERE TxIn.tx = ?
               ORDER BY TxOut.n ASC;'''
    cur.execute(query, (tx,))
    rows = cur.fetchall()
    for row in rows:
        txin.append({'Address': row[0],
                     'BTC': row[1]})
        txincnt = txincnt + 1
        txinbtc = txinbtc + row[1]
    # Get output information
    txoutcnt = 0
    txoutbtc = 0
    txout = []
    query = '''SELECT AddrID.addr, TxOut.btc
               FROM TxOut
               INNER JOIn AddrID 
                 ON AddrID.id = TxOut.addr
               WHERE TxOut.tx = ?
               ORDER BY TxOut.n ASC;'''
    cur.execute(query, (tx,))
    rows = cur.fetchall()
    for row in rows:
        txout.append({'Address': row[0],
                     'BTC': row[1]})
        txoutcnt = txoutcnt + 1
        txoutbtc = txoutbtc + row[1] 

    # Calculate fee
    fee = txinbtc - txoutbtc
    
    return {'TxID': txid,
            'Block height': blockheight,
            'Block hash': blockhash,
            'Mining time': miningtime,
            'In count': txincnt,
            'In BTC': txinbtc,
            'Out count': txoutcnt,
            'Out BTC': txoutbtc,
            'Fee': fee,
            'In information': txin,
            'Out information': txout}


@app.get('/clusters/search', summary='Search cluster information')
async def clusters_search(clustername: Union[str, None] = None):
    response = []
    global cur
    global conn
    if clustername is None:
        return response
    # Addr, TagID list
    clusters = []
    query = '''SELECT DBSERVICE.AddrTag.addr, DBSERVICE.AddrTag.tag
               FROM DBSERVICE.AddrTag
               WHERE DBSERVICE.AddrTag.tag IN (
                 SELECT DBSERVICE.TagID.id
                 FROM DBSERVICE.TagID
                 WHERE DBSERVICE.TagID.tag = ?);'''
    for row in cur.execute(query, (clustername,)):
        clusters.append({'addr': row[0], 'tagid': row[1]})
    # ClusterID list
    query = '''SELECT DBSERVICE.Cluster.cluster
               FROM DBSERVICE.Cluster
               WHERE DBSERVICE.Cluster.addr = ?;'''
    for cluster in clusters:
        for row in cur.execute(query, (cluster['addr'],)):
            cluster['clusterid'] = row[0]
    # Make responses!!
    query = '''SELECT Income.degree+Outcome.degree AS Degree, 
                      Income.value-Outcome.value AS Balance
               FROM (
                 SELECT COUNT(*) AS degree, SUM(DBCORE.TxOut.btc) AS value
                 FROM DBCORE.TxOut
                 WHERE DBCORE.TxOut.addr = ?) AS Income, (
                 SELECT COUNT(*) AS degree, SUM(DBCORE.TxOut.btc) AS value
                 FROM DBCORE.TxIn
                 INNER JOIN DBCORE.TxOut ON DBCORE.TxIn.ptx = DBCORE.TxOut.tx AND 
                            DBCORE.TxIn.pn = DBCORE.TxOut.n
                 WHERE DBCORE.TxOut.addr = ?) AS Outcome;'''
    for cluster in clusters:
        cur.execute(query, (cluster['addr'], cluster['addr']))
        row = cur.fetchone()
        response.append({'clusterID': cluster['clusterid'],
                         'clusterName': clustername,
                         'category': clustername,
                         'balance': row[1],
                         'transferCount': row[0],
                         'hasOsint': True})
    return response
