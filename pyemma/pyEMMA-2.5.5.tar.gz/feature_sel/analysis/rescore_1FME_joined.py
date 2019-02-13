import os
import pyemma
from celery import Celery

from pyemma._ext.sklearn.parameter_search import ParameterGrid

print('pyemma path:', pyemma.__path__)
import numpy as np
import sys

sys.path.append(os.path.expanduser('~/feature_sel/analysis/'))
print(sys.path[-1])

features = ( 'xyz',
            #  'backbone',
            #  'side_sidechain_torsions',
            #  'dist_ca',
            #  'shrake_ruply',
            # 'res_mindist',
            # 'res_mindist_d1',
            # 'res_mindist_d2',
            # 'res_mindist_expd',
            # 'res_mindist_c_0.4',
            # 'res_mindist_c_0.5',
            # 'res_mindist_c_0.6',
            # 'res_mindist_c_0.8',
            # 'res_mindist_c_1.0',
            )

scores = (
    #'VAMPE',
    #'VAMP1',
    'VAMP2',)

grid = ParameterGrid({
    'feature': features,
    'score': scores})

print('grid len:', len(grid))
for i, e in enumerate(grid):
    print(i, e)

output_path = '/home/marscher/NO_BACKUP/1FME_joined'
#output_path = '/group/ag_cmb/marscher/feature_sel/joined3/'
broker_url = 'amqp://marscher:foobar@wallaby:5672/myvhost'
app = Celery('tasks', broker=broker_url)


def xyz(featurizer, reference):
    # create featurizer with alignment to first frame of dataset as reference
    def center(traj):
        xyz = traj.superpose(reference).xyz
        return xyz.reshape(len(xyz), -1)

    featurizer.add_custom_func(center, dim=reference.n_atoms * 3)


#### features
def shrake_ruply(featurizer):
    def featurize(traj):
        import mdtraj
        res = mdtraj.shrake_rupley(traj, probe_radius=0.14, n_sphere_points=960, mode='atom')
        return res

    featurizer.add_custom_func(featurize, dim=featurizer.topology.n_atoms)


def backbone(featurizer):
    featurizer.add_backbone_torsions(cossin=True)


def dist_ca(featurizer):
    featurizer.add_distances_ca()


def res_mindist(featurizer):
    featurizer.add_residue_mindist(scheme='closest-heavy')


def side_sidechain_torsions(featurizer):
    print("adding feature sidechain torssions to featurizer")
    from mdtraj.geometry.dihedral import indices_chi1, indices_chi2, indices_chi3, indices_chi4, indices_chi5, \
        indices_omega
    top = featurizer.topology
    indices = np.vstack((indices_chi1(top),
                         indices_chi2(top),
                         indices_chi3(top),
                         indices_chi4(top),
                         indices_chi5(top),
                         indices_omega(top)))
    assert indices.shape[1] == 4
    from mdtraj import compute_dihedrals

    def compute_side_chains(traj):
        res = compute_dihedrals(traj, indices)
        # cossin
        rad = np.dstack((np.cos(res), np.sin(res)))
        rad = rad.reshape(rad.shape[0], rad.shape[1] * rad.shape[2])
        print('shape chunk:', rad.shape)
        return rad

    featurizer.add_custom_func(compute_side_chains, dim=len(indices) * 2)


@app.task
def run(id):
    print('job number: ', id)
    params = grid[id]
    feature = params['feature']
    test_system = '1FME'
    score = params['score']
    lag = 500
    fname = os.path.join(output_path,'scores_test_sys_{test_system}_lag_{lag}_feat_{feature}_score_{scoring_method}.npz'.format(
        test_system=test_system,
        lag=lag,
        mode='sliding',
        splitter='kfold',
        scoring_method=score,
        feature=feature
    ))
    print(fname)
    if os.path.exists(fname):
        print("results file %s already exists. Skipping" % fname)
        return

    try:
        from pyemma.coordinates.estimation.covariance import Covariances
        reader = pyemma.coordinates.source([
            '/home/marscher/NO_BACKUP/1FME_joined/1FME-0.dcd',
            '/home/marscher/NO_BACKUP/1FME_joined/1FME-1.dcd',
#'/group/ag_cmb/simulation-data/DESRES-Science2011-FastProteinFolding/1FME_joined/1FME-0.dcd',
#'/group/ag_cmb/simulation-data/DESRES-Science2011-FastProteinFolding/1FME_joined/1FME-1.dcd',
            #'/srv/public/1FME_joined/1FME-0.dcd',
            #'/srv/public/1FME_joined/1FME-1.dcd',
        ],
            #top='/srv/public/1FME_joined/1FME-0-protein.pdb'
            top='/home/marscher/NO_BACKUP/1FME_joined/1FME-0-protein.pdb'
            #top='/group/ag_cmb/simulation-data/DESRES-Science2011-FastProteinFolding/1FME_joined/1FME-0-protein.pdb'
        )
        featurizer = reader.featurizer

        if feature == 'xyz':
            import mdtraj
            reference = mdtraj.load_frame('/data/scratch/marscher/1FME_joined/reference.dcd',
                                          top='/data/scratch/marscher/1FME_joined/1FME-0-protein.pdb',
                                          index=0)

            xyz(featurizer=featurizer, reference=reference)
        elif feature == 'resmin_dist':
            res_mindist(featurizer)
        elif feature == 'dist_ca':
            dist_ca(featurizer)
        elif feature == 'side_chain_torsions':
            side_sidechain_torsions(featurizer)
        elif feature == 'shrake_ruply':
            shrake_ruply(featurizer)
        elif feature.startswith('res_mindist'):
            # transform feature if needed (distances).
            res_mindist(featurizer)
            if feature.startswith('res_mindist_'):
                # if we compute contacts or transformations, add this computation.
                import re
                match = re.match('res_mindist_c_(.*)', feature)
                if match is not None:
                    arg = {'c': float(match.group(1))}
                else:
                    arg = {'scheme': re.match('res_mindist_(.*)', feature).group(1)}
                import estimate as e
                trans = e.DistTrans(dim=reader.ndim, **arg)
                trans.data_producer = reader
                reader = trans

        reader.chunksize = 10000
        cov = Covariances(n_covs=30, tau=lag, mode='sliding', n_save=2, fixed_seed=42)
        print('estimating....')
        cov.estimate(reader)
        print('finished')

        parameters = np.array({'lag': lag,
                               'splitter': 'kfold',
                               'mode': 'sliding',
                               'test_system': test_system,
                               'scoring_method': 'vamp2',
                               })

        import estimate as e
        e.score_and_save(cov, fname=fname, splitter='kfold', parameters=parameters,
                         n_splits=10, scoring_method='VAMP2')

        np.savez_compressed(fname, **results)
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
