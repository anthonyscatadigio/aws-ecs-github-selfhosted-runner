FROM gcr.io/kaniko-project/executor AS kaniko

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV RUNNER_ALLOW_RUNASROOT=true
RUN echo "APT::Get::Assume-Yes \"true\";" > /etc/apt/apt.conf.d/90assumeyes

# Install and Setup kaniko
COPY --from=kaniko /kaniko/executor /kaniko/docker-credential-gcr /kaniko/docker-credential-ecr-login /kaniko/docker-credential-acr /kaniko/
COPY --from=kaniko /kaniko/ssl/certs/ /kaniko/ssl/certs/
COPY --from=kaniko /kaniko/.docker /kaniko/.docker
COPY --from=kaniko /etc/nsswitch.conf /etc/nsswitch.conf
ENV HOME=/root \
    USER=root \
    PATH=${PATH}:/kaniko \
    SSL_CERT_DIR=/kaniko/ssl/certs \
    DOCKER_CONFIG=/kaniko/.docker/ \
    DOCKER_CREDENTIAL_GCR_CONFIG=/kaniko/.config/gcloud/docker_credential_gcr_config.json
RUN docker-credential-gcr config --token-source=env && \
    echo '{ "credsStore": "ecr-login" }' > /kaniko/.docker/config.json

# Install base OS dependencies
RUN apt-get update && \
    apt-get upgrade && \
    apt-get install --no-install-recommends \
      ca-certificates \
      curl \
      jq \
      git \
      iputils-ping \
      libcurl4 \
      libunwind8 \
      netcat && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Install github runner
RUN GH_RUNNER_VERSION=${GH_RUNNER_VERSION:-$(curl --silent "https://api.github.com/repos/actions/runner/releases/latest" | grep tag_name | sed -E 's/.*"v([^"]+)".*/\1/')} && \
    mkdir /actions-runner && cd /actions-runner && \
    curl -sLS "https://github.com/actions/runner/releases/download/v${GH_RUNNER_VERSION}/actions-runner-linux-x64-${GH_RUNNER_VERSION}.tar.gz" | tar -xz && \
    /actions-runner/bin/installdependencies.sh && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
COPY ./files/start.sh /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
CMD ["/actions-runner/bin/runsvc.sh"]
