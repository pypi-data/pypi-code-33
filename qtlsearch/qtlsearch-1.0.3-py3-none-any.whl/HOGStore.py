#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains a class definition that
    enables the saving of HOG state (including the annotations) to a SQLite DB.

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
from .Annotations import Annotations
from property_manager import lazy_property
from tqdm import tqdm
import os
import logging
import pickle


LOG = logging.getLogger(__name__)


class HOGStore(object):
    def __init__(self, hog_parser, targets, show_progress=True, fn=None,
                 *args, **kwargs):
        '''
            If called without a filename, will create a temporary file that is
            deleted when python closes.
        '''
        if fn is None or not os.path.isfile(fn):
            self.hogs = {}
            self._add_hogs(hog_parser, targets, show_progress)
            self._add_annotations(hog_parser, *args, **kwargs)
        else:
            LOG.info('Loading QTLSearch DB.')
            with open(fn, 'rb') as fp:
                self.hogs = pickle.load(fp)
            LOG.info('Finished loading QTLSearch DB.')

        if fn is not None and not os.path.isfile(fn):
            LOG.info('Saving QTLSearch DB.')
            with open(fn, 'wb') as fp:
                pickle.dump(self.hogs, fp)
            LOG.info('Finished saving QTLSearch DB.')

        # Backup species
        self.species = hog_parser.species

    @lazy_property
    def gene_map(self):
        '''
            Create gene-map from gene ID to top level HOG ID.
        '''
        return {g: hog.id for hog in self.hogs.values() for g in hog.gene_ids}

    def _add_hogs(self, hog_parser, targets, show_progress=True):
        '''
            Save all the hogs from the passed iterable to the database.
        '''
        for hog in tqdm(hog_parser.HOGs(None, targets),
                        desc='Loading HOGs', unit=' HOGs',
                        miniters=0, mininterval=10, maxinterval=20,
                        disable=(not show_progress)):
            # Save in DB
            self.hogs[hog.id] = hog

            hog_parser.semaphore.release()

    def _add_annotations(self, hog_parser, *args, **kwargs):
        '''
            Add the annotations to the HOGs loaded.
        '''
        # Load the xrefs tables
        hog_parser.species.load_extra_xrefs(kwargs.get('xref_mappings'))

        # Load the annotations
        annots = Annotations(species=hog_parser.species,
                             relevant_genes=set(self.gene_map.keys()),
                             *args,
                             **kwargs)

        for hog in self.hogs.values():
            hog._load_annots(annots=annots, *args, **kwargs)
