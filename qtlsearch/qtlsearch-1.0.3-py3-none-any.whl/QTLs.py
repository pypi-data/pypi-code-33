#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains functions relevant to
    QTLSearch, rather than alterations from the original HOGPROP algorithm.

    QTLSearch is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    QTLSearch is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with QTLSearch.  If not, see <http://www.gnu.org/licenses/>.
'''
from .Annotations import AnnotationTerm
from collections import defaultdict
from itertools import chain
from functools import lru_cache
from property_manager import lazy_property
from tqdm import tqdm
import logging
import numpy as np
import pandas as pd
import random


LOG = logging.getLogger(__name__)


# Hard-coded information
SOURCE = 'QTL'
SOURCE_IN_OUTPUT = ['UNIPROT-GOA', 'CHEBI', 'QTL']


class GeneLocations(object):
    '''
        Store for gene locations.
    '''
    def __init__(self, fn, species=None, id_as_int=False):
        self.locs = pd.read_csv(fn, sep='\t',
                                names=['id', 'chr', 'start', 'end'],
                                dtype={'id': ('str' if not id_as_int else int),
                                       'chr': 'str'})
        if species is not None:
            self.locs['id'] = self.locs['id'].apply(lambda i:
                                                    species.resolve_xref(i))
        # Sort and index the table
        self.locs.sort_values(['chr', 'start', 'end'], inplace=True)

        # Split into chromosomes
        self.chrs = list(map(lambda c: list(c[1].id), self.locs.groupby('chr')))
        self.weights = list(map(lambda c: len(c), self.chrs))

        # Index the table
        self.locs.set_index(['chr', 'start', 'end'], inplace=True)

    @property
    def gene_ids(self):
        '''
            Return the gene IDs from the locations frame.
        '''
        return self.locs.id

    def find(self, chromosome, start, end):
        '''
            Finds the entries in a particular region of the chromosome.
        '''
        return list(self.locs.loc[chromosome, start:end, start:end].id)

    def random_chromosome(self):
        '''
            Choose a random chromosome -- weighted by the number of genes
            on each chromosome (not the length)
        '''
        return random.choices(self.chrs, weights=self.weights)[0]

    def random_region(self, n):
        '''
            Returns a set of n contiguous genes from a single chromosome.
        '''
        # Get random chromosome
        c = self.random_chromosome()

        # Find a contiguous region of length n
        if len(c) > n:
            i = random.randint(0, (len(c) - n))
            return c[i:(i + n)]
        else:
            return c


class QTLs(object):
    '''
        Object to store QTLs. Iterable.
    '''
    def __init__(self, species, gene_locations, qtls, dataset_names=None):
        self.species = species

        dataset_names = (list(range(len(qtls))) if dataset_names is None else
                         dataset_names)

        self._qtls = [(GeneLocations(fn1, self.species),
                       self.load_qtl(fn2),
                       name)
                      for (fn1, fn2, name) in zip(gene_locations,
                                                  qtls,
                                                  dataset_names)]

    def load_qtl(self, fn):
        '''
            Load the QTLs from the file in the standardised format.
        '''
        with open(fn, 'rt') as fp:
            n_cols = len(next(fp).split('\t'))
        columns = ['annot_id', 'chr', 'inf.Mbp', 'sup.Mbp']
        columns = (['qtl_id'] + columns) if n_cols == 5 else columns
        qtls = pd.read_csv(fn,
                           sep='\t',
                           names=columns,
                           dtype={'annot_id': 'str', 'chr': 'str'})
        if columns[0] != 'qtl_id':
            qtls['qtl_id'] = qtls.index

        return qtls

    @lazy_property
    def targets(self):
        '''
            Generate a list of targets to use in HOG-filtering.
        '''
        return frozenset(chain.from_iterable(qtl.genes
                                             for qtl in self.qtls(None)))

    @lazy_property
    def all_genes(self):
        '''
            Return a list of all the gene IDs defined in the GeneLocations
            objects paired to the QTLs.
        '''
        return frozenset(chain.from_iterable(locs.gene_ids
                                             for (locs, *_) in self._qtls))

    def qtls(self, hogs):
        for (locs, qtls, name) in self._qtls:
            yield from map(lambda qtl: QTL(name, locs, qtl[1], hogs),
                           qtls.iterrows())

    # def qtl(self, i, hogs, qtl_set=None):
    #     '''
    #         Retrieves a single QTL.
    #     '''
    #     qtl_set = 0 if qtl_set is None else qtl_set
    #     (locs, qtls) = self._qtls[qtl_set]
    #     return QTL(locs, i, qtls.loc[i], hogs)

    def predict(self, hogs, with_p=False, replicates=1000, individually=None,
                traits=None):
        '''
            Takes a HOGStore object to predict the causal genes.
        '''
        LOG.info('Starting prediction.')
        if with_p:
            LOG.info('p-value estimates will be computed.')
        else:
            LOG.info('p-value estimates will be skipped.')
        cols = ['dataset'] if len(self._qtls) > 1 else []
        cols += ['qtl_id', 'id', 'inc']
        cols += ['p'] if with_p else []
        cols += list(map(lambda x: 'from-{}'.format(x), SOURCE_IN_OUTPUT))

        sort_cols = ['dataset'] if len(self._qtls) > 1 else []
        ascending_cols = [True] if len(self._qtls) > 1 else []
        sort_cols += ['qtl_id', ('inc' if not with_p else 'p')]
        ascending_cols += [True, with_p]

        if individually:
            results = []
            for qtl in tqdm(self.qtls(hogs),
                            desc='Predicting QTLs',
                            unit=' QTL'):
                inc = qtl.compute_increases(with_p=with_p,
                                            replicates=replicates)
                inc['id'] = inc['id'].apply(self.species.get_xref)
                inc['qtl_id'] = qtl.i
                inc['dataset'] = qtl.dataset
                results.append(inc[cols])

        else:
            traits = self.get_traits(traits)
            # The compute_increases method yields per-trait
            results = [df[cols]
                       for (trait, df) in self.compute_increases(
                           hogs,
                           with_p=with_p,
                           replicates=replicates,
                           traits=traits)]

        return pd.concat(results).sort_values(sort_cols,
                                              ascending=ascending_cols)

    def get_traits(self, traits):
        if traits is not None:
            ts = list(sorted({t
                              for qtl in self._qtls
                              for t in qtl[1]['annot_id']}))
            return {ts[trait] for trait in traits}

    # DISABLED - probably buggy
    # def compute_increases(self, hogs, random=None, with_p=False,
    #                       replicates=1000, traits=None):
    #     '''
    #         Compute the increases with annotations from ALL QTLs being
    #         considered at once, per-trait.
    #     '''
    #     rel_hogs = self._relevant_hogs(hogs, random=random, traits=traits)
    #     for (trait, trait_genes, trait_hogs) in tqdm(rel_hogs,
    #                                                  desc='Predicting',
    #                                                  unit=' trait'):
    #         # Initialise increases for the trait
    #         trait_inc = {g: [0.0, []]
    #                      for (_, genes) in trait_genes
    #                      for g in genes}
    #
    #         for (hog, hog_genes) in tqdm(map(lambda h: (hogs.hogs[h[0]], h[1]),
    #                                          trait_hogs.items()),
    #                                      desc='Predicting HOGs',
    #                                      unit=' HOG'):
    #             z = {'qtl{}'.format(q.i): ';'.join(map(str, sorted(gs)))
    #                  for (q, gs) in hog_genes}
    #             self.__hog_genes = hog_genes
    #             trait_inc.update(self._propagate_through_hog(trait, hog, **z))
    #
    #         if random:
    #             yield (trait, trait_inc, trait_genes)
    #         else:
    #             def get_result_lines(g):
    #                 (g_id, g_inc) = g
    #                 z = {'id': g_id, 
    #                      'xref_id': self.species.get_xref(g_id),
    #                      'inc': g_inc[0]}
    #                 for (source, gs) in g_inc[1].items():
    #                     y = (';'.join(map(self._hogs.species.get_xref,
    #                                       gs)) if g_inc[0] > 0 else '')
    #                     z['from-{}'.format(source)] = y
    #                 return z
    #
    #             df1 = pd.DataFrame.from_records(map(get_result_lines, trait_inc.items()))
    #             # df1 = pd.DataFrame.from_records(
    #             #      ({'id': g_id,
    #             #        'xref_id': self.species.get_xref(g_id),
    #             #        'inc': g_inc[0],
    #             #        'considered': (';'.join(map(self.species.get_xref,
    #             #                                    g_inc[1])) if g_inc[0] > 0
    #             #                       else '')}
    #             #       for (g_id, g_inc) in trait_inc.items()))
    #
    #             if with_p and any(df1.inc > 0):
    #                 # Check that there's actually point in calculating the
    #                 # empirical distribution & then do it...
    #                 distn = self.empirical_distribution(hogs,
    #                                                     replicates,
    #                                                     traits)[trait]
    #                 # Speed this part up.
    #                 df1s = []
    #                 z = len(distn)
    #                 for (inc, df) in df1.sort_values('inc').groupby('inc'):
    #                     distn = distn[distn >= inc]
    #                     df['p'] = (len(distn) / z)
    #                     df1s.append(df)
    #                 df1 = pd.concat(df1s)
    #                 # df1['p'] = df1['inc'].apply(lambda inc:
    #                 #                             (sum(distn >= inc) /
    #                 #                              len(distn)))
    #             elif with_p:
    #                 # No increase, p-value is 1.0
    #                 df1['p'] = 1.0
    #
    #             # Create a table of id -> qtl id, dataset for each relevant...
    #             df2 = pd.DataFrame.from_records(
    #                 ({'id': g_id,
    #                   'qtl_id': qtl.i,
    #                   'dataset': qtl.dataset}
    #                  for (qtl, qtl_genes) in trait_genes
    #                  for g_id in qtl_genes))
    #
    #             # merge results with this and yield! :)
    #             df = pd.merge(df1, df2, on='id', how='inner')
    #             df.drop('id', axis=1, inplace=True)
    #             df.rename(columns={'xref_id': 'id'}, inplace=True)
    #             yield (trait, df)

    @lru_cache(None)
    def _propagate_through_hog(self, trait, hog, **kwargs):
        all_hog_genes = {g
                         for (_, genes) in self.__hog_genes
                         for g in genes}
        has_annots = any(filter(lambda ts:
                                any(filter(lambda t: t.id == trait,
                                           ts)),
                                hog.annots.annotations))

        if not has_annots and len(all_hog_genes) == 1:
            # No increase possible - skip. This is most likely situation
            return {}
        else:
            # Sort out annotations
            hog.annots.reset(id=trait)

            # Create gene_id: qtls - then do sorted() and take top
            annots = defaultdict(list)
            for (qtl, qtl_hog_genes) in self.__hog_genes:
                for g in qtl_hog_genes:
                    annots[g].append(qtl)
            annots = {k: sorted(v,
                                key=(lambda qtl: qtl.t.get_belief()),
                                reverse=True)[0].t
                      for (k, v) in annots.items()}

            # Might be able to do better here
            hog_genes = []
            for (g_id, t) in annots.items():
                hog_genes += hog.add_annotation(t, {g_id})

            # Propagate
            hog.propagate_up()
            hog.push_down()

            # Look at the increases
            trait_inc = {}
            for (g_id, g_node) in hog_genes:
                t = list(hog.annots.get(g_node))[0]
                trait_inc[g_id] = [(t.get_belief() -
                                    annots[g_id].get_belief()),
                                   t.relevant_genes]

            return trait_inc

    def _relevant_hogs(self, hogs, random=None, traits=None):
        '''
            Retreives the HOGs -> (term, gene) sets for ALL QTLs.
            Randomises them first if required.
        '''
        all_hogs = defaultdict(lambda: defaultdict(list))  # Term -> HOG -> list
        all_genes = defaultdict(list)

        for qtl in self.qtls(hogs):
            # Skip if not our trait to compute...
            if traits is not None and qtl.t.id not in traits:
                continue

            # Get relevant genes
            genes = qtl.genes if not random else qtl.random_region

            # Save the genes
            all_genes[qtl.t.id].append((qtl, genes))

            # Add genes per-HOG
            qtl_hogs = defaultdict(set)
            for g in filter(lambda g: g in hogs.gene_map, genes):
                qtl_hogs[hogs.gene_map[g]].add(g)

            # Save gene set in a global listing...
            for (hog, hog_genes) in qtl_hogs.items():
                all_hogs[qtl.t.id][hog].append((qtl, hog_genes))

        return map(lambda x: (x[0], all_genes[x[0]], x[1]),
                   all_hogs.items())

    def empirical_distribution(self, hogs, replicates=1000, traits=None):
        '''
            Computes the empirical distribution for a number of replicates

        '''
        # Needs to be based on the REAL length of all qtls put together, rather
        # than simply the genes returned. others == 0.0
        trait_qtl = defaultdict(list)
        for qtl in self.qtls(hogs):
            trait_qtl[qtl.t.id].append(qtl)

        trait_lengths = {t: sum(len(qtl) for qtl in qtls)
                         for (t, qtls) in trait_qtl.items()}
        distn = {t: np.zeros(((replicates * t_len),),
                             dtype=np.float16)
                 for (t, t_len) in trait_lengths.items()
                 if traits is None or t in traits}

        for i in tqdm(range(replicates),
                      desc='Calculating Empirical Distribution',
                      unit=' replicates'):
            for (trait, inc, genes) in self.compute_increases(hogs,
                                                              random=True,
                                                              traits=traits):
                # Need to add the extra for every gene in the genes pool.
                inc = np.array([inc[g][0] for (_, gs) in genes for g in gs],
                               dtype=np.float16)
                j = i * trait_lengths[trait]

                distn[trait][j:(j + len(inc))] = inc

        return distn


class QTL(object):
    '''
        QTL: store the information required to estimate the p value for the
        entries in this region.
    '''
    def __init__(self, dataset, locs, qtl, hogs):
        # Backup
        self.locs = locs
        self.dataset = dataset
        self.i = qtl['qtl_id']
        self.qtl = qtl
        self._hogs = hogs

    @lazy_property
    def genes(self):
        # Find our actual genes, etc.
        genes = set(self.locs.find(self.qtl['chr'],
                                   int(self.qtl['inf.Mbp'] * 1e6),
                                   int(self.qtl['sup.Mbp'] * 1e6)))
        assert (len(genes) > 0), 'No genes found for QTL {}.'.format(self.i)

        return genes

    @lazy_property
    def t(self):
        # Annotation term
        return AnnotationTerm(self.qtl['annot_id'],
                              'trait',
                              (1.0 / len(self)),
                              is_not=False,
                              source=SOURCE)

    def __len__(self):
        return len(self.genes)

    def _relevant_hogs(self, genes):
        '''
            Find the relevant HOGs for a set of genes.
        '''
        hogs = defaultdict(set)
        for g in filter(lambda g: g in self._hogs.gene_map, genes):
            hogs[self._hogs.gene_map[g]].add(g)

        return map(lambda h: (self._hogs.hogs[h[0]], h[1]),
                   hogs.items())

    @property
    def annotations(self):
        '''
            Return the actual set of annotations. Don't expand this to a
            dictionary like the GOA sets.
        '''
        return (self.t, self.genes, self._relevant_hogs(self.genes))

    def empirical_distribution(self, replicates=1000):
        '''
            Estimates an empirical distribution for a
        '''
        distn = np.zeros(((replicates * len(self)),), dtype=np.float16)
        for i in tqdm(range(replicates),
                      desc='Calculating Empirical Distribution',
                      unit=' replicates'):
            # Get the increases
            rand_inc = self.compute_increases(random=True)

            # Set the increases in distribution
            rand_inc = np.array([i[0] for i in rand_inc.values()],
                                dtype=np.float16)
            j = i * len(self)
            distn[j:(j + len(rand_inc))] = rand_inc
        return distn

    def compute_increases(self, random=None, with_p=None, replicates=1000):
        '''
            Computes the observed increases.
        '''
        genes = self.genes if not random else self.random_region
        inc = dict(map(lambda g: (g, [0.0, []]), genes))

        for (hog, hog_genes) in tqdm(self._relevant_hogs(genes),
                                     desc='Propagating',
                                     unit=' HOG',
                                     disable=random):
            has_annots = any(filter(lambda ts:
                                    any(filter(lambda t: t.id == self.t.id,
                                               ts)),
                                    hog.annots.annotations))
            if not has_annots and len(hog_genes) == 1:
                # No increase possible - skip. This is most likely situation...
                pass
            else:
                # Sort out annotations
                hog.annots.reset(id=self.t.id)
                hog.targets = hog_genes  # Set this for filtering shortcut
                hog_genes = hog.add_annotation(self.t, hog_genes)

                # Propagate
                hog.propagate_up()
                hog.push_down()

                # Look at the increases
                for (g_id, g_node) in hog_genes:
                    t = list(hog.annots.get(g_node))[0]
                    inc[g_id][0] = (t.get_belief() - self.t.get_belief())
                    inc[g_id][1] = t.relevant_genes

        if random:
            return inc
        else:
            def get_result_lines(g):
                (g_id, g_inc) = g
                z = {'id': g_id, 'inc': g_inc[0]}
                if g_inc[0] > 0:
                    for (source, gs) in g_inc[1].items():
                        y = (';'.join(map(self._hogs.species.get_xref,
                                          gs)) if g_inc[0] > 0 else '')
                        z['from-{}'.format(source)] = y
                for k in filter(lambda k: k not in z,
                                map(lambda x: 'from-{}'.format(x), SOURCE_IN_OUTPUT)):
                    z[k] = None
                return z

            df = pd.DataFrame.from_records(map(get_result_lines, inc.items()))
            
            if with_p and any(df.inc > 0):
                # Check that there's actually point in calculating the
                # empirical distribution & then do it...
                distn = self.empirical_distribution(replicates)

                dfs = []
                z = len(distn)
                for (inc, df) in df.sort_values('inc').groupby('inc'):
                    distn = distn[distn >= inc]
                    df['p'] = (len(distn) / z)
                    dfs.append(df)
                df = pd.concat(dfs)
            elif with_p:
                # No increase, p-value is 1.0
                df['p'] = 1.0

            return df

    @property
    def random_region(self):
        '''
            Return a random region with the HOGs.
        '''
        return set(self.locs.random_region(len(self)))
