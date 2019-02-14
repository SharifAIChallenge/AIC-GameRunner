FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y curl
RUN apt-get install -y vim
RUN apt-get install -y netcat

RUN pip3 install --upgrade pip
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN mkdir /gamerunner
WORKDIR /gamerunner

COPY requirements.txt /gamerunner/
RUN pip install -r requirements.txt

COPY . /gamerunner/

RUN chmod +x docker-entrypoint.sh
RUN chmod +x manage.py
