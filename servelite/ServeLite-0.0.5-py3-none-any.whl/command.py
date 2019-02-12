import click
import os
import shutil

@click.group()
def main():
    pass

@click.command()
def init():
    """
    创建一个样例程序
    需要一个配置文件，配置内容。
    - redis服务器和密码。默认在本机运行redis服务。

    """
    path = os.getcwd()
    file_dir = os.path.dirname(os.path.abspath(__file__))

    # 新建ini文件
    shutil.copy(file_dir + '/config_template.py', path + '/config.py')


@click.command()
def test():
    """
    创建一个样例程序
    """
    click.echo('test')

main.add_command(init)
main.add_command(test)

if __name__ == '__main__':
    main()
