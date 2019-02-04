# Installation

## Install Postgres
Install postgres on your server
```
$ sudo apt update
$ sudo apt install postgresql postgresql-contrib
```
Connect postgres from postgres account on your server
```
$ sudo -u postgres psql
```
Create database for project
```
postgres=# CREATE DATABASE game_runner;
```
Create role for project
```
postgres=# CREATE USER game_runner_user WITH PASSWORD 'password';
postgres=# ALTER ROLE game_runner_user SET client_encoding TO 'utf8';
postgres=# ALTER ROLE game_runner_user SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE game_runner_user SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE game_runner TO game_runner_user;
postgres=# \q
```

## Install Docker 

## Create SSL Certificate
```
$ sudo ./scripts/create_registry_certificates.sh <middle_ip>
```

## Install Dependencies
Run make_me_big.sh in scripts folder as root
```
$ sudo ./scripts/make_me_big.sh <nfs_dir_middle> <nfs_dir_worker> <middle_ip> <certificate_file>
```

## Start Docker Registry
```
sudo ./scripts/docker_start_registry.sh 
```
Or for more security:
```
sudo ./scripts/secure_docker_start_registry.sh <username> <password> [pull_through_cache]
```
* pull_through_cache can be used for cache settings

## Mount NFS
mount nfs in master server:
```
sudo ./scripts/nfs_server_create.sh <nfs_dir> <client_ips(space sperated in qoutations)>
```
mount nfs in worker:
```
sudo ./scripts/nfs_client_v2.sh <nfs_dir_on_server> <nfs_dir_on_client> <server_ip>
```

## Start Project
Collect statics and serve it using nginx
Run project using gunicorn or create system service for service 