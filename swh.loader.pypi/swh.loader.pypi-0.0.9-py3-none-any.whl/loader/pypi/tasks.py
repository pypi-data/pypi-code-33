# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from celery import current_app as app

from .loader import PyPILoader


@app.task(name=__name__ + '.LoadPyPI')
def load_pypi(project_name, project_url, project_metadata_url=None):
    return PyPILoader().load(project_name,
                             project_url,
                             project_metadata_url=project_metadata_url)
