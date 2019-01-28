#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 jack <jack@iOSTdeMacBook-Pro.local>
#
# Distributed under terms of the MIT license.

"""
test
"""

import boto3

from idevops import aws
from idevops.utils import *

name = 'example'


def main():
    from idevops.aws import get_all
    import boto3

    ecs = get_all("example", all_region=True)
    for i in ecs:
        i.terminate()


if __name__ == "__main__":
    main()
