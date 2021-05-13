echo "Installing MySQL and Wayfcoin dependencies..."
apt -qq update
MYSQL_ROOT_PASSWORD='S92JvPAmQUgr5RAk'
echo "Installing Wayfcoin dependencies..."
apt -qq install build-essential libtool automake autotools-dev autoconf pkg-config libssl-dev libgmp3-dev libevent-dev bsdmainutils wget screen apt-utils unzip -y
apt -qq install libboost-system-dev libboost-filesystem-dev libboost-chrono-dev libboost-program-options-dev libboost-test-dev libboost-thread-dev -y
apt -qq install python3 python3-pip python3-dev libffi-dev -y
echo "Dependencies has been installed successfully!"
export DEBIAN_FRONTEND=noninteractive
apt-get install -y tzdata
echo debconf mysql-server/root_password password $MYSQL_ROOT_PASSWORD | debconf-set-selections
echo debconf mysql-server/root_password_again password $MYSQL_ROOT_PASSWORD | debconf-set-selections
echo "Installing and configuring MySQL..."
apt-get -qq install mysql-server > /dev/null
/etc/init.d/mysql restart
apt-get -qq install expect > /dev/null
tee ~/secure_our_mysql.sh > /dev/null << EOF
spawn $(which mysql_secure_installation)
expect "Enter password for user root:"
send "$MYSQL_ROOT_PASSWORD\r"
expect "Press y|Y for Yes, any other key for No:"
send "y\r"
expect "Please enter 0 = LOW, 1 = MEDIUM and 2 = STRONG:"
send "2\r"
expect "Change the password for root ? ((Press y|Y for Yes, any other key for No) :"
send "n\r"
expect "Remove anonymous users? (Press y|Y for Yes, any other key for No) :"
send "y\r"
expect "Disallow root login remotely? (Press y|Y for Yes, any other key for No) :"
send "y\r"
expect "Remove test database and access to it? (Press y|Y for Yes, any other key for No) :"
send "y\r"
expect "Reload privilege tables now? (Press y|Y for Yes, any other key for No) :"
send "y\r"
EOF
expect ~/secure_our_mysql.sh
rm -v ~/secure_our_mysql.sh
mysql -u root -pS92JvPAmQUgr5RAk -e "CREATE DATABASE wayfapi CHARACTER SET utf8 COLLATE utf8_general_ci;"
echo "MySQL has been installed and configured successfully!"
apt -qq install software-properties-common -y
add-apt-repository ppa:bitcoin/bitcoin -y
apt -qq update
apt -qq install libdb4.8-dev libdb4.8++-dev -y
apt -qq install libminiupnpc-dev -y
apt-get -qq install zlib1g-dev -y
apt-get -qq install libssl1.0-dev -y
wget https://github.com/wayfcoin/source/releases/download/2/Wayfcoind_boost
chmod +x Wayfcoind_boost
mv Wayfcoind_boost /usr/bin/Wayfcoind
screen -S wayfdaemon -d -m Wayfcoind -daemon -rpcport=10257 -rpcallowip=127.0.0.1 -rpcuser=admin -rpcpassword=123 -addnode=194.58.104.157
sleep 5
screen -S wayfdaemon -d -m Wayfcoind -daemon -rpcport=10257 -rpcallowip=127.0.0.1 -rpcuser=admin -rpcpassword=123 -addnode=194.58.104.157
echo "Wayfcoin daemon has been installed successfully, it can be accessed via Wayfcoind"
echo "It is installed to /usr/bin/Wayfcoind, so you can run it directly from shell"
echo "Wayfcoind -daemon -rpcport=10257 -rpcuser=admin -rpcpassword=123 getinfo"
pip3 install --upgrade pip
pip3 install flask pymysql requests scp paramiko gunicorn flask-recaptcha tqdm
#screen -S parser -d -m python3 watchdog.py parse_bc.py
#screen -S api -d -m gunicorn wayfvm_api:app -b 0.0.0.0:3000
cd / && echo "/etc/init.d/mysql start" > start.sh
cd / && echo "cd wayfcoin_sc" >> start.sh
cd / && echo "Wayfcoind -daemon -rpcport=10257 -rpcallowip=127.0.0.1 -rpcuser=admin -rpcpassword=123 -addnode=194.58.104.157" >> start.sh
cd / && echo "screen -S parser -d -m python3 watchdog.py parse_bc.py" >> start.sh
cd / && echo "screen -S api -d -m gunicorn wayfvm_api:app -b 0.0.0.0:3000" >> start.sh
cd / && echo "/bin/bash" >> start.sh
cd / && echo "tail -f /dev/null" >> start.sh
cd / && chmod +x start.sh
