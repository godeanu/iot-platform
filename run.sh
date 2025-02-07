#!/bin/bash

export SCD_DVP=/var/lib/docker/volumes

echo "Building Docker images..."
docker build -t adaptor_image ./server
docker build -t generator_image ./generator

echo "Deploying Docker Swarm stack..."
docker stack deploy -c stack.yml scd3

echo "Stack deployed!"
