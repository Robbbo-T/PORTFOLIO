param([Parameter(Mandatory=$true)][ValidateSet("proto-lint","proto-gen","java","agent")]$cmd)

switch ($cmd) {
  "proto-lint" { buf format -w; buf lint; buf breaking --against ".git#branch=main" }
  "proto-gen"  { buf generate }
  "java"       { pushd services\controlplane-java; ./gradlew.bat --no-daemon clean build; popd }
  "agent"      { $env:CONTROLPLANE_ADDR = $env:CONTROLPLANE_ADDR ?? "http://localhost:9090";
                 dotnet run --project clients\dotnet\device-agent\DeviceAgent\DeviceAgent.csproj }
}