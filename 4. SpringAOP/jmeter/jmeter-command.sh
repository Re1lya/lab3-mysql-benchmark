#!/bin/bash
set -eu
cd "$(dirname "$0")"
export JVM_ARGS="-Xms256m -Xmx768m -Xss512k -XX:MaxMetaspaceSize=192m"
name=$1-$2-$3-$4
echo "testing ${name} ....."
mkdir ${name}
jmeter -n -t $1.jmx -Jthread.num=$2 -Jrampup.period=$3 -Jloop.count=$4 -l ${name}.jtl -e -o ${name}/

