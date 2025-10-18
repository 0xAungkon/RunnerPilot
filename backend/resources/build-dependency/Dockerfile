from ubuntu:20.04
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    unzip \
    python3 \
    sudo \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*