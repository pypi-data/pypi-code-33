import matplotlib
matplotlib.use('Agg')
import pylab

import pyemma

print('pyemma path:', pyemma.__path__)
import numpy as np
import sys
import os

from pyemma._ext.sklearn.parameter_search import ParameterGrid

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--output', default='/group/ag_cmb/marscher/feature_sel/msm/')
parser.add_argument('id_', type=int)
args = parser.parse_args()

output_path = args.output

if not os.path.exists(output_path):
    sys.exit(23)

test_systems = [
    #'1FME',
    #'2F4K',
    #'2JOF',
    #'2WAV',
    'A3D',
    'CLN025',
    #'GTT',
    #'lambda',
    #'NuG2',
    'PRB',
    #'UVF',
    #'NTL9',
]

features = (#'xyz',
            #'backbone',
            #'side_sidechain_torsions',
            #'dist_ca',
            #'shrake_ruply',
            'res_mindist',
            #'res_mindist_d1',
            #'res_mindist_d2',
            #'res_mindist_expd',
            #'res_mindist_c_0.4',
            #'res_mindist_c_0.5',
            'res_mindist_c_0.6',
            #'res_mindist_c_0.8',
            #'res_mindist_c_1.0',
            )


grid = ParameterGrid([{'0_test_system': test_systems,
                       'lag': [500],  # dt=200ps, lag=100ns
                       '1_feature': list(features),
                       'n_micro': [100],#, 150, 200, 250],
                       'k': [10],
                       }])


def get_output_file_name(grid, id_):
    params = grid[id_]
    feature = params['1_feature']
    test_system = params['0_test_system']
    n_micro = params['n_micro']

    fname_its = os.path.join(output_path, 'its_test_sys_{test_system}_nstates_{n_states}_feat_{feature}.pdf'.format(
        test_system=test_system,
        feature=feature,
        n_states=n_micro
    ))
    fname_cktest = os.path.join(output_path, 'cktest_test_sys_{test_system}_nstates_{n_states}_feat_{feature}.pdf'.format(
         test_system=test_system,
         feature=feature,
         n_states=n_micro
    ))
    fname_cluster = os.path.join(output_path, 'cl_test_sys_{sys}_nstates_{n_states}_feat_{feat}.h5'.format(
        sys=test_system, n_states=n_micro, feat=feature))
    from collections import namedtuple
    t = namedtuple("output_names", ["its", "ck", "cl"])
    return t(fname_its, fname_cktest, fname_cluster)


def missing(grid, output_path, verbose=False):
    import os
    res = []
    for id_ in range(len(grid)):
        fns = get_output_file_name(grid, id_)
        for f in fns:
            path = os.path.join(output_path, f)
            if not os.path.exists(path):
                res.append(id_)
                if verbose:
                    print(id_, 'does not have', path)
    return set(res)


def __myrepr__(x):
    s = ",".join([str(x_) for x_ in x])
    return s

print('missing:\n',__myrepr__(missing(grid, output_path, verbose=True)))


def run(id):
    print('job number: ', id)
    params = grid[id]
    feature = params['1_feature']
    test_system = params['0_test_system']
    n_micro = params['n_micro']

    out_names = get_output_file_name(grid, id)

    fname_its = out_names.its
    fname_cktest = out_names.ck
    fname_cluster = out_names.cl

    if os.path.exists(fname_its):
        print("results file %s already exists. Skipping" % fname_its)
        return
    print('current path: %s' % os.getcwd())
    try:
        if False: #os.path.exists(fname_cluster):
            cluster = pyemma.load(fname_cluster)
        else:
            import paths as p
            if feature == 'xyz':
                reader = p.create_cartesian_reader(test_system)
            else:
                reader = p.create_fragmented_reader(test_system, feature)

            assert np.all(reader.trajectory_lengths() > 0)
            assert reader.chunksize > 0

            fname_cov = os.path.join(output_path, p.get_output_file_name(grid, id, include_k=False) + '_covs.h5')
            covariances = pyemma.load(fname_cov)
            c00, c01, c11, mean_0, mean_t = covariances._aggregate(covariances.covs_)
            assert np.all(np.isfinite(c00))
            assert np.all(np.isfinite(c01))
            assert np.all(np.isfinite(c11))
            assert np.all(np.isfinite(mean_0))
            """ TICA """
            """
            from pyemma.coordinates.transform import TICA
            t = TICA(lag=500, dim=10)
            t.data_producer = reader
            t.cov = c00
            t.cov_tau = c01
            t.mean = mean_0
            print('real?:', np.all(np.isreal(t.eigenvectors)))
            """
            from pyemma.coordinates.transform import VAMP
            t = VAMP(lag=500, dim=10)
            t.data_producer = reader
            t.model.mean_0 = mean_0
            t.model.mean_t = mean_t
            t.model.C00 = c00
            t.model.C0t = c01
            t.model.Ctt = c11

            cluster = pyemma.coordinates.cluster_kmeans(k=n_micro, max_iter=100, stride=2)
            cluster.estimate(t)
            cluster.dtrajs
            cluster.save(fname_cluster)
        from pyemma.msm import timescales_msm
        from matplotlib.pylab import figure, savefig, title
        # its
        # lags=[1, 100, 200, 250, 300, 500, 700, 800, 1000]
        its = timescales_msm(cluster.dtrajs, lags=5000, errors='bayes', n_jobs=None)
        figure(1, figsize=(12, 8))
        pyemma.plots.plot_implied_timescales(its, dt=.2, units='ns', nits=10)
        title('Implied timescales for {sys} with feature {feat}'.format(sys=test_system, feat=feature))
        savefig(fname_its)
        its.save(fname_its+'.h5')

        # cktest
        figure(1, figsize=(12, 8))
        # TODO: shouldn't this be 10 states, as we use 10 slowest processes in scoring?
        # TODO: how to choose the 'converged' estimate here?
        ck = its.estimators[0].cktest(5)
        pyemma.plots.plot_cktest(ck, diag=True)
        savefig(fname_cktest)

    except BaseException as e:
        import pdb
        pdb.post_mortem()
        print('bad:', e, id)
        import traceback
        traceback.print_exc(file=sys.stdout)
    else:
        print('successful')


if __name__ == '__main__':
    run(args.id_)
