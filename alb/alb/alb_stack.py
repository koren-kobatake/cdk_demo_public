from aws_cdk import (
    aws_ec2 as _ec2,
    aws_elasticloadbalancingv2 as _elbv2,
    core,
)
import pandas as pd


class AlbStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC取得
        vpc = get_vpc(self)

        # セキュリティグループ作成
        security_group_alb = create_security_group(self, vpc)

        # ALB
        create_alb(self, vpc, security_group_alb)

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

    # ALB
    security_group_alb = _ec2.SecurityGroup(
        self, 'DEMO-ALB-SG',
        vpc=vpc,
        description='DEMO-ALB-SG',
        security_group_name='DEMO-ALB-SG',
    )
    add_inbound(self, './security_group/inbound_rules/alb.csv', security_group_alb)

    return security_group_alb

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
                description = description,
                connection = _ec2.Port.tcp(port),
            )
        elif type == 'prefix':
            security_group.add_ingress_rule(
                peer = _ec2.Peer.prefix_list(peer),
                description = description,
                connection = _ec2.Port.tcp(port),
            )
        else:
            security_group.add_ingress_rule(
                peer = _ec2.Peer.ipv4(peer),
                description = description,
                connection = _ec2.Port.tcp(port),
            )

########################################################
# ターゲットグループ作成
########################################################
def create_target_group(self, vpc, tg_name):
    tg = _elbv2.ApplicationTargetGroup(
        self, tg_name,
        port=80,
        target_type=_elbv2.TargetType.IP,
        target_group_name=tg_name,
        vpc=vpc,
        health_check=_elbv2.HealthCheck(path='/login'),
    )
    tg.enable_cookie_stickiness(core.Duration.seconds(1800))
    return tg

########################################################
# ALB作成
########################################################
def create_alb(self, vpc, security_group_alb):

    # ALB作成
    alb = _elbv2.ApplicationLoadBalancer(
        self, 'Alb',
        vpc=vpc,
        load_balancer_name='DEMO-ALB',
        security_group=security_group_alb,
        vpc_subnets=_ec2.SubnetSelection(subnet_type=_ec2.SubnetType.PUBLIC),
        internet_facing=True,
    )

    # ターゲットグループ作成
    tg_blue = create_target_group(self, vpc, 'DEMO-BLUE-TG')
    tg_green = create_target_group(self, vpc, 'DEMO-GREEN-TG')

    # リスナー追加
    # ＜Product＞
    listenerProduct = alb.add_listener(
        'AlbAddListnerProduct',
        port=80
    )
    listenerProduct.add_target_groups(
        'AlbAddTgProduct',
        target_groups=[tg_blue]
    )
    # ＜Test＞
    listenerTest = alb.add_listener(
        'AlbAddListnerTest',
        port=8080
    )
    listenerTest.add_target_groups(
        'AlbAddTgTest',
        target_groups=[tg_green]
    )
