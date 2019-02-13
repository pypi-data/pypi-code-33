import os
import sys

import numpy as np

import pyemma
from paths import missing

print('pyemma path:', pyemma.__path__)

sys.path.append('/home/mi/marscher/workspace/pyemma/feature_sel/analysis/')
sys.path.append('/home/feature_sel/analysis/')
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

features = ('xyz',
            #'dist_ca', # TODO: this is the same feature as res_mindist basically.
            'flex_torsions',
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


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--output', default='/group/ag_cmb/marscher/feature_sel/')
parser.add_argument('--lag', type=int, default=500) # dt=200ps, lag=500ns
parser.add_argument('id_', type=int)
args = parser.parse_args()

output_path = args.output
assert os.path.exists(output_path)

# prefix test sys and feature to force sorting group these.
grid = ParameterGrid([{'0_test_system': test_systems,
                       'lag': [args.lag],  # dt=200ps, lag=500ns
                       '1_feature': list(features),
                       #'k': [3,4,5,6,7,8,9,10],
'k':[5]
                       }])

print('grid len:', len(grid))
#for i, e in enumerate(grid):
#    print(i, e)

def __myrepr__(x):
    s = ",".join([str(x_) for x_ in x])
    return s

print("missing:\n%s" % __myrepr__(missing(grid=grid, output_path=output_path)))


#@app.task
def run(id_):
    print('job number: ', id_)
    params = grid[id_]
    feature = params['1_feature']
    test_system = params['0_test_system']
    lag = params['lag']
    pyemma.config.coordinates_check_output = True
    import estimate as e
    from paths import get_output_file_name
    cov = None
    try:
        for lag in range(500, 2600, 250):
            grid.param_grid[0]['lag'] = [lag]
            for k in (5, 10):  #[1,2,3,4,5,6,7,8,9,10]:
                grid.param_grid[0]['k'] = [k]
                #print(grid.param_grid)
                fname = get_output_file_name(grid, id_)
                fname = os.path.join(output_path, fname)
                # TODO: exclude k param from cov file name to avoid recomp.
                fname_cov = os.path.join(output_path, get_output_file_name(grid, id_, include_k=False) + '_covs.h5')
                print('output file: %s' % fname)
                if os.path.exists(fname):
                    print("results file %s already exists. Skipping" % fname)
                    continue
                parameters = np.array({'lag': lag,
                                       'splitter': 'kfold',
                                       'mode': 'sliding',
                                       'test_system': test_system,
                                       'scoring_method': 'vamp2',
                                       'feature': feature,
                                       'k': k
                                       })

                if not os.path.exists(fname_cov):
                    print('estimating covs')
                    cov = e.estimate_covs(test_system=test_system, feature=feature, lag=lag, n_covs=100)
                    cov.save(fname_cov)
                elif cov is None:
                    print('loading covs from', fname_cov)
                    cov = pyemma.load(fname_cov)
                assert cov is not None
                e.score_and_save(cov,
                                 splitter='kfold',
                                 fname=fname,
                                 k=k,
                                 fixed_seed=False,
                                 scoring_method='VAMP2',
                                 parameters=parameters, n_splits=50)

    except BaseException as e:
        print('bad: %s. failed id: %s' %(e, id_))
        import traceback
        traceback.print_exc()
    else:
        print('successful')


if __name__ == '__main__':
    run(args.id_)
