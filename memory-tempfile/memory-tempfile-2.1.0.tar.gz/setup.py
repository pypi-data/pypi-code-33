# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['memory_tempfile']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'memory-tempfile',
    'version': '2.1.0',
    'description': 'Helper functions to identify and use paths on the OS (Linux-only for now) where RAM-based tempfiles can be created.',
    'long_description': "# Overview\n\nOften there is a need to temporarily save a file to 'disk' for the consumption of external tools. Or maybe you can pipe some input info to an external tool\nbut has no way of forcing such external tool to pipe its output straight to your software: **it wants to write a file to disk**.\nDisk operations are slow and if repeated too often can shorten the lifespan of underlying media.\n\nOn Linux, most distributions offer a /tmp directory BUT it is on physical media. However, modern distributions often offer at east two\nplaces where one can safely create temporary files in RAM: /dev/run/<uid>, /run/shm and /dev/shm\n\n/dev/run/<uid> is ideal for your temporary files. It is writable and readable only by your user.\n/dev/shm is usually world-readable and world-writable (just like /tmp), it is often used for IPC (inter process communication) but can also serve well as a temporary RAM-based tempdir\n\nThis module is very simple and tries not to reinvent the wheel. It will check /tmp to see if it in a ramdisk or not. And it will also check\nif you have other options where to place your temporary files/dirs on a memory-based file system like tmpfs or ramfs.\n\nWith this info you are well served by pythons builtin modules and external packages like pathlib or pyfilesystem2 to move on to do your things.   \n\n**To know more, I recommend the following links:**\nhttps://unix.stackexchange.com/questions/162900/what-is-this-folder-run-user-1000\nhttps://superuser.com/questions/45342/when-should-i-use-dev-shm-and-when-should-i-use-tmp\n\n\n# API\nThis module searches for paths hosted on filesystems of type belonging to MEM_BASED_FS ('tmpfs' or 'ramfs').\nPaths in SUITABLE_PATHS are searched and the first path found that exists and is stored on a filesystem whose type \nbelongs to MEM_BASED_FS will be used as the tempdir.\nIf no suitable path is found, then if fallback = True, we will fallback to default tempdir (as determined by tempfile stdlib). If fallback is a path, then we will default to it.\nIf fallback is false, a RunTimeError exception is raised.\n\nThe MemoryTempfile constructor has arguments that let you change how the algorith works.\nYou can change the order of paths (with preferred_paths), add new paths to the seach (with preferred_paths and/or with additional_paths) \nand you can exclude certain paths (with removed_paths).\nYou can change the filesystem types you accept (with filesystem_types) and specify whether or not to fallback to a vanilla tempdir as a last resort.\n\nThen, all methods available from tempfile stdlib are available through MemoryTempfile.\n\n# Usage\n\n## Example 1:\n\n    from memory_tempfile import MemoryTempfile\n    \n    tempfile = MemoryTempfile()\n    \n    with tempfile.TemporaryFile() as \n        # as usual...\n        \n## Example 2:\n\n    # We now do not want to use /dev/shm or /run/shm and no ramfs paths\n    # If /run/user/{uid} is available, we prefer it to /tmp\n    # And we want to try /var/run as a last resort\n    # If all fails, fallback to platform's tmp dir\n    \n    from memory_tempfile import MemoryTempfile\n    import memory_tempfile\n\n    # By the way, all paths with string {uid} will have it replaced with the user id\n    tempfile = MemoryTempfile(preferred_paths=['/run/user/{uid}'], remove_paths=['/dev/shm', '/run/shm'],\n                              additional_paths=['/var/run'], filesystem_types=['tmpfs'], fallback=True)\n    \n    if tempfile.found_mem_tempdir():\n        print('We could use any of the followig paths: {}'.format(tempfile.get_usable_mem_tempdir_paths()))\n        print('And we are using now: {}'.format(tempfile.gettempdir()))\n    \n    with tempfile.NamedTemporaryFile() as ntf:\n        # use it as usual...\n        pass",
    'author': 'mbello',
    'author_email': 'mbello@users.noreply.github.com',
    'url': 'https://github.com/mbello/memory-tempfile',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
