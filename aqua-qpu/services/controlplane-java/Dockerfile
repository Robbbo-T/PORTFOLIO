# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jdk AS build
WORKDIR /workspace
# Bring in service and proto so Gradle can compile from ../../proto
COPY services/controlplane-java/ ./services/controlplane-java/
COPY proto/ ./proto/
WORKDIR /workspace/services/controlplane-java
RUN ./gradlew --no-daemon clean bootJar

FROM eclipse-temurin:21-jre AS runtime
WORKDIR /app
ENV JAVA_OPTS=""
COPY --from=build /workspace/services/controlplane-java/build/libs/controlplane-java-*.jar /app/app.jar
EXPOSE 9090
ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar /app/app.jar"]