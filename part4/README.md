# Part 4 - Secondary Deployment Cluster (Optional)

A second cluster for deploying a container. This is an optional step as the original github runner cluster can be used
rather than defining and entirely new cluster.

A generic nginx image is used initially for the stack to deploy successfully.

The following are create:

* ECS Cluster
* ECS Service
* ECS Task
* IAM Roles for cluster and tasks
* ECR Repository
* APplication load balancer for serving traffic
* Log group

## CDK Environment

If you do not have CDK locally, you can use a container by running:

```bash
docker run -it --rm --volume "${PWD}":/pwd --workdir=/pwd --volume "${HOME}/.aws":/root/.aws --entrypoint=/bin/bash ghcr.io/theidledeveloper/cdk-docker:latest
```

## Setup CDK Environment

### Create Virtual Environment

You should only need to run this step once as the virtual environment will be stored within this subfolder for later
use:

```bash
python3 -m venv .venv
```

### Activate Virtual Environment

Provide your shell access to the virtual environment binaries:

```bash
source .venv/bin/activate
```

### Install CDK Python general dependencies

```bash
pip install -r requirements.txt
```

## CDK Inside Alpine container

If you are running CDK from inside a Alpine linux container and using SSO (for authentication) you will need to install
some additional tools to allow CDK and aws cli v2 to work:

```bash
apk --no-cache --update add curl unzip binutils
GLIBC_VER=$(curl -s https://api.github.com/repos/sgerrand/alpine-pkg-glibc/releases/latest | grep tag_name | cut -d : -f 2,3 | tr -d \",' ')
curl -sL https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub -o /etc/apk/keys/sgerrand.rsa.pub
curl -sLO https://github.com/sgerrand/alpine-pkg-glibc/releases/download/${GLIBC_VER}/glibc-${GLIBC_VER}.apk
curl -sLO https://github.com/sgerrand/alpine-pkg-glibc/releases/download/${GLIBC_VER}/glibc-bin-${GLIBC_VER}.apk
apk add --no-cache --update glibc-${GLIBC_VER}.apk glibc-bin-${GLIBC_VER}.apk
curl -SsL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
unzip /tmp/awscliv2.zip -d /tmp
rm -f /tmp/awscliv2.zip
/tmp/aws/install
rm -rf /tmp/aws/
rm -f /usr/local/aws-cli/v2/*/dist/aws_completer \
      /usr/local/aws-cli/v2/*/dist/awscli/data/ac.index \
      /usr/local/aws-cli/v2/*/dist/awscli/examples
apk --no-cache del binutils
rm -f glibc-${GLIBC_VER}.apk rm glibc-bin-${GLIBC_VER}.apk
```

Install [yawsso](https://github.com/victorskl/yawsso) to generate the credentials for CDK to use:

```bash
pip install yawsso
```

Generate credentials for your profile (where <> are your personal preference and substitute these values):

```bash
yawsso -p "<>"
```

## Obtain VPC ID for CDK

CDK will need to know the ID of the existing VPC (where <> are your personal preference and match what were used to
create stack 1):

```bash
PART1_STACK_NAME="<>"
PART4_STACK_NAME"<>"
REGION="<>"
PROFILE="<>"
VPC_ID="$(aws cloudformation describe-stacks --stack-name "${PART1_STACK_NAME}" --region "${REGION}" --query 'Stacks[*].Outputs[?OutputKey==`VpcId`].OutputValue' --output text --profile "${PROFILE}")"
```

## Generate (synth) configuration

Synth the CDK configuration:

```bash
cdk synth --quiet -c stack_name="${PART4_STACK_NAME}" -c vpc_id="${VPC_ID}" --profile "${PROFILE}"
```

## Deploy

Deploy the CDK application:

```bash
cdk deploy -c stack_name="${PART4_STACK_NAME}" -c vpc_id="${VPC_ID}" --profile "${PROFILE}"
```

### Access front end

To access the front end of the deployed service, obtain the DNS of the load balancer and access the URL:

```bash
PART4_STACK_NAME"<>"
SERVICE_DNS="$(aws cloudformation describe-stacks --stack-name "${PART4_STACK_NAME}" --region "${REGION}" --query 'Stacks[*].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' --output text)"
curl ${SERVICE_DNS}
```

## Delete Stack

In order to delete the stack, first the ECR images need to be deleted (where <> match what were used to create the
stack):

```bash
PART4_STACK_NAME"<>"
REGION="<>"
ECR_REPOSITORY_NAME="$(aws cloudformation describe-stacks --stack-name "${PART4_STACK_NAME}" --region "${REGION}" --query 'Stacks[*].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' --output text | awk -F '/' '{print $NF}')"
IMAGES_TO_DELETE=$(aws ecr list-images --repository-name "${ECR_REPOSITORY_NAME}" --region "${REGION}"  --query 'imageIds[*]' --output json)
aws ecr batch-delete-image --region "${REGION}" --repository-name "${ECR_REPOSITORY_NAME}" --image-ids "${IMAGES_TO_DELETE}"
```

Deploy the CDK application:

```bash
cdk destroy --profile "${PROFILE}"
```
