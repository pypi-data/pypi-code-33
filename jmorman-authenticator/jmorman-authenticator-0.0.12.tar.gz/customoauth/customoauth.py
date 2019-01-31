from oauthenticator.azuread import AzureAdOAuthenticator
from tornado import gen

class AzureAdOAuthenticatorExtended(AzureAdOAuthenticator):
    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # auth_state not enabled
            return
        spawner.environment['ACCESS_TOKEN'] = auth_state['access_token']
        spawner.environment['JUPYTERHUB_CRYPT_KEY'] = "8cf4fbafda2a59b63a307bba1a41295f18e566cfd8d103a1bacc29b38e00455e"
    def foo():
        return ""
