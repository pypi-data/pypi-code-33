#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

swiftlint_rule_content = '''
whitelist_rules:
  - empty_count
  - generic_type_name
  - array_init
  - closure_spacing
  - vertical_whitespace
  - compiler_protocol_init
  - force_cast
  - comma
  - void_return
  - closing_brace
  - block_based_kvo
  - colon
  - fatal_error_message
  - force_unwrapping
  - force_try
'''

commit_msg_enter = '''#!/usr/bin/env python
import sys
from supercommit.index import run_commit_msg
run_commit_msg(sys.argv[1])
'''

def excute_swiftlint_lint():
    return excute_core_swiftlint('swiftlint lint --use-script-input-files --reporter "json" --config ~/.supercommit/.swiftlint-rule.yml')

def excute_swiftlint_clip():
    return excute_core_swiftlint('swiftlint autocorrect --use-script-input-files')

def excute_core_swiftlint(statement):
    result = os.popen("""#! /bin/bash
command -v swiftlint >/dev/null 2>&1 || { echo >&2 "请先安装Swiftlint"; exit 1; }
temp_file=$(mktemp)
git ls-files -m  | grep ".swift" > ${temp_file}
git diff --name-only --cached  | grep ".swift" >> ${temp_file}
counter=0
for f in `sort ${temp_file} | uniq`
do
    export SCRIPT_INPUT_FILE_${counter}=${f}
    counter=`expr $counter + 1`
done
if (( counter > 0 )); then
    export SCRIPT_INPUT_FILE_COUNT=${counter}
    %s
fi
    """ % statement).read()
    return result