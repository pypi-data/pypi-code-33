
from subprocess import check_output, run, PIPE


def run_cmd(cmd):
    process = run(cmd, shell=True, stdout=PIPE, check=True)
    return process.stdout.decode('utf-8')


def md5_sum(filename):
    cmd = f'openssl md5 -binary {filename} | base64'
    checksum = run_cmd(cmd).strip()
    return checksum
