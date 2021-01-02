#!/bin/bash -x
docker tag speedbot:latest 192.168.1.32:5000/speedbot:stable
docker -l debug push 192.168.1.32:5000/speedbot:stable
docker rmi 192.168.1.32:5000/speedbot:stable
