#!/usr/bin/env python3

import os
import sys
import json
import pathlib
import attr


app_dir = os.environ.get("GETUP_APP_PATH")
if app_dir:
    APP_DIR = pathlib.Path(app_dir)
    sys.path.append(str(APP_DIR.resolve()))
    sys.path.append(str(APP_DIR.resolve().parent))

cur_dir = os.environ.get("PWD")
if cur_dir:
    CUR_DIR = pathlib.Path(cur_dir)
    sys.path.append(str(CUR_DIR.resolve()))
    sys.path.append(str(CUR_DIR.resolve().parent))


def main():

    from django.core.management import execute_from_command_line

    # Delegate to Django management
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
