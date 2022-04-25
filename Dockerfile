FROM ubuntu:20.04

# system basics
RUN apt-get update
RUN apt-get -y install build-essential curl python3 python3-pip

RUN pip install -r requirements.txt
