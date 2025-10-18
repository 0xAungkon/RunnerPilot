#!/bin/bash
set -e

if [ ! -f "./is_configured" ]; then
    ./config.sh --unattended --url "${RUNNER_URL}" --token "${RUNNER_TOKEN}" --name "${RUNNER_NAME}" --labels "${RUNNER_LABELS}"
    touch ./is_configured
fi

exec ./run.sh
