#!/usr/bin/env bash

if [ "$(whoami)" != "root" ]
then
    echo "Run me as root"
    exit 1
fi

echo "Removing current registry if exists."
sudo docker rm -f /registry

if [ $# -eq 3 ]
	then
		if [ $3 == "pull_through_cache" ]
			then
			    mkdir auth
                docker run --entrypoint htpasswd registry:2 -Bbn $1 $2 > auth/htpasswd
				echo "Starting Registry As A Pull Through Cache."
				sudo docker run\
                -d\
                -p 5000:5000\
                -v `pwd`/auth:/auth\
                -e "REGISTRY_AUTH=htpasswd"\
                -e "REGISTRY_AUTH_HTPASSWD_REALM=AIC Private Registry."\
                -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd\
                -e REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io\
				-v "`pwd`/data":/var/lib/registry\
                -v "`pwd`/certs":/certs\
                -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/registry.crt\
                -e REGISTRY_HTTP_TLS_KEY=/certs/registry.key\
                -e REGISTRY_HTTP_ADDR=0.0.0.0:5000 \
                --restart=always\
                --name registry\
                registry:2
			else
				echo "Bad argument provided."
		fi
elif [ $# -eq 2 ]
then
            mkdir auth
            docker run --entrypoint htpasswd registry:2 -Bbn $1 $2 > auth/htpasswd
            echo "Starting Registry."
            sudo docker run\
            -d\
            -p 5000:5000\
            -v `pwd`/auth:/auth\
		    -v "`pwd`/data":/var/lib/registry\
            -v "`pwd`/certs":/certs\
            -e "REGISTRY_AUTH=htpasswd"\
            -e "REGISTRY_AUTH_HTPASSWD_REALM=AIC Private Registry."\
            -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd\
            -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/registry.crt\
            -e REGISTRY_HTTP_TLS_KEY=/certs/registry.key\
            -e REGISTRY_HTTP_ADDR=0.0.0.0:5000 \
            --restart=always\
            --name registry\
            registry:2
else
    echo "Usage: secure_docker_start_registry.sh <certificate_name> [pull_through_cache]"
    exit 1
fi