from aws_cdk import (
    # Duration,
    Stack,
    CfnTag,
    aws_ec2 as _ec2,
    # aws_sqs as sqs,
)
from constructs import Construct

class VpcV2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC作成
        vpc = create_vpc(self)

        # インターネットゲートウェイ作成
        internet_gateway = create_internet_gateway(self)

        # インターネットゲートウェイアタッチメント作成
        internet_gateway_attachment = create_internet_gateway_attachment(self, vpc, internet_gateway)

        # サブネット作成
        subnet_dictionary = create_subnets(self, vpc)

        # ElasticIP作成
        elastic_ip = create_elastic_ip(self, internet_gateway_attachment)

        # NATゲートウェイ作成
        nat_gateway = create_nat_gateway(self, subnet_dictionary, elastic_ip)

        # ルートテーブル作成（PRIVATE）
        route_table_private = create_private_route_table(self, vpc, nat_gateway)

        # ルートテーブル作成（PUBLIC）
        route_table_public = create_public_route_table(self, vpc, internet_gateway)

        # サブネット関連付け
        subnet_association_private(self, route_table_private, subnet_dictionary)
        subnet_association_public(self, route_table_public, subnet_dictionary)

########################################################
# VPC作成
########################################################
def create_vpc(self):
    # VPC
    vpc = _ec2.CfnVPC(
        self, 'CfnVPC',
        cidr_block='10.5.5.0/24',
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags=[
            CfnTag(
                key='Name',
                value='DEMO-VPC',
            )
        ]
    )
    return vpc

########################################################
# インターネットゲートウェイ作成
########################################################
def create_internet_gateway(self):
    # インターネットゲートウェイ
    internet_gateway = _ec2.CfnInternetGateway(
        self, 'CfnInternetGateway',
        tags=[
            CfnTag(
                key='Name',
                value='DEMO-IGW',
            )
        ]
    )
    return internet_gateway

########################################################
# インターネットゲートウェイアタッチメント作成
########################################################
def create_internet_gateway_attachment(self, vpc, internet_gateway):
    internet_gateway_attachment = _ec2.CfnVPCGatewayAttachment(
        self, 'CfnVPCGatewayAttachment',
        vpc_id=vpc.ref,
        internet_gateway_id=internet_gateway.ref,
    )
    return internet_gateway_attachment

########################################################
# サブネット作成
########################################################
def create_subnets(self, vpc):
    # PRIVATE
    subnet_private_a = create_subnet(self,
                                     vpc,
                                     'DEMO-PRIVATE-SUBNET-A',
                                     '10.5.5.0/26',
                                     'ap-northeast-1a')
    subnet_private_c = create_subnet(self,
                                     vpc,
                                     'DEMO-PRIVATE-SUBNET-C',
                                     '10.5.5.64/26',
                                     'ap-northeast-1c')
    # PUBLIC
    subnet_public_a = create_subnet(self,
                                    vpc,
                                    'DEMO-PUBLIC-SUBNET-A',
                                    '10.5.5.128/26',
                                    'ap-northeast-1a')
    subnet_public_c = create_subnet(self,
                                    vpc,
                                    'DEMO-PUBLIC-SUBNET-C',
                                    '10.5.5.192/26',
                                    'ap-northeast-1c')

    # DICTIONARY作成
    subnet_dictionary = {}
    subnet_dictionary['DEMO-PRIVATE-SUBNET-A'] = subnet_private_a
    subnet_dictionary['DEMO-PRIVATE-SUBNET-C'] = subnet_private_c
    subnet_dictionary['DEMO-PUBLIC-SUBNET-A'] = subnet_public_a
    subnet_dictionary['DEMO-PUBLIC-SUBNET-C'] = subnet_public_c
    return subnet_dictionary

########################################################
# サブネット作成
########################################################
def create_subnet(self, vpc, subnet_name, cidr_block, availability_zone):
    subnet = _ec2.CfnSubnet(
        self,
        subnet_name,
        vpc_id=vpc.ref,
        cidr_block=cidr_block,
        availability_zone=availability_zone,
        tags=[
            CfnTag(
                key='Name',
                value=subnet_name,
            )
        ]
    )
    return subnet

########################################################
# EIP作成
########################################################
def create_elastic_ip(self, internet_gateway_attachment):

    # EIP1 (for NATGW)
    elastic_ip = _ec2.CfnEIP(
        self, 'CfnEIP',
        domain="vpc",
        tags=[
            CfnTag(
                key='Name',
                value='DEMO-EIP',
            )
        ]
    )
    elastic_ip.add_depends_on(internet_gateway_attachment)
    return elastic_ip

########################################################
# NATゲートウェイ作成
########################################################
def create_nat_gateway(self, subnet_dictionary, elastic_ip):

    # NatGateway
    nat_gateway = _ec2.CfnNatGateway(
        self, 'CfnNatGateway',
        allocation_id=elastic_ip.attr_allocation_id,
        subnet_id=subnet_dictionary.get('DEMO-PUBLIC-SUBNET-A').ref,
        tags=[
            CfnTag(
                key='Name',
                value='DEMO-NAT-GATEWAY',
            )
        ]
    )
    return nat_gateway

########################################################
# ルートテーブル作成（PRIVATE）
########################################################
def create_private_route_table(self, vpc, nat_gateway):

    # RouteTable of PrivateSubnet
    route_table_private = _ec2.CfnRouteTable(
        self, 'CfnRouteTablePrivate',
        vpc_id=vpc.ref,
        tags=[
            CfnTag(key="Name",
                        value='DEMO-ROUTE-TABLE-PRIVATE'),
        ]
    )

    _ec2.CfnRoute(
        self, 'CfnRoutePrivate',
        route_table_id=route_table_private.ref,
        destination_cidr_block="0.0.0.0/0",
        nat_gateway_id=nat_gateway.ref
    )
    return route_table_private

########################################################
# ルートテーブル作成（PUBLIC）
########################################################
def create_public_route_table(self, vpc, internet_gateway):

    # RouteTable of PublicSubnet
    route_table_public = _ec2.CfnRouteTable(
        self, 'CfnRouteTablePublic',
        vpc_id=vpc.ref,
        tags=[
            CfnTag(key="Name",
                        value='DEMO-ROUTE-TABLE-PUBLIC'),
        ]
    )
    _ec2.CfnRoute(
        self, 'CfnRoutePublic',
        route_table_id=route_table_public.ref,
        destination_cidr_block="0.0.0.0/0",
        gateway_id=internet_gateway.ref
    )
    return route_table_public

########################################################
# サブネット関連付け（PRIVATE）
########################################################
def subnet_association_private(self, route_table_private, subnet_dictionary):

    _ec2.CfnSubnetRouteTableAssociation(
        self, 'CfnSubnetRouteTableAssociationPrivateA',
        route_table_id=route_table_private.ref,
        subnet_id=subnet_dictionary.get('DEMO-PRIVATE-SUBNET-A').ref
    )
    _ec2.CfnSubnetRouteTableAssociation(
        self, 'CfnSubnetRouteTableAssociationPrivateC',
        route_table_id=route_table_private.ref,
        subnet_id=subnet_dictionary.get('DEMO-PRIVATE-SUBNET-C').ref
    )

########################################################
# サブネット関連付け（PUBLIC）
########################################################
def subnet_association_public(self, route_table_public, subnet_dictionary):
    _ec2.CfnSubnetRouteTableAssociation(
        self, 'CfnSubnetRouteTableAssociationPublicA',
        route_table_id=route_table_public.ref,
        subnet_id=subnet_dictionary.get('DEMO-PUBLIC-SUBNET-A').ref
    )
    _ec2.CfnSubnetRouteTableAssociation(
        self, 'CfnSubnetRouteTableAssociationPublicC',
        route_table_id=route_table_public.ref,
        subnet_id=subnet_dictionary.get('DEMO-PUBLIC-SUBNET-C').ref
    )
