#!/bin/bash
docker build -t minikeyvalue -f Dockerfile .           # build image from Dockerfile
docker run --hostname localhost -p 3000:3000 -p 3001:3001 -p 3002:3002 --name minikeyval --rm minikeyval bash -c "cd /tmp"   #&& test/bringup.sh"   #c is CPU shares


# build Dockerfile
# specify ports for volume and master servers

