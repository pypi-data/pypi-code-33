import json
from arms.utils import exe


def build_system():
    # docker相关
    assert exe('apt-get update')
    assert exe('apt-get install -y apt-transport-https ca-certificates curl software-properties-common')
    assert exe('curl -fsSL https://download.daocloud.io/docker/linux/ubuntu/gpg | sudo apt-key add -')
    assert exe('add-apt-repository "deb [arch=$(dpkg --print-architecture)] https://download.daocloud.io/docker/linux/ubuntu $(lsb_release -cs) stable"')
    assert exe('apt-get update')
    assert exe('apt-get install -y -q docker-ce')
    assert exe('service docker start')
    assert exe('docker ps')
    open("/etc/docker/daemon.json", "w").write(json.dumps({
        "insecure-registries": ["rap.parsec.com.cn:9980"],
        "registry-mirrors": ["http://11854a36.m.daocloud.io"]
    }))
    assert exe('service docker restart')
    # docker-compose相关
    assert exe('wget http://h5.parsec.com.cn/arms/docker-compose-$(uname -s)-$(uname -m)')
    assert exe('chmod +x docker-compose-Linux-x86_64')
    assert exe('mv docker-compose-Linux-x86_64 /usr/local/bin/docker-compose')
    # 前端build工具
    assert exe('curl -sL https://deb.nodesource.com/setup_8.x | bash -')
    assert exe('curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -')
    assert exe('echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list')
    assert exe('apt-get update && sudo apt-get install -y nodejs yarn')
    # gitlab-runner相关
    # assert exe('curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash')
    assert exe('curl https://packages.gitlab.com/gpg.key 2> /dev/null | sudo apt-key add - &>/dev/null')
    open('/etc/apt/sources.list.d/gitlab-runner.list', 'w').write(
        'deb https://mirrors.tuna.tsinghua.edu.cn/gitlab-runner/ubuntu xenial main\n')
    assert exe('apt-get update')
    assert exe('apt-get install -y gitlab-runner')
    assert exe('usermod -a -G docker gitlab-runner')
    assert exe('mkdir -p /opt/docker_volumes && chown gitlab-runner /opt/docker_volumes')
    assert exe('mkdir -p /mnt/docker_volumes && chown gitlab-runner /mnt/docker_volumes')
    assert exe('docker network create common')
