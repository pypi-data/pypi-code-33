import boto3

from orchestrate.core.services.base import Service


class AwsAutoScalingService(Service):
  def __init__(self, services, **kwargs):
    super(AwsAutoScalingService, self).__init__(services)
    self._client = boto3.client('autoscaling', **kwargs)

  @property
  def client(self):
    return self._client

  def put_cpu_tracking_scaling_policy(self, asg_name):
    return self.client.put_scaling_policy(
      AutoScalingGroupName=asg_name,
      PolicyName='cpu-tracking-scaling',
      PolicyType='TargetTrackingScaling',
      TargetTrackingConfiguration=dict(
        PredefinedMetricSpecification=dict(
          PredefinedMetricType='ASGAverageCPUUtilization',
        ),
        TargetValue=50.0,
      )
    )
