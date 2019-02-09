# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['rcache']
install_requires = \
['redis>=3.1,<4.0']

setup_kwargs = {
    'name': 'rcache',
    'version': '1.0.0',
    'description': 'Redis memoize cache',
    'long_description': '# rcache.py\n\n[![pipeline status](https://gitlab.com/the_speedball/redis.cache.py/badges/master/pipeline.svg)](https://gitlab.com/the_speedball/redis.cache.py/commits/master)\n\n# What is it\n\nrcache.py is a cache and works on redis so it is suitable for multi threaded and multi process applications.\nIt has been inspired and based on `cache.py` library https://github.com/bwasti/cache.py\n\n# Usage\n\nTo use the file, `import rcache` and annotate functions with `@rcache.rcache()`.\n\n```python\nimport rcache\n\n@rcache.rcache()\ndef expensive_func(arg, kwarg=None):\n  # Expensive stuff here\n  return arg\n\n```\n\nThe `@rcache.rcache()` function can take multiple arguments.\n\n- `@rcache.rcache(timeout=20)` - Only caches the function for 20 seconds.\n- `@rcache.rcache(url="http://other_redis:6379")` - Saves cache to specified Redis url (defaults to `http://localhost:6379`)\n- `@rcache.rcache(key=rcache.ARGS[KWARGS,NONE])` - Check against args, kwargs or neither of them when doing a cache lookup.\n\n# How it works\n\n`rcache.py` queries `redis` and checks against the name, arguments and hash of a function\'s source\nto decide if the function has been run before.  If it has it returns the cached result immediately.\n\n',
    'author': 'Michal Klich',
    'author_email': 'michal@michalklich.com',
    'url': 'https://gitlab.com/the_speedball/redis.cache.py',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
