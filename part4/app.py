#!/usr/bin/env python3
import os
from aws_cdk import (core, aws_ecs as ecs, aws_ecr as ecr, aws_ec2 as ec2, aws_iam as iam, aws_logs as logs, aws_elasticloadbalancingv2 as elbv2)
from aws_cdk.core import App, Stack, Environment

app = core.App()
stack = core.Stack(app, app.node.try_get_context("stack_name"),
                    env=core.Environment(
                        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                        region=os.getenv('CDK_DEFAULT_REGION'),
                    ),)

ecr_repository = ecr.Repository(stack,
                                "ecs-github-repository",
                                repository_name="ecs-github",
                                removal_policy=core.RemovalPolicy.DESTROY)

vpc = ec2.Vpc.from_lookup(stack, "VPC",
    vpc_id = stack.node.try_get_context("vpc_id")
)

cluster = ecs.Cluster(stack,
                        "ecs-github-cluster",
                        cluster_name="ecs-github",
                        vpc=vpc)

execution_role = iam.Role(stack,
                            "ecs-github-execution-role",
                            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                            role_name="ecs-github-execution-role")
execution_role.add_to_policy(iam.PolicyStatement(
    effect=iam.Effect.ALLOW,
    resources=["*"],
    actions=[
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        ]
))
task_role = iam.Role(stack,
                            "ecs-github-task-role",
                            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                            role_name="ecs-github-task-role")
task_role.add_to_policy(iam.PolicyStatement(
    effect=iam.Effect.ALLOW,
    resources=["*"],
    actions=[
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        ]
))
logDetail = logs.LogGroup(stack, "ecs-github-log-group", log_group_name="/ecs/github-nginx", retention=logs.RetentionDays.TWO_WEEKS, removal_policy=core.RemovalPolicy.DESTROY)

task_definition = ecs.FargateTaskDefinition(stack,
                                            "ecs-github-task-definition",
                                            execution_role=execution_role,
                                            family="ecs-devops-task-definition")

container = task_definition.add_container(
    "ecs-github-task",
    image=ecs.ContainerImage.from_registry("nginx"),
    logging=ecs.LogDriver.aws_logs(stream_prefix = "ecs", log_group=logDetail),
    linux_parameters=ecs.LinuxParameters(stack, "ecs-github-linux-parameters",  init_process_enabled=True),
    port_mappings=[ecs.PortMapping(container_port=80)]
)

security_group = ec2.SecurityGroup(stack, "ecs-github-security-group", vpc=vpc, description="Security group to allow access to service")
security_group.add_ingress_rule(
    peer=ec2.Peer.any_ipv4(),
    connection=ec2.Port.tcp(443),
    description="allow https traffic",
)
security_group.add_ingress_rule(
    peer=ec2.Peer.any_ipv4(),
    connection=ec2.Port.tcp(80),
    description="allow http traffic",
)

security_group_ecs = ec2.SecurityGroup(stack, "ecs-github-security-group-ecs", vpc=vpc, description="Security group to allow access to service from the ALB")
security_group_ecs.add_ingress_rule(
    peer=security_group,
    connection=ec2.Port.tcp(443),
    description="allow https traffic",
)
security_group_ecs.add_ingress_rule(
    peer=security_group,
    connection=ec2.Port.tcp(80),
    description="allow http traffic",
)

application_load_balancer = elbv2.ApplicationLoadBalancer(stack, "ecs-github-load-balancer",
    vpc=vpc,
    internet_facing=True,
    security_group=security_group
)

service = ecs.FargateService(stack,
                                "ecs-github-service1",
                                assign_public_ip=True,
                                cluster=cluster,
                                task_definition=task_definition,
                                service_name="ecs-github-service",
                                security_groups=[security_group_ecs])

listener = application_load_balancer.add_listener("ecs-github-load-listener", port=80)
listener.add_targets("ecs-github-load-targer", port=80, targets=[service])
listener.connections.allow_default_port_from_any_ipv4("Open to the world")

core.CfnOutput(
    stack, "ECRRepositoryUri",
    description="The Repository URI",
    value=ecr_repository.repository_uri,
 )

core.CfnOutput(
    stack, "LoadBalancerDNS",
    description="DNS fort load balancer",
    value=application_load_balancer.load_balancer_dns_name,
)

app.synth()
