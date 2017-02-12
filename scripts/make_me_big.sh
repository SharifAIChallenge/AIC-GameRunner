#!/usr/bin/env bash

if [ "$(whoami)" != "root" ]
then
    echo "Run me as root"
    exit 1
fi

if [ "$#" != "4" ]
then
    echo "Make this machine a big brain node."
    echo "Usage: $0 nfs_directory_on_server directory_on_client server_ip certificate_file"
    echo "Example: $0 /data/nfs /data/nfs 84.200.16.245 ca.crt"
    exit 1
fi

echo "Adding certificate ..."
mkdir -p "/etc/docker/certs.d/$3:5000"
cp "$4" "/etc/docker/certs.d/$3:5000/ca.crt"
echo "Added certificate. "

echo "Configuring NFS..."
#./nfs_client_v2.sh $1 $2 $3
#./nfs_client_automount.sh $1 $2 $3
echo "Configured NFS..."



echo "Run the following on a manager node:"
echo "$ docker swarm join-token worker"
echo "Then run the command provided by the manager node here to make this node a worker for that manger. "