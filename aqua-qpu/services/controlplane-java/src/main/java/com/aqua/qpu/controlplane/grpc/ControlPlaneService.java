package com.aqua.qpu.controlplane.grpc;

import com.aqua.qpu.v1.ControlPlaneGrpc;
import com.aqua.qpu.v1.BiasCommand;
import com.aqua.qpu.v1.DeviceState;
import com.google.protobuf.Empty;
import com.google.protobuf.Timestamp;
import io.grpc.stub.StreamObserver;
import org.springframework.stereotype.Service;

import java.time.Instant;

// OpenTelemetry (no-op unless configured with SDK/agent)
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

@Service
public class ControlPlaneService extends ControlPlaneGrpc.ControlPlaneImplBase {

  private static final Tracer TRACER =
      GlobalOpenTelemetry.getTracer("com.aqua.qpu.controlplane", "0.1.0");

  @Override
  public void getState(Empty request, StreamObserver<DeviceState> responseObserver) {
    Span span = TRACER.spanBuilder("GetState").startSpan();
    try (Scope ignore = span.makeCurrent()) {
      var now = Instant.now();
      var ts = Timestamp.newBuilder().setSeconds(now.getEpochSecond()).setNanos(now.getNano()).build();
      var state = DeviceState.newBuilder()
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
    } finally {
      span.end();
    }
  }

  @Override
  public StreamObserver<BiasCommand> applyBias(StreamObserver<Empty> responseObserver) {
    return new StreamObserver<>() {
      @Override public void onNext(BiasCommand cmd) {
        Span span = TRACER.spanBuilder("ApplyBias").startSpan();
        try (Scope ignore = span.makeCurrent()) {
          span.setAttribute("channel", cmd.getChannel());
          span.setAttribute("volts", cmd.getVolts());
          span.setAttribute("slew_v_per_s", cmd.getSlewVPerS());
          // TODO: route to hardware bridge (Kafka, device agent RPC, etc.)
          System.out.printf("ApplyBias: %s -> %.3f V (slew=%.3f V/s)%n",
              cmd.getChannel(), cmd.getVolts(), cmd.getSlewVPerS());
        } finally {
          span.end();
        }
      }
      @Override public void onError(Throwable t) { /* log */ }
      @Override public void onCompleted() { responseObserver.onNext(Empty.getDefaultInstance()); responseObserver.onCompleted(); }
    };
  }
}