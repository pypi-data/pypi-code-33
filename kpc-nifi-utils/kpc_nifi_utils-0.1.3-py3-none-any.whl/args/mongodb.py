from kpc_nifi_utils.common.args_parser import Args


class MongoArgs(Args):
    def __init__(self):
        super().__init__()

        self.add('--mongostring', '-mgcs', type=str)
        self.add('--mongodbname', '-mgdbn', type=str)

    def get_connection_string(self):
        return self.get('mongostring')

    def get_db_name(self):
        return self.get('mongodbname')
