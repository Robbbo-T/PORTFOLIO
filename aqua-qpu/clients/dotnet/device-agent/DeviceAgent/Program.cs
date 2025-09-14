using System.Net.Http;
using Aqua.Qpu.V1;
using Google.Protobuf.WellKnownTypes;
using Grpc.Net.Client;

var addr = Environment.GetEnvironmentVariable("CONTROLPLANE_ADDR") ?? "http://localhost:9090";
var httpHandler = new SocketsHttpHandler { PooledConnectionIdleTimeout = TimeSpan.FromMinutes(2) };
using var channel = GrpcChannel.ForAddress(addr, new GrpcChannelOptions { HttpHandler = httpHandler });
var client = new ControlPlane.ControlPlaneClient(channel);

// Poll state
var state = await client.GetStateAsync(new Empty());
Console.WriteLine($"Device {state.DeviceId} T={state.TemperatureK:F2}K P={state.VacuumPa:E2}Pa");

// Send a couple of bias commands (client streaming)
using var call = client.ApplyBias();
await call.RequestStream.WriteAsync(new BiasCommand { Channel = "ch1", Volts = 0.10, SlewVPerS = 0.5 });
await call.RequestStream.WriteAsync(new BiasCommand { Channel = "ch2", Volts = -0.05, SlewVPerS = 0.5 });
await call.RequestStream.CompleteAsync();
await call.ResponseAsync;

Console.WriteLine("Bias commands sent.");