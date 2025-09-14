SHELL := /bin/bash

.PHONY: help proto.lint proto.gen run.java run.agent build.java build.dotnet test.java

help:
	@echo "Targets:"
	@echo "  proto.lint      - buf format/lint/breaking"
	@echo "  proto.gen       - buf generate to ./gen (not committed)"
	@echo "  build.java      - build Spring service"
	@echo "  run.java        - run Spring service (gRPC:9090)"
	@echo "  build.dotnet    - build .NET agent"
	@echo "  run.agent       - run .NET agent (CONTROLPLANE_ADDR env)"
	@echo "  test.java       - run Java tests"

proto.lint:
	buf format -w
	buf lint
	@if git show-ref --verify --quiet refs/heads/main; then buf breaking --against '.git#branch=main'; fi

proto.gen:
	buf generate

build.java:
	(cd services/controlplane-java && ./gradlew --no-daemon clean build)

run.java:
	(cd services/controlplane-java && ./gradlew --no-daemon bootJar && java -jar build/libs/controlplane-java-*.jar)

build.dotnet:
	dotnet build clients/dotnet/device-agent/DeviceAgent.sln -c Release

run.agent:
	CONTROLPLANE_ADDR?=http://localhost:9090
	CONTROLPLANE_ADDR=$(CONTROLPLANE_ADDR) dotnet run --project clients/dotnet/device-agent/DeviceAgent/DeviceAgent.csproj

test.java:
	(cd services/controlplane-java && ./gradlew --no-daemon test)