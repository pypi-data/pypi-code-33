# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018年8月23日 14:26:49
from . import file_operation
from .file_operation import absdir
from .file_operation import abspath
from .file_operation import append_to_file
from .file_operation import concat_path
from .file_operation import cp
from .file_operation import create_if_not_exist_path
from .file_operation import create_if_not_exists
from .file_operation import dirname
from .file_operation import file_append
from .file_operation import file_exists
from .file_operation import file_md5sum
from .file_operation import format_path
from .file_operation import get_file_lines
from .file_operation import get_file_size
from .file_operation import is_abspath
from .file_operation import load_file_contents
from .file_operation import mkdtemp
from .file_operation import refine_path
from .file_operation import remove_file
from .file_operation import write_file_contents
from .file_operation import write_iterable_as_lines
from .file_operation import write_json_contents
from .file_operation import write_line
from .file_operation import write_pid
from ..compat import happy_move_functions

happy_move_functions(file_operation, abspath, absdir, dirname, file_exists, get_file_size,
                     get_file_lines, remove_file, create_if_not_exist_path,
                     create_if_not_exists, concat_path, cp, format_path,
                     is_abspath, refine_path, file_md5sum, file_append,
                     append_to_file, write_line, write_pid, write_json_contents,
                     write_file_contents, write_iterable_as_lines,
                     load_file_contents, mkdtemp)
