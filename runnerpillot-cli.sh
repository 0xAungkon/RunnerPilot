#!/bin/bash

echo "=== Runner Pilot: Self-Hosted GitHub Actions Runner CLI ==="

read -p "Enter GitHub Repository URL (e.g., https://github.com/org/repo): " RUNNER_URL
read -p "Enter GitHub Runner Token: " RUNNER_TOKEN
read -p "Enter Runner Name: " RUNNER_NAME
read -p "Enter Runner Labels (comma-separated): " RUNNER_LABELS

CONTAINER_NAME=$(echo "$RUNNER_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

echo "Spinning up GitHub Actions Runner: $RUNNER_NAME ..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart always \
  -e RUNNER_URL="$RUNNER_URL" \
  -e RUNNER_TOKEN="$RUNNER_TOKEN" \
  -e RUNNER_NAME="$RUNNER_NAME" \
  -e RUNNER_LABELS="$RUNNER_LABELS" \
  0xaungkon/gh-runner:latest

echo "Runner '$RUNNER_NAME' deployed successfully as container '$CONTAINER_NAME'."
