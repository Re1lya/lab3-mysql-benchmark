#!/bin/sh
set -eu
if [ "$#" -ne 4 ]; then
  echo "Usage: sh jmeter-command.sh ReadProduct|WriteProduct threads rampup_seconds loops" >&2
  exit 2
fi
case "$1" in ReadProduct|WriteProduct) ;; *) echo 'Unsupported test plan' >&2; exit 2;; esac
for value in "$2" "$3" "$4"; do
  case "$value" in ''|*[!0-9]*|0) echo 'Arguments must be positive integers' >&2; exit 2;; esac
done
cd "$(dirname "$0")"
export HEAP="${HEAP:--Xms256m -Xmx768m -XX:MaxMetaspaceSize=192m}"
export JVM_ARGS="${JVM_ARGS:--Xss512k}"
run_name="$1-$2-$3-$4-$(date +%Y%m%d-%H%M%S)-$$"
result_root="${RESULT_DIR:-/root/lab3-results}"
mkdir -p "$result_root"
echo "Run: $run_name; target: ${TARGET_HOST:-172.31.1.202}:${TARGET_PORT:-8080}"
jmeter -n -t "$1.jmx" \
  -Jthread.num="$2" -Jrampup.period="$3" -Jloop.count="$4" \
  -Jhostname="${TARGET_HOST:-172.31.1.202}" -Jport="${TARGET_PORT:-8080}" \
  -Jshop.id="${SHOP_ID:-10}" -Jjmeter.reportgenerator.overall_granularity=1000 \
  -l "$result_root/$run_name.jtl" -j "$result_root/$run_name.log" \
  -e -o "$result_root/$run_name"
echo "Results: $result_root/$run_name.jtl"
