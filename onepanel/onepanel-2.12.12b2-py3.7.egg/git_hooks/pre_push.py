import onepanel.git_hooks.pre_push_to_endpoint_hook

class PrePush:
    version = None

    def __init__(self):
        self.version = '1.0.0'

    @staticmethod
    def read_self():
        file_path = __file__
        if file_path.endswith('.pyc'):
            file_path = file_path.replace('pyc','py')
        with open(file_path,'r') as f:
            return f.read()


if __name__ == '__main__':
    onepanel.git_hooks.pre_push_to_endpoint_hook.PrePushToEndpointHook.ping_endpoint()