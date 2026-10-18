#!/bin/bash
set -euo pipefail
set -a
source /root/.config/lab3/deploy.env
set +a
docker stack deploy --resolve-image never \
  -c '/root/spring-fundamentals/4. SpringAOP/conf/docker/productdemoaop-docker.yml' lab
docker service ls
