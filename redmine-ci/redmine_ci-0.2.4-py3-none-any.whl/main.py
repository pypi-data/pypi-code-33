#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info.major == 3:
    from redmineci import redmineci
else:
    import redmineci


def run():
    redmineci.main(sys.argv[1:])


if __name__ == '__main__':
    run()
