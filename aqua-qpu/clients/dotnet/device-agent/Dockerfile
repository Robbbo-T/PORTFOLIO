FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
# Bring in agent and proto so Grpc.Tools can see the shared include
COPY clients/dotnet/device-agent/ ./clients/dotnet/device-agent/
COPY proto/ ./proto/
WORKDIR /src/clients/dotnet/device-agent
RUN dotnet publish DeviceAgent/DeviceAgent.csproj -c Release -o /app/out

FROM mcr.microsoft.com/dotnet/runtime:8.0 AS runtime
WORKDIR /app
ENV CONTROLPLANE_ADDR=http://controlplane:9090
COPY --from=build /app/out/ .
ENTRYPOINT ["dotnet","DeviceAgent.dll"]