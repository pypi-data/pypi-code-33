#!/usr/local/bin/python3

import sys
import os
import json


def get_dir_name():
    return sys.argv[1]


def mkdir(name):
    try:
        os.mkdir(name)
    except FileExistsError as e:
        print('dir is exist')


def gen_files(dir_name):
    with open('{}/index.vue'.format(dir_name), 'w') as fv:
        fv.write('<template></template> \n')
        fv.write('<script></script> \n')
        fv.write('<style scoped></style')

    with open('{}/main.js'.format(dir_name), 'w') as fm:
        fm.write("import Vue from 'vue'\n")
        fm.write("import App from './index'\n \n")
        fm.write("const app = new Vue(App) \n")
        fm.write("app.$mount()")

    with open('{}/main.json'.format(dir_name), 'w') as fjson:
        json_str = json.dumps({
            "navigationBarTitleText": "新增订单"
        }, indent=4, ensure_ascii=False)
        fjson.write(json_str)


def main():
    dir_name = get_dir_name()
    mkdir(dir_name)
    gen_files(dir_name)


if __name__ == '__main__':
    main()
