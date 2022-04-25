#!/bin/bash
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT       # kill the script on exit

./volume tmp/volume1/ &                                        # volume and master
PORT=3002 ./volume tmp/volume1/ &
./master localhost:3001,localhost:3002 /tmp/cachedb/ &


