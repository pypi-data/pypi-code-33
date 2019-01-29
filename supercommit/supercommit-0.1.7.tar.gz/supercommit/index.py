#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import stat
import pathlib
import shutil
import json
from pathlib import Path
import hashlib

import click
import inquirer
from translate import Translator
from terminaltables import AsciiTable
from configparser import ConfigParser

from supercommit import Version
from supercommit import echo
from supercommit import executor
from supercommit.executor import swiftlint_rule_content
from supercommit.executor import commit_msg_enter

vailed_header = ['feat', 'fix', 'docs', 'ref', 'chore', 'test', 'style', 'Merge', 'Revert']
header_desc = ['新功能（feature）', '修补问题', '更新文档', '重构（即不是新增功能，也不是修改bug的代码变动）', 'bump version to ${版本号}', '增加测试', '格式变更（不影响代码运行的变动）']

# 源根目录
source_path = pathlib.Path(__file__).resolve().parent
# 全局路径
gobal_path = os.path.join(Path.home(), '.supercommit')
# 用户lint路径
swiftlint_rule_path = os.path.join(gobal_path, '.swiftlint-rule.yml')
# 配置文件路径
global_config_path = os.path.join(gobal_path, 'config')
# 源lint路径
source_swiftlint_rule_path = os.path.join(source_path, 'swiftlint-rule.yml')

cfg = ConfigParser()
translator= Translator(to_lang="zh")

@click.command()
@click.option('--bury', is_flag=True)
@click.option('--no-lint', is_flag=True)
@click.option('--clip', is_flag=True)
def cli(bury, no_lint, clip):
    if bury:
        install_commit_hook()
        install_global_rules()
        echo.success('🎉  Git Hook 已经更新')
        return
    if clip:
        result = executor.excute_swiftlint_clip()
        echo.info(result)
        return
    pre_run()
    questions = [
    inquirer.List('commit',
                    message="请选择一个您想要的commit类型",
                    choices=[
                            'feat:      %s' % header_desc[0],
                            'fix:       %s' % header_desc[1],
                            'docs:      %s' % header_desc[2],
                            'refactor:  %s' % header_desc[3],
                            'chore:     %s' % header_desc[4],
                            'test:      %s' % header_desc[5],
                            'style:     %s' % header_desc[6]
                            ],
                ),
    ]
    data = inquirer.prompt(questions)
    if data == None:
        return
    module = click.prompt(echo.OKGREEN +'请输入提交所影响的模块(如果在子工程中可以忽略不填 eg: 个人中心)', default='默认为空')
    type_prefix = None
    for x in vailed_header:
        if x in data['commit']:
            type_prefix = x
            break
    message = None
    isVaild = False
    while not isVaild:
        current_message = click.prompt(echo.OKGREEN + '请输入具体commit信息')
        if len(current_message) < 2:
            echo.error('message内容不能少于2个字符!')
            continue
        if len(current_message) > 100:
            echo.error('message内容不能超过100个字符!')
            continue
        isVaild = True
        message = current_message
    command = None
    if module == '默认为空':
        command = 'git commit -m "%s: %s"' % (type_prefix, message)
    else:
        command = 'git commit -m "%s: [%s] %s"' % (type_prefix, module, message)
    if no_lint:
        command += ' --no-verify'
    call_command(command)

def call_command(command):
    result = os.popen(command).read()
    echo.normal(result)

def pre_run():
    pwd = os.getcwd()
    git_path = os.path.join(pwd, '.git')
    git_exit = os.path.exists(git_path)
    if not git_exit:
        echo.error('当前目录非Git目录或者非Git根目录，请切换目录再试~')  
        exit(1)
    sc_path = os.path.join(git_path, 'sc')
    sc_exit = os.path.exists(sc_path)
    version_path = os.path.join(sc_path, 'version')
    if not sc_exit:
        # 如果不存在那么创建并且写入
        os.mkdir(sc_path)
        with open(version_path, 'w') as f:
            f.write(Version)
        install_all_cache()
    else:
        current_version = None
        with open(version_path, 'r') as f:
            current_version = f.read()
        if current_version != Version:
            install_all_cache()

'''
安装所有的配置
'''
def install_all_cache():
    install_commit_hook()
    install_global_rules()

'''
安装GIt钩子
'''
def install_commit_hook():
    pwd = os.getcwd()
    hook_path = os.path.join(pwd, '.git/hooks')
    deti_path = str(hook_path) + '/commit-msg'
    if not os.path.exists(hook_path):
        os.mkdir(hook_path)
    with open(deti_path, 'w+') as f:
        f.write(commit_msg_enter)
    os.chmod(deti_path, 0o777)

'''
安装全局的规则
'''
def install_global_rules():
    gobal_path = os.path.join(Path.home(), '.supercommit')
    if not os.path.exists(gobal_path): os.mkdir(gobal_path)
    with open(swiftlint_rule_path, 'w+') as f:
        f.write(swiftlint_rule_content)

''''
Git commit-msg hook
'''
def run_commit_msg(message_file):
    is_vailed = False
    with open(message_file, 'r') as txt_file:
        commit_message = txt_file.read()
        for header in vailed_header:
            if commit_message.startswith(header):
                is_vailed = True
    if not is_vailed:
        echo.error("==> commit message不符合规范,请遵守以下规范:" + generate_rule_text())
        exit(1)
    result = executor.excute_swiftlint_lint()
    if not result: return
    json_body = json.loads(result)
    cfg = get_global_config()
    if len(json_body) > 0:
        table_data = []
        table_data.append(['File', 'Line', 'Reason'])
        for item in json_body:
            reason = item['reason']
            zn_reason = get_translate_from_cache(reason) + reason
            table_data.append((item['file'], item['line'], zn_reason))
        sync_global_config()
        table = AsciiTable(table_data)
        echo.warning(table.table)
        echo.error('您的提交内容不规范,请修改之后提交，具体规则请移步: https://github.com/github/swift-style-guide')
        exit(1)

def generate_rule_text():
    rule_text = ''
    for index, item in enumerate(header_desc):
        rule_text += '\n%s: %s' % (vailed_header[index], item)
    return rule_text

def get_translate_from_cache(source):
    m = hashlib.md5()
    m.update(source.encode('utf-8'))
    key = str(m.hexdigest())
    try:
        result = cfg.get('language', key)
    except Exception:
        result = translator.translate(source)
        cfg.set('language', key, result)
    return result

'''
获取全局的配置方法
'''
def get_global_config():
    if not os.path.exists(global_config_path):
        cfg.add_section('language')
        Path(global_config_path).touch()
        sync_global_config()
    else:
        cfg.read(global_config_path)
    if "language" not in cfg:
        cfg.add_section('language')
    return cfg

'''
配置文件同步
'''
def sync_global_config():
    with open(global_config_path, 'w+') as f:
        cfg.write(f)