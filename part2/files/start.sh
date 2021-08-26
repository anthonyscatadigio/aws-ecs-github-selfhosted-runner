#!/bin/bash
set -e

REGISTRATION_URL="https://api.github.com/repos/${GITHUB_USER}/${GITHUB_REPOSITORY}/actions/runners/registration-token"

deregister_runner() {
  echo "Caught SIGTERM. Deregistering runner"
  /actions-runner/config.sh remove --unattended --token "${token}"
  exit
}

trap deregister_runner SIGINT SIGQUIT SIGTERM EXIT HUP INT TERM

export token=$(curl -s -XPOST \
    -H "authorization: token ${PAT}" \
    "${REGISTRATION_URL}" |\
    jq -r .token)

/actions-runner/config.sh --url "https://github.com/${GITHUB_USER}/${GITHUB_REPOSITORY}" --unattended --token "${token}" --name "aws-runner-$(hostname)" --work _work
/actions-runner/run.sh
