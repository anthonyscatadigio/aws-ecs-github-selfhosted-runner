# Self hosted GitHub Runner on AWS ECS

Deployment of ECS cluster for running the GitHub runner and deploying a task into ECS.

This has only been tested on personal github accounts.

The repository is broken down into 5 parts, each with a distinct purpose. The breakdown is due to dependencies of
different resources.

Each folder contains a README.md file wth the relevant instructions for that part.

## Local Requirements

The following tools are required:

* aws cli (preferably v2)
* docker (or any other compatible container build tool)
* aws account
* github account and ability to generate personal tokens

## Part 1 - Base Infrastructure

Base VPC and ECS cluster [Part 1](./part1)

## Part 2

GitHub runner image to be pushed into ECR [Part 2](./part2)

## Part 3

Fargate Service for hosting the GitHub runner [Part 3](./part3)

## Part 4 (Optional)

Secondary cluster for deployment from GitHub  [Part 4](./part4)

## Part 5

Sample container for deployment via GitHub  [Part 5](./part5)

## Cleanup

The cleanup should be executed in the reverse order following due to dependencies between them. The readme contains
instructions on how to perform the cleanup steps. The order is:

* Part 4 (Optional)
* Part 3
* Part 1
