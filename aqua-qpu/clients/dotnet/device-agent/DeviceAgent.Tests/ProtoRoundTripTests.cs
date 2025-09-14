using Aqua.Qpu.V1;
using Google.Protobuf;
using Xunit;

public class ProtoRoundTripTests
{
    [Fact]
    public void DeviceState_RoundTrip()
    {
        var original = new DeviceState { DeviceId = "X", TemperatureK = 3.14, VacuumPa = 1e-7 };
        var bytes = original.ToByteArray();
        var parsed = DeviceState.Parser.ParseFrom(bytes);

        Assert.Equal(original.DeviceId, parsed.DeviceId);
        Assert.Equal(original.TemperatureK, parsed.TemperatureK);
        Assert.Equal(original.VacuumPa, parsed.VacuumPa);
    }
}