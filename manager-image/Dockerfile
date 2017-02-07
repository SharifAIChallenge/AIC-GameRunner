FROM ubuntu

RUN apt-get update
RUN apt-get install -y curl python python-pip
RUN apt-get install -y apt-transport-https ca-certificates
RUN curl -fsSL https://yum.dockerproject.org/gpg | apt-key add -
RUN echo "deb https://apt.dockerproject.org/repo/ ubuntu-xenial main" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y install docker-engine
RUN pip install PyYAML

ADD run.sh /run.sh
ADD sc.py /sc.py

CMD [ "/bin/bash" , "/run.sh" ]
