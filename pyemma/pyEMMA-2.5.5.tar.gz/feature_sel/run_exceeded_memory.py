from celery import group

#failed = [16, 23, 35, 59, 71, 78, 83, 92, 95, 116, 128, 140, 164, 167]
from analysis import calc_cov_single_feat

if __name__ == '__main__':
    tasks = [calc_cov_single_feat.run.s(id_) for id_ in range(0, 12)]
    jobs = group(tasks)
    result = jobs.apply_async()
