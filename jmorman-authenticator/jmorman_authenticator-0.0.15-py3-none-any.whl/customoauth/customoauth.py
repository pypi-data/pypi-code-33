from oauthenticator.azuread import AzureAdOAuthenticator
from tornado import gen

class AzureAdOAuthenticatorExtended(AzureAdOAuthenticator):
    @gen.coroutine
    def authenticate(self, handler, data=None):
        code = handler.get_argument("code")
        http_client = AsyncHTTPClient()

        params = dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type='authorization_code',
            code=code,
            resource=self.client_id,
            redirect_uri=self.get_callback_url(handler))

        data = urllib.parse.urlencode(
            params, doseq=True, encoding='utf-8', safe='=')

        url = azure_token_url_for(self.get_tenant())

        headers = {
            'Content-Type':
            'application/x-www-form-urlencoded; ; charset=UTF-8"'
        }
        req = HTTPRequest(
            url,
            method="POST",
            headers=headers,
            body=data  # Body is required for a POST...
        )

        resp = yield http_client.fetch(req)
        s = resp.body.decode('utf8', 'replace')
        resp_json = json.loads(s)
        
        # app_log.info("Response %s", resp_json)
        access_token = resp_json['access_token']

        id_token = resp_json['id_token']
        decoded = jwt.decode(id_token, verify=False)

        userdict = {"name": decoded['name']}
        userdict["auth_state"] = auth_state = {}
        auth_state['access_token'] = access_token
        auth_state['json'] = s
        # results in a decoded JWT for the user data
        auth_state['user'] = decoded

        return userdict


    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # auth_state not enabled
            return
        spawner.environment['ACCESS_TOKEN'] = auth_state['access_token']
        spawner.environment['ACCESS_TOKEN_JSON'] = auth_state['json']
        spawner.environment['JUPYTERHUB_CRYPT_KEY'] = "8cf4fbafda2a59b63a307bba1a41295f18e566cfd8d103a1bacc29b38e00455e"
    def foo():
        return ""
