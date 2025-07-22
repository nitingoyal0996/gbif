#!/bin/bash
# Update deployment script
# This script is used to update the deployment of the gbif docker container
# It is run by the root user on the server
# Pull the latest code from the repo > rebuild the docker image > stop and remove the existing container > run the new container > check if the container is running

PORT=29195

if [ $(id -u) -ne 0 ]; then
    echo "Please run this script as root"
    exit 1
fi
git pull

docker build -t gbif .
docker stop gbif
docker rm gbif
docker run -d -p $PORT:9999 --name gbif gbif
docker ps
