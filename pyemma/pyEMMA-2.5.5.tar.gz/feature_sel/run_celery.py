from celery import group
import cache_features_celery

if __name__ == '__main__':
    tasks = [cache_features_celery.run.s(id_) for id_ in range(0, 7391)]
    jobs = group(tasks)
    result = jobs.apply_async()
