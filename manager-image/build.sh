#!/bin/bash
apt-get update
apt-get install -y curl python python-pip
apt-get install -y apt-transport-https ca-certificates
curl -fsSL https://yum.dockerproject.org/gpg | apt-key add -
echo "deb https://apt.dockerproject.org/repo/ ubuntu-xenial main" >> /etc/apt/sources.list
apt-get update
apt-get -y install docker-engine
pip install PyYAML

