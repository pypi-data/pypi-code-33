# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gevent_tasks']

package_data = \
{'': ['*']}

install_requires = \
['crontab>=0.22.4,<0.23.0', 'gevent>=1.4.0,<2.0.0']

setup_kwargs = {
    'name': 'gevent-tasks',
    'version': '0.3.1',
    'description': 'Background task management using gevent and green threads.',
    'long_description': '# gevent-tasks\n\n[![pypi](https://img.shields.io/pypi/v/gevent-tasks.svg?style=flat)](https://pypi.python.org/pypi/gevent-tasks)\n[![docs](https://readthedocs.org/projects/gevent-tasks/badge/?version=latest)](http://gevent-tasks.readthedocs.io/en/latest/)\n[![MIT License](https://img.shields.io/github/license/blakev/gevent-tasks.svg?style=flat)](https://github.com/blakev/gevent-tasks/blob/master/LICENSE)\n\n\nBackground task manager using Gevent and Green threads.\n\n- Check out [the documentation](http://gevent-tasks.readthedocs.io/en/latest/).\n- Learn about [Gevent]().\n\nThis library is designed to allow a developer to run arbitrary "tasks" as background\nthreads on a fixed/normalized interval.  Each task is a wrapped\ncallable that takes at least one parameter `task`, a reference to itself. Timings\nand related metadata can be accessed via the `task` value as well as the ability\nto stop and reschedule itself for future events.\n\n\n`TaskManager` has a `TaskPool` that runs `Tasks`.\n\n## Installation\n\nThe latest version from pypi,\n\n```bash\n$ pip install gevent-tasks\n```\n\nThe latest development version from source,\n\n```bash\n$ pip install git+git@github.com:blakev/gevent-tasks.git@develop\n```\n\n\n\n## Examples\n\nA classic example,\n\n```python\n# print our system uptime every minute, indefinitely\n\nfrom datetime import timedelta\nfrom gevent_tasks import TaskManager, cron\n\nmanage = TaskManager()\n\n@manage.task(interval=cron(\'* * * * *\'))\ndef system_uptime(task):\n    with open(\'/proc/uptime\', \'r\') as f:\n        uptime_seconds = float(f.readline().split()[0])\n        uptime = str(timedelta(seconds=uptime_seconds))\n    print(uptime)\n\nmanage.forever(stop_after_exc=False)\n```\n\nContrived example,\n\n```python\nfrom gevent.monkey import patch_all\npatch_all()\n\nfrom gevent_tasks import Task, TaskManager, TaskPool\n\nfrom myapp.tasks import check_websockets, check_uptime, check_health\n\npool = TaskPool(size=25)\nmanager = TaskManager(pool=pool)\n\nmanager.add_many(\n    Task(\'WebsocketHealth\', check_websockets, interval=7.5),\n    Task(\'ApplicationHealth\', check_uptime, interval=30.0),\n    Task(\'SystemHealth\', check_health, args=(\'localhost\',), interval=2.5)\n)\nmanager.start_all()\n..\n..\nhttp_server.serve_forever()\n```\n\nUsing the [`parse-crontab`](https://github.com/josiahcarlson/parse-crontab)\n module we\'re able to define intervals with cron syntax,\n\n```python\nfrom gevent_tasks import Task, cron\n..\n..\nTask(\'ShowCharts\', show_charts, interval=cron(\'* * * * *\'), timeout=30.0)\n```\n\nThe manager instance can also be used to register tasks via decorator. Calling \n`TaskManager.forever()` will block the code until there are no longer scheduled tasks or until an `Exception` \nis thrown inside one of the running Tasks.\n\n```python\nmanage = TaskManager()\n\n@manage.task(interval=cron(\'* * * * *\'))\ndef every_minute(task, *args):\n    print(\'hi\', args, task, task.timing)\n\nmanage.forever()\n```\n\nYou can also reference the previous return value, allowing tasks to build on\nthemselves over time without human / programmatic interaction.\n\n```python\n@manage.task(interval=1)\ndef random_number(task):\n    num = random.randint(0, 100)\n    print(task.value, num)\n    return num\n\n.. output ..\n\nNone 51\n51 50\n50 88\n88 26\n```\n\n### Attribution\n\nThis module relies primarily on the [`gevent`](http://www.gevent.org/index.html) \nproject for all its core functionality.\n\n### MIT License\n\nCopyright (c) 2017 Blake VandeMerwe\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n',
    'author': 'Blake VandeMerwe',
    'author_email': 'blakev@null.net',
    'url': 'https://github.com/blakev/gevent-tasks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
