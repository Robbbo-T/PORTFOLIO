package com.aqua.qpu.controlplane.grpc;

import aqua.qpu.v1.ControlPlaneGrpc;
import aqua.qpu.v1.ControlPlaneOuterClass;
import aqua.qpu.v1.ControlPlaneOuterClass.BiasCommand;
import com.google.protobuf.Empty;
import com.google.protobuf.Timestamp;
import io.grpc.stub.StreamObserver;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Service
public class ControlPlaneService extends ControlPlaneGrpc.ControlPlaneImplBase {

  @Override
  public void getState(Empty request, StreamObserver<ControlPlaneOuterClass.DeviceState> responseObserver) {
    var now = Instant.now();
    var ts = Timestamp.newBuilder().setSeconds(now.getEpochSecond()).setNanos(now.getNano()).build();
    var state = ControlPlaneOuterClass.DeviceState.newBuilder()
        .setDeviceId("BLG-DW-001")
        .setTemperatureK(4.20)
        .setMagneticFieldT(0.00)
        .setVacuumPa(1.0e-7)
        .putAnalog("bias_ch1_V", 0.0)
        .putStatus("mode", "IDLE")
        .setTime(ts)
        .build();
    responseObserver.onNext(state);
    responseObserver.onCompleted();
  }

  @Override
  public StreamObserver<BiasCommand> applyBias(StreamObserver<Empty> responseObserver) {
    return new StreamObserver<>() {
      @Override public void onNext(BiasCommand cmd) {
        // TODO: route to hardware bridge (Kafka, device agent RPC, etc.)
        System.out.printf("ApplyBias: %s -> %.3f V (slew=%.3f V/s)%n",
            cmd.getChannel(), cmd.getVolts(), cmd.getSlewVPerS());
      }
      @Override public void onError(Throwable t) { /* log */ }
      @Override public void onCompleted() { responseObserver.onNext(Empty.getDefaultInstance()); responseObserver.onCompleted(); }
    };
  }
}