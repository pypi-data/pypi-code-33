import os
import ftplib
from ftplib import FTP


class FTPS:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password


    def upload_file(self, local_path, filename, remote_path):
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            try:
                ftp.cwd(remote_path)
                with open(local_path, 'rb') as fp:
                    res = ftp.storlines("STOR " + filename, fp)
                    print(res)
            except ftplib.all_errors as e:
                print('FTP error:', e)


    def download_file(self, download_file, remote_path):
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            try:
                with open(download_file, 'w') as fp:
                    res = ftp.retrlines('RETR ' + remote_path, fp.write)
                    if not res.startswith('226 Transfer complete'):
                        print('Download failed')
                        if os.path.isfile(download_file):
                            os.remove(download_file)
            except ftplib.all_errors as e:
                print('FTP error:', e)


    def make_dir(self, dir_name):
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            try:
                ftp.mkd(dir_name)
            except Exception as e:
                raise e


    def list_dir(self, remote_path=''):
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            return ftp.dir()

