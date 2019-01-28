# coding=utf-8
# https://blog.ixxoo.me/argparse.html
# https://docs.python.org/2/library/argparse.html#module-argparse 有了这篇文章一切就搞定了

"""
author: wangssuyan@baidu.com
time: 2019-01-25
"""

import pprint
import argparse
import ku_dot
import ku_img_found

"""
错误总结：

 case1：命令程序需要一个参数，却未指定
➜  tools python3 ku.py
usage: ku.py [-h] dot
ku.py: error: the following arguments are required: dot

➜  tools python3 ku.py foo
参数错误，命令行程序没有这个参数
ku.py: error: unrecognized arguments: foo

参数写错了，应该是 --verbose 而不是 -verbose
➜  tools python3 ku.py 11 111 111 11111 -verbose
usage: ku.py [-h] [-v] dot dot_header dot_source_path dot_dest_path
ku.py: error: argument -v/--verbose: ignored explicit argument 'erbose'
➜  tools python3 ku.py 11 111 111 11111 --verbose

参数的值错误，只能为 0，1，2
➜  tools python3 log.py 4 -v 3
usage: log.py [-h] [-v {0,1,2}] square
log.py: error: argument -v/--verbosity: invalid choice: 3 (choose from 0, 1, 2)
"""


# prog 参数为命令行工具的名字
parser = argparse.ArgumentParser(description="ku 是百度文库iOS命令行工具，只为提升你的效率！", prog="ku")

# 命令执行的函数
# 日志打点工具
def dot(args):
    """
    usage: ku dot [-h] dot_header dot_source_path dot_dest_path

    positional arguments:
    dot_header       用来解析打点文件，打点文件有固定的格式
    dot_source_path  指定要解析文件的路径，文件必须为CSV文件
    """

    # ku_dot.excute('/Users/wangsuyan/Desktop/baidu/tools/upload_answer.csv')
    ku_dot.excute(args.verbose, args.dot_header, args.dot_source_path)

def img(args):
    print("🔍 正在查找名为 %s 的图片......\n"%(args.img_name))
    ressult = set()
    ku_img_found.find_image(args.img_path, args.img_name, ressult)
    if len(ressult) > 0:
        print("🔍  共找到了 %s 张图片"%(len(ressult)))
    else:
        print("🔍  未找到你要查找的图")

"""
文库打点日志工具，用来解析日志并自动生成打点代码片段

命令执行方法:

ku dot uploadAnswer ./Desktop/wsy.log ./Desktop/result.log 

帮助信息，自动生成的
ku.py -h


"""

"""
添加参数，执行命令时就需要使用这个参数，并指定输入值的类型为字符串
执行 python3 ku.py 1111，args.dot 的值就为 1111
"""

# 执行子，命令时可以找到对应的名字
subparsers = parser.add_subparsers(help="subcommands", dest='subparser_name')

# 打点工具 ===================
dot_parser = subparsers.add_parser('dot', help="自动生成打点代码工具")
# parser.add_argument('dot', help="解析打点日志工具", type=str)
dot_parser.add_argument('dot_header', help="用来解析打点文件，打点文件有固定的格式", type=str)
dot_parser.add_argument('dot_source_path', help="指定要解析文件的路径，文件必须为CSV文件", type=str)
# dot_parser.add_argument('dot_dest_path', help="指定解析文件完成后保存的路径", type=str)
dot_parser.set_defaults(func=dot)


# image 工具 ===================
img_parser = subparsers.add_parser('img', help="根据图片名，找到图片在项目的位置")
img_parser.add_argument('img_path', help="项目地址")
img_parser.add_argument('img_name', help="项目地址")
img_parser.set_defaults(func=img)

# 全局配置 ========================
# ➜  tools python3 ku.py 11 111 111 11111 -verbose 1 可选参数-verbose后必须添加值
# parser.add_argument('--verbose', help="显示帮助信息")

# # ➜  tools python3 ku.py 11 111 111 11111 -verbose 可选参数-verbose后不需要添加值，如果指定 -verbose
# parser.add_argument('--verbose', help="显示帮助信息", action="store_true")
parser.add_argument('-v', "--verbose", help="显示更多信息", action="store_true")

# 解析命令
args = parser.parse_args()
# 调用命令中的函数
args.func(args)

