#!/bin/bash
# Compatibility entry: the teacher-version script is authoritative.
set -euo pipefail
exec bash "$(dirname "$0")/build-teacher.sh" "$@"
