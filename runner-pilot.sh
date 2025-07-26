#!/bin/bash

set -e

REPO_BASE="https://raw.githubusercontent.com/0xAungkon/RunnerPilot/refs/heads/main"
INSTALL_PATH="/bin/runner-pilot"
TMP_DIR="/tmp/run-pillot"
RUN_SCRIPT="$TMP_DIR/run.sh"
DOCKERFILE="$TMP_DIR/Dockerfile"

require_root() {
  if [[ $EUID -ne 0 ]]; then
    echo "Error: sudo user required for this operation."
    exit 7530
  fi
}

require_dependencies() {
  for cmd in curl docker; do
    if ! command -v $cmd &>/dev/null; then
      echo "Error: '$cmd' is required but not installed."
      exit 7530
    fi
  done
}

print_help() {
  cat <<EOF
Usage: runner-pilot.sh [COMMAND] [ARGS]

Commands:
  install                   Install RunnerPilot to /bin/
  run <repo-url> <token>   Run a GitHub Actions runner container
  ps                        List running/stopped runner containers
  down -p <container-id>    Stop a specific runner container
  down -r <container-id>    Remove a specific runner container
  --help                    Show this help message
EOF
}

install_runner() {
  require_root
  curl -fsSL "$REPO_BASE/runner-pilot" -o "$INSTALL_PATH"
  chmod +x "$INSTALL_PATH"
  "$INSTALL_PATH" --help
}

run_runner() {
  require_root
  require_dependencies

  REPO_URL="$1"
  GITHUB_TOKEN="$2"

  mkdir -p "$TMP_DIR"

  [[ -f "$RUN_SCRIPT" ]] || curl -fsSL "$REPO_BASE/runner-pillot/run.sh" -o "$RUN_SCRIPT"
  [[ -f "$DOCKERFILE" ]] || curl -fsSL "$REPO_BASE/runner-pillot/Dockerfile" -o "$DOCKERFILE"
  chmod +x "$RUN_SCRIPT"

  "$RUN_SCRIPT" --url "$REPO_URL" --token "$GITHUB_TOKEN"
}

list_containers() {
  docker ps -a --format '{{.Names}}\t{{.Status}}\t{{.CreatedAt}}' | grep '^runner_' || true
}

stop_container() {
  require_root
  docker stop "$1"
}

remove_container() {
  require_root
  docker rm -f "$1"
}

main() {
  case "$1" in
    install)
      install_runner
      ;;
    run)
      [[ -z "$2" || -z "$3" ]] && { echo "Error: Missing arguments for run"; exit 1; }
      run_runner "$2" "$3"
      ;;
    ps)
      list_containers
      ;;
    down)
      [[ "$2" == "-p" && -n "$3" ]] && stop_container "$3" && exit 0
      [[ "$2" == "-r" && -n "$3" ]] && remove_container "$3" && exit 0
      echo "Error: Invalid down usage"
      exit 1
      ;;
    --help)
      print_help
      ;;
    *)
      echo "Error: Unknown command"
      print_help
      exit 1
      ;;
  esac
}

main "$@"
