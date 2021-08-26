# Part 3 - Fargate

ECS fargate service and task for the github runner. Takes some of the output from the stack created in part 1 and image
created in part 2.

The following are create:

* Task security group
* ECS service
* ECS Task
* IAM Roles for cluster and tasks

## Create Stack

Create the environment using CloudFormation (where <> are your personal preference and match what were used to create
stack 1):

```bash
PART3_STACK_NAME="<>"
PART1_STACK_NAME="<>"
REGION="<>"
ECR_REPOSITORY_URI="$(aws cloudformation describe-stacks --stack-name "${PART1_STACK_NAME}" --region "${REGION}" --query 'Stacks[*].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' --output text)"
aws cloudformation create-stack --template-body file://./part3.yaml --stack-name "${PART3_STACK_NAME}" --region "${REGION}" --parameters ParameterKey=InfrastructureStack,ParameterValue="${PART1_STACK_NAME}" ParameterKey=ContainerImage,ParameterValue="${ECR_REPOSITORY_URI}:latest" --capabilities CAPABILITY_IAM
```

### Create Wait

If you wish to wait until the stack is created:

```bash
aws cloudformation wait stack-create-complete --stack-name "${PART3_STACK_NAME}" --region "${REGION}"
```

## Stack Status

Check on the status and state of the stack:

```bash
aws cloudformation describe-stacks --stack-name "${PART3_STACK_NAME}"
```

## Update Stack

```bash
PART3_STACK_NAME="<>"
PART1_STACK_NAME="<>"
REGION="<>"
ECR_REPOSITORY_URI="$(aws cloudformation describe-stacks --stack-name "${PART1_STACK_NAME}" --region "${REGION}" --query 'Stacks[*].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' --output text)"
aws cloudformation update-stack --template-body file://./part3.yaml --stack-name "${PART3_STACK_NAME}" --region "${REGION}" --parameters ParameterKey=InfrastructureStack,ParameterValue="${PART1_STACK_NAME}" ParameterKey=ContainerImage,ParameterValue="${ECR_REPOSITORY_URI}:latest" --capabilities CAPABILITY_IAM
```

### Update Wait

If you wish to wait until the stack is updated:

```bash
aws cloudformation wait stack-update-complete --stack-name "${PART3_STACK_NAME}" --region "${REGION}"
```

## Command line access

You can access the terminal of the running task.

First find the current running task id:

```bash
PART3_STACK_NAME="<>"
REGION="<>"
CLUSTER_NAME="$(aws cloudformation describe-stacks --stack-name "${PART3_STACK_NAME}" --region "${REGION}" --query 'Stacks[*].Outputs[?OutputKey==`Cluster`].OutputValue' --output text | awk -F '/' '{print $NF}')"
task_id=$(aws ecs list-tasks --cluster "${CLUSTER_NAME}" --desired-status RUNNING --query "taskArns[*]" --output text | awk -F '/' '{print $NF}')
```

Access task terminal:

```bash
aws ecs execute-command --region "${REGION}" --cluster "${CLUSTER_NAME}" --task "${task_id}" --container github-runners --command "/bin/bash" --interactive
```

## Delete Stack

To clean up the stack once you are finished (where <> match what were used to create the stack):

```bash
PART3_STACK_NAME="<>"
REGION="<>"
aws cloudformation delete-stack --stack-name "${PART3_STACK_NAME}" --region "${REGION}"
```

### Delete Wait

If you wish to wait until the stack is deleted:

```bash
aws cloudformation wait stack-delete-complete --stack-name "${PART3_STACK_NAME}" --region "${REGION}"
```
