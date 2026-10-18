#!/bin/bash
# Run on the load generator. HTML reports are generated AFTER all sampling.
set -euo pipefail
source /etc/profile.d/lab3-tools.sh
operation=$1; threads=$2; ramp=$3; loops=$4; duration=$5; timed=$6; run_id=$7
case "$operation" in ReadProduct|WriteProduct) ;; *) exit 2;; esac
[[ "$run_id" =~ ^[A-Za-z0-9_-]+$ ]] || exit 2
out=/root/lab3-results/comparison-20261018/$run_id
mkdir -p "$out"
cd '/root/spring-fundamentals/5. SpringAOP/jmeter'
export HEAP='-Xms256m -Xmx768m -XX:MaxMetaspaceSize=192m'
export JVM_ARGS='-Xss512k'
date -Is > "$out/start.txt"
timeout --signal=TERM --kill-after=20s "$((duration + 90))s" jmeter -n \
  -t "${operation}Comparison.jmx" -Jthread.num="$threads" -Jrampup.period="$ramp" \
  -Jloop.count="$loops" -Jduration="$duration" -Jtimed="$timed" -Jrun.id="$run_id" \
  -Jhostname=172.31.1.202 -Jport=8080 -Jshop.id=10 \
  -Jsample_variables=response_id -Jjmeter.save.saveservice.timestamp_format=ms \
  -Jjmeter.reportgenerator.overall_granularity=1000 \
  -l "$out/samples.jtl" -j "$out/jmeter.log" > "$out/console.log" 2>&1
date -Is > "$out/end.txt"
