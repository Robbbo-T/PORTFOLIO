package com.aqua.qpu.controlplane.grpc;

import com.aqua.qpu.v1.ControlPlaneGrpc;
import com.aqua.qpu.v1.BiasCommand;
import com.google.protobuf.Empty;
import io.grpc.inprocess.InProcessChannelBuilder;
import io.grpc.inprocess.InProcessServerBuilder;
import io.grpc.stub.StreamObserver;
import org.junit.jupiter.api.Test;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

class ControlPlaneServiceTest {

  @Test
  void getState_returnsDeviceState() throws Exception {
    var name = InProcessServerBuilder.generateName();
    var server = InProcessServerBuilder.forName(name).directExecutor()
        .addService(new ControlPlaneService())
        .build().start();
    try {
      var channel = InProcessChannelBuilder.forName(name).directExecutor().build();
      var blocking = ControlPlaneGrpc.newBlockingStub(channel);
      var state = blocking.getState(Empty.getDefaultInstance());
      assertEquals("BLG-DW-001", state.getDeviceId());
      assertTrue(state.getTemperatureK() > 0.0);
    } finally {
      server.shutdownNow().awaitTermination(5, TimeUnit.SECONDS);
    }
  }

  @Test
  void applyBias_streamCompletes() throws Exception {
    var name = InProcessServerBuilder.generateName();
    var server = InProcessServerBuilder.forName(name).directExecutor()
        .addService(new ControlPlaneService())
        .build().start();
    try {
      var channel = InProcessChannelBuilder.forName(name).directExecutor().build();
      var async = ControlPlaneGrpc.newStub(channel);
      var latch = new CountDownLatch(1);
      StreamObserver<Empty> respObs = new StreamObserver<>() {
        @Override public void onNext(Empty value) {}
        @Override public void onError(Throwable t) { fail(t); }
        @Override public void onCompleted() { latch.countDown(); }
      };
      var req = async.applyBias(respObs);
      req.onNext(BiasCommand.newBuilder().setChannel("ch1").setVolts(0.1).setSlewVPerS(0.5).build());
      req.onNext(BiasCommand.newBuilder().setChannel("ch2").setVolts(-0.05).setSlewVPerS(0.5).build());
      req.onCompleted();
      assertTrue(latch.await(2, TimeUnit.SECONDS));
    } finally {
      server.shutdownNow().awaitTermination(5, TimeUnit.SECONDS);
    }
  }
}