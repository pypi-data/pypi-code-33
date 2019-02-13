import itertools

import matplotlib
from pyemma.msm.estimators._dtraj_stats import blocksplit_dtrajs

matplotlib.use('Agg')
import pylab

import pyemma
import hashlib
h = hashlib.md5()
h.update(open(__file__).read().encode('utf-8'))
print('file_hash:', h.hexdigest())

print('pyemma path:', pyemma.__path__)
import numpy as np
import sys
import os

from pyemma._ext.sklearn.parameter_search import ParameterGrid
from pyemma.util.debug import register_signal_handlers as reg

reg()

test_systems = [
    # '1FME',
    # '2F4K',
    # '2JOF',
    # '2WAV',
    #'A3D',
    #'CLN025',
    #'GTT',
    # 'lambda',
    'NuG2',
    # 'PRB',
    #'UVF',
    # 'NTL9',
]

k_per_system = {10: {'A3D': 5,
                     'CLN025': 2,
                     'UVF': 5,
                     'GTT': 5,
                     'PRB': 3},
                5: {'CLN025': 2,
                    'UVF': 5,
                    'GTT': 5,
                    'NuG2': 5,
                }
                }

features = ['xyz',
            'flex_torsions',
            'res_mindist_expd',
            'flex_torsions+expd',
            ]

grid = ParameterGrid([{'0_test_system': test_systems,
                       'lag': [500],  # dt=200ps, lag=100ns
                       # 'lag': [500, 750, 1000, 1250, 1500, 1750, 2000],
                       '1_feature': features,
                       'n_centers': [50, 500, 1000],
                       'k': [5],  # TODO: 5 and 10 procs should not matter for cov reconstruction as the full input dim is stored?
                       }])

for i, p in enumerate(grid):
    print(i, p)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output')
parser.add_argument('--cov_path')
parser.add_argument('id_', type=int)
args = parser.parse_args()

output_path = args.output

if not os.path.exists(output_path):
    sys.exit(23)


def get_output_file_name(grid, id_):
    params = grid[id_]
    feature = params['1_feature']
    test_system = params['0_test_system']
    n_states = params['n_centers']

    fname_cluster = os.path.join(output_path, 'cl_test_sys_{sys}_nstates_{n_states}_feat_{feat}.h5'.format(
        sys=test_system, n_states=n_states, feat=feature))

    fname_msm = os.path.join(output_path, 'msm_score_test_sys_{sys}_lag_{lag}_nstates_{n_states}_feat_{feat}.npz'.format(
        sys=test_system, lag=params['lag'], feat=feature, n_states=n_states,
    ))

    from collections import namedtuple
    t = namedtuple("output_names", ["cl", "msm"])
    return t(fname_cluster, fname_msm)


def _recreate_vamp_obj_from_covs(grid, id_):
    lag = grid[id_]['lag']
    test_sys = grid[id_]['0_test_system']
    dim = 5 #k_per_system[grid[id_]['k']][test_sys]
    v = pyemma.coordinates.vamp(lag=lag, dim=dim)
    from paths import get_output_file_name as out_name_score
    fname_cov = os.path.join(args.cov_path, out_name_score(grid, id_, include_k=False) + '_covs.h5')
    covs = pyemma.load(fname_cov)
    c00, c01, c11, mean_0, mean_t = covs._aggregate(covs.covs_)
    v.model.C00 = c00
    v.model.C0t = c01
    v.model.Ctt = c11
    v.model.mean_0 = mean_0
    v.model.mean_t = mean_t
    v._estimated = True
    return v


def run(id_):
    print('job number: ', id_)
    params = grid[id_]
    test_system = params['0_test_system']
    feature = grid[id_]['1_feature']
    n_centers = grid[id_]['n_centers']
    lag = params['lag']

    out_names = get_output_file_name(grid, id_)
    print('current path: %s' % os.getcwd())
    k = 5
    try:
        import paths as p
        if feature == 'xyz':
            reader = p.create_cartesian_reader(test_system)
        elif feature == 'flex_torsions+expd':
            from calc_cov_expd_torsions import get_expd_flex_torsions_reader
            reader = get_expd_flex_torsions_reader(test_system)
        else:
            reader = p.create_fragmented_reader(test_system, feature)

        assert np.all(reader.trajectory_lengths() > 0)
        assert reader.chunksize > 0

        t = _recreate_vamp_obj_from_covs(grid, id_=id_)
        t.data_producer = reader
        foo = next(t.iterator(chunk=1, return_trajindex=False))
        assert foo.shape[1] == 5, foo.shape
        y = t.get_output()

        out_names = get_output_file_name(grid=grid, id_=id_)

        # let sklearn.model.selection grab a 50/50 split for these chunks
        # concatenate the train data set. For the test set we need to ensure we do not create artificial transitions.
        splitted = np.array(blocksplit_dtrajs(y, lag=9999, sliding=False, shift=0))

        splitted = list(filter(lambda x: x.size > 0, splitted))
        from sklearn.model_selection import train_test_split
        ts = []
        for trial in range(5):
            y_train, y_test = train_test_split(splitted, train_size=0.5, shuffle=True) 
            test_size = sum(x.size for x in y_test)
            train_size = sum(x.size for x in y_train)
            print('train size:', train_size, 'test_size:', test_size)
            cluster_args = dict(k=n_centers, max_iter=10, stride=1, chunksize=0, n_jobs=16)
            cluster_train = pyemma.coordinates.cluster_kmeans(data=y_train, **cluster_args)

            dtrajs = []
            for test_traj in y_test:
                dtrajs.append(cluster_train.assign(test_traj))

            msm = pyemma.msm.estimate_markov_model(dtrajs, lag=lag)
            #score_msm = msm.score(dtrajs, score_k=5)
            ts.append(msm.timescales(5))
            msm.save(out_names.msm + '.pyemma', model_name=str(trial), overwrite=True)
        from pyemma._base.serialization.h5file import H5File
        import h5py
        with h5py.File(out_names.msm + '.pyemma', mode='a') as fh:
            fh.create_dataset('timescales', data=np.array(ts))
    except BaseException as e:
        print('bad:', e, id_)
        import traceback
        traceback.print_exc(file=sys.stdout)
        import pdb
        pdb.post_mortem()
        raise
    else:
        print('successful')


if __name__ == '__main__':
    run(args.id_)
