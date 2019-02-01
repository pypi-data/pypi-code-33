# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 12:01:50 2019

@author: hus20664877
"""

import gaitutils
import itertools
from gaitutils import videos, sessionutils, cfg


session = gaitutils.nexus.get_sessionpath()

files = sessionutils.get_session_enfs(session)
#enfs, tags = zip(*sessionutils._filter_by_tags(files, '1', return_tag=True))

files = sessionutils.get_c3ds(session, tags=cfg.eclipse.tags, trial_type='dynamic')

print list(files)



