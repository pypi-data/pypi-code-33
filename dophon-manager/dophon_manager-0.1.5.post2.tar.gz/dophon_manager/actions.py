# encoding:utf-8
import os
import toml
import xml.etree.ElementTree as ET
import time
import subprocess
import re
import platform
from poetry import locations


def entity_file_struct(entity_function: str = 'run'):
    return """from dophon import boot

# 启动服务器
def """ + entity_function + """():
    boot.run_app()

__path__ = """ + entity_function + """()"""


class ActionObj:
    def init_modulexml(self, modules_list: list, project_name: str):
        # 创建根节点(dophon)
        a = ET.Element("dophon")
        # 创建子节点，并添加属性
        b = ET.SubElement(a, "modules")
        for m in modules_list:
            # 创建对应模块节点
            c = ET.SubElement(b, 'module')
            d = ET.SubElement(c, 'pre-name')
            d.text = 'dophon'
            e = ET.SubElement(c, 'name')
            e.text = m
        # 创建模块文件
        tree = ET.ElementTree(a)
        tree.write(os.sep.join([os.getcwd(), project_name, "module.xml"]))

    def new_action(
            self,
            project_name: str
    ):
        # 利用poetry创建项目
        print('create new project,name (default:dophon_project):\n>>>', project_name)
        project_path = os.getcwd() + os.sep + project_name
        # 判断项目是否存在
        if os.path.exists(project_path):
            print('===== warning !! project(' + project_name + ') exists! =====')
            return
        os.system('poetry new %s' % (project_name,))
        while True:
            if not os.path.exists(project_path):
                # 未创建项目,则等待
                time.sleep(1)
            # 询问必要参数
            while True:
                entity_point = input(
                    'project boot file (default:Bootstrap:run):\nlike:(<file_name>:<function_name>)\n>>>')
                entity_point = entity_point if entity_point else 'Bootstrap:run'
                # 校验输入
                if re.match('^([a-zA-Z_.])+:([a-zA-Z_.])+$', entity_point):
                    break
                else:
                    print('input illegal!must like:(<file_name>:<function_name>)')
            toml_file_path = os.sep.join([os.getcwd(), project_name, 'pyproject.toml'])
            # 读取项目toml文件
            toml_file = toml.load(open(toml_file_path))
            # 组装项目入口信息
            toml_file['tool']['poetry']['scripts'] = {project_name: entity_point}
            toml_file['tool']['poetry']['dependencies']['dophon'] = '*'
            print('======project name : ' + project_name + '======')
            # 询问是否添加其他模块
            add_modules = input('add others modules?\n(db/mq)\ncan add multi,please sep with ,\n>>>').strip()
            if add_modules:
                # 添加其余模块
                modules_list = add_modules.split(',')
                for m in modules_list:
                    print('======add dophon module : dophon-' + m + '======')
                    toml_file['tool']['poetry']['dependencies']['dophon-' + m] = '*'
                # 询问是否初始化模块文件
                init_module_file_flag = input('want to init module.xml?(default:False)\n(True/False)\n>>>')
                init_module_file_flag = bool(init_module_file_flag) \
                    if init_module_file_flag \
                    else False
                if init_module_file_flag:
                    print('======init module.xml======')
                    # 初始化模块文件
                    self.init_modulexml(modules_list, project_name)
            # 保存toml文件信息
            with open(toml_file_path, 'w') as final_toml:
                print('======writing pyproject.toml======')
                final_toml.write(toml.dumps(toml_file))
            # 初始化项目,安装相关依赖
            self.project_install(project_path)
            self.init_env_setting(project_name, project_path)
            # 初始化项目文件
            self.init_project_file(project_path, project_name, entity_point)
            break

    def init_project_file(self, project_path, project_name, entity_point):
        entity_prefix = entity_point.split(':')[0].split('.')
        entity_file = entity_prefix.pop() + '.py'
        entity_file_path = project_path + os.sep + project_name + os.sep + os.sep.join(entity_prefix)
        if not os.path.exists(entity_file_path):
            os.makedirs(entity_file_path)
        entity_function_name = entity_point.split(':')[1]
        with open(entity_file_path + os.sep + entity_file, 'wb') as e_file:
            e_file.write(bytes(entity_file_struct(entity_function_name), encoding='utf-8'))

    def project_install(self, project_path):
        install_ask = input('would you want to initial project?(y/n),default no\n>>>')
        if install_ask == 'y':
            print('======initialing project======')
            print('start initialing project,please wait')
            install_process = subprocess.Popen('poetry install', cwd=project_path, shell=True, stdout=subprocess.PIPE,
                                               universal_newlines=True)
            install_process.wait()
            self.listen_popen(install_process)

    def listen_popen(self, popen):
        result_lines = popen.stdout.readlines()  # 从子进程 p 的标准输出中读取所有行，并储存在一个list对象中
        # 对比前后行数
        for line in result_lines:
            print(line.strip())

    def init_action(
            self,
            project_name
    ):
        """
        初始化项目(dophon)

        --name: Name of the package.
        --description: Description of the package.
        --author: Author of the package.
        --dependency: Package to require with a version constraint. Should be in format foo:1.0.0.
        --dev-dependency: Development requirements, see --require.
        :return:
        """
        if not project_name and project_name != os.getcwd().split(os.sep)[-1]:
            print(
                f"""current directory name ({os.getcwd().split(os.sep)[-1]}) is different to project directory name ("""
                f"""{project_name}),some warning or error will be coming when use "dophon" command to active project""")
        project_name = os.getcwd().split(os.sep)[-1] if not project_name else project_name
        project_path = os.getcwd() + os.sep + project_name
        entity_point = 'Bootstrap:run'
        # 初始化poetry项目
        command = 'poetry init --name=%s --description=%s --author=%s' % (
            project_name, project_name, platform.node())
        print(command)
        os.system(
            command
        )
        # 初始化dophon项目配置文件
        toml_file_path = os.sep.join([os.getcwd(), 'pyproject.toml'])
        # 读取项目toml文件
        toml_file = toml.load(open(toml_file_path))
        # 组装项目入口信息
        toml_file['tool']['poetry']['scripts'] = {project_name: entity_point}
        toml_file['tool']['poetry']['dependencies']['dophon'] = '*'
        # 询问是否添加其他模块
        add_modules = input('add others modules?\n(db/mq)\ncan add multi,please sep with ,\n>>>').strip()
        if add_modules:
            # 添加其余模块
            modules_list = add_modules.split(',')
            for m in modules_list:
                print('======add dophon module : dophon-' + m + '======')
                toml_file['tool']['poetry']['dependencies']['dophon-' + m] = '*'
        # 保存toml文件信息
        with open(toml_file_path, 'w') as final_toml:
            print('======writing pyproject.toml======')
            final_toml.write(toml.dumps(toml_file))
        self.init_project_file(project_path, '', entity_point)
        os.system('poetry install')
        self.init_env_setting(project_name, project_path)

    def init_env_setting(self, project_name, project_path):
        """
        初始化虚拟环境设置
        :param project_name:
        :return:
        """
        try:
            virtual_path = subprocess.Popen('poetry config settings.virtualenvs.path', cwd=project_path, shell=True,
                                            stdout=subprocess.PIPE, universal_newlines=True)
            virtual_path.wait()
            virtual_package = eval(virtual_path.stdout.readline())
            print(f'virtual environment was in \n {virtual_package}')
            env_path = virtual_package + os.sep.join([
                '',
                '%s-py%s' % (project_name, platform.python_version()[0:3]),
                'Scripts'
            ])
        except Exception as e:
            print(f'raise exception:{e},use default virtual environment path {locations.CACHE_DIR}')
            env_path = locations.CACHE_DIR + os.sep.join([
                '',
                'virtualenvs',
                '%s-py%s' % (project_name, platform.python_version()[0:3]),
                'Scripts'
            ])
        command = '%s%s%s' % (env_path, os.sep, 'activate')
        if platform.system() == 'Windows':
            print('windows user please copy and execute this command: \n%s' % (command,))
            os.system(command)
        else:
            command = 'source %s%s%s' % (env_path, os.sep, 'activate')
            print("""
            if can\'t find virtual environment active script,please fallow these step;
            1.navigate to this path (%s) and find your project
            2.find Script director
            3.run active script,active.bat for Windows,active for Linux
            """ % (locations.CACHE_DIR,))
            os.system(command)

    def dev_action(self, project_name):
        """
        调试
        :return:
        """
        # project_name = os.getcwd().split(os.sep)[-1]
        # # 初始化dophon项目配置文件
        # toml_file_path = os.sep.join([os.getcwd(), 'pyproject.toml'])
        # # 读取项目toml文件
        # toml_file = toml.load(open(toml_file_path))
        # entity_file_str = toml_file['tool']['poetry']['scripts'][project_name]
        # entity_file_path = os.getcwd() + os.sep + re.sub(':.*', '', entity_file_str)
        # command = 'python -m %s' % (entity_file_path,)
        # os.system(command)
        print("""this version didn't has dev tools,please wait for new version""")

    def run_action(self, project_name):
        """
        运行
        :return:
        """
        project_name = os.getcwd().split(os.sep)[-1]
        # 初始化dophon项目配置文件
        toml_file_path = os.sep.join([os.getcwd(), 'pyproject.toml'])
        # 读取项目toml文件
        toml_file = toml.load(open(toml_file_path))
        entity_file_str = toml_file['tool']['poetry']['scripts'][project_name]
        entity_file_path = project_name + '.' + re.sub(':.*', '', entity_file_str)
        command = 'python -m %s' % (entity_file_path,)
        os.system(command)
