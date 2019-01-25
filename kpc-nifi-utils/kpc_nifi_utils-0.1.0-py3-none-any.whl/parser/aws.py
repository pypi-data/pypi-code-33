from kpc_nifi_utils.common.args_parser import Args


class AwsArgs(Args):
    def __init__(self):
        super().__init__()

        self.add('--AWSKEY', type=str)
        self.add('--AWSSECRET', type=str)

    def get_key(self):
        return self.get('AWSKEY')

    def get_secret(self):
        return self.get('AWSSECRET')
