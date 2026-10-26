#!/bin/bash
# Runs the given command and retries it with increasing delays if it fails.
# TeX Live mirrors are occasionally unreachable or serve broken certificates. mirror.ctan.org redirects to a different
# mirror on each request, so a retry usually reaches a working one.
# Exits with the exit code of the last attempt.
# Usage: retry.sh <command> [args...]

if [ "$#" -eq 0 ]; then
    echo "usage: retry.sh <command> [args...]" >&2
    exit 2
fi

max_attempts=5

for attempt in $(seq 1 "$max_attempts"); do
    "$@"
    exit_code=$?
    if [ "$exit_code" -eq 0 ]; then
        exit 0
    fi
    echo "attempt ${attempt}/${max_attempts} failed with exit code ${exit_code}: $*" >&2
    if [ "$attempt" -lt "$max_attempts" ]; then
        sleep $((attempt * 10))
    fi
done
exit "$exit_code"
