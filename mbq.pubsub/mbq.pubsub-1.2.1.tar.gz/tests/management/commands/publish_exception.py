import json

from django.core.management.base import BaseCommand

import boto3
from mbq import env


class Command(BaseCommand):
    def handle(self, *args, **options):
        sns = boto3.client("sns")
        sns.publish(
            TargetArn=env.get("SNS_ARN"),
            MessageStructure="json",
            Message=json.dumps(
                {
                    "default": json.dumps(
                        {"message_type": "pubsub.update_raise_exception", "payload": {"foo": "bar"}}
                    )
                }
            ),
        )
