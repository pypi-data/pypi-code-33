from paramiko import SSHClient, SFTPClient, AutoAddPolicy
from socket import socket, AF_INET, SOCK_DGRAM
from pathlib import Path
import sys


class Controller:
    def __init__(self, host_entry, project_path):
        self.local_host = self._get_local_host()
        self.host_entry = host_entry
        if self.local_host == self.host_entry:
            self.project_path = Path(project_path)
            execute_file_path = sys.argv[0].replace(project_path, './').replace('\\', '/')
            self.execute_file_path = execute_file_path if execute_file_path else self.project_path.name
        self.host_set = {}

    def host(self, host, username=None, password=None):
        def wrapper(execute_function):
            self.host_set[host] = {
                'host': host,
                'username': username,
                'password': password,
                'execute_function': execute_function,
            }
        return wrapper

    def deploy(self):
        # 部署（在本地部署非本地）
        if self.local_host == self.host_entry:
            for host, item in self.host_set.items():
                if host != self.host_entry:
                    assert item['username'] and item['password']
                    with SSHClient() as ssh:
                        ssh.set_missing_host_key_policy(AutoAddPolicy())
                        ssh.connect(hostname=host, port=22, username=item['username'], password=item['password'])
                        with SFTPClient.from_transport(ssh.get_transport()) as sftp:
                            self._transfer_file(ssh, sftp, self.project_path)
                            message = ssh.exec_command(f'python3 {self.execute_file_path}')[1].read()
                            if message:
                                print(message)
                            else:
                                print(f'Remote host({host}) deployment failed.')
        # 运行
        self.host_set[self.local_host]['execute_function']()
        print(f'Remote host({self.local_host}) deployment succeeded.')

    def _transfer_file(self, ssh, sftp, file_path, root_path='.'):
        root_path = f'{root_path}/{file_path.name}'
        if file_path.is_dir():
            ssh.exec_command(f'mkdir {root_path}')[1].read()
            for f in file_path.iterdir():
                self._transfer_file(ssh, sftp, file_path / f.name, f'{root_path}')
        else:
            sftp.put(file_path, f'{root_path}')

    @staticmethod
    def _get_local_host():
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
