from celery import group
from analysis import calc_cov_single_feat_a3d

if __name__ == '__main__':
    tasks = [calc_cov_single_feat_a3d.run.s(id_) for id_ in range(0, 5)]
    jobs = group(tasks)
    result = jobs.apply_async()
