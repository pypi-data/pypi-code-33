# coding=utf-8 

import os
import re
import csv
import sys

LOG_DEST_DOT = '/Users/wangsuyan/Desktop/dot.txt'
LOG_DEST_CODE = '/Users/wangsuyan/Desktop/code.txt'

# 桌面打点文件
def dot_path():
    return os.path.join(os.path.expanduser("~"), 'Desktop/ku_dot.txt')

# 桌面代码文件
def code_path():
    return os.path.join(os.path.expanduser("~"), 'Desktop/ku_code.txt')

def is_num(text):
    regx = '[^0-9]'
    matchs = re.findall(regx, text)
    return len(matchs) == 0

def excute(is_verbose, header, source_path):
    if is_verbose:
        print('🐶 begin parse csv file ......')
    with open(source_path, 'rU') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        log_str_file = open(dot_path(), 'w')
        log_code_file = open(code_path(), 'w')
        for row in csv_reader:
            if len(row) < 2:
                if is_verbose:
                    print('❌ find a row is error, length than 2')
                continue
            if not is_num(row[1]):
                if is_verbose:
                    print('❌ is not a valid item: ' + row[1])
                continue

            # static NSString *const LOG_COOKIE_LOSE_5666 = @"5666";
            # item_value = "static NSString *const" + ' ' + LOG_HEADER + row[1] + ' = ' +  row[1] + ';'
            log_name = "%s_%s"%(header, row[1])
            item_value = "static NSString *const %s = @\"%s\";"%(log_name, row[1])
            item_comment = "/*** " + row[0]
            if len(row)>2:
                item_comment += row[2]
            item_comment += ' */'
            # print item_comment.decode('gb2312')
            # print item_value
            log_str_file.writelines([item_comment, '\n', item_value, '\n\n'])
            if len(row) > 2 and len(row[2]) > 0:
                log_code = "[BDELogManager logActionWithId:%s params:@{@\"type\" : @(1)}];"%(log_name)
            else:
                log_code = "[BDELogManager logActionWithId:%s];"%(log_name)
            log_code_file.writelines([log_code, '\n\n'])

        print('✅ parse successful, code saved to %s, dot saved to %s'%(code_path(), dot_path()))

