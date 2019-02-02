#!/usr/bin/env python3
# coding=utf-8

import sys
from github_dir_tree.get_option import OptDict, get_option
import configparser
import os
import shutil
from github_dir_tree.generate_tree import Tree

if __name__ == '__main__':

    # init env
    Usage_description = "Usage: main.py [option] project_root"
    project_root = ""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    conf_temp = os.path.join(script_dir, "conf_temp")
    conf_file = ".github_dir_tree"

    # init options
    opt = OptDict()
    opt['c', 'comment'] = (
        True,
        "   -c --comment   search all files special comment and add it to tree"
    )
    opt['l', 'level'] = (
        0,
        "   -l --level   the distance between root and dir is level, only distance less than level will show"
    )
    opt['generate-conf'] = (
        True,
        "   --generate-conf  generate .github_dir_tree file if it not exists")
    opt['update-readme'] = (
        False, "   --update-readme  auto update/add tree to README.md")
    opt['filters'] = ([],
                      "   --update-readme  auto update/add tree to README.md")
    opt['start-line'] = (
        "# 目录结构",
        "   --start_line='str'  the first line that replace in readme")
    opt['end-line'] = (
        "---", "   --end_line='str'  the end line that replace in readme")
    opt['comment-match'] = (
        "// comment: ",
        "   --end_line='// comment: '  line in file whose prefix string is this will match"
    )
    opt['max-line-len'] = (
        120, "   --max-line-len=120  the max line nums in readme.md")
    opt['dir-description'] = (
        ".dir_desc", "   --max-line-len=120  the max line nums in readme.md")
    conf_file_opt = opt
    target_dir = get_option(sys.argv[1:], opt)

    # check project root is dir or not
    if len(target_dir) != 1:
        print(Usage_description)
        exit(1)
    else:
        if not os.path.exists(target_dir[0]) or not os.path.isdir(
                target_dir[0]):
            print("Project root not exists: " + target_dir[0])
            exit(2)
        else:
            project_root = os.path.abspath(target_dir[0])

    # auto generate .github_dir_tree configure file if it's not exists in project root
    conf_file_abs = os.path.join(project_root, conf_file)
    if not os.path.exists(conf_file_abs):
        if not os.path.exists(conf_temp):
            print("Error: {} not exists, please re-download script".format(
                conf_temp))
        shutil.copy(conf_temp, conf_file_abs)

    # load configure
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read(conf_file_abs, encoding="utf-8")

    # add configure into default options
    file_filters = []
    for i in config['ignore-files']:
        file_filters.append(i)
    conf_file_opt["filters"] = file_filters
    for i in config['common']:
        for key_tuple in conf_file_opt.keys():
            if i in key_tuple:
                conf_file_opt[key_tuple] = config['common'][i]
                break

    # conf option cover with user input option
    for opt_name in opt.get_input_option():
        conf_file_opt[opt_name] = opt[opt_name]

    tree = Tree(target_dir[0])
    tree.file_filter = conf_file_opt["filters"]
    tree.start_line = conf_file_opt["start-line"]
    tree.end_line = conf_file_opt["end-line"]
    tree.comment_match_key = conf_file_opt["comment-match"]
    tree.max_line_len = conf_file_opt["max-line-len"]
    tree.dir_desc = conf_file_opt["dir-description"]
    tree.level = conf_file_opt["level"]
    tree.print_tree()
