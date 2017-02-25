if [ "$(whoami)" != "root" ]
then
    echo "Run me as root"
    exit 1
fi

if [ "$#" != "2" ]
then
    echo "NFS Server Reconfigure Script!"
    echo "Usage: $0 nfs_directory client_ips"
    echo "Example: $0 /data/nfs '78.47.157.48 192.168.1.1'"
    exit 1
fi

printf "$1" > /etc/exports
for ip in $2
do
    printf " $ip(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports
done
echo '' >> /etc/exports

systemctl restart nfs-kernel-server
