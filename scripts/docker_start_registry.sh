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
				 -e "REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io"\
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
                 -p 5000:5000\
                 --restart=always\
                 --name registry\
                 registry:2
fi
