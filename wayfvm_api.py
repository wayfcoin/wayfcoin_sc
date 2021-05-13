from flask import Flask, jsonify, request
import json, time, requests
import pymysql
import settings

def create_connection():
    return pymysql.connect(
        host=settings.host,
        db=settings.db,
        user=settings.user,
        password=settings.password,
        port=settings.port,
        autocommit=True
    )


class RPCHost(object):
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}

    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        print(payload)
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self._url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
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
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

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

@app.route('/api/txs', methods=['GET'])
def list_txs():
    id_to_get = request.args.get('id')
    if id_to_get != None:
        sql = "SELECT * FROM data WHERE id = %s" % (int(id_to_get),)
    else:
        sql = "SELECT * FROM data"
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    tx_list = []
    for i in result:
        tx_list_inserting = {}
        tx_list_inserting['id'] = i[0]
        tx_list_inserting['sender'] = i[3]
        if str(i[4][:5]) == 'text:':
            txcomment = str(i[4][5:])
        else:
            txcomment = str(i[4])
        tx_list_inserting['data'] = txcomment
        tx_list_inserting['uuid'] = str(i[2])
        tx_list_inserting['time'] = str(i[6])
        tx_list.append(tx_list_inserting)
    return jsonify([{'total_txs':get_lastid()},tx_list])


@app.route('/api/txs', methods=['POST'])
def send_tx():
    data = json.loads(request.data.decode('utf-8'))
    code = data['code']
    try:
        new_addr = host.call('getnewaddress')
        sent_tx = host.call('sendtoaddress', str(new_addr), float(0.0001), "", "", str(code))
        return {
            'success': 'true',
            'message': '',
            'hash': sent_tx
        }
    except Exception as e:
        return {
            'success': 'false',
            'message': str(e),
            'hash': ''
        }


@app.errorhandler(404)
def page_not_found(e):
    return '404', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002)
