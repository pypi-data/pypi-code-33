import requests
from syncloudlib.integration.ssh import run_scp, run_ssh

class Device():

    def __init__(self, main_domain, device_host, domain, device_user, device_password, redirect_user, redirect_password, ssh_env_vars):
        self.main_domain = main_domain
        self.device_host = device_host
        self.domain = domain
        self.device_user = device_user
        self.device_password = device_password
        self.redirect_user = redirect_user
        self.redirect_password = redirect_password
        self.ssh_env_vars = ssh_env_vars
        self.ssh_password = 'syncloud'
        
    def activate(self):

        response = requests.post('http://{0}:81/rest/activate'.format(self.device_host),
                                 data={'main_domain': self.main_domain,
                                       'redirect_email': self.redirect_user,
                                       'redirect_password': self.redirect_password,
                                       'user_domain': self.domain,
                                       'device_username': self.device_user,
                                       'device_password': self.device_password})
        if response.status_code == 200:
            self.ssh_password = self.device_password
        return response

    def login(self, retries=5):
    
        retry = 0
        while True:
            try:
                session = requests.session()
                session.post('https://{0}/rest/login'.format(self.device_host), verify=False, data={'name': self.device_user, 'password': self.device_password})
                assert session.get('https://{0}/rest/user'.format(self.device_host), verify=False, allow_redirects=False).status_code == 200
                return session
            except Exception, e:
                retry += 1
                if retry > retries:
                    raise e
                print(e.message)
                print('retry {0} of {1}'.format(retry, retries))

    def run_ssh(self, cmd):
        return run_ssh(self.device_host, cmd, password=self.ssh_password, env_vars=self.ssh_env_vars)

        