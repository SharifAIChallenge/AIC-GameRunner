#!/usr/bin/env bash
echo "Removing current registry if exists."
sudo docker rm -f /registry

mkdir -p certs && openssl req \
 -newkey rsa:4096 -nodes -sha256 -keyout certs/$1.key \
 -x509 -days 365 -out certs/$1.crt

if [ $# -eq 2 ]
	then
		if [ $2 == "pull_through_cache" ]
			then
				echo "Starting Registry As A Pull Through Cache."
				sudo docker run\
				 -d\
				 -p 443:5000\
				 -e REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io\
                 -v `pwd`/certs:/certs\
                 -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/$1.crt\
                 -e REGISTRY_HTTP_TLS_KEY=/certs/$1.key\
				 --restart=always\
				 --name registry\
				 registry:2
			else
				echo "Bad argument provided."
		fi
	else
                echo "Starting Registry."
                sudo docker run\
                 -d\
				 -p 443:5000\
				 -e REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io\
                 -v `pwd`/certs:/certs\
                 -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/$1.crt\
                 -e REGISTRY_HTTP_TLS_KEY=/certs/$1.key\
                 --restart=always\
                 --name registry\
                 registry:2
fi
