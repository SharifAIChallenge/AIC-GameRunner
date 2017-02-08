if [ "$(whoami)" != "root" ]
then
    echo "Run me as root"
    exit 1
fi

if [ "$#" != "3" ]
then
    echo "NFS Client Script!"
    echo "Usage: $0 nfs_directory_on_server directory_on_client server_ip"
    echo "Example: $0 /data/nfs 84.200.16.245"
    exit 1
fi

apt-get update
apt-get install nfs-common -y

mkdir -p $2
mount $3:$1 $2

#For Auto Mount On Boot add to fstab: $3:$1    $2   nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0
