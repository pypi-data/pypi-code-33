'''What is my external IP address?'''

import requests


def external_ip():
    data = requests.get('http://ip-api.com/json?lang=zh-CN').json()
    ip = data['query']
    country = data['country']
    region = data['regionName']
    print('%s %s %s' % (ip, country, region))


if __name__ == '__main__':
    external_ip()
