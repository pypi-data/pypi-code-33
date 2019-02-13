#!/usr/bin/env python

import os
from glob import glob

import numpy as np
import sys

import pyemma

pyemma.config.show_progress_bars = False
pyemma.config.use_trajectory_lengths_cache = False
from pyemma.coordinates.estimation.covariance import Covariances

fast_folders_dir_src = '/nfs/group/ag_cmb/simulation-data/DESRES-Science2011-FastProteinFolding/'
fast_folders_dir_dest = os.path.join(os.path.expanduser('~'), 'NO_BACKUP/data/feature_sel/')
test_systems = ['1FME', '2F4K', '2JOF', '2WAV', 'A3D', 'CLN025', 'GTT', 'lambda', 'NuG2', 'PRB', 'UVF',
                'NTL9-0-protein_fixed_CC']


def copy_data():
    from  distutils.dir_util import copy_tree
    for part in test_systems:
        pattern = fast_folders_dir_src + '/' + '*' + part + '*'
        dirs = glob(pattern)
        for d in dirs:
            print('copying %s ... ' % d)
            copy_tree(d, fast_folders_dir_dest)


'''
input parameters
----------------
* protein
* mode (linear, splitting)
* lag time (1, 10, 100, 1000)
* splitter (LOO, Kfold, Shuffle)
* scoring method (vamp1, vamp2, vampe): vamp-e designed for cross-validation,
'''

from sklearn.model_selection import ParameterGrid

param_grid = {'test_system': test_systems,
              'lag': [1, 10, 100, 1000],
              'splitter': ['shuffle', 'LOO', 'kfold'],
              'mode': ['linear', 'sliding'],
              'scoring_method': ['vamp2'],
              }

grid = ParameterGrid(param_grid)
# this should be equal to njobs for slurm!
print("num total jobs:", len(list(grid)))


def run(test_system, lag, mode, splitter, scoring_method):
    # check existance of output file, in case a job will be restarted due to a cluster failure (which seems to be quite common....)
    fname = 'scores_test_sys_{test_system}_lag_{lag}_mode_{mode}_splitter_{splitter}_score_method_{scoring_method}.npz'.format(
        test_system=test_system,
        lag=lag,
        mode=mode,
        splitter=splitter,
        scoring_method=scoring_method,
    )
    if os.path.exists(fname):
        print('output file name %s already exists. SKIPPING' % fname)

    pattern = fast_folders_dir_dest + '/*' + test_system + '*/*.dcd'
    trajs = glob(pattern)  # [0]
    top = glob(fast_folders_dir_dest + '/*' + test_system + '*/*.pdb')[0]
    splitter_ = splitter
    print('top: {} \n\ntrajs: {}'.format(top, trajs))

    assert trajs

    results = {}

    reader = pyemma.coordinates.source(trajs, top=top, chunk_size=5000)
    featurizer = reader.featurizer

    results['n_frames'] = reader.n_frames_total()

    def score_it():
        cov = Covariances(n_covs=30, tau=lag, mode=mode, n_save=1)
        cov.estimate(reader, stride=1)
        print('<Scoring> ', reader.describe()[:3])
        nonlocal splitter_
        # shuffle is currently the default value, so handle only the other cases explicitly.
        if splitter_ not in ('shuffle', 'LOO', 'kfold'):
            raise ValueError('unknown splitter mode: ' + str(splitter_))

        if splitter_ == 'LOO':
            from sklearn.model_selection import LeaveOneOut
            splitter_input = LeaveOneOut()
        elif splitter_ == 'kfold':
            from sklearn.model_selection import KFold
            splitter_input = KFold(n_splits=10)
        elif splitter_ == 'shuffle':
            splitter_input = splitter_

        res = cov.score_cv(k=10, scoring_method=scoring_method, splitter=splitter_input)
        print('<Scoring> ended', reader.describe()[:3])
        return res

    # TODO: make these functions and combine them via input parameters to gain maximum parallism
    featurizer.active_features = []
    featurizer.add_backbone_torsions()
    results['backbone_torsions'] = score_it()

    featurizer.active_features = []
    featurizer.add_distances_ca()
    results['distances_ca'] = score_it()

    featurizer.active_features = []
    featurizer.add_all()
    results['cartesian'] = score_it()

    featurizer.active_features = []
    featurizer.add_residue_mindist()
    results['residue_mindist'] = score_it()

    featurizer.active_features = []

    def shrake_ruply(traj):
        import mdtraj
        res = mdtraj.shrake_rupley(traj, probe_radius=0.14, n_sphere_points=960, mode='atom')
        return res

    featurizer.add_custom_func(shrake_ruply, dim=featurizer.topology.n_atoms)
    results['shrake_rupley'] = score_it()

    # TODO: add combined features

    parameters = np.array({'lag': lag,
                           'splitter': splitter,
                           'mode': mode,
                           'test_system': test_system,
                           'scoring_method': scoring_method,
                           })

    np.savez_compressed(fname, parameters=parameters, **results)


def spawn(id):
    params = grid[id]
    print("<START> id=", id)
    print("launching for job id %s with params: %s" % (id, params))
    run(**params)
    print("<END> id=", id)


if __name__ == '__main__':
    # copy_data()

    try:
        idx = sys.argv.index('--query-id')
        query_index = int(sys.argv[idx + 1])
        print('params for index %s:\n%s' % (query_index, grid[query_index]))
        sys.exit(0)
    except ValueError:
        pass

    id = int(sys.argv[1])
    spawn(id)
