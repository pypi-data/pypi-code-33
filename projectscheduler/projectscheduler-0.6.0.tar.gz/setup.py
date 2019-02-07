# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['projectscheduler']

package_data = \
{'': ['*']}

install_requires = \
['svgwrite>=1.2,<2.0']

entry_points = \
{'console_scripts': ['schedule = projectscheduler.plot:main']}

setup_kwargs = {
    'name': 'projectscheduler',
    'version': '0.6.0',
    'description': 'Simple project scheduling tool',
    'long_description': 'Simple Scheduler\n================\nI occasionally do freelancing work and needed a simple way to build\nout a notional schedule based on estimated task length. There are many\nGantt chart builders out there, but they typically require choosing\nstart dates for each individual task. In addition, all the online builders\nmake you enter the tasks in their own interface (clunky), cost money after\nsome short trial (too much overhead), or don\'t offer an easy way to share\nthe schedule with someone else.\n\nSimple Scheduler asks for just a CSV of tasks, how long they\'ll take,\nwho is going to work on each task, and any dependencies of each task.\nFrom there it spits out an SVG with each task scheduled based on the rules:\n\n- Tasks are scheduled in the order they are in the CSV.\n- A resource (person) can only perform one task at a time.\n- A task\'s dependencies must be complete before it can begin.\n- (by default) No work is done on weekends.\n\nInstallation\n============\n\n.. code:: shell\n\n   pip install projectscheduler\n\nUsage\n=====\n\nCreate a CSV with your tasks in the format:\n\n===================  ======== ========== =========================\nTask                 Duration Resources  Dependency\n===================  ======== ========== =========================\nName of task 1       6        Person 1\nSome other task      3        Person 1\nSome other task 3    12       Person 2   Name of task 1\n===================  ======== ========== =========================\n\nWhere duration is given in days. Multiple resources can be separated by a "/". (I.E, "Person1/Person2").\n\nAn `example csv`_ can found found in the repository. It builds into:\n\n.. image:: https://raw.githubusercontent.com/traherom/simple-scheduler/master/example/example.png\n        :alt: Example output\n        :width: 100%\n        :align: center\n\n(We are displaying the PNG here so that GitHub displays it. The SVG_ is what was actually produced.)\n\n.. _SVG: https://raw.githubusercontent.com/traherom/simple-scheduler/master/example/example.svg\n.. _example csv: https://raw.githubusercontent.com/traherom/simple-scheduler/master/example/example.csv\n\n.. code:: shell\n\n   schedule input.csv output.svg\n\nTODO\n====\n1. Multiple dependencies for a task?\n\nCredits\n=======\nPython-gantt_ was the original inspiration for this project. I originally built the scheduler around it,\nbut didn\'t like certain aspects of the API. This tool uses the rendering\ncode from that project.\n\n.. _Python-gantt: http://xael.org/pages/python-gantt-en.html\n',
    'author': 'Ryan Morehart',
    'author_email': 'ryan@moreharts.com',
    'url': 'https://github.com/traherom/simple-scheduler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
