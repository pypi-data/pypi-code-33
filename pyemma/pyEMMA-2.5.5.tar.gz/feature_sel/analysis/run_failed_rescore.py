failed = [
          10,
          11,
          13,
          14,
          15,
          16,
          17,
          19,
          2,
          2,
          20,
          21,
          22,
          221,
          222,
          227,
          23,
          236,
          237,
          4,
          5,
          6,
          7,
          8,
          9,
]

from celery import group
import rescore
tasks = group([rescore.run.s(id) for id in failed])
tasks.apply_async()
