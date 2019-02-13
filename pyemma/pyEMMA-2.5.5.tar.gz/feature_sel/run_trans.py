
from tasks import transform_angles_cossin

from celery import group

if __name__ == '__main__':
    from glob import glob
    files = glob('/group/ag_cmb/marscher/feature_sel/*backbone*')
    tasks = [transform_angles_cossin.s(f) for f in files]
    print("num tasks:", len(tasks))
    jobs = group(tasks)
    result = jobs.apply_async()
