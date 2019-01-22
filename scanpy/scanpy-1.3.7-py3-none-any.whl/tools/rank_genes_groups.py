"""Rank genes according to differential expression.
"""

import numpy as np
import pandas as pd
from math import sqrt, floor
from scipy.sparse import issparse

from .. import utils
from .. import settings
from .. import logging as logg
from ..preprocessing import simple


def rank_genes_groups(
        adata,
        groupby,
        use_raw=True,
        groups='all',
        reference='rest',
        n_genes=100,
        rankby_abs=False,
        key_added=None,
        copy=False,
        method='t-test_overestim_var',
        corr_method='benjamini-hochberg',
        **kwds):
    """Rank genes for characterizing groups.

    Parameters
    ----------
    adata : :class:`~anndata.AnnData`
        Annotated data matrix.
    groupby : `str`
        The key of the observations grouping to consider.
    use_raw : `bool`, optional (default: `True`)
        Use `raw` attribute of `adata` if present.
    groups : `str`, `list`, optional (default: `'all'`)
        Subset of groups, e.g. `['g1', 'g2', 'g3']`, to which comparison shall
        be restricted. If not passed, a ranking will be generated for all
        groups.
    reference : `str`, optional (default: `'rest'`)
        If `'rest'`, compare each group to the union of the rest of the group.  If
        a group identifier, compare with respect to this group.
    n_genes : `int`, optional (default: 100)
        The number of genes that appear in the returned tables.
    method : `{'logreg', 't-test', 'wilcoxon', 't-test_overestim_var'}`, optional (default: 't-test_overestim_var')
        If 't-test', uses t-test, if 'wilcoxon', uses Wilcoxon-Rank-Sum. If
        't-test_overestim_var', overestimates variance of each group. If
        'logreg' uses logistic regression, see [Ntranos18]_, `here
        <https://github.com/theislab/scanpy/issues/95>`__ and `here
        <http://www.nxn.se/valent/2018/3/5/actionable-scrna-seq-clusters>`__, for
        why this is meaningful.
    corr_method : `{'benjamini-hochberg', 'bonferroni'}`, optional (default: 'benjamini-hochberg')
        p-value correction method. Used only for 't-test', 't-test_overestim_var',
        and 'wilcoxon' methods.
    rankby_abs : `bool`, optional (default: `False`)
        Rank genes by the absolute value of the score, not by the
        score. The returned scores are never the absolute values.
    **kwds : keyword parameters
        Are passed to test methods. Currently this affects only parameters that
        are passed to `sklearn.linear_model.LogisticRegression
        <http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html>`__.
        For instance, you can pass `penalty='l1'` to try to come up with a
        minimal set of genes that are good predictors (sparse solution meaning
        few non-zero fitted coefficients).

    Returns
    -------
    names : structured `np.ndarray` (`.uns['rank_genes_groups']`)
        Structured array to be indexed by group id storing the gene
        names. Ordered according to scores.
    scores : structured `np.ndarray` (`.uns['rank_genes_groups']`)
        Structured array to be indexed by group id storing the score for each
        gene for each group. Ordered according to scores.
    logfoldchanges : structured `np.ndarray` (`.uns['rank_genes_groups']`)
        Structured array to be indexed by group id storing the log2
        fold change for each gene for each group. Ordered according to
        scores. Only provided if method is 't-test' like.
    pvals : structured `np.ndarray` (`.uns['rank_genes_groups']`)
        p-values.
    pvals_adj : structured `np.ndarray` (`.uns['rank_genes_groups']`)
        Corrected p-values.

    Notes
    -----
    There are slight inconsistencies depending on whether sparse
    or dense data are passed. See `here <https://github.com/theislab/scanpy/blob/master/scanpy/tests/test_rank_genes_groups.py>`__.
    """
    if 'only_positive' in kwds:
        rankby_abs = not kwds.pop('only_positive')  # backwards compat
        
    logg.info('ranking genes', r=True)
    avail_methods = {'t-test', 't-test_overestim_var', 'wilcoxon', 'logreg'}
    if method not in avail_methods:
        raise ValueError('Method must be one of {}.'.format(avail_methods))

    avail_corr = {'benjamini-hochberg', 'bonferroni'}
    if corr_method not in avail_corr:
        raise ValueError('Correction method must be one of {}.'.format(avail_corr))

    
    adata = adata.copy() if copy else adata
    utils.sanitize_anndata(adata)
    # for clarity, rename variable
    groups_order = groups
    if isinstance(groups_order, list) and isinstance(groups_order[0], int):
        groups_order = [str(n) for n in groups_order]
    if reference != 'rest' and reference not in set(groups_order):
        groups_order += [reference]
    if (reference != 'rest'
        and reference not in set(adata.obs[groupby].cat.categories)):
        raise ValueError('reference = {} needs to be one of groupby = {}.'
                         .format(reference,
                                 adata.obs[groupby].cat.categories.tolist()))
    
    groups_order, groups_masks = utils.select_groups(
        adata, groups_order, groupby)

    if key_added is None:
        key_added = 'rank_genes_groups'
    adata.uns[key_added] = {}
    adata.uns[key_added]['params'] = {
        'groupby': groupby,
        'reference': reference,
        'method': method,
        'use_raw': use_raw,
        'corr_method': corr_method,
    }

    # adata_comp mocks an AnnData object if use_raw is True
    # otherwise it's just the AnnData object
    adata_comp = adata
    if adata.raw is not None and use_raw:
        adata_comp = adata.raw
    X = adata_comp.X

    # for clarity, rename variable
    n_genes_user = n_genes
    # make sure indices are not OoB in case there are less genes than n_genes
    if n_genes_user > X.shape[1]:
        n_genes_user = X.shape[1]
    # in the following, n_genes is simply another name for the total number of genes
    n_genes = X.shape[1]
    
    n_groups = groups_masks.shape[0]
    ns = np.zeros(n_groups, dtype=int)
    for imask, mask in enumerate(groups_masks):
        ns[imask] = np.where(mask)[0].size
    logg.msg('consider \'{}\' groups:'.format(groupby), groups_order, v=4)
    logg.msg('with sizes:', ns, v=4)
    if reference != 'rest':
        ireference = np.where(groups_order == reference)[0][0]
    reference_indices = np.arange(adata_comp.n_vars, dtype=int)

    rankings_gene_scores = []
    rankings_gene_names = []
    rankings_gene_logfoldchanges = []
    rankings_gene_pvals = []
    rankings_gene_pvals_adj = []
    
    if method in {'t-test', 't-test_overestim_var'}:
        from scipy import stats
        from statsmodels.stats.multitest import multipletests
        # loop over all masks and compute means, variances and sample numbers
        means = np.zeros((n_groups, n_genes))
        vars = np.zeros((n_groups, n_genes))
        for imask, mask in enumerate(groups_masks):
            means[imask], vars[imask] = simple._get_mean_var(X[mask])
        # test each either against the union of all other groups or against a
        # specific group
        for igroup in range(n_groups):
            if reference == 'rest':
                mask_rest = ~groups_masks[igroup]
            else:
                if igroup == ireference: continue
                else: mask_rest = groups_masks[ireference]
            mean_rest, var_rest = simple._get_mean_var(X[mask_rest])
            ns_group = ns[igroup]  # number of observations in group
            if method == 't-test': ns_rest = np.where(mask_rest)[0].size
            elif method == 't-test_overestim_var': ns_rest = ns[igroup]  # hack for overestimating the variance for small groups
            else: raise ValueError('Method does not exist.')
            
            denominator = np.sqrt(vars[igroup]/ns_group + var_rest/ns_rest)
            denominator[np.flatnonzero(denominator == 0)] = np.nan
            scores = (means[igroup] - mean_rest) / denominator #Welch t-test
            mean_rest[mean_rest == 0] = 1e-9  # set 0s to small value
            foldchanges = (means[igroup] + 1e-9) / mean_rest
            scores[np.isnan(scores)] = 0
            #Get p-values
            denominator_dof = (np.square(vars[igroup]) / (np.square(ns_group)*(ns_group-1))) + (
                (np.square(var_rest) / (np.square(ns_rest) * (ns_rest - 1))))
            denominator_dof[np.flatnonzero(denominator_dof == 0)] = np.nan
            dof = np.square(vars[igroup]/ns_group + var_rest/ns_rest) / denominator_dof # dof calculation for Welch t-test
            dof[np.isnan(dof)] = 0
            pvals = stats.t.sf(abs(scores), dof)*2 # *2 because of two-tailed t-test

            if corr_method == 'benjamini-hochberg':
                pvals[np.isnan(pvals)] = 1  # set Nan values to 1 to properly convert using Benhjamini Hochberg
                _, pvals_adj, _, _ = multipletests(pvals, alpha=0.05, method='fdr_bh')
            elif corr_method == 'bonferroni':
                pvals_adj = pvals * n_genes

            scores_sort = np.abs(scores) if rankby_abs else scores
            partition = np.argpartition(scores_sort, -n_genes_user)[-n_genes_user:]
            partial_indices = np.argsort(scores_sort[partition])[::-1]
            global_indices = reference_indices[partition][partial_indices]
            rankings_gene_scores.append(scores[global_indices])
            rankings_gene_logfoldchanges.append(np.log2(np.abs(foldchanges[global_indices])))
            rankings_gene_names.append(adata_comp.var_names[global_indices])
            rankings_gene_pvals.append(pvals[global_indices])
            rankings_gene_pvals_adj.append(pvals_adj[global_indices])
            
    elif method == 'logreg':
        # if reference is not set, then the groups listed will be compared to the rest
        # if reference is set, then the groups listed will be compared only to the other groups listed
        from sklearn.linear_model import LogisticRegression
        reference = groups_order[0]
        if len(groups) == 1:
            raise Exception('Cannot perform logistic regression on a single cluster.')
        adata_copy = adata[adata.obs[groupby].isin(groups_order)]        
        adata_comp = adata_copy
        if adata.raw is not None and use_raw:
            adata_comp = adata_copy.raw
        X = adata_comp.X

        clf = LogisticRegression(**kwds)
        clf.fit(X, adata_copy.obs[groupby].cat.codes)
        scores_all = clf.coef_
        for igroup, group in enumerate(groups_order):
            if len(groups_order) <= 2:  # binary logistic regression
                scores = scores_all[0]
            else:
                scores = scores_all[igroup]
            partition = np.argpartition(scores, -n_genes_user)[-n_genes_user:]
            partial_indices = np.argsort(scores[partition])[::-1]
            global_indices = reference_indices[partition][partial_indices]
            rankings_gene_scores.append(scores[global_indices])
            rankings_gene_names.append(adata_comp.var_names[global_indices])
            if len(groups_order) <= 2:
                break

    elif method == 'wilcoxon':
        from scipy import stats
        from statsmodels.stats.multitest import multipletests
        CONST_MAX_SIZE = 10000000
        means = np.zeros((n_groups, n_genes))
        vars = np.zeros((n_groups, n_genes))
        # initialize space for z-scores
        scores = np.zeros(n_genes)
        # First loop: Loop over all genes
        if reference != 'rest':
            for imask, mask in enumerate(groups_masks):
                means[imask], vars[imask] = simple._get_mean_var(X[mask])  # for fold-change
                if imask == ireference: continue
                else: mask_rest = groups_masks[ireference]
                ns_rest = np.where(mask_rest)[0].size
                mean_rest, var_rest = simple._get_mean_var(X[mask_rest]) # for fold-change
                if ns_rest <= 25 or ns[imask] <= 25:
                    logg.hint('Few observations in a group for '
                              'normal approximation (<=25). Lower test accuracy.')
                n_active = ns[imask]
                m_active = ns_rest

                # Now calculate gene expression ranking in chunkes:
                chunk = []
                # Calculate chunk frames
                n_genes_max_chunk = floor(CONST_MAX_SIZE / (n_active + m_active))
                if n_genes_max_chunk < n_genes - 1:
                    chunk_index = n_genes_max_chunk
                    while chunk_index < n_genes - 1:
                        chunk.append(chunk_index)
                        chunk_index = chunk_index + n_genes_max_chunk
                    chunk.append(n_genes - 1)
                else:
                    chunk.append(n_genes - 1)

                left = 0
                # Calculate rank sums for each chunk for the current mask
                for chunk_index, right in enumerate(chunk):
                    # Check if issparse is true: AnnData objects are currently sparse.csr or ndarray.
                    if issparse(X):
                        df1 = pd.DataFrame(data=X[mask, left:right].todense())
                        df2 = pd.DataFrame(data=X[mask_rest, left:right].todense(),
                                           index=np.arange(start=n_active, stop=n_active + m_active))
                    else:
                        df1 = pd.DataFrame(data=X[mask, left:right])
                        df2 = pd.DataFrame(data=X[mask_rest, left:right],
                                           index=np.arange(start=n_active, stop=n_active + m_active))
                    df1 = df1.append(df2)
                    ranks = df1.rank()
                    # sum up adjusted_ranks to calculate W_m,n
                    scores[left:right] = np.sum(ranks.loc[0:n_active, :])
                    left = right + 1

                scores = (scores - (n_active * (n_active + m_active + 1) / 2)) / sqrt(
                    (n_active * m_active * (n_active + m_active + 1) / 12))
                scores[np.isnan(scores)] = 0
                pvals = 2 * stats.distributions.norm.sf(np.abs(scores))

                if corr_method == 'benjamini-hochberg':
                    pvals[np.isnan(pvals)] = 1  # set Nan values to 1 to properly convert using Benhjamini Hochberg
                    _, pvals_adj, _, _ = multipletests(pvals, alpha=0.05, method='fdr_bh')
                elif corr_method == 'bonferroni':
                    pvals_adj = pvals * n_genes

                mean_rest[mean_rest == 0] = 1e-9  # set 0s to small value
                foldchanges = (means[imask] + 1e-9) / mean_rest
                scores_sort = np.abs(scores) if rankby_abs else scores
                partition = np.argpartition(scores_sort, -n_genes_user)[-n_genes_user:]
                partial_indices = np.argsort(scores_sort[partition])[::-1]
                global_indices = reference_indices[partition][partial_indices]
                rankings_gene_scores.append(scores[global_indices])
                rankings_gene_names.append(adata_comp.var_names[global_indices])
                rankings_gene_logfoldchanges.append(np.log2(np.abs(foldchanges[global_indices])))
                rankings_gene_pvals.append(pvals[global_indices])
                rankings_gene_pvals_adj.append(pvals_adj[global_indices])


        # If no reference group exists, ranking needs only to be done once (full mask)
        else:
            scores = np.zeros((n_groups, n_genes))
            chunk = []
            n_cells = X.shape[0]
            n_genes_max_chunk = floor(CONST_MAX_SIZE / n_cells)
            if n_genes_max_chunk < n_genes - 1:
                chunk_index = n_genes_max_chunk
                while chunk_index < n_genes - 1:
                    chunk.append(chunk_index)
                    chunk_index = chunk_index + n_genes_max_chunk
                chunk.append(n_genes - 1)
            else:
                chunk.append(n_genes - 1)
            left = 0
            for chunk_index, right in enumerate(chunk):
                # Check if issparse is true
                if issparse(X):
                    df1 = pd.DataFrame(data=X[:, left:right].todense())
                else:
                    df1 = pd.DataFrame(data=X[:, left:right])
                ranks = df1.rank()
                # sum up adjusted_ranks to calculate W_m,n
                for imask, mask in enumerate(groups_masks):
                    scores[imask, left:right] = np.sum(ranks.loc[mask, :])
                left = right + 1

            for imask, mask in enumerate(groups_masks):
                means[imask], vars[imask] = simple._get_mean_var(X[mask]) #for fold-change
                mask_rest = ~groups_masks[imask]
                mean_rest, var_rest = simple._get_mean_var(X[mask_rest]) #for fold-change

                scores[imask, :] = (scores[imask, :] - (ns[imask] * (n_cells + 1) / 2)) / sqrt(
                    (ns[imask] * (n_cells - ns[imask]) * (n_cells + 1) / 12))
                scores[np.isnan(scores)] = 0
                pvals = 2 * stats.distributions.norm.sf(np.abs(scores[imask,:]))

                if corr_method == 'benjamini-hochberg':
                    pvals[np.isnan(pvals)] = 1  # set Nan values to 1 to properly convert using Benhjamini Hochberg
                    _, pvals_adj, _, _ = multipletests(pvals, alpha=0.05, method='fdr_bh')
                elif corr_method == 'bonferroni':
                    pvals_adj = pvals * n_genes

                mean_rest[mean_rest == 0] = 1e-9  # set 0s to small value
                foldchanges = (means[imask] + 1e-9) / mean_rest
                scores_sort = np.abs(scores) if rankby_abs else scores
                partition = np.argpartition(scores_sort[imask, :], -n_genes_user)[-n_genes_user:]
                partial_indices = np.argsort(scores_sort[imask, partition])[::-1]
                global_indices = reference_indices[partition][partial_indices]
                rankings_gene_scores.append(scores[imask, global_indices])
                rankings_gene_names.append(adata_comp.var_names[global_indices])
                rankings_gene_logfoldchanges.append(np.log2(np.abs(foldchanges[global_indices])))
                rankings_gene_pvals.append(pvals[global_indices])
                rankings_gene_pvals_adj.append(pvals_adj[global_indices])


    groups_order_save = [str(g) for g in groups_order]
    if (reference != 'rest' and method != 'logreg') or (method == 'logreg' and len(groups) == 2):
        groups_order_save = [g for g in groups_order if g != reference]
    adata.uns[key_added]['scores'] = np.rec.fromarrays(
        [n for n in rankings_gene_scores],
        dtype=[(rn, 'float32') for rn in groups_order_save])
    adata.uns[key_added]['names'] = np.rec.fromarrays(
        [n for n in rankings_gene_names],
        dtype=[(rn, 'U50') for rn in groups_order_save])

    if method in {'t-test', 't-test_overestim_var', 'wilcoxon'}:
        adata.uns[key_added]['logfoldchanges'] = np.rec.fromarrays(
            [n for n in rankings_gene_logfoldchanges],
            dtype=[(rn, 'float32') for rn in groups_order_save])
        adata.uns[key_added]['pvals'] = np.rec.fromarrays(
            [n for n in rankings_gene_pvals],
            dtype=[(rn, 'float64') for rn in groups_order_save])
        adata.uns[key_added]['pvals_adj'] = np.rec.fromarrays(
            [n for n in rankings_gene_pvals_adj],
            dtype=[(rn, 'float64') for rn in groups_order_save])
    
    logg.info('    finished', time=True, end=' ' if settings.verbosity > 2 else '\n')
    logg.hint(
        'added to `.uns[\'{}\']`\n'
        '    \'names\', sorted np.recarray to be indexed by group ids\n'
        '    \'scores\', sorted np.recarray to be indexed by group ids\n'
        .format(key_added)
        + ('    \'logfoldchanges\', sorted np.recarray to be indexed by group ids\n'
           '    \'pvals\', sorted np.recarray to be indexed by group ids\n'
           '    \'pvals_adj\', sorted np.recarray to be indexed by group ids'
           if method in {'t-test', 't-test_overestim_var', 'wilcoxon'} else ''))
    return adata if copy else None
