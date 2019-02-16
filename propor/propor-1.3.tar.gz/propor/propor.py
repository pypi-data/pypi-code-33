from paramiko import SSHClient, SFTPClient, AutoAddPolicy
from pathlib import Path


def _transferring(ssh, sftp, file_path, root_path):
    file_path = Path(file_path)
    root_path = f'{root_path}/{file_path.name}'
    if file_path.is_dir():
        ssh.exec_command(f'mkdir -p {root_path}')[1].read()
        for f in file_path.iterdir():
            _transferring(ssh, sftp, file_path / f.name, f'{root_path}')
    else:
        sftp.put(file_path, f'{root_path}')


def transfer_file(host, username, password, from_path, to_path='.'):
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=host, username=username, password=password)
        with SFTPClient.from_transport(ssh.get_transport()) as sftp:
            _transferring(ssh, sftp, from_path, to_path)
