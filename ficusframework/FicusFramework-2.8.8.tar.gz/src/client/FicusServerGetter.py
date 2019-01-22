import random
import threading

import requests

from init.app import ec


class FicusServerGetter(object):
    """
     Ficus服务的地址获取类,通过这个单例的类 可以获取到ficus服务的地址
    """

    def __init__(self, server_id='sobeyficus'):
        self.server_id = server_id
        self._server_url = None
        self.mutex = threading.Lock()

    @property
    def server_url(self):
        if self._server_url is None:
            # 如果_server_url为空,那么就尝试去获取一次服务地址,有可能获取出来还是空.那么这个时候就说明是服务一个实例都没得
            self.change_new_server()

        return self._server_url

    def change_new_server(self):

        """
        切换服务的地址
        :return:
        """
        if self.mutex.acquire(60):  # 这里加了一个互斥锁
            try:
                if self._server_url and self._check_url_available(self._server_url):
                    # 说明是有效的url,不替换了
                    return

                # 说明确实是连不通的
                self._server_url = self._get_usable_server_url()
            finally:
                self.mutex.release()

    def _get_usable_server_url(self):
        """
        获取真正可用的服务的url
        :return:
        """

        # 逻辑是这样的,从eureka上找到 ficus服务的地址,然后从中随便找一个
        urls = ec.get_instance_urls(self.server_id)

        return self._get_one_url(urls)

    def _get_one_url(self, urls):
        """
        从多个url里面随机的找一个可用的url返回
        :param urls:
        :return:
        """

        while urls:
            url = urls[random.randint(0, len(urls) - 1)]
            if url == "":
                # 如果是空串 就不要
                urls.remove(url)
                continue

            if self._check_url_available(url):
                # 说明url可用,那么就返回这个了
                return url

            # 说明这个url不可用,那么就去掉
            urls.remove(url)
            # 然后开始下一次循环

        # 说明没有可用的地址
        return None

    def _check_url_available(self, url):
        try:
            r = requests.get(f"{url}actuator/info")
            r.raise_for_status()
            #  说明是连得通的,就不重新获取了
            return True
        except requests.exceptions.RequestException:
            pass
        return False


ficusServerGetter = FicusServerGetter()
