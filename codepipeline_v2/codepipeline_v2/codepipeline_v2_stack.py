import os
from aws_cdk import (
    RemovalPolicy,
    SecretValue,
    Stack,
    aws_iam as _iam,
    aws_ec2 as _ec2,
    aws_codedeploy as _cd,
    aws_ecs as _ecs,
    aws_codebuild as _cb,
    aws_codepipeline as _cp,
    aws_codepipeline_actions as _cpa,
    aws_s3 as _s3,
)
from constructs import Construct

class CodepipelineV2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.operation()

    ########################################################
    # CDK処理
    ########################################################
    def operation(self):

        # バケット
        source_bucket = create_source_bucket(self)
        artifact_bucket = create_artifact_bucket(self)

        # ロール
        role = create_role(self)

        # CodeBuild
        build_project = create_build_project(self, role, source_bucket)

        # CodePipeLine
        create_codepipeline(self, build_project, source_bucket, artifact_bucket)

########################################################
# バケット作成(Source用)
########################################################
def create_source_bucket(self):
    # S3
    _s3.Bucket(self, 'SourceBucket',
               bucket_name = 'demo-codepipeline-source-bucket',
               block_public_access =
               _s3.BlockPublicAccess(
                   block_public_acls=False,
                   block_public_policy=False,
                   ignore_public_acls=False,
                   restrict_public_buckets=False
               ),
               versioned = True,
               removal_policy = RemovalPolicy.DESTROY
               )

    source_bucket=_s3.Bucket.from_bucket_name(
        self, 'SourceBucketName',
        'demo-codepipeline-source-bucket'
    )
    return source_bucket

########################################################
# バケット作成(Artifact用)
########################################################
def create_artifact_bucket(self):
    # S3
    _s3.Bucket(self, 'ArtifactBucket',
       bucket_name = 'demo-codepipeline-artifact-bucket',
       block_public_access =
           _s3.BlockPublicAccess(
               block_public_acls=False,
               block_public_policy=False,
               ignore_public_acls=False,
               restrict_public_buckets=False
           ),
       versioned = False,
       removal_policy = RemovalPolicy.DESTROY
   )

    artifact_bucket=_s3.Bucket.from_bucket_name(
        self, 'ArtifactBucketName',
        'demo-codepipeline-artifact-bucket'
    )
    return artifact_bucket

########################################################
# ロール作成
########################################################
def create_role(self):

    role = _iam.Role(
        self, 'CodeBuildRole',
        role_name='DEMO-CODE-BUILD-ROLE',
        assumed_by=_iam.ServicePrincipal('codebuild.amazonaws.com')
    )
    role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('AWSCodeBuildAdminAccess'))
    role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
    role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryFullAccess'))

    return role

########################################################
# Buildプロジェクト作成
########################################################
def create_build_project(self, role, source_bucket):
    build_project = _cb.Project(
        self, 'CodeBuildProject',
        project_name='DEMO-BUILD',
        source=_cb.Source.s3(
            bucket=source_bucket,
            path='archive.zip'
        ),
        environment=_cb.BuildEnvironment(
            build_image=_cb.LinuxBuildImage.STANDARD_3_0,
            privileged=True
        ),
        environment_variables={
            'IMAGE_REPO_NAME': _cb.BuildEnvironmentVariable(value='demo-repository'),
            'AWS_DEFAULT_REGION': _cb.BuildEnvironmentVariable(value=os.environ.get('REGION')),
            'AWS_ACCOUNT_ID': _cb.BuildEnvironmentVariable(value=os.environ.get('ACCOUNT_ID')),
            'CONTAINER_NAME': _cb.BuildEnvironmentVariable(value='DEMO-CONTAINER'),
        },
        build_spec=_cb.BuildSpec.from_source_filename(filename='etc/cicd/buildspec.yml'),
        artifacts=_cb.Artifacts.s3(
            bucket=source_bucket,
            name='artifact-codebuild.zip',
            package_zip=True,
            include_build_id=False
        ),
        role=role
    )
    return build_project

########################################################
# SourceStage作成
########################################################
def create_source_stage(self, source_output, from_bucket):
    source_stage=_cp.StageProps(
        stage_name='Source',
        actions=[
            _cpa.GitHubSourceAction(
                action_name='source_from_github',
                owner='koren-kobatake',
                repo='aws-study',
                branch='master',
                trigger=_cpa.GitHubTrigger.POLL,
                oauth_token=SecretValue.plain_text('21063a42a37fa2b93804b3ed776a9f4fbe450f2f'),
                output=source_output
            )
        ]
    )
    return source_stage

########################################################
# BuildStage作成
########################################################
def create_build_stage(self, source_output, build_project):
    build_stage=_cp.StageProps(
        stage_name='Build',
        actions=[
            _cpa.CodeBuildAction(
                action_name='Build',
                input=source_output,
                project=build_project,
                run_order=1,
                environment_variables={
                  'ENV': _cb.BuildEnvironmentVariable(value='develop'),
                  'FAMILY_NAME': _cb.BuildEnvironmentVariable(value='DEMO-TASK'),
                },
                outputs=[_cp.Artifact(artifact_name='BuildArtifact')],
            )
        ]
    )
    return build_stage

########################################################
# ApprovalStage作成
########################################################
def create_approval_stage(self):
    approval_stage=_cp.StageProps(
        stage_name='Approval',
        actions=[
            _cpa.ManualApprovalAction(
                action_name='Approval',
                run_order=1
            )
        ]
    )
    return approval_stage

########################################################
# DeployStage作成
########################################################
def create_deploy_stage(self, source_build_output):
    deploy_stage=_cp.StageProps(
        stage_name='Deploy',
        actions=[
            _cpa.CodeDeployEcsDeployAction(
                action_name='Deploy',
                container_image_inputs=[
                    _cpa.CodeDeployEcsContainerImageInput(
                        input=source_build_output,
                        task_definition_placeholder='IMAGE_NAME'
                    )
                ],
                run_order=1,
                deployment_group=_cd.EcsDeploymentGroup.from_ecs_deployment_group_attributes(
                    self, 'DeploymentGroupAttributes',
                    application=_cd.EcsApplication.from_ecs_application_name(
                        self, 'ApplicationName',
                        'AppECS-DEMO-CLUSTER-DEMO-SERVICE'
                    ),
                    deployment_group_name='DgpECS-DEMO-CLUSTER-DEMO-SERVICE'
                ),
                app_spec_template_file=_cp.ArtifactPath(
                    source_build_output,
                    'appspec.yml'
                ),
                task_definition_template_file=_cp.ArtifactPath(
                    source_build_output,
                    'taskdef.json'
                )
            )
        ]
    )
    return deploy_stage

########################################################
# CodePipeLine作成
########################################################
def create_codepipeline(self, build_project, source_bucket, artifact_bucket):
    # アーティファクト取得
    source_output=_cp.Artifact(artifact_name='SourceArtifact')
    source_build_output=_cp.Artifact(artifact_name='BuildArtifact')

    # コードパイプライン作成
    pipeline=_cp.Pipeline(
        self, 'Pipeline',
        pipeline_name='DEMO-PIPELINE',
        artifact_bucket=artifact_bucket,
        stages=[
            # Source
            create_source_stage(self, source_output, source_bucket),
            # Build
            create_build_stage(self, source_output, build_project),
            # # Approval
            # create_approval_stage(self),
            # Deploy
            create_deploy_stage(self, source_build_output),
        ]
    )