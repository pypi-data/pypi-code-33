import json
import argparse


def deal_url(url, args, kwargs, express) -> str:
    if '?' not in url or args.params:
        return url
    url, string = url.split('?', 1)
    kwargs['params'] = dict(i.split('=', 1) for i in string.split('&'))
    express['params'] = 'params'
    return url


def get_method(args, express) -> str:
    if args.data_binary or args.data:
        if args.scrapy:
            express['method'] = "'POST'"
        return 'post'
    else:
        return 'get'


def cookie(string) -> dict:
    return dict(i.split('=', 1) for i in string.split('; ') if i)


def headers(args, kwargs) -> None:
    if not args.header:
        return
    items = dict(i.split(': ', 1) for i in args.header)
    items = {k.lower(): v for k, v in items.items()}
    if args.raw:
        kwargs['headers'] = items
    else:
        simplified = ['referer', 'user-agent', 'cookie']
        kwargs['headers'] = {k: items[k]
                             for k in items.keys() if k in simplified}
    if not args.cookies and 'cookie' in kwargs['headers']:
        kwargs['cookies'] = cookie(kwargs['headers'].pop('cookie'))


def data(args) -> dict:
    return dict(i.split('=', 1) for i in args.data.split('&'))


def body(args, kwargs, express) -> None:
    if args.data:
        if args.scrapy:
            kwargs['body'] = data()
            express['body'] = 'json.dumps(body)'
        else:
            kwargs['data'] = data()
            express['data'] = 'data'
    elif args.data_binary:
        if args.scrapy:
            kwargs['data'] = json.loads(args.data_binary)
            kwargs['headers']['Content-Type'] = 'application/json'
            express['body'] = 'json.dumps(data)'
        else:
            kwargs['data'] = json.loads(args.data_binary)
            express['json'] = 'data'


def main():
    parser = argparse.ArgumentParser(description='trans curl command')
    # parser.add_argument('curl', action='count', help='curl command string')
    parser.add_argument('-H', '--header', action='append')
    parser.add_argument('--data', action='store')
    parser.add_argument('--data-binary', action='store')
    parser.add_argument('--compressed', action='store_true')

    parser.add_argument('-R', '--raw', action='store_true',
                        help='do not simplify headers')
    parser.add_argument('-P', '--params', action='store_true',
                        help='do not formatter params')
    parser.add_argument('-C', '--cookies', action='store_true',
                        help='do not formatter cookies')
    parser.add_argument('-S', '--scrapy', action='store_true',
                        help='Format output scrapy style')
    args, not_known = parser.parse_known_args()
    url = ''
    for i in not_known:
        if i.startswith('http'):
            url = i
            break

    kwargs = {}
    express = {}
    headers(args, kwargs)
    body(args, kwargs, express)
    method = get_method(args, express)
    print()
    text = f'url = "{deal_url(url, args, kwargs, express)}"\n'
    for k, v in kwargs.items():
        text += f'{k} = {json.dumps(v, indent=4)}\n'

    if kwargs['headers']:
        express['headers'] = 'headers'

    if args.scrapy:
        if 'params' in kwargs:
            text += "url = f'{url}?' + '&'.join([f'{k}={v}' for k, v in params.items()])\n"
            express.pop('params')

        text += 'yield scrapy.Request(url, \n\t'
        temp = ', \n\t'.join([f'{k}={v}' for k, v in express.items()])
        if temp:
            text += f'{temp}, \n\t'
        text += 'callback=self.parse)'
    else:
        text += f'r = requests.{method}(url, \n\t'
        temp = ', \n\t'.join([f'{k}={v}' for k, v in express.items()])
        if temp:
            text += f'{temp}'
        text += ')'

    print(text)


if __name__ == '__main__':
    main()
