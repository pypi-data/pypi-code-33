#!/usr/bin/env python

import os
from glob import glob

import numpy as np
import sys

import pyemma
import tables
pyemma.config.show_progress_bars = False
pyemma.config.use_trajectory_lengths_cache = False
#from pyemma.coordinates.estimation.covariance import Covariances

fast_folders_dir_src = '/nfs/group/ag_cmb/simulation-data/DESRES-Science2011-FastProteinFolding/'
#fast_folders_dir_dest = os.path.join(os.path.expanduser('~'), 'NO_BACKUP/data/feature_sel/')
fast_folders_dir_dest = '/group/ag_cmb/simulation-data/DESRES-Science2011-FastProteinFolding/'
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

def create_traj_top_pairs(test_system):
    # match trajectory files with topology
    patterns = fast_folders_dir_dest + '/*' + test_system + '*/*.dcd'
    trajs = glob(patterns)
    top = glob(fast_folders_dir_dest + '/*' + test_system + '*/*.pdb')[0]

    trajs_with_top = [(traj, top) for traj in trajs]
    return trajs_with_top


#### features
def shrake_ruply(featurizer):
    def featurize(traj):
        import mdtraj
        res = mdtraj.shrake_rupley(traj, probe_radius=0.14, n_sphere_points=960, mode='atom')
        return res

    featurizer.add_custom_func(featurize, dim=featurizer.topology.n_atoms)

def backbone(featurizer):
    featurizer.add_backbone_torsions()

def dist_ca(featurizer):
    featurizer.add_distances_ca()

def res_mindist(featurizer):
    featurizer.add_residue_mindist(scheme='ca')


features = (dist_ca, res_mindist, backbone, shrake_ruply)
#### end of features



from sklearn.model_selection import ParameterGrid
import itertools
stuff = [create_traj_top_pairs(test_system=t) for t in test_systems]
param_grid = {'traj_top': list(itertools.chain.from_iterable(stuff)),
              'feature': features,
              }

grid = ParameterGrid(param_grid)
# this should be equal to njobs for slurm!
print("num total jobs:", len(list(grid)))


def run(traj_top, feature):
    import os
    os.chdir('/group/ag_cmb/marscher/feature_sel')

    traj, top = traj_top
    print('top: {} \n\ntrajs: {}'.format(top, traj))

    reader = pyemma.coordinates.source(traj, top=top, chunk_size=5000)
    featurizer = reader.featurizer

    feature(featurizer)
    import h5py
    feature_name = feature.__name__
    file_name = "{traj}_{feat}.h5".format(traj=os.path.basename(traj), feat=feature_name)
    print("writing to", file_name)
    with h5py.File(name=file_name, mode='a') as f:
        dataset = f.create_dataset(feature_name, shape=(reader.n_frames_total(), reader.ndim),
                                   compression=32001)

        t = 0
        with reader.iterator(return_trajindex=False) as it:
            for chunk in it:
                dataset[t:t+len(chunk)] = chunk
                t += len(chunk)


def spawn(id):
    params = grid[id]
    print("<START> id=", id)
    print("launching for job id %s with params: %s" % (id, params))
    run(**params)
    print("<END> id=", id)


if __name__ == '__main__':

    first_arg = sys.argv[1]
    if first_arg == 'spawn':
        # this is the master, if we have no id take it from the grid

        from pssh import ParallelSSHClient, utils
        hosts = ['klotz', 'helix', 'nawab',
                 'zatar', 'kendall']
        client = ParallelSSHClient(hosts)
        max = 100
        outs = []
        for id in range(len(grid)):
            out = client.run_command("{exe} cache_features.py {id}".format(exe=sys.executable, id=id))
            outs.append(out)
        map(client.join, outs)
    else:
        spawn(first_arg)

