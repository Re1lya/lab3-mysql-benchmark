#!/bin/bash
set -euo pipefail
source /etc/profile.d/lab3-tools.sh
export MAVEN_OPTS='-Xmx640m -XX:MaxMetaspaceSize=256m'
cd /root/spring-fundamentals
mvn -B -ntp -f clonefactory/pom.xml -Dmaven.compiler.release=21 -Dmaven.test.skip=true install
mvn -B -ntp -f '4. SpringAOP/pom.xml' -Djava.version=21 -pl core -am -Dmaven.test.skip=true install
mvn -B -ntp -f '4. SpringAOP/pom.xml' -Djava.version=21 -Dmaven.test.skip=true package
docker build --build-arg JAR_FILE=target/productdemoaop-0.0.1-SNAPSHOT.jar \
  -t xmu-javaee/productdemoaop:lab3-teacher-20261018 '4. SpringAOP/productdemoaop'
docker image inspect xmu-javaee/productdemoaop:lab3-teacher-20261018 --format '{{.Id}}'
