#!/usr/bin/env bash

# A crude but good-enough way to build a Docker image locally.
# This script assumes you understand Google Application Default Credentials
# and have set GOOGLE_APPLICATION_CREDENTIALS to point to a service account key
# Details: https://cloud.google.com/docs/authentication/application-default-credentials

set -euo pipefail

time docker build \
  --secret id=gcloud-key.json,src="${GOOGLE_APPLICATION_CREDENTIALS}" \
  --target test .

IMAGE_TAG=${1:-$(basename "$PWD")}:latest
ARCH=$(uname -m)  # Now that we're in the age of silicon and architecture wars, this is a bit more complex

# Define architecture key-value pairs; no clue if anything beside arm64 works, tho
declare -A ARCHITECTURE_MAP=(
  ["x86_64"]="linux/amd64"
  ["arm64"]="linux/arm64"
  ["armv7l"]="linux/arm/v7"
  ["armv6l"]="linux/arm/v6"
)

# Check if architecture is supported
if [[ -z "${ARCHITECTURE_MAP[$ARCH]:-}" ]]; then
  echo "Unsupported architecture: $ARCH"
  exit 1
fi

# Get the Docker platform for the detected architecture
PLATFORM="${ARCHITECTURE_MAP[$ARCH]}"

GIT_COMMIT=$(git rev-parse --short HEAD)
BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
BUILD_LOG_URL="localhost"
time docker build \
  --secret id=gcloud-key.json,src="${GOOGLE_APPLICATION_CREDENTIALS}" \
  --platform "$PLATFORM" \
  --build-arg GIT_COMMIT="$GIT_COMMIT" \
  --build-arg BUILD_TIMESTAMP="$BUILD_TIMESTAMP" \
  --build-arg BUILD_LOG_URL="$BUILD_LOG_URL" \
  -t "$IMAGE_TAG" .
