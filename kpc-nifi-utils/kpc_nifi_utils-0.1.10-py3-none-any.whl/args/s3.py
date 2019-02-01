from kpc_nifi_utils.args.aws import AwsArgs


class S3Args(AwsArgs):
    def __init__(self):
        super().__init__()

        self.add('--s3bucket', type=str)

    def get_bucket(self):
        return self.get('s3bucket')
