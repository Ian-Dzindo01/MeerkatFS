FROM ubuntu:20.04

# system basics
RUN apt-get update && apt-get -y install build-essential curl python3 python3-pip libffi-dev

#copies from local source to destination container
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
COPY . /tmp/

# instructions to set up container
