#!/usr/bin/env bash
set -euo pipefail
case "${1:-}" in
  proto-lint) buf format -w && buf lint && buf breaking --against '.git#branch=main' || true ;;
  proto-gen)  buf generate ;;
  java)       (cd services/controlplane-java && ./gradlew --no-daemon clean build) ;;
  agent)      CONTROLPLANE_ADDR=${CONTROLPLANE_ADDR:-http://localhost:9090} \
              dotnet run --project clients/dotnet/device-agent/DeviceAgent/DeviceAgent.csproj ;;
  *) echo "Usage: dev.sh {proto-lint|proto-gen|java|agent}"; exit 1 ;;
esac