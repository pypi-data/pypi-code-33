import socket
from glob import glob

import pyemma

print('pyemma path:', pyemma.__path__)
import numpy as np
import sys
import os
import re

sys.path.append(os.path.dirname(__file__))
import estimate

from pyemma._ext.sklearn.parameter_search import ParameterGrid

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


grid = ParameterGrid([{'0_test_system': test_systems,
                       'lag': [500],  # dt=200ps, lag=100ns
                       'score': ['VAMP2'],
                       '1_feature': ['flex_torsions+expd'],
                       }])

print('grid len:', len(grid))
for i, p in enumerate(grid):
    print(i, p)

def run(id_, args):
    print('job number: %s' % id_)
    params = grid[id_]

    test_system = params['0_test_system']
    lag = params['lag']
    score = params['score']
    try:

        import re
        import paths as p
        import estimate as e
        cov = None
        reader = get_expd_flex_torsions_reader(test_system)

        for k in [5, 10, ]:
            grid.param_grid[0]['k'] = [k]
            fname = os.path.join(args.output, p.get_output_file_name(grid, id_))
            print('output file:', fname)
            if os.path.exists(fname):
                print("results file %s already exists. Skipping" % fname)
                continue

            fname_cov = os.path.join(output_path, p.get_output_file_name(grid, id_, include_k=False) + '_covs.h5')
            print('output file cov:', fname_cov)
            if not os.path.exists(fname_cov):
                print('estimating covs')
                #reader_expd = p.create_fragmented_reader(test_system, 'res_mindist_expd')
                #reader_flex_torsions = p.create_fragmented_reader(test_system, 'flexible_torsions')
                #reader = pyemma.coordinates.sources_merger((reader_expd, reader_flex_torsions))

                cov = estimate.estimate_covs(test_system=test_system, feature='dummy', lag=lag, n_covs=50,
                                       reader=reader)
                print('finished covs calc, scoring...')
                cov.save(fname_cov)
            elif cov is None:
                print('loading covs from', fname_cov)
                cov = pyemma.load(fname_cov)

            assert cov is not None
            parameters = np.array({'lag': lag,
                                   'splitter': 'kfold',
                                   'mode': 'sliding',
                                   'test_system': test_system,
                                   'scoring_method': score,
                                   'k': k,
                                   })
            e.score_and_save(cov,
                             splitter='kfold',
                             fname=fname,
                             k=k,
                             fixed_seed=False,
                             scoring_method='VAMP2',
                             parameters=parameters, n_splits=50)

            print('finished scoring... %s' % id_)

    except BaseException as e:
        print('bad:', e, id_)
        print('failed on node:', socket.gethostname())
        import traceback
        traceback.print_exc()
        #import pdb
        #pdb.post_mortem()
        sys.exit(1)
    else:
        print('successful %s' % id_)


def get_expd_flex_torsions_reader(test_system):
    #  create FragmentedReader per feature, which groups all the files of a system.
    # independent runs for each test system are named like $test_system-[0-9]-feat.dcd.h5
    import paths as p
    reader_contacts = p.create_fragmented_reader(test_system=test_system, feature='res_mindist_expd')
    reader_flextorsions = p.create_fragmented_reader(test_system=test_system, feature='flex_torsions')
    assert reader_contacts.n_frames_total()
    assert reader_flextorsions.n_frames_total()
    assert reader_contacts.n_frames_total() == reader_flextorsions.n_frames_total()
    # re-calc contacts (apply cutoffs)
    #trans = p.DistTrans(reader_contacts.dimension(), c=c)
    #trans.data_producer = reader_contacts
    #reader_contacts = trans
    assert isinstance(reader_contacts, p.DistTrans)
    from pyemma.coordinates import combine_sources
    reader = combine_sources((reader_contacts, reader_flextorsions), chunksize=20000)
    assert reader.n_frames_total()
    return reader


if __name__ == '__main__':

    import re
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='/group/ag_cmb/scratch/marscher/feature_sel/')
    parser.add_argument('--lag', type=int, default=500)  # dt=200ps, lag=500ns
    parser.add_argument('--best', action='store_true', default=True)
    parser.add_argument('--only_best_c', action='store_true', default=False)
    parser.add_argument('id_', type=int)
    args = parser.parse_args()

    output_path = args.output
    if not os.path.exists(output_path):
        sys.exit(23)

    run(args.id_, args)
