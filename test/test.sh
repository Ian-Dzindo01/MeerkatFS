#!/bin/bash
docker build -t minikeyval -f Dockerfile .
docker run -p 3000:3000 -p 3001:3001 -p 3002:3002 --rm minikeyval minikeyval
