FROM ubuntu:latest

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential cmake git wget curl unzip python3 sudo python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY actions-runner-linux-x64-2.329.0.tar.gz /app/actions-runner.tar.gz
RUN mkdir -p /app && \
    tar -xzf /app/actions-runner.tar.gz -C /app && \
    rm /app/actions-runner.tar.gz

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && \
    useradd -m runner && chown -R runner:runner /app

WORKDIR /app
USER runner
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
