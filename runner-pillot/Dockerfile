FROM debian:bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        unzip \
        ca-certificates \
        gnupg \
        libicu72 \
        libkrb5-3 \
        libssl3 \
        libcurl4 \
        libunwind8 \
        && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash runner

WORKDIR /home/runner/actions-runner

ENV RUNNER_VERSION=2.327.0 \
    RUNNER_ARCH=linux-x64 \
    RUNNER_FILENAME=actions-runner-linux-x64-2.327.0.tar.gz

RUN curl -O -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_FILENAME} && \
    tar xzf ${RUNNER_FILENAME} && \
    rm ${RUNNER_FILENAME} && \
    chown -R runner:runner /home/runner/actions-runner

USER runner

ENTRYPOINT ["bash", "-c", "./config.sh --url $GITHUB_REPO_URL --token $GITHUB_RUNNER_TOKEN --unattended && ./run.sh"]
