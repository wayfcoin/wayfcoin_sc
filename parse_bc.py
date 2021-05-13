import pymysql
import requests
import json
import time
import os
import settings
import uuid
from tqdm import tqdm

if not settings.debug:
    if 'sync.pid' in os.listdir('.'):
        print('Syncing...')
        exit()
else:
    pass


def create_connection():
    return pymysql.connect(
        host=settings.host,
        db=settings.db,
        user=settings.user,
        password=settings.password,
        port=settings.port,
        autocommit=True
    )


schema = """
CREATE TABLE data (
id INT(11),
block INT(11),
txid VARCHAR(1000),
sender VARCHAR(1000),
txcomment VARCHAR(1000),
uuid VARCHAR(1000),
blocktime INT(11)
)
"""

schema_info = """
CREATE TABLE info (
last_block INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY
)
"""

try:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(schema)
    conn.commit()
    conn.close()
except:
    pass
try:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(schema_info)
    conn.commit()
    conn.close()
except:
    pass

open('sync.pid', 'w')

def get_randomstring(length):
    return str(uuid.uuid4().hex.upper()[0:length])

def get_lastid():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM data")
    result = cursor.fetchall()[0][0]
    conn.close()
    if result == None:
        return 0
    else:
        return result + 1

def get_lastblock():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(last_block) FROM info")
    result = cursor.fetchall()[0][0]
    conn.close()
    if result == None:
        return 0
    else:
        return result + 1

def add_to_database(height,txid,sender,txcomment,unixtime):
    uuid = get_randomstring(16)
    sql_insert = "INSERT INTO data VALUES (%s, %s, '%s', '%s', '%s', '%s',%s)" % (
        int(get_lastid()), int(height), str(txid), str(sender), str(txcomment).replace("'",'"'),str(uuid),int(unixtime))
    print(sql_insert)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(sql_insert)
    conn.commit()
    conn.close()

class RPCHost(object):
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}

    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self._url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                hadFailedConnections = True
                print(
                    "Couldn't connect for remote procedure call, will sleep for five seconds and then try again ({} more tries)".format(
                        tries))
                print("Check your daemon or creditinals")
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']


host = RPCHost(settings.serverURL)

coin_height = host.call('getblockcount')
print('Starting from:', get_lastblock())
print('Finishing on:', coin_height)
for height in tqdm(range(get_lastblock(), coin_height+1)):
    try:
        if height == 0:
            pass
        else:
            block_info = host.call('getblockbynumber', height)
            tx_list = block_info['tx']
            for transaction in tx_list:
                tx_info = host.call('gettransaction', transaction)
                unixtime = tx_info['time']
                txcomment = tx_info['txcomment']
                txid = tx_info['txid']
                vin = tx_info['vin'][0]
                try:
                    vin['coinbase']
                except:
                    pass
                if txcomment != '':
                    sender_info = host.call('gettransaction', vin['txid'])
                    sender = sender_info['vout'][0]['scriptPubKey']['addresses'][0]
                    add_to_database(height, txid, sender, txcomment, unixtime)
                else:
                    pass
    except:
        pass

sql_insert_block = "INSERT INTO info VALUES (%s)" % (
    int(coin_height),)
conn = create_connection()
cursor = conn.cursor()
cursor.execute(sql_insert_block)
conn.commit()
conn.close()

os.remove('sync.pid')
