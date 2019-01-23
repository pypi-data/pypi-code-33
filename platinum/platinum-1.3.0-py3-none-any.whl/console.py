from argparse import ArgumentParser

from .user_agent import generate_user_agent


def script_gua():
    parser = ArgumentParser()
    parser.add_argument('-o', '--os')
    parser.add_argument('-n', '--navigator')
    parser.add_argument('-d', '--device-type')
    opts = parser.parse_args()
    gua = generate_user_agent(os=opts.os,
                                navigator=opts.navigator,
                                device_type=opts.device_type)
    print(gua)
