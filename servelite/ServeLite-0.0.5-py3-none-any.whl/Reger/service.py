

from Service.service import baseService
from Reger.config import default
from Config import JSONKeeper
from Reger.models import Servers, get_session

class Reger(baseService):
    def __init__(self):
        baseService.__init__(self, __name__, default)

        self.info = JSONKeeper('info.json')
        self.info['reg_pubkey'] = self.config['pubkey']

        from Reger.app.api import api
        self.register_blueprint(api)

        from Reger.app.auth import auth
        self.register_blueprint(auth)

    @staticmethod
    def get_server(server_hash):
        """
        通过server_hash找到一个server表的行，避免每次都初始化session
        :param server_hash:
        :rtype: Servers
        :return:
        """
        session = get_session()
        server = session.query(Servers).filter_by(hash=server_hash).first()
        session.close()
        return server


reger = Reger()
if __name__ == '__main__':
    reger.run(port=8888, debug=True)
