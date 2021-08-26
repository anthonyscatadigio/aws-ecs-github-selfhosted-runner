# Part 1 - Base Infrastructure

Base infrastructure for the github ecs cluster using fargate. The infrastructure is self contained and assumes nothing
has already been created.

The following resources are created:

* VPC
* Internet Gateway
* Nat Gateway
* Subnets
  * 2x Public
* Route tables
* ECR repository
* ECS Cluster

## Create Stack

Create the environment using CloudFormation (where <> are your personal preference and substitute these values):

```bash
PART1_STACK_NAME="<>"
REGION="<>"
GITHUB_USER="<>"
GITHUB_REPOSITORY="<>"
aws cloudformation create-stack --template-body file://./part1.yaml --stack-name "${PART1_STACK_NAME}" --region "${REGION}" --parameters ParameterKey=GitHubUser,ParameterValue="${GITHUB_USER}" ParameterKey=GitHubRepository,ParameterValue="${GITHUB_REPOSITORY}" --capabilities CAPABILITY_IAM
```

### Create Wait

If you wish to wait until the stack is created:

```bash
aws cloudformation wait stack-create-complete --stack-name "${PART1_STACK_NAME}" --region "${REGION}"
```

## Stack Status

Check on the status and state of the stack:

```bash
aws cloudformation describe-stacks --stack-name "${PART1_STACK_NAME}"
```

### Update Stack

In the event the stack needs to be updated execute (where <> match what were used to create the stack):

```bash
PART1_STACK_NAME="<>"
REGION="<>"
GITHUB_USER="<>"
GITHUB_REPOSITORY="<>"
aws cloudformation update-stack --template-body file://./part1.yaml --stack-name "${PART1_STACK_NAME}" --region "${REGION}" --parameters ParameterKey=GitHubUser,ParameterValue="${GITHUB_USER}" ParameterKey=GitHubRepository,ParameterValue="${GITHUB_REPOSITORY}" --capabilities CAPABILITY_IAM
```

### Update Wait

If you wish to wait until the stack is updated:

```bash
aws cloudformation wait stack-update-complete --stack-name "${PART1_STACK_NAME}" --region "${REGION}"
```

## Github parameters

To prevent the task or image from containing sensitive information the GitHub token secret used to connect the runner
is stored in an SSM parameter. Unfortunately cloudformation does not support the creation of SSM secrets so this needs
to be performed via the command line. Generate the required access token in your github account at
[tokens](https://github.com/settings/tokens) with the permissions:

* repo
* admin:repo_hook

```bash
GUTHUB_TOKEN="<>"
PART1_STACK_NAME="<>"
REGION="<>"
aws ssm put-parameter --name "/${PART1_STACK_NAME}/github_runners_pat" --value "${GUTHUB_TOKEN}" --region "${REGION}" --type SecureString
```

### Delete Stack

In order to delete the stack, first the ECR images need to be deleted (where <> match what were used to create the
stack):

```bash
PART1_STACK_NAME="<>"
REGION="<>"
ECR_REPOSITORY_NAME="$(aws cloudformation describe-stacks --stack-name "${PART1_STACK_NAME}" --region "${REGION}" --query 'Stacks[*].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' --output text | awk -F '/' '{print $NF}')"
IMAGES_TO_DELETE=$(aws ecr list-images --repository-name "${ECR_REPOSITORY_NAME}" --region "${REGION}"  --query 'imageIds[*]' --output json)
aws ecr batch-delete-image --region "${REGION}" --repository-name "${ECR_REPOSITORY_NAME}" --image-ids "${IMAGES_TO_DELETE}"
```

To clean up the stack once you are finished (where <> match what were used to create the stack):

```bash
PART1_STACK_NAME="<>"
REGION="<>"
aws cloudformation delete-stack --stack-name "${PART1_STACK_NAME}" --region "${REGION}"
```

Delete the manually created SSM GitHub token

```bash
GUTHUB_TOKEN="<>"
PART1_STACK_NAME="<>"
REGION="<>"
aws ssm delete-parameter --name "/${PART1_STACK_NAME}/github_runners_pat" --region "${REGION}"
```

### Delete Wait

If you wish to wait until the stack is deleted:

```bash
aws cloudformation wait stack-delete-complete --stack-name "${PART1_STACK_NAME}" --region "${REGION}"
```
