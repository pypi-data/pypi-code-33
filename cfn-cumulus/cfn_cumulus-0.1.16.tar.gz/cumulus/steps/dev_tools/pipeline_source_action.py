import awacs
import awacs.aws
import awacs.ec2
import awacs.iam
import awacs.logs
import awacs.s3
import awacs.sts
import troposphere
from troposphere import iam, \
    codepipeline

import cumulus.policies
import cumulus.policies.codebuild
from cumulus.chain import step
from cumulus.steps.dev_tools import META_PIPELINE_BUCKET_POLICY_REF
from cumulus.types.codebuild.buildaction import SourceS3Action
from cumulus.util.template_query import TemplateQuery


class PipelineSourceAction(step.Step):

    def __init__(self,
                 action_name,
                 output_artifact_name,
                 s3_bucket_name,
                 s3_object_key,
                 poll_for_source_changes=None,
                 ):
        """
        :type poll_for_source_changes: None or boolean - not setting this seems to have a different behaviour
                                                         than setting it to false.  To not have the pipeline trigger by s3 state changes
                                                          set this to False.  For normal S3 triggering, do not set this.
        :type s3_object_key: basestring Path of the artifact in the bucket.
        :type s3_bucket_name: basestring or troposphere.Ref Object of the bucket name.
        :type input_artifact_name: basestring The artifact name in the pipeline.
              (should contain buildspec.yml. You can override that name in a codebuild action)
        :type action_name: basestring Displayed on the console
        :type environment: troposphere.codebuild.Environment Optional if you need ENV vars or a different build.
        :type vpc_config.Vpc_Config: Only required if the codebuild step requires access to the VPC
        """
        step.Step.__init__(self)
        self.poll_for_source_changes = poll_for_source_changes
        self.s3_object_key = s3_object_key
        self.s3_bucket_name = s3_bucket_name
        self.output_artifact_name = output_artifact_name
        self.action_name = action_name

    def handle(self, chain_context):
        print("Adding source action %s." % self.action_name)

        template = chain_context.template

        policy_name = "CodeBuildPolicy%s" % chain_context.instance_name
        codebuild_policy = cumulus.policies.codebuild.get_policy_code_build_general_access(policy_name)

        role_name = "PipelineSourceRole%s" % self.action_name
        codebuild_role = iam.Role(
            role_name,
            Path="/",
            AssumeRolePolicyDocument=awacs.aws.Policy(
                Statement=[
                    awacs.aws.Statement(
                        Effect=awacs.aws.Allow,
                        Action=[awacs.sts.AssumeRole],
                        Principal=awacs.aws.Principal(
                            'Service',
                            "codebuild.amazonaws.com"
                        )
                    )]
            ),
            Policies=[
                codebuild_policy
            ],
            ManagedPolicyArns=[
                chain_context.metadata[META_PIPELINE_BUCKET_POLICY_REF]
            ]
        )

        source_action = SourceS3Action(
            Name=self.action_name,
            OutputArtifacts=[
                codepipeline.OutputArtifacts(
                    Name=self.output_artifact_name
                )
            ],
            Configuration={
                "S3Bucket": self.s3_bucket_name,
                "S3ObjectKey": self.s3_object_key,
            },
        )

        # TODO: support CFN params here. Use conditionals. Set to NoValue instead of None, using the same logic as below
        if self.poll_for_source_changes is not None:
            # if it's none - we shouldn't touch this.
            source_action.Configuration['PollForSourceChanges'] = self.poll_for_source_changes

        template.add_resource(codebuild_role)

        found_pipelines = TemplateQuery.get_resource_by_type(
            template=chain_context.template,
            type_to_find=codepipeline.Pipeline)
        pipeline = found_pipelines[0]

        # Alternate way to get this
        # dummy = TemplateQuery.get_resource_by_title(chain_context.template, 'AppPipeline')

        stages = pipeline.Stages  # type: list

        # TODO: find stage by name
        first_stage = stages[0]

        # TODO accept a parallel action to the previous action, and don't +1 here.
        first_stage.Actions.append(source_action)

        template.add_output(
            troposphere.Output(
                "PipelineBucket%s" % self.action_name,
                Value=self.s3_bucket_name,
                Description="A pipeline source bucket",
            )
        )
        template.add_output(
            troposphere.Output(
                "PipelineTriggerObject%s" % self.action_name,
                Value=self.s3_object_key,
                Description="An s3 object key in the pipeline bucket "
                            "that will trigger the pipeline",
            )
        )
