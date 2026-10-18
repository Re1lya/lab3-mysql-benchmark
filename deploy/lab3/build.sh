#!/bin/bash
# Run on CDWY3. Preserve old images; bypass the image-removal Maven phase.
set -euo pipefail
source /etc/profile.d/lab3-tools.sh
export MAVEN_OPTS='-Xmx640m -XX:MaxMetaspaceSize=256m'
image="${APP_IMAGE:-xmu-javaee/productdemoaop:lab3-comparison-20261018}"
cd /root/spring-fundamentals
mvn -B -ntp -f clonefactory/pom.xml -Dmaven.compiler.release=21 -Dmaven.test.skip=true install
mvn -B -ntp -f '5. SpringAOP/pom.xml' -Djava.version=21 -Dmaven.test.skip=true package
docker build --build-arg JAR_FILE=target/productdemoaop-0.0.1-SNAPSHOT.jar \
  -t "$image" '5. SpringAOP/productdemoaop'
docker image inspect "$image" --format '{{.Id}}'
