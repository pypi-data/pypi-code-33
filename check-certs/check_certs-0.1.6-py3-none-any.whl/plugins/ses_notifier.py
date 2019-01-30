#!/usr/bin/env python

from botocore.exceptions import ClientError
import boto3
import logging

class SesNotifier:
    def __init__(self, params):
        # This address must be verified with Amazon SES.
        self.sender = params.get("sender", "")

        # If your account is still in the sandbox, this address must be verified.
        self.recipient = params.get("recipient", "")

        self.aws_region = params.get("aws_region", "us-west-2")

        # The character encoding for the email.
        self.charset = "UTF-8"
        # Create a new SES resource and specify a region.
        self.client = boto3.client('ses',region_name=self.aws_region)

    def send(self, info):
        # The subject line for the email.
        subject = "%s expires on %s, and in %d days" % (
            info.get("site", "SITE_NOT_PROVIDED"),
            info.get("not_valid_after", "NOT_VALID_AFTER_NOT_PROVIDED"),
            info.get("expires_in_days", "EXPIRES_IN_DAYS_NOT_PROVIDED"),
        )

        body_text = "%s expires on %s, and in %d days" % (
            info.get("site", "SITE_NOT_PROVIDED"),
            info.get("not_valid_after", "NOT_VALID_AFTER_NOT_PROVIDED"),
            info.get("expires_in_days", "EXPIRES_IN_DAYS_NOT_PROVIDED"),
        )

        try:
            #Provide the contents of the email.
            response = self.client.send_email(
                Destination={
                    'ToAddresses': [
                        self.recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': self.charset,
                            'Data': body_text,
                        },
                    },
                    'Subject': {
                        'Charset': self.charset,
                        'Data': subject,
                    },
                },
                Source=self.sender,
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
            raise e
        else:
            logging.info("Email sent! Message ID: %s" % response['ResponseMetadata']['RequestId'])

def setup(app, params):
    app.register_notifier(SesNotifier(params))
