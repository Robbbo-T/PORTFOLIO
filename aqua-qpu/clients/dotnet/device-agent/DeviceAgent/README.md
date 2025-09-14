# DeviceAgent (.NET)

- Builds stubs at compile time via `Grpc.Tools`.
- Points to ControlPlane at `CONTROLPLANE_ADDR` (default `http://localhost:9090`).
- Run:
  ```bash
  dotnet run --project DeviceAgent/DeviceAgent.csproj
  ```

* Native AOT publish (optional):

  ```bash
  dotnet publish -c Release -r win-x64 -p:PublishAot=true --self-contained true
  ```