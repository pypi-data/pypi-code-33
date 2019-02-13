import os
import pyemma
from celery import Celery
from sklearn.model_selection import ParameterGrid

print('pyemma path:', pyemma.__path__)
import numpy as np
import sys

sys.path.append(os.path.expanduser('~/workspace/pyemma/feature_sel/analysis/'))
print(sys.path[-1])
import paths

test_systems = [
    #'1FME',
    #'2F4K',
    #'2JOF',
    '2WAV',
    'A3D',
    #'CLN025',
    #'GTT',
    'lambda',
    'NuG2',
    #'PRB',
    #'UVF',
    'NTL9',
]

features = ( 'xyz',
            # 'backbone',
            # 'side_sidechain_torsions',
            # 'dist_ca',
            # 'shrake_ruply',
            'res_mindist',
            #'res_mindist_d1',
            #'res_mindist_d2',
            'res_mindist_expd',
            #'res_mindist_c_0.4',
            'res_mindist_c_0.5',
            #'res_mindist_c_0.6',
            #'res_mindist_c_0.8',
            'res_mindist_c_1.0',
            )

scores = (
    #'VAMPE',
    #'VAMP1',
    'VAMP2',)

grid = ParameterGrid({
    'test_system': test_systems,
    'feature': features,
    'score': scores})

print('grid len:', len(grid))
for i, e in enumerate(grid):
    print(i, e)

output_path = '/group/ag_cmb/marscher/feature_sel/vamp_branch/'

broker_url = 'amqp://marscher:foobar@wallaby:5672/myvhost'
app = Celery('tasks', broker=broker_url)


@app.task
def run(id):
    print('job number: ', id)
    params = grid[id]
    feature = params['feature']
    test_system = params['test_system']
    score = params['score']
    lag = 500
    fname = output_path + 'scores_test_sys_{test_system}_lag_{lag}_feat_{feature}_score_{scoring_method}.npz'.format(
        test_system=test_system,
        lag=lag,
        mode='sliding',
        splitter='kfold',
        scoring_method=score,
        feature=feature
    )
    print(fname)
    if os.path.exists(fname):
        print("results file %s already exists. Skipping" % fname)
        return

    # get covariances from previous cached result file
    input_fname = paths.PRE_CALC_FEATURES_PATH + 'scores_test_sys_{test_system}_lag_{lag}_feat_{feature}.npz'.format(
        test_system=test_system,
        lag=lag,
        mode='sliding',
        splitter='kfold',
        scoring_method='vamp2',
        feature=feature
    )
    try:
        from pyemma.coordinates.estimation.covariance import Covariances
        has_covariances = True
        with np.load(input_fname) as fh:
            try:
                ################## PERFORM COV CALC AGAIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                raise KeyError
                covs_ = fh['covs_']
                cov = Covariances(n_covs=30, tau=lag, mode='sliding', n_save=4)
                cov.covs_ = covs_
            except KeyError:
                from estimate import estimate_covs
                from paths import files_by_test_system
                cov = estimate_covs(test_system=test_system, lag=lag, feature=feature)
                has_covariances = False

        from sklearn.model_selection import KFold
        splitter_input = KFold(n_splits=10)

        scores = cov.score_cv(k=10, scoring_method=score, splitter=splitter_input)
        parameters = np.array({'lag': lag,
                               'splitter': 'kfold',
                               'mode': 'sliding',
                               'test_system': test_system,
                               'scoring_method': 'vamp2',
                               })

        results = {'scores': scores, 'parameters': parameters}

        np.savez_compressed(fname, **results)
        if not has_covariances:
            with np.load(input_fname) as fh:
                content = {k: fh[k] for k in fh}
                content.pop('covs_', None)
            np.savez_compressed(input_fname, covs_=cov.covs_, **content)

    except BaseException as e:
        print('bad:', e, id)
        import traceback

        traceback.print_exc(file=sys.stdout)
    else:
        print('successful')


if __name__ == '__main__':
    try:
        id_ = int(sys.argv[1])
        run(id_)
    except (IndexError, ValueError):
        print('provide an id as argument')
        sys.exit(1)
