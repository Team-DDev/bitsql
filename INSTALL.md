# The manual for building BitSQL database with MariaDB

## Requirements

0. Library

```bash
sudo apt install libmariadb-dev
```

1. Download (bitcoin core)[https://bitcoin.org/en/download] and Block data

```bash
./bitcoind
```

2. configuration edit

- Download sample [bitcoin.conf](https://github.com/bitcoin/bitcoin/blob/master/share/examples/bitcoin.conf)

- Edit file

```
# add at line 75
server=1
    
# add at line 102: result from `generate_rpcauth.py`
rpcauth=...

# add at line 153
txindex=1
```

3. Reindex and Rescan (JUST ONCE!!)

- After performing once, run without parameters

```bash
bitcoind -reindex -rescan
```

4. Check bitcoin-cli COMMAND

```bash
./bitcoin-cli getblockheight 1
```

5. Create MariaDB container on docker

- Install docker and mariadb

- [Install on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

```bash
sudo apt install ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# uno to focal
sudo vi /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

- (Recommended) Running docker on a non-root user

- [Guide: Post-installation steps for Linux](https://docs.docker.com/engine/install/linux-postinstall/)

```bash
sudo usermod -aG docker $USER
```

- [MariaDB Docker Hub Reference](https://hub.docker.com/_/mariadb)

  - [System Variable](https://mariadb.com/kb/en/server-system-variables/)

```bash
docker pull mariadb
docker run --name bitsqldb -p 3306:3306 -v /my/own/datadir/var/lib/mysql:/var/lib/mysql -e MARIADB_ROOT_PASSWORD=my-secret-pw -d mariadb:latest --innodb_buffer_pool_size=137438953472 --key_buffer_size=137438953472 --max_allowed_packet=1073741824
```

- Create user and database

```bash
docker exec -it bitsqldb bash
mariadb -uroot -p
```

```sql
CREATE DATABASE bitsqldb;
CREATE USER IF NOT EXISTS user@bitsqldb IDENTIFIED BY 'user-secret-pw';
SHOW WARNINGS;
GRANT ALL PRIVILEGES ON bitsqldb.* TO 'user'@'%' IDENTIFIED BY 'user-secret-pw';
FLUSH PRIVILEGES;
SET GLOBAL query_cache_size = 1073741824;
```

- Create `secret.py`

```python
# Contents of secret.py
rpcuser = USER
rpcpassword = PASSWORD
dbrootpassword = PASSWORD
dbdatabase = DATABASE
dbuser = USER
dbpassword = PASSWORD
dbhost = HOST
dbport = PORT
```

6. Install python3 library and install library

```bash
apt install libmariadb-dev
python3 -m venv venv
source venv/bin/activate
pip3 install --upgrade -r requirements.txt
```
