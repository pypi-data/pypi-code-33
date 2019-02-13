import os
from glob import glob
import pyemma
from celery import Celery

print('pyemma path:', pyemma.__path__)
import numpy as np
import sys

from pyemma._ext.sklearn.parameter_search import ParameterGrid
from pyemma.coordinates import source
from pyemma.coordinates.data._base.transformer import StreamingTransformer
from pyemma.coordinates.estimation.covariance import Covariances

test_systems = [
    '1FME',
    '2F4K',
    '2JOF',
    '2WAV',
    'A3D',
    'CLN025',
    'GTT',
    'lambda',
    'NuG2',
    'PRB',
    'UVF',
    'NTL9',
]

features = (#'xyz',
            #'backbone',
            #'side_sidechain_torsions',
            #'dist_ca',
            #'dist_ca_d1',
            #'dist_ca_d2',
            #'dist_ca_expd',
            #'dist_ca_c_0.4',
            #'dist_ca_c_0.5',
            #'dist_ca_c_0.6',
            #'dist_ca_c_0.8',
            #'dist_ca_c_1.0',
            #'shrake_ruply',
            'res_mindist',
'res_mindist_d1',
'res_mindist_d2',
'res_mindist_expd',
'res_mindist_c_0.4',
'res_mindist_c_0.5',
'res_mindist_c_0.6',
'res_mindist_c_0.8',
'res_mindist_c_1.0',
            )
#RAW_TRAJS_PATH = '/home/marscher/NO_BACKUP/data/feature_sel'
#PRE_CALC_FEATURES_PATH = '/home/marscher/NO_BACKUP/data/feature_sel/cached_features/'
RAW_TRAJS_PATH = '/group/ag_cmb/simulation-data/DESRES-Science2011-FastProteinFolding/'
PRE_CALC_FEATURES_PATH = '/group/ag_cmb/marscher/feature_sel/'
output_path = '/group/ag_cmb/marscher/feature_sel/'

files = {
    name: {feature: sorted(glob(PRE_CALC_FEATURES_PATH + '/*{sys}*{feat}*.h5'.format(sys=name, feat='res_mindist')))
           for feature in features
           # omit cartesian coordinates here, because there are not preprocessed.
           }
    for name in test_systems}

#print (files)

def create_traj_top_pairs(test_system):
    # match trajectory files with topology

    if 'NTL9' not in test_system:
        patterns = RAW_TRAJS_PATH + '/*' + test_system + '*/*' + test_system + '*/*.dcd'
        print(patterns)
        top = glob(RAW_TRAJS_PATH + '/*' + test_system + '*/*' + test_system + '*/*.pdb')[0]
    else:
        patterns = RAW_TRAJS_PATH + '/' + test_system + '*/*.dcd'
        top = glob(RAW_TRAJS_PATH + '/' + test_system + '*/*.pdb')[0]
    trajs = sorted(glob(patterns))
    assert trajs

    import re
    # lambda has 4 independent runs, remove empty sub lists later on.
    files_for_features_independent_runs = [[], [], [], []]
    for f in trajs:
        m = re.match('.*{sys}-([0-9]).*'.format(sys=test_system), f)
        assert m
        ind_run = int(m.group(1))
        files_for_features_independent_runs[ind_run].append(f)
    files_for_features_independent_runs = list(filter(lambda x: x, (e for e in files_for_features_independent_runs)))

    assert top
    assert files_for_features_independent_runs

    trajs_with_top = {'trajs': files_for_features_independent_runs, 'top': top}
    return trajs_with_top


grid = ParameterGrid([{
'test_system': test_systems,
'feature': features,
                       'lag': [500],  # dt=200ps, lag=100ns

                       # + [('backbone', 'dist_ca'),
                       #                   ('res_mindist', 'shrake_ruply'),
                       #                   ('cartesian', 'backbone')
                       #                   ]}]
                       }])

print('grid len:', len(grid))
for i, e in enumerate(grid):
    print(i, e)
# sys.exit(0)


class DistTrans(StreamingTransformer):
    def __init__(self, scheme='d1', c=None):
        super(DistTrans, self).__init__(10000)
        assert scheme in ('d1', 'd2', 'expd')
        self.scheme = scheme
        self.c = c

    def _transform_array(self, X):
        if self.c is None:
            if self.scheme == 'd1':
                return 1.0 / X
            elif self.scheme == 'd2':
                return 1.0 / np.sqrt(X)
            elif self.scheme == 'expd':
                return np.exp(-X)
        else:
            # apply cut-off
            mask = X >= self.c
            X[mask] = 0.0
            X[~mask] = 1.0
            return X

    def describe(self):
        pass

    def dimension(self):
        return super(DistTrans, self).dimension()


broker_url = 'amqp://marscher:foobar@wallaby:5672/myvhost'
app = Celery('tasks', broker=broker_url)


@app.task
def run(id):
    print('job number: ', id)
    params = grid[id]
    feature = params['feature']
    test_system = params['test_system']
    lag = params['lag']

    fname = output_path + 'scores_test_sys_{test_system}_lag_{lag}_feat_{feature}.npz'.format(
        test_system=test_system,
        lag=lag,
        mode='sliding',
        splitter='kfold',
        scoring_method='vamp2',
        feature=feature
    )
    print(fname)
    if os.path.exists(fname):
        print("results file %s already exists. Skipping" % fname)
        return

    try:
        files_for_features = [files[test_system][feature]]
        # lambda has 4 independent runs, remove empty sub lists later on.
        files_for_features_independent_runs = [[], [], [], []]
        import re
        for flist in files_for_features:
            for f in flist:
                m = re.match('.*{sys}-([0-9]).*'.format(sys=test_system), f)
                assert m
                ind_run = int(m.group(1))
                files_for_features_independent_runs[ind_run].append(f)
        # remove empty sub lists.
        files_for_features_independent_runs = list(
            filter(lambda x: x, (e for e in files_for_features_independent_runs)))
        assert files_for_features_independent_runs[0]
        #  create FragmentedReader per feature, which groups all the files of a system.
        # independent runs for each test system are named like $test_system-[0-9]-feat.dcd.h5
        reader = source(files_for_features_independent_runs, chunk_size=6000)

        # transform feature if needed (distances).
        if feature.startswith('res_mindist_'):
            name = feature
            match = re.match('res_mindist_c_(.*)', feature)
            if match is not None:
                arg = {'c': float(match.group(1))}
            else:
                arg = {'scheme': re.match('res_mindist_(.*)', name).group(1)}
            trans = DistTrans(**arg)
            trans.data_producer = reader
            reader = trans

        from sklearn.model_selection import KFold
        splitter_input = KFold(n_splits=10)
        cov = Covariances(n_covs=30, tau=lag, mode='sliding', n_save=4)

        cov.estimate(reader)
        scores = cov.score_cv(k=10, scoring_method='vamp2', splitter=splitter_input)
        parameters = np.array({'lag': lag,
                               'splitter': 'kfold',
                               'mode': 'sliding',
                               'test_system': test_system,
                               'scoring_method': 'vamp2',
                               })

        results = {'scores': scores, 'covs_': cov.covs_}

        np.savez_compressed(fname, parameters=parameters, **results)

    except BaseException as e:
        print('bad:', e, 'id:', id)
        import traceback
        traceback.print_last()

    print('successful')


if __name__ == '__main__':
    try:
        id_ = int(sys.argv[1])
        run(id_)
    except (IndexError, ValueError):
        print('provide an id as argument')
        sys.exit(1)
