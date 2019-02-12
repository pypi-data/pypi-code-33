#!/usr/bin/env python3
"""gorep - Gor Grep Middleware.

Gor Middleware, 过滤掉不符合 PATTERN 的 Request/Response。

注意：只有 gor 使用了 --input-raw-track-response 参数时，才会收到 Response。
"""
import re
import sys
import time
from collections import namedtuple

import click

REQUEST_FIELDS = ['type', 'request_id', 'timestamp',
                  'method', 'path', 'version', 'headers', 'body']

RESPONSE_FIELDS = ['type', 'request_id', 'timestamp', 'latency',
                   'version', 'status_code', 'status_text', 'headers', 'body']


class Request(namedtuple('Request', REQUEST_FIELDS)):
    raw_line = ''


class Response(namedtuple('Response', RESPONSE_FIELDS)):
    raw_line = ''


def log(message):
    sys.stderr.write(time.strftime('%Y-%m-%d %H:%M:%S ' + message + '\n'))
    sys.stderr.flush()


def error(message):
    log('ERROR: ' + message)


def split_http_message(data: bytes):
    first_line, data = data.split(b'\r\n', 1)
    pos = data.index(b'\r\n\r\n') + 4
    headers = data[:pos]
    body = data[pos:]
    return first_line, headers, body


def parse_request(payload):
    start_line, headers, body = split_http_message(payload)
    start_line = start_line.decode('utf-8')
    method, path, version = start_line.split(' ', 2)
    return method, path, version, headers.decode('utf-8'), body


def parse_response(payload):
    status_line, headers, body = split_http_message(payload)
    status_line = status_line.decode('utf-8')
    version, status_code, status_text = status_line.split(' ', 2)
    return version, status_code, status_text, headers.decode('utf-8'), body


def parse_line(line):
    """分析消息
    """
    data = bytes.fromhex(line.rstrip())

    metadata, payload = data.split(b'\n', 1)
    message_type, *toks = metadata.decode('ascii').split(' ')
    message_type = int(message_type)

    if message_type == 1:
        message = Request(message_type, *toks, *parse_request(payload))
    elif message_type == 2:
        message = Response(message_type, *toks, *parse_response(payload))
    else:
        error('不支持的消息类型: %s, %s' % (message_type, line))
        return None

    message.raw_line = line
    return message


def match_message(message, pattern, fields):
    """匹配消息的指定字段"""
    for field_name in fields:
        if not hasattr(message, field_name):
            continue
        field_value = getattr(message, field_name)
        if isinstance(field_value, str):
            if re.search(pattern, field_value):
                return True
        elif isinstance(field_value, bytes):
            if re.search(pattern.encode('utf-8'), field_value):
                return True
        elif field_value:
            if re.search(pattern, str(field_value)):
                return True
    return False


def process_request(request, response, pattern, location, fields):
    """匹配 Request, Response，如果成功则输出
    """
    if location == 'request':
        m = match_message(request, pattern, fields)
    elif location == 'response':
        m = match_message(response, pattern, fields)
    else:
        m = match_message(request, pattern, fields) or match_message(response, pattern, fields)

    if m:
        sys.stdout.write(request.raw_line)
        sys.stdout.write(response.raw_line)
        sys.stdout.flush()


def process(pattern, location, fields):
    """处理 Gor 发送过来的数据
    """
    requests = {}

    for line in sys.stdin:
        message = parse_line(line)

        if isinstance(message, Request):
            requests[message.request_id] = message
        elif isinstance(message, Response):
            response = message
            request = requests.pop(message.request_id, None)
            if request:
                process_request(request, response, pattern, location, fields)
        else:
            pass


@click.command()
@click.option('-Q', '--request', is_flag=True, help='搜索 HTTP Request.')
@click.option('-S', '--response', is_flag=True, help='搜索 HTTP Response.')
@click.option('-m', '--method', is_flag=True, help='搜索 HTTP Method.')
@click.option('-p', '--path', is_flag=True, help='搜索 HTTP Path.')
@click.option('-v', '--version', is_flag=True, help='搜索 HTTP Version.')
@click.option('-c', '--status-code', is_flag=True, help='搜索 HTTP Status Code.')
@click.option('-t', '--status-text', is_flag=True, help='搜索 HTTP Status Text.')
@click.option('-h', '--headers', is_flag=True, help='搜索 HTTP Headers.')
@click.option('-b', '--body', is_flag=True, help='搜索 HTTP Body.')
@click.argument('pattern')
def cli(pattern, request, response, method, path, version, status_code, status_text, headers, body):
    """
    仅输出匹配 PATTERN 的消息。

    默认情况下搜索 Request 和 Response。如果需要仅搜索其中一个，则需要明确指定（-Q, -S）。

    默认情况下搜素 HTTP Headers 和 Body 字段。如果需要搜索其他字段，则需要明确指定，比如 -mphb 表示搜索 Method, Path, Headers, Body。

    典型用法：

    gor --input-raw-track-response --input-raw :80 --output-stdout --middleware "gorep something"
    """

    # location 表示搜索哪些消息
    if request and not response:
        location = 'request'
    elif response and not request:
        location = 'response'
    else:
        location = 'all'

    # fields 用来保存搜索哪些字段
    fields = []
    if any((method, path, version, status_code, status_text, headers, body)):
        method and fields.append('method')
        path and fields.append('path')
        version and fields.append('version')
        status_code and fields.append('status_code')
        status_text and fields.append('status_text')
        headers and fields.append('headers')
        body and fields.append('body')
    else:
        fields.append('headers')
        fields.append('body')

    process(pattern, location, fields)


if __name__ == '__main__':
    cli()
