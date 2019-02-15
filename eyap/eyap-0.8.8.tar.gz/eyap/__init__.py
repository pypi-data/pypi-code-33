"""Extended yap package for comment management.

With eyap, you can choose a backend to manage your comments. A key goal of
the eyap package is that you can write your code in a generic way and easily
switch the back-end. For example, you can use a simple file back-end with
something like like the following:

```

>>> import eyap, tempfile, os, shutil  # Import some things used for demo.
>>> backend = 'file'                   #  Use a simple file backend for demo.
>>> finfo = {'owner': 'emin63', 'realm': tempfile.mkdtemp(), 'topic': 'test'}
>>> comment_thread = eyap.Make.comment_thread('file', **finfo)
>>> comment_thread.add_comment('Testing things', allow_create=True)
>>> comment_thread.add_comment('is great!')

```

The code above will create a new comment thread and add a comment to it
while also creating the thread if it does not exist. Later, you could
access the thread via something like:

```
>>> print(str(comment_thread.lookup_comments())) # doctest: +ELLIPSIS
========================================
Subject: Testing things ...
Timestamp: ...
----------
Testing things
========================================
Subject: is great! ...
Timestamp: ...
----------
is great!

```

The main reason for the existence of something like eyap is so that you
could use pretty much the same exact code with a different backend. For
example, using 'github' instead of 'file' and setting realm/owner to the
organization/repo in github while providing a valid user/token for github
access will post or read an issue from github.

```

>>> ginfo = {'owner': 'emin63', 'realm': 'eyap', 'topic': 'Describe usage'}
>>> g_thread = eyap.Make.comment_thread('github', **ginfo)
>>> print(str(g_thread.lookup_comments())) # doctest: +ELLIPSIS
========================================
Subject: We need a simple description of how to u ...
Timestamp: ...
----------
We need a simple description of how to use eyap.
========================================
Subject: Start with top-level README.md ...
Timestamp: ...
----------
Start with top-level README.md
========================================
Subject: All done! ...
Timestamp: ...
----------
All done!

```

Note that in the above, we only read from github since we did not provide
any username or password. If you had a username and token or password, you
could post comments to github as well.

   Plesae do *NOT* post to above issue; use your own repo for tests.  :)

Finally, we cleanup the file based backend since we don't need it anymore.

```

>>> shutil.rmtree(finfo['realm'])  # Remove the directory to cleanup test.
>>> os.path.exists(finfo['realm']) # Verify we cleaned up.
False

```

See the [README.md on
github](https://github.com/emin63/eyap/blob/master/README.md) for
further details on usage, how to create new backends, etc.

"""

VERSION = '0.8.8'

import logging
import doctest

from eyap.core import comments, github_comments

try:  # Try to import redis if possible
    from eyap.core import redis_comments
except ImportError as prob:  # Create mock class to complain about install.
    msg = '\n'.join(['Could not import redis_comments because of error:',
                     str(prob), 'If the problem is that redis is missing,'
                     'Consider installing via `pip install redis`.'])
    logging.debug(msg)
    class ComplainOnRedis:
        "Mock module to complain if we try to use redis backend."
        class RedisCommentThread:
            "Mock class to complain if we try to use redis backend."
            def __init__(self, *args, **kwargs):
                dummy = args, kwargs
                raise Exception(msg)

    redis_comments = ComplainOnRedis


class Make(object):

    _known_backends = {
        'file': comments.FileCommentThread,
        'github': github_comments.GitHubCommentThread,
        'redis': redis_comments.RedisCommentThread
        }

    @classmethod
    def comment_thread(cls, backend, *args, **kwargs):
        """Create a comment thread for the desired backend.

        :arg backend:        String name of backend (e.g., 'file',
                             'github', 'redis', etc.).

        :arg *args, **kwargs:   Arguments to be passed to contructor
                                for that backend.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  A CommentThread sub-class for the given backend.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  Some simple syntatic sugar for creating the desired
                  backend.

        """
        ct_cls = cls._known_backends.get(backend)
        if not ct_cls:
            return None
        return ct_cls(*args, **kwargs)

if __name__ == '__main__':
    doctest.testmod()
    print('Finished Tests')
