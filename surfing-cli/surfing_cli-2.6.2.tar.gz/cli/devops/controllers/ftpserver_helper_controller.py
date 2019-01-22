"""
ftpserver_helper cli 需要的功能将都在这里支持
"""
from fabric import Connection
from fabric import Result
from invoke import Responder
from ..py_configs.ftp_server_config import *
from cli.packages.controllers.package_analysis_controller import PackageAssistantController
import os.path as path
import cli, os, zipfile, time


# ftp 上传目录解释结果存放类
class FtpInfo:

    def __init__(self, target_path):
        """

        :param str target_path:
        """
        self.target_path = target_path
        self.project_code = None
        self.company_code = None
        self.ftp_id = 0

        # 去分析路径
        self.init()

    def init(self):
        path_list = self.target_path.strip("/").split("/")
        if len(path_list) != 5:
            cli.error("路径分析结果不匹配，请核对路径")
            raise AttributeError("路径拆分个数({})不等于5".format(len(path_list)))

        self.project_code = path_list[2]
        self.company_code = path_list[3]
        self.ftp_id = str(path_list[4]).split("_")[1]

    def __str__(self):
        return " path:{}\n <项目代号:{},外包代号:{},ftp_id:{}>".format(self.target_path, self.project_code,
                                                               self.company_code, self.ftp_id)


# ftp 服务器上的第一步逻辑处理器
class FtpServerHelperStep1:

    def __init__(self, zipfile_path):
        """

        :param str zipfile_path:
        """
        self.zipfile_path = zipfile_path
        self.zipfile_root_foldername = self.get_zipfile_rootpath(zipfile_path)  # 解压后的根目录名
        if not self.zipfile_root_foldername:
            cli.error("无法获取压缩包的根目录")
            exit()

        # ftp 信息
        self.ftp_info = FtpInfo(path.dirname(self.zipfile_path))

        self.zip_uploads_path = path.dirname(self.zipfile_path)  # ftp 上传目录
        self.zip_process_path = path.join(ftp_data_tmp_path(),
                                          self.ftp_info.project_code,
                                          self.ftp_info.company_code + "_fid_" + self.ftp_info.ftp_id
                                          )  # ftp 上传的数据临时处理目录

        self.zipfile_newname = "{}_{}_{}.zip".format(self.ftp_info.project_code,
                                                     self.ftp_info.company_code + "_fid" + self.ftp_info.ftp_id,
                                                     time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                                                     )
        # 执行本地linux 命令实例
        self.local_connection = Connection("localhost")

    # 获取zip 根目录
    def get_zipfile_rootpath(self, zip_file_path):
        """
        :param str zip_file_path:
        :return: None if not a zip file,else  rootname of zip
        """
        # 检测是否是zip 文件
        if not zipfile.is_zipfile(zip_file_path):
            return None

        # 分析根目录
        zip_file = zipfile.ZipFile(zip_file_path, "r")
        zip_root_dir_name = zip_file.infolist()[0]
        return zip_root_dir_name.filename.rstrip("/")

    def show_tree(self):
        """
        显示出给定目录的tree 结构，默认两层，将调用系统自带的tree命令
        :return:
        """
        self.local_connection.local("tree -L {level} {path}".format(path=self.zip_process_path, level=2))

    def ls_lah(self, file_path):
        cli.info("ls -lah {}".format(file_path))
        self.local_connection.local("ls -lah {}".format(file_path))

    def show_zipfile_info(self):
        """
        分析给定的ftp上传目录，获取相关的项目代号，外包代号,ftp id 等信息
        :return:
        """
        cli.info(str(self.ftp_info))

    def mv(self):
        """
        移动文件到数据处理目录下
        :return:
        """

        if not path.exists(self.zip_process_path):
            os.makedirs(self.zip_process_path, exist_ok=True)  # 不存在则新建，存在则不管
        self.local_connection.local("mv {} {}".format(self.zipfile_path,
                                                      path.join(self.zip_process_path, self.zipfile_newname)
                                                      ))

    def unzip(self):
        """
        解压
        :return:
        """
        responder = Responder(
            pattern=r".*",
            response="A\n",
        )
        cli.info("unzip {} -d {}".format(path.join(self.zip_process_path,
                                                   self.zipfile_newname),
                                         self.zip_process_path))
        result = self.local_connection.local("unzip {} -d {}".format(path.join(self.zip_process_path,
                                                                               self.zipfile_newname),
                                                                     self.zip_process_path),
                                             pty=True)  # type:Result
        # if result.ok:
        #     cli.info("解压完成")
        # elif result.failed:
        #     cli.error("解压出错了")
        #     cli.error(result.stderr + "\n")
        #     exit(result.return_code)

        # 压缩包解压后的名字按命名规范重命名
        cli.info("mv {} {}".format(path.join(self.zip_process_path, self.zipfile_root_foldername),
                                   path.join(self.zip_process_path, self.zipfile_newname[:-4])
                                   ))
        self.local_connection.local("mv {} {}".format(path.join(self.zip_process_path, self.zipfile_root_foldername),
                                                      path.join(self.zip_process_path, self.zipfile_newname)[:-4]
                                                      ))

    # 包分析
    def package_analysis(self):
        # 最后一个 ''字符拼接必须得有，后期调整逻辑
        packages_folder = path.join(self.zip_process_path, self.zipfile_newname[:-4])
        cli.info("分析目录:{}".format(packages_folder))

        assistant_controller = PackageAssistantController(packages_folder)
        assistant_controller.do_analysis()

        # wav 目录下的文件移到wav同级目录下
        assistant_controller.replace_folder_wav_files()

        # 删除 包中出现的 m4a mp3 temp 目录
        assistant_controller.delete_unknown_folders()

        # 删除后缀 skip、sk、pk等文件
        assistant_controller.delete_unknown_suffix_file()

        # .u后缀文件rename
        assistant_controller.rename_endswith_u_file()

        # 删除重复录制产生的 xxx_1.wav xxx_2.wav 这种文件
        assistant_controller.delete_duplicated_underline_number_file()

        # 解密被加密的文件
        assistant_controller.decrypt_endswith_enc_file()

        # 删除没有对应音频的txt
        assistant_controller.delete_single_txt()

        # 输出结果，生成excel 和 运行结果文件
        assistant_controller.result_echo_no_via_pager()
        assistant_controller.result_write_2_file()
        assistant_controller.package_info_write_to_excel()

        # 发送邮件通知
        assistant_controller.send_mail(True, True)


# 按命名规范起名的目录信息
class PackagesFolderInfo:
    def __init__(self, packages_folder_path):
        self.packages_folder_path = packages_folder_path
        self.packages_folder_name = path.basename(packages_folder_path)
        self.project_code, self.company_code, self.ftp_id = self.packages_folder_name.split("_")[:3]
        self.ftp_id = self.ftp_id[len("fid"):]
        self.packages_count = len([package for package in os.listdir(packages_folder_path)
                                   if path.isdir(path.join(packages_folder_path, package))
                                   ])

    def __str__(self):
        return "目录名称解析信息:{}\n".format(str(vars(self)))

    # def __repr__(self):
    #     return str(vars(self))


# ftp 服务器上的第一步逻辑处理器
class FtpServerHelperStep2:

    def __init__(self, packages_folder_path):
        """

        :param zipfile_path:
        """
        self.packages_folder_path = packages_folder_path
        self.packages_folder_info = PackagesFolderInfo(packages_folder_path)
        self.tar_path = path.join(data_sync_backup_path(), self.packages_folder_info.project_code)
        self.tar_name = "{}_packagecount{}".format(path.join(self.tar_path,
                                                             self.packages_folder_info.packages_folder_name
                                                             ),
                                                   self.packages_folder_info.packages_count
                                                   )

        # 执行本地linux 命令实例
        self.local_connection = Connection("localhost")

    # 目录下的包总数
    def compress_folder(self):
        # 检测压缩存放目录是否存在，不存在则创建
        if not path.exists(self.tar_path):
            os.makedirs(self.tar_path, exist_ok=True)  # 不存在则新建，存在则不管

        command = "tar -zcf {}.tar.gz {} ".format(self.tar_name, self.packages_folder_path)
        cli.info(command)
        self.local_connection.local(command)

    def upload_2_weiruan(self):
        """
        上传到微软服务器的逻辑
        :return:
        """
        #surfing@surfing.chinanorth.cloudapp.chinacloudapi.cn 因这种登录方式不便于使用服务器改动，也不想读配置文件
        #此处的ssh 信息将应该是~/.ssh/config中配置好然后直接使用它的host
        command = "rsync -avz --progress {} SurfingtechProductionServer:{}".format(
            path.join(data_sync_backup_path(), self.packages_folder_info.project_code, self.tar_name + ".tar.gz"),
            "/SurfingDataDisk/ftpserver_synchronize_folder"
        )
        cli.info(command)

        self.local_connection.local(command)
