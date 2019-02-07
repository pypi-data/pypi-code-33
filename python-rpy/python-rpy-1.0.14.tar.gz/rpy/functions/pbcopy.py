# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import subprocess

from rpy.functions.encoding import force_bytes


def pbcopy(text):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(force_bytes(text))
    p.stdin.close()
    retcode = p.wait()
