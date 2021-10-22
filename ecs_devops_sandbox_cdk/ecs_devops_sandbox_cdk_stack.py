from aws_cdk import (core, aws_ecs as ecs, aws_ecr as ecr, aws_ec2 as ec2, aws_iam as iam, aws_logs,aws_ecs_patterns as ecs_patterns)


class EcsDevopsSandboxCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        ecr_repository = ecr.Repository(self,  
                                        "django-app-repository", 
                                         repository_name="django-app-repository")


        vpc = ec2.Vpc(self,  "django-app-vpc",  max_azs=3)

        cluster = ecs.Cluster(self,  
					  "django-app-cluster", 
					  cluster_name="django-app-cluster",
					  vpc=vpc)
        
        execution_role = iam.Role(self,  
                                  "django-app-execution-role", 
                                  assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"), 
                                  role_name="django-app-execution-role")

        execution_role.add_to_policy(iam.PolicyStatement( effect=iam.Effect.ALLOW, 
                                                            resources=["*"], 
                                                            actions=["ecr:*",  
                                                                     "logs:*",  
                                                                     "ecs:*",
                                                                     "cloudwatch:*",  ]  ))
        
        ecs_patterns.ApplicationLoadBalancedFargateService(self, "django-app-lb-service",
            service_name="django-app-service",
            cluster=cluster,            # Required
            cpu=512,                    # Default is 256
            desired_count=2,            # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
                family="django-app-task-definition",
                container_port=80,
                execution_role=execution_role,
                container_name="django_app"),
            memory_limit_mib=2048,      # Default is 512
            public_load_balancer=True)  # Default is False

        log_group = aws_logs.LogGroup(self,
                                      "django-app-service-logs-groups",
                                      log_group_name="django-app-service-logs")