#!/usr/bin/env bash
echo "Removing current registry if exists."
sudo docker rm -f /registry

if [ $# -eq 1 ]
	then
		if [ $1 == "pull_through_cache" ]
			then
				echo "Starting Registry As A Pull Through Cache."
				sudo docker run\
                -d\
                -p 5000:5000\
                -e REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io\
                -v `pwd`/certs:/certs\
                -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/registry.crt\
                -e REGISTRY_HTTP_TLS_KEY=/certs/registry.key\
                -e REGISTRY_HTTP_ADDR=0.0.0.0:5000 \
                --restart=always\
                --name registry\
                registry:2
			else
				echo "Bad argument provided."
		fi
elif [ $# -eq 0 ]
then
            echo "Starting Registry."
            sudo docker run\
            -d\
            -p 5000:5000\
            -v `pwd`/certs:/certs\
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
