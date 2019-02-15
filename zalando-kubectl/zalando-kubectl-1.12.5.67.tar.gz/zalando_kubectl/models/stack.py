import json
import subprocess


class StackUpdateError(Exception):
    pass


class Stack:
    def __init__(self, kubectl, name, namespace):
        self.kubectl = kubectl
        self.name = name
        self.namespace = namespace

    def annotate_restart(self, restart_id):
        patch = [{'op': 'add', 'path': '/spec/podTemplate/metadata/annotations', 'value': {'restart': restart_id}}]
        command = [self.kubectl, 'patch', 'stack', self.name, '--type', 'json', '--patch',
                   '{}'.format(json.dumps(patch))]
        if self.namespace:
            command.extend(['-n', self.namespace])
        try:
            subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise StackUpdateError('Failed to add annotations to pod template: %s'.format(e.stderr))
