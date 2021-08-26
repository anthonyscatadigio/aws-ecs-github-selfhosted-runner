# Part 2 - Github Runner Image

Image used by the ECS task to act as the github runner.

## Create Runner Image Locally

Simple build of the image:

```bash
docker build -t githubrunner:latest .
```

### Force rebuild

As the image uses `curl` to retrieve the current (latest) runner version at build time you may need to force the rebuild
of the image without cache in order for the new version to be used. This can be achieved by running:

```bash
docker build --no-cache --pull -t githubrunner:latest .
```

## Push Image to ECR

As the ECR repository is created in part 1 you can manually push the image to the repository ECR (where <> match what
were used to create the stack in part 1):

```bash
PART1_STACK_NAME="<>"
REGION="<>"
ACCOUNT_NUMBER="$(aws sts get-caller-identity --query 'Account' --output text)"
ECR_IMAGE="$(aws cloudformation describe-stacks --stack-name "${PART1_STACK_NAME}" --region "${REGION}" --query 'Stacks[*].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' --output text)"
aws ecr get-login-password --region "${REGION}" | docker login --username AWS --password-stdin "${ACCOUNT_NUMBER}.dkr.ecr.${REGION}.amazonaws.com"
docker tag githubrunner:latest "${ECR_IMAGE}"
docker push "${ECR_IMAGE}"
```
