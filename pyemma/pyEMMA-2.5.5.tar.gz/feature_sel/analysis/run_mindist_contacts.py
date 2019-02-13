# coding: utf-8

from celery import group
import calc_cov_single_feat_res_mindist
tasks = group([calc_cov_single_feat_res_mindist.run.s(i) for i in range(0, 60)])
tasks.apply_async()
