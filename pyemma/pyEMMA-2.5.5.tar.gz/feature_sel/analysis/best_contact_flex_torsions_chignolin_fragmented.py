from glob import glob
import numpy as np
import pyemma
from pyemma.coordinates.estimation.covariance import Covariances

#pyemma.config.show_progress_bars = True

path = '/group/ag_cmb/simulation-data/DESRES-Science2011-FastProteinFolding/DESRES-Trajectory_CLN025-0-protein/CLN025-0-protein/'
trajs = [glob(path+'/*.dcd')]
top= glob(path+'/CLN025-0-protein.pdb')[0]

lag = 500
dim = 5

try:
    data = pyemma.load("data-all.pyemma")
    data_flex = pyemma.load("data-flex.pyemma")
    contacts = pyemma.load("contacts.pyemma")
except:
    feat_flex = pyemma.coordinates.featurizer(top)
    feat_flex.add_sidechain_torsions(cossin=True)
    feat_flex.add_backbone_torsions(cossin=True)

    data_flex = pyemma.coordinates.load(trajs, features=feat_flex)
    print(data_flex.shape)

    feat_res_mindist = pyemma.coordinates.featurizer(top)
    feat_res_mindist.add_residue_mindist(scheme='closest-heavy')
    res_mindist = pyemma.coordinates.load(trajs, features=feat_res_mindist)
    print(res_mindist.shape)

    mask = res_mindist <= 0.5
    contacts = np.zeros_like(res_mindist)
    contacts[mask] = 1.0

    data = np.concatenate((data_flex, contacts), axis=1)
    print(data.shape)
    pyemma.coordinates.source(data).save('data-all.pyemma')
    pyemma.coordinates.source(data_flex).save('data-flex.pyemma')
    pyemma.coordinates.source(contacts).save('contacts.pyemma')

length = data.trajectory_length(0)
first_half = slice(0, length // 2)
snd_half = slice(length // 2, length - 1)


combined_estimator = pyemma.coordinates.vamp(data.data[0][first_half], lag=lag, dim=dim)
combined_estimator.save('combined_plain.pyemma', overwrite=True)
score_combined = combined_estimator.score(data.data[0][snd_half])
score_flex = pyemma.coordinates.vamp(data_flex.data[0][first_half], lag=lag, dim=dim).score(data_flex.data[0][snd_half])
score_contacts = pyemma.coordinates.vamp(contacts.data[0][first_half], lag=lag, dim=dim).score(contacts.data[0][snd_half])

print('score combined k=%s:' % dim, score_combined)
print('score flex:', score_flex)
print('score contacts:', score_contacts)


def covariances(mode='sliding', n_save=1, n_covs=50):
    covs = Covariances(n_covs=n_covs, tau=lag, mode=mode, n_save=n_save, shift=0)
    covs.estimate(data)
    n_covs = max(n_covs, covs.n_covs_)
    combined_estimator.save('combined_soph.pyemma', overwrite=True)

    train_indices = np.random.random_integers(0, n_covs-1, n_covs // 2)
    test_indices = np.setdiff1d(np.arange(n_covs), train_indices)

    covs_score_all = covs.score(train_covs=train_indices, test_covs=test_indices, k=dim)

    covs.estimate(data_flex)
    covs_score_flex = covs.score(train_covs=train_indices, test_covs=test_indices, k=dim)

    covs.estimate(contacts)
    covs_score_contacts = covs.score(train_covs=train_indices, test_covs=test_indices, k=dim)

    return covs_score_all, covs_score_flex, covs_score_contacts

covs_score_all, covs_score_flex, covs_score_contacts = covariances(n_covs=2, n_save=8)
covs_score_all_lin, covs_score_flex_lin, covs_score_contacts_lin = covariances(mode='linear')

print('covs (sliding) score all:', covs_score_all)
print('covs (sliding) score flex:', covs_score_flex)
print('covs (sliding) score contacts:', covs_score_contacts)

print('covs (linear) score all:', covs_score_all_lin)
print('covs (linear) score flex:', covs_score_flex_lin)
print('covs (linear) score contacts:', covs_score_contacts_lin)


