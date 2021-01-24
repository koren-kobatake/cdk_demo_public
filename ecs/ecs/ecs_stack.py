import pandas as pd
from aws_cdk import (
    aws_ec2 as _ec2,
    aws_ecr as _ecr,
    aws_ecs as _ecs,
    aws_iam as _iam,
    aws_logs as _logs,
    core,
)

class EcsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.operation()

    ########################################################
    # CDK処理
    ########################################################
    def operation(self):

        # ECR
        repository = create_repository(self)

        # VPC取得
        vpc = get_vpc(self)

        # セキュリティグループ作成
        sg_dictionary = create_security_group(self, vpc)

        # ECS
        create_ecs(self, vpc, sg_dictionary, repository)

########################################################
# リポジトリ作成
########################################################
def create_repository(self):
    repository = _ecr.Repository(
        self, 'Repository',
        repository_name='demo-repository'
    )
    return repository

########################################################
# VPC取得
########################################################
def get_vpc(self):
    vpc = _ec2.Vpc.from_lookup(
        self, 'VpcFromLookup',
        vpc_name='DEMO-VPC'
    )
    return vpc

########################################################
# セキュリティグループ作成
########################################################
def create_security_group(self, vpc):

    # SERVICE
    sg_service = _ec2.SecurityGroup(
        self, 'DEMO-SERVICE-SG',
        vpc=vpc,
        description='DEMO-SERVICE-SG',
        security_group_name='DEMO-SERVICE-SG',
    )
    add_inbound(self, './security_group/inbound_rules/service.csv', sg_service)

    # Dictionary作成
    sg_dictionary = {}
    sg_dictionary['DEMO-SERVICE-SG']=sg_service

    return sg_dictionary

########################################################
# インバウンド設定追加（セキュリティグループ）
########################################################
def add_inbound(self, path, security_group):
    csv_input = pd.read_csv(filepath_or_buffer=path, encoding='utf_8', sep=',')
    for index, row in csv_input.iterrows():
        type =row[0]
        peer = row[1]
        description = row[2]
        port = row[3]
        if type == 'any_ipv4':
            security_group.add_ingress_rule(
                peer = _ec2.Peer.any_ipv4(),
                description  = description,
                connection = _ec2.Port.tcp(port),
            )
        elif type == 'prefix':
            security_group.add_ingress_rule(
                peer = _ec2.Peer.prefix_list(peer),
                description  = description,
                connection = _ec2.Port.tcp(port),
            )
        else:
            security_group.add_ingress_rule(
                peer = _ec2.Peer.ipv4(peer),
                description  = description,
                connection = _ec2.Port.tcp(port),
            )

########################################################
# ECS作成
########################################################
def create_ecs(self, vpc, sg_dictionary, repository):

    # Cluster
    cluster = _ecs.Cluster(
        self, 'Cluster',
        cluster_name='DEMO-CLUSTER',
        vpc=vpc
    )

    # Role(task execution)
    execution_role = _iam.Role(
        self, 'ExecutionRole',
        role_name='DEMO-TASK-EXECUTION-ROLE',
        assumed_by=_iam.ServicePrincipal('ecs-tasks.amazonaws.com')
    )
    execution_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonECSTaskExecutionRolePolicy'))

    # TaskDefinition
    task_def = _ecs.TaskDefinition(
        self, 'TaskDefinition',
        compatibility=_ecs.Compatibility.FARGATE,
        cpu='2048',
        memory_mib='8192',
        network_mode=_ecs.NetworkMode.AWS_VPC,
        execution_role=execution_role,
        family='DEMO-TASK',
        task_role=execution_role,
    )

    # Container
    container = task_def.add_container(
        id='DEMO-CONTAINER',
        image=_ecs.ContainerImage.from_ecr_repository(repository),
        logging=_ecs.LogDriver.aws_logs(
            stream_prefix='ecs',
            log_group=_logs.LogGroup(
                self, 'LogGroup',
                log_group_name='/ecs/'+'DEMO-TASK',
                retention=_logs.RetentionDays.INFINITE,
            )
        )
    )
    container.add_port_mappings(_ecs.PortMapping(container_port=8080))
