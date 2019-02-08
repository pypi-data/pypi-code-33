#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains methods that override the
    HOGParser ones for HOGParser and HOG.

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
from .HOGAnnotations import HOGAnnotations
from .HOGParser import HOGParser as _HOGParser
from .HOGParser import HOG as _HOG
from copy import copy
import multiprocessing as mp


MAXQUEUE = 1000


class HOGParser(_HOGParser):
    '''
        Special HOGParser just for HOGPROP.
    '''
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super().__init__(kwargs['oxml'], *args, **kwargs)
        nthreads = kwargs.get('nthreads', 1)
        maxqueue = kwargs.get('maxqueue', MAXQUEUE)
        self.semaphore = mp.BoundedSemaphore(maxqueue * nthreads)

    def HOGs(self, annots, targets):
        self.kwargs['annots'] = annots
        self.targets = targets

        for hog in filter(lambda hog: (hog is not None), super().HOGs()):
            # Update targets
            if self.targets is None:
                pass
            else:
                self.targets -= hog.gene_ids

            # Get lock
            self.semaphore.acquire()
            yield hog

            if self.targets is None or len(self.targets) > 0:
                pass
            else:
                # Parsed all HOGs we care about. Done.
                break

    def _HOG(self, g):
        hog = HOG(g, self.targets, *self.args, **self.kwargs)
        return hog if not hog.skip else None


class HOG(_HOG):
    '''
        Special HOG just for HOGPROP.
    '''
    def __init__(self, el, targets, *args, **kwargs):
        super().__init__(el)
        self._target_check(targets)

        if not self.skip and kwargs.get('annots') is not None:
            self._load_annots(*args, **kwargs)

    def _load_annots(self, *args, **kwargs):
        self.annots = HOGAnnotations(self, *args, **kwargs)
        self._setup()

    def _target_check(self, targets):
        # Ensure HOG contains any desired targets. Don't care about other HOGs
        self.skip = (False if targets is None else
                     (len(targets & self.gene_ids) == 0))
        if self.skip:
            self.cleanup()

    def _setup(self):
        # Pass through some HOGAnnotations methods.
        self.propagate_up = self.annots.propagate_up
        self.push_down = self.annots.push_down
        self.results = self.annots.results
        self.save = self.annots.save_state

    def tostring(self, *args, **kwargs):
        '''
            Includes annotations in the XML and returns it as a string.
        '''
        if hasattr(self, 'annots'):
            self.annots.include_in_xml(delete=True)
        return super().tostring(*args, **kwargs)

    def __getstate__(self):
        # Get HOG state
        state = super().__getstate__()

        # DISABLED IN QTLSEARCH!
        # Ensure we cleanup the HOG to stop memory leak
        # self.cleanup()

        return state

    def __setstate__(self, state):
        # Recreate the annots object
        super().__setstate__(state)
        self.skip = False
        self.annots = HOGAnnotations(self)
        self._setup()

    def add_annotation(self, t, genes):
        '''
            Use this to add a term to any gene IDs listed that are present in
            this HOG.
        '''
        gene_nodes = list(map(lambda g: (g, self.get_gene(g)),
                              (set(genes) & self.gene_ids)))
        for (g_id, g) in gene_nodes:
            annots = self.annots.get(g)
            if annots is not None:
                # Blow up the annotations that exist and take the maximum term
                # if we have overlap.
                annots = {t1.id: t1 for t1 in annots}
                if (t.id not in annots) or (annots[t.id].get_belief() <
                                            t.get_belief()):
                    annots[t.id] = copy(t)
                    annots[t.id].set_relevant_genes((g_id, t.get_source()))
                annots = set(annots.values())
            else:
                t1 = copy(t)
                t1.set_relevant_genes((g_id, t.get_source()))
                annots = {t1}

            # Save in the node
            self.annots.update(annots, g)

        return gene_nodes

    def genes_with_annot(self):
        '''
            Returns a list of gene IDs that have annotations.
        '''
        return {int(g.attrib['id'])
                for g in self.geneRefs()
                if len(self.annots.get(g)) > 0}
