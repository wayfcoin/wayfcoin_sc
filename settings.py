debug = False

if debug:  # Debug mode
    host = '127.0.0.1'
    db = 'vm'
    user = 'dev'
    password = 'qwertyuiop'
    port = 3306
    rpcPort = 10257
    rpcUser = 'wayfcoin'
    rpcPassword = 'dJLK0iuw6loAt8ZstLGYG6DRoR8DuPJVge'
    serverURL = 'http://' + rpcUser + ':' + rpcPassword + '@192.168.1.35:' + str(rpcPort)
else:  # Production mode
    host = '127.0.0.1'
    db = 'wayfapi'
    user = 'root'
    password = 'S92JvPAmQUgr5RAk'
    port = 3306
    rpcPort = 10257
    rpcUser = 'admin'
    rpcPassword = '123'
    serverURL = 'http://' + rpcUser + ':' + rpcPassword + '@localhost:' + str(rpcPort)
