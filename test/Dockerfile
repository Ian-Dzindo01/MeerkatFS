FROM ubuntu:20.04

# system basics
RUN apt-get update
RUN apt-get -y install build-essential curl python3 python3-pip

COPY requirements.txt minikeyval/requirements.txt
RUN pip3 install --no-cache-dir -r minikeyval/requirements.txt
