import ftplib


class FTPUploader:
    def __init__(self, host=None, port=21, login=None, password=None):
        self.ftp = ftplib.FTP()
        self.host = host
        self.port = port
        self.login = login
        self.password = password

    def create_dir(self, name):
        try:
            self.ftp.mkd(name)
        except ftplib.error_perm as e:
            if 'File exists' in str(e):
                pass
            else:
                raise

    def send(self, stock, image_name, image):
        self.ftp.connect(host=self.host, port=self.port, timeout=60)
        self.ftp.login(self.login, self.password)
        self.create_dir('data')
        self.ftp.cwd('data/')
        self.create_dir(stock)
        self.ftp.cwd(stock)
        self.ftp.storbinary("STOR " + image_name, open(image, "rb"), 1024)
        self.ftp.quit()
