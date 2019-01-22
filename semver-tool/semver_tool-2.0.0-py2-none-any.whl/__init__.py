from .__version__ import version as __version__

import subprocess as sp
import datetime
import logging
import re
import os

log = logging.getLogger()


class GitSemVer(object):
    def __init__(self, root, rc_prefix='rc'):
        self.info = {
            "major": 0,
            "minor": 1,
            "patch": 0,
            "rc": 0,
            "rc_prefix": rc_prefix,
            "build": None,
            "dirty": None,
        }
        os.chdir(root)
        ver = sp.check_output('git describe --long --dirty',
                              shell=True).strip()
        if ver.endswith('-dirty'):
            ver = ver[:-6]
            self.info['dirty'] = 'd{time:%Y%m%d}'.format(time=datetime.datetime.now())

        ver = ver.rsplit('-', 2)
        tagre = 'v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
        m = re.match(tagre, ver[0])
        if not m:
            log.error("%s is not SemVer tag, eg M.N.P", ver[0])
            exit(1)
        mnp = m.groupdict()
        for i, e in mnp.iteritems():
            mnp[i] = int(e)
        self.info.update(mnp)
        self.info['build'] = ver[2]
        self.info['rc'] = int(ver[1])
        if self.info['dirty']:
            self.info['rc'] += 1
        if self.info['rc']:
            self.info['patch'] += 1

    def is_exact_tag(self):
        return not self.info['rc']

    def format(self, fmt='MNPRBD'):
        ret = ''
        ver = []
        if 'M' in fmt:
            ver.append('%(major)s')
        if 'N' in fmt:
            ver.append('%(minor)s')
        if 'P' in fmt:
            ver.append('%(patch)s')
        ver = '.'.join(ver)
        ret += ver
        if 'R' in fmt:
            if self.info['rc']:
                ret += '-%(rc_prefix)s%(rc)s'
        build = []
        if 'B' in fmt:
            build.append('%(build)s')
        if 'D' in fmt:
            if self.info['dirty']:
                build.append('%(dirty)s')
        if build:
            ret += '+' + '.'.join(build)
        return ret % self.info
