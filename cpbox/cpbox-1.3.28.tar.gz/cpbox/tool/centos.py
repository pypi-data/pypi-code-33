import commands
import shlex
import subprocess

def docker0_ip():
    cmd="ip addr show docker0 | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | awk '{print $1}' | head  -1"
    ip = run_cmd_ret(cmd)
    if not ip:
        ip = '172.20.0.1'
    return ip

def run_cmd(cmd, mute=False):
    if not mute:
        print cmd
    return commands.getstatusoutput(cmd)

def call(cmd, mute=False):
    if not mute:
        print cmd
    args = ['/bin/bash', '-c', cmd]
    return subprocess.call(args)

def run_cmd_ret(cmd, mute=False):
    return run_cmd(cmd, mute)[1]

def stop_container(container_name):
    cmd="docker ps -a -f name='^/%s$' | grep '%s' | awk '{print $1}' | xargs -I {} docker rm -f --volumes {}" % (container_name, container_name)
    call(cmd)

def firewall_list_public_access():
    code, list = run_cmd('firewall-cmd --zone=public --list-port')
    if code == 0:
        list = list.split()
        list.sort()
        return list
    return []

def firewall_ensure_public_access(ports):
    for port in ports:
        run_cmd("firewall-cmd --zone=public --add-port=%s --permanent" % port)
    if len(ports) > 0:
        run_cmd("firewall-cmd --reload")

def firewall_remove_public_access(ports):
    for port in ports:
        run_cmd("firewall-cmd --zone=public --remove-port=%s --permanent" % port)
    if len(ports) > 0:
        run_cmd("firewall-cmd --reload")

def run_cmd_(cmd):
    print cmd
