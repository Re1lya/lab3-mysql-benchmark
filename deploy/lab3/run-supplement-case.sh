#!/bin/bash
# Supplemental matrix; unchanged JMX payloads and assertions.
set -euo pipefail
source /etc/profile.d/lab3-tools.sh
operation=$1; threads=$2; ramp=$3; loops=$4; run_id=$5
case "$operation" in ReadProduct|WriteProduct) ;; *) exit 2;; esac
[[ "$run_id" =~ ^[A-Za-z0-9_-]+$ ]] || exit 2
out=/root/lab3-results/supplement-20261018/$run_id
test ! -e "$out/samples.jtl" || exit 3
mkdir -p "$out"
cd '/root/spring-fundamentals/4. SpringAOP/jmeter'
export HEAP='-Xms256m -Xmx768m -XX:MaxMetaspaceSize=192m'
export JVM_ARGS='-Xss512k'
date -Is > "$out/start.txt"
timeout --signal=TERM --kill-after=20s 180s jmeter -n -t "$operation.jmx" \
  -Jthread.num="$threads" -Jrampup.period="$ramp" -Jloop.count="$loops" \
  -Jjmeter.save.saveservice.timestamp_format=ms -Jjmeter.reportgenerator.overall_granularity=1000 \
  -l "$out/samples.jtl" -j "$out/jmeter.log" > "$out/console.log" 2>&1
date -Is > "$out/end.txt"
