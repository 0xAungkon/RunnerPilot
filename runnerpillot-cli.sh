#!/bin/bash

APP_NAME="Runner Pilot"
IMAGE_NAME="0xaungkon/gh-runner:latest"

show_help() {
  echo "Usage: runner-pilot [command]"
  echo ""
  echo "Commands:"
  echo "  --help        Show this help message"
  echo "  --init        Pull the GitHub Actions Runner Docker image"
  echo "  run           Start an interactive TUI to configure and launch a self-hosted runner"
  echo ""
}

check_docker() {
  if ! command -v docker &> /dev/null; then
    echo "Error: Docker not found. Please install Docker and try again."
    exit 1
  fi
}

init_runner() {
  check_docker
  echo "Initializing $APP_NAME..."
  echo "Pulling image: $IMAGE_NAME"
  docker pull "$IMAGE_NAME"
  echo "Initialization complete."
}

run_tui() {
  check_docker
  echo "=== $APP_NAME: Self-Hosted GitHub Actions Runner Setup ==="
  echo ""

  read -p "Enter GitHub Repository URL (e.g., https://github.com/org/repo): " RUNNER_URL
  read -p "Enter GitHub Runner Token: " RUNNER_TOKEN
  read -p "Enter Runner Name: " RUNNER_NAME
  read -p "Enter Runner Labels (comma-separated): " RUNNER_LABELS

  if [ -z "$RUNNER_URL" ] || [ -z "$RUNNER_TOKEN" ] || [ -z "$RUNNER_NAME" ]; then
    echo "Error: All fields are required."
    exit 1
  fi

  CONTAINER_NAME=$(echo "$RUNNER_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

  echo ""
  echo "--------------------------------------"
  echo "Runner Name   : $RUNNER_NAME"
  echo "Repository URL: $RUNNER_URL"
  echo "Labels        : $RUNNER_LABELS"
  echo "Container     : $CONTAINER_NAME"
  echo "--------------------------------------"
  echo ""

  read -p "Proceed to launch runner? (y/N): " CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi

  docker run -d \
    --name "$CONTAINER_NAME" \
    --restart always \
    -e RUNNER_URL="$RUNNER_URL" \
    -e RUNNER_TOKEN="$RUNNER_TOKEN" \
    -e RUNNER_NAME="$RUNNER_NAME" \
    -e RUNNER_LABELS="$RUNNER_LABELS" \
    "$IMAGE_NAME"

  echo ""
  echo "Runner '$RUNNER_NAME' is now active as container '$CONTAINER_NAME'."
}

case "$1" in
  --help)
    show_help
    ;;
  --init)
    init_runner
    ;;
  run)
    run_tui
    ;;
  *)
    echo "Unknown command: $1"
    echo "Use '--help' for usage information."
    ;;
esac