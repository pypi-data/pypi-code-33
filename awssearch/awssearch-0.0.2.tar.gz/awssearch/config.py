import pinkboto
from awssearch.sh import sh
from awssearch.cli.cli import aws_profiles

connections = []
if not aws_profiles:
    for p in sh("grep -oP '(?<=^\[)\w+(?=\])' ~/.aws/credentials"):
        connections += [
            pinkboto.aws(profile=p, region='us-east-1', cache=None)
        ]
else:
    aws_profiles = aws_profiles.split(',')
    for aws_profile in aws_profiles:
        connections += [
            pinkboto.aws(profile=aws_profile, region='us-east-1', cache=None)
        ]
