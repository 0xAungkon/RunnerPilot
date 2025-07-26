#!/bin/bash

VERSION="2.327.0"

docker image inspect github-runner:$VERSION > /dev/null 2>&1 || docker build -t github-runner:$VERSION .

if [ $# -ne 2 ]; then
  echo "Usage: $0 <github_repo_url> <github_token>"
  exit 1
fi

REPO_URL="$1"
GITHUB_TOKEN="$2"
REPO_NAME=runner_$(basename "$REPO_URL" | tr '[:upper:]' '[:lower:]')

docker stop $REPO_NAME
docker rm $REPO_NAME
docker run -d --restart=always \
  -e GITHUB_REPO_URL=$REPO_URL \
  -e GITHUB_RUNNER_TOKEN=$GITHUB_TOKEN \
  --name $REPO_NAME \
  github-runner:$VERSION
