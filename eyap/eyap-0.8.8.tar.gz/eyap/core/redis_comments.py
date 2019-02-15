"""Module for working comments from redis backend.
"""

import datetime
import doctest
import json
import logging
import redis

from eyap.core import comments


class RedisCommentThread(comments.CommentThread):
    """Class to represent a thread of redis comments.
    """

    def __init__(self, *args, ltrim=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ltrim = ltrim
        self.redis = redis.Redis()

    def lookup_thread_id(self):
        return 'eyap:%s:%s' % (self.realm, self.topic)

    def add_comment(self, body, allow_create=False, allow_hashes=False,
                    summary=None):
        """Add comment as required by comments.CommentThread parent class.
        """
        thread_id = self.lookup_thread_id()
        if not allow_create and not self.redis.exists(thread_id):
            raise ValueError('Tried to add comment to non-exist thread %s' % (
                thread_id))

        comment = comments.SingleComment(
            self.user, datetime.datetime.now(datetime.timezone.utc), body, 
            summary=summary)
        lpush = self.redis.lpush(thread_id, comment.to_json())
        logging.debug('Pushing comment to redis returned %s', str(lpush))
        if self.ltrim:
            ltrim = self.redis.ltrim(thread_id, 0, self.ltrim)
            logging.debug('Redis ltrim returend %s', str(ltrim))
        else:
            ltrim = None

        return {'status': 'OK', 'lpush': lpush, 'ltrim': ltrim}

    def create_thread(self, body):
        return self.add_comment(body, allow_create=True)

    def delete_thread(self, really=False):
        thread_id = self.lookup_thread_id()        
        if not really:
            raise ValueError(
                'Cowardly refusing to delete thread %s since really=%s' % (
                    thread_id, really))
        self.redis.delete(thread_id)

    def lookup_comments(self, reverse=False):
        thread_id = self.lookup_thread_id()
        data = self.redis.lrange(thread_id, 0, -1)
        clist = []
        for jitem in data:
            citem = json.loads(jitem.decode('utf8'))
            clist.append(comments.SingleComment(**citem))
        if reverse:
            clist = list(reversed(clist))

        return comments.CommentSection(clist)

    def __getstate__(self):
        "Do not pickle redis connection"
        return {k: v for k, v in self.__dict__.items() if k != 'redis'}

    def __setstate__(self, state):
        for key, val in state.items():
            setattr(self, key, val)
        self.redis = redis.Redis()
        

    @staticmethod
    def _regr_test_pickle():
        """
>>> import pickle
>>> from eyap.core import redis_comments
>>> rc = redis_comments.RedisCommentThread(
...     'test-owner', 'test-realm', 'test-topic', 'test-owner')
>>> x=pickle.dumps(rc)
>>> y=pickle.loads(x)
"""

    @staticmethod
    def _regr_test():
        """
>>> from eyap.core import redis_comments
>>> rc = redis_comments.RedisCommentThread(
...     'test-owner', 'test-realm', 'test-topic', 'test-owner')
>>> rc.delete_thread(really=True)
>>> status = rc.add_comment('test_comment', allow_create=True)
>>> print(', '.join(['%s: %s' % (k, status[k]) for k in sorted(status)]))
lpush: 1, ltrim: None, status: OK
>>> sec = rc.lookup_comments('test-topic')
>>> print(sec.show())  # doctest: +ELLIPSIS
========================================
Subject: test_comment ...
Timestamp: ...
----------
test_comment
        """
    

if __name__ == '__main__':
    doctest.testmod()
    print('Finished tests')
