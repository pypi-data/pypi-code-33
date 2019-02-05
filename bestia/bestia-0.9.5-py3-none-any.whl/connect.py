from os import system
from subprocess import check_output, CalledProcessError
from uuid import UUID
import requests
from time import sleep

from bestia.output import echo
from bestia.iterate import random_unique_items_from_list

_WEB_BROWSERS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', # chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0', # firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393', # Edge
    'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko', # IE11
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 Vivaldi/2.2.1388.37', # Vivaldi
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15', # Safari
]

def http_get(url, retries=3, verbose=False, browser='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'):
    try:
        headers = {
            'User-Agent': browser,
            # 'Referer': referer,
            # 'Cookie': '__cfduid=dc007f70cc6e84fe5cf05b13786ac361536178218; _ga=GA1.2.1741958857.1512378240; _gid=GA1.2.1955541911.1536178240; ppu_main_b1f57639c83dbef948eefa8b64183e1e=1; ppu_sub_b1f57639c83dbef9488abc6b64183e1e=1; _gat=1'
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            html = r.text
            if type(html) != str:
                if verbose:
                    echo('http request returned {} insetad of <str>'.format(type(html)), 'red')
                return False
            return html
        else:
            return False
    except requests.exceptions.ConnectionError:
        if retries < 1:
            if verbose:
                echo('Unable to connect', 'red')
            return False
        else:
            if verbose:
                echo('No connection, {} attempts left...'.format(retries), 'red')
            sleep(5)
            http_get(url, retries=retries-1, verbose=verbose, browser=browser)


def __command_output(*args):
    output = None
    try:
        output = check_output(args)
        if output:
            output = output.decode().strip()
    except CalledProcessError:
        pass
    finally:
        return output


if __name__ == '__main__':
    # r = bla('http://localhost/sam/target.php?do=login')

    # r = bla('http://releases.ubuntu.com/18.04.1.0/ubuntu-18.04.1.0-live-server-amd64.iso?_ga=2.37110947.2086347288.1548630714-895763213.1548630714')

    # r = bla('https://dl2018.sammobile.com/premium/NV1aQy8rLD1WLDc8QDcoQUdYLzwuMEcqNyVUKDU8JFoOARlJUyA5RSRbVkc1UlNGQF9aQFlJThwXGwBNSVlbRUVbUEBa/A530FXXU3BRK3_A530FOGC3BRK1_FTM.zip')

    # r = __command_output('hostname','')

    # echo(r, 'red')