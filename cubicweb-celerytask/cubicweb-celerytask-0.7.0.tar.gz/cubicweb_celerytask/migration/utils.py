# -*- coding: utf-8 -*-
# copyright 2018 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gzip

from logilab.common.shellutils import ProgressBar
from cw_celerytask_helpers.filelogger import get_log_filename
from cw_celerytask_helpers.redislogger import get_task_logs, flush_task_logs


def migrate_task_logs_to_bfss(cnx):
    """Migrate logs from redis and from database to logs files in
    celerytask-log-dir"""
    to_flush = set()
    rset = cnx.execute('Any X, T WHERE X is CeleryTask, X task_id T')
    pb = ProgressBar(len(rset))
    for eid, task_id in rset:
        entity = cnx.entity_from_eid(eid)
        logs = get_task_logs(task_id)
        if logs is not None:
            to_flush.add(task_id)
        else:
            if entity.task_logs is not None:
                logs = entity.task_logs.read()
        if logs is not None:
            fname = get_log_filename(task_id)
            with gzip.open(fname, 'wb') as f:
                f.write(logs)
        pb.update()
    cnx.commit()
    for task_id in to_flush:
        flush_task_logs(task_id)
