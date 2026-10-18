#!/bin/bash
# Run on CDWY1. Credentials remain outside the repository.
set -euo pipefail
set -a
source /root/.config/lab3/deploy.env
set +a
docker stack deploy --resolve-image never \
  -c '/root/spring-fundamentals/5. SpringAOP/conf/docker/productdemoaop-docker.yml' lab
docker service ls
