#!/bin/bash
cp -r compose compose-fin
cd compose-fin
name=ttt
nodeid=`docker info 2> /dev/null | grep NodeID | awk 'NF>1{print $NF}'`
nos=`python -c  'import yaml; print(len( yaml.load(open("docker-compose.yml")) )) '`
python ../sc.py $nodeid > docker-compose-final.yml

echo Number of services: $nos

docker stack deploy -c docker-compose-final.yml $name
while [ $nos -ne `docker stack ps $name | tail -n +2 | awk '{print $5}' | grep Running | wc -l` ] ; 
do
    sleep 0.5
done
echo All services are running

while [ $nos -ne `docker stack ps $name | tail -n +2 | awk '{print $5}' | grep Shutdown | wc -l` ] ; 
do
    sleep 0.5
done

echo All services done their job

docker stack rm $name
