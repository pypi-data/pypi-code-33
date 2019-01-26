import paramiko

__all__ = ["LiunxCmd"]

class LiunxCmd(object):
    r'''
    本模块命令，必须配置SSH免密登录方可使用。
    '''
    def __init__(self, host):
        self.hostName = host
        self.uname = 'root'
        
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())        
    
    def rCmd(self, comend, getResult = True):
        keyPath = r"/Users/bernie/Library/Mobile Documents/com~apple~CloudDocs/Key/id_rsa"
        #使用目标的私钥来登录
        private_key = paramiko.RSAKey.from_private_key_file(keyPath)   
        
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.ssh.connect(hostname=self.hostName, 
                    port=22,
                    username=self.uname, 
                    pkey=private_key)
        
        stdin, stdout, stderr = self.ssh.exec_command(comend)    
        
        if getResult:
            result = stdout.read()
            if not result:
                result = stderr.read()
            return(result.decode())

    def __delete__(self):
        self.ssh.close()
        
    def __call__(self, comend):
        result = self.rCmd(comend)
        print(result)