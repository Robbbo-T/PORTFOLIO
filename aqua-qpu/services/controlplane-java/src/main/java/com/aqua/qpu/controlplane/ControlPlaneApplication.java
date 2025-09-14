package com.aqua.qpu.controlplane;

import io.grpc.Server;
import io.grpc.netty.shaded.io.grpc.netty.NettyServerBuilder;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.concurrent.TimeUnit;

@SpringBootApplication
public class ControlPlaneApplication {

  public static void main(String[] args) throws Exception {
    var ctx = SpringApplication.run(ControlPlaneApplication.class, args);

    var svc = ctx.getBean(com.aqua.qpu.controlplane.grpc.ControlPlaneService.class);

    // gRPC server on port 9090
    Server server = NettyServerBuilder.forPort(9090)
        .addService(svc)
        .maxInboundMessageSize(16 * 1024 * 1024)
        .keepAliveTime(30, TimeUnit.SECONDS)
        .build()
        .start();

    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
      try { server.shutdown().awaitTermination(5, TimeUnit.SECONDS); }
      catch (InterruptedException ignored) {}
    }));

    server.awaitTermination();
  }
}