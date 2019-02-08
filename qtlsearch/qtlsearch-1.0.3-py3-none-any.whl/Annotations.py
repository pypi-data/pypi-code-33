#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains definitions of a class which 
    holds generalised annotations.

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
from .OBOParser import ONTOLOGIES, ObsoleteOntologyTerm, UnknownOntologyTerm
from .parsers.utils import load_parser, get_ontology
from collections import defaultdict
from property_manager import lazy_property
import pandas as pd


# Hard-coded source enumeration - if this changes, pickles will likely fail.
SOURCE_INT_TO_STR = ['?', 'UNIPROT-GOA', 'CHEBI', 'STANDALONE', 'HOG',
                     'HOG-Basic1', 'HOG-Sum', 'HOG-Max', 'HOG-OneMax',
                     'HOG-Dist1', 'HOG-Dist2a', 'HOG-Dist2b', 'QTL']
SOURCE_STR_TO_INT = {b: a for (a, b) in enumerate(SOURCE_INT_TO_STR)}


class Annotations(object):
    '''
        This defines a structure to hold all our annotations.
    '''

    def __init__(self, annot_types, share_manager=None, *args, **kwargs):
        '''
            Initialise the annotations object.
        '''
        # Initialise annotations
        self.annotations = (dict() if share_manager is None else
                            share_manager.dict())

        # Annotation map.
        self._annot_map = kwargs.get('annotation_map')
        self._relevant_genes = kwargs.get('relevant_genes')

        parsers = []
        for ont in annot_types:
            # For each annotation type...
            parser = load_parser(ont).AnnotationParser(*args,
                                                       annot_map=self.annot_map,
                                                       **kwargs)
            parsers.append((ont, parser, get_ontology(ont, args)))

        # Import annotations
        self._import_entries(parsers)

    @lazy_property
    def annot_map(self):
        '''
            Load the annotation map.
        '''
        def more_specific(ont, i):
            if ont in ONTOLOGIES:
                yield from ONTOLOGIES[ont].children(
                    ONTOLOGIES[ont]._id_to_int(i), include_self=True)
            else:
                yield i

        if self._annot_map is None or self._annot_map is 'None':
            return None

        self.annot_map_ont = None
        mapping = defaultdict(lambda: defaultdict(list))
        for fn in self._annot_map:
            df = pd.read_csv(fn, sep='\t')
            annot_map_ont = list(df.keys())[0]
            if ((self.annot_map_ont is not None) and
                    (annot_map_ont != self.annot_map_ont)):
                raise ValueError('Not mapping to the same annotation type.')
            else:
                self.annot_map_ont = annot_map_ont

            for (_, r) in df.iterrows():
                y = r[self.annot_map_ont]
                for x in (set(df.keys()) - {self.annot_map_ont}):
                    if not pd.isnull(r[x]):
                        for i in more_specific(x, r[x]):
                            mapping[x][i].append(y)

        return mapping

    def print(self):
        '''
            Prints the annotations in the structure.
        '''
        if type(self.annotations) is dict:
            for (entry, annotations) in self.annotations.items():
                print('Entry {:s}'.format(str(entry)))
                for annot in annotations:
                    print(' - {:s}'.format(str(annot)))
        else:
            raise ValueError('Can\'t print shared annotations table.')

    def __getitem__(self, ids):
        '''
            Retrieve annotations of a list (i.e., group) of entries,
            or an individual ID by indexing the annotations object directly.
        '''
        return self.get(ids)

    def __iter__(self):
        yield from self.annotations.items()

    def get(self, ids):
        '''
            Retrieve annotations of a list (i.e., group) of entries,
            or an individual ID.
        '''
        if not isinstance(ids, list):
            ids = [ids]

        return {x: self.annotations[x]
                for x in ids
                if x in self.annotations}

    def _import_entries(self, parsers):
        '''
            Import all the annotation entries from annotations file.
        '''
        for (ont, parser, ontology) in parsers:
            for entry in parser():
                self._import_entry(ont, ontology, entry)

    def _import_entry(self, ont, ontology, entry):
        '''
            Imports a single entry.

            All entries are considered valid at the moment and rely on
            pre-processing of the annotations.
        '''
        # Extract parts of entry...
        try:
            entry_num = int(entry['entry_num'])
        except ValueError:
            entry_num = entry['entry_num']

        # Filter out irrelevant genes if setup as such...
        if ((self._relevant_genes is not None) and
                (entry_num not in self._relevant_genes)):
            return

        annot_ids = [entry['annot_id']]
        # Check that the annot_id is in DB
        if ontology is not None:
            try:
                ontology.get(annot_ids[0])
            except (ObsoleteOntologyTerm, UnknownOntologyTerm):
                return

        # Annotation ID -> trait ID mapping
        if self.annot_map is None:
            pass
        elif ont not in self.annot_map:
            # Print warning?
            return
        else:
            annot_ids = self.annot_map[ont].get(annot_ids[0])
            ont = self.annot_map_ont
            if (annot_ids is None) or len(annot_ids) == 0:
                return

        alpha = float(entry['alpha']) if 'alpha' in entry else 1.0
        is_not = (entry['is_not'] is True) if 'is_not' in entry else False
        source = entry['source'] if 'source' in entry else '?'

        for annot_id in annot_ids:
            # Form the term...
            t = AnnotationTerm(annot_id,
                               ont,
                               alpha,
                               is_not,
                               source=source)

            # Save the entry - need to do it this way due to DictProxy.
            if entry_num in self.annotations:
                d = self.annotations[entry_num]
                add_t = True
                for t1 in list(filter(lambda t1: t1.id == t.id, d)):
                    # Is this always
                    if t1.get_belief() >= t.get_belief():
                        add_t = False
                    else:
                        # Remove from d
                        d.remove(t1)

                if add_t:
                    d.add(t)
                    self.annotations[entry_num] = d
            else:
                self.annotations[entry_num] = {t}


class AnnotationTerm(object):
    '''
        This defines the structure of an annotation term.
    '''
    def __init__(self, id_, ont, alpha, is_not=None, source=None):
        '''
            Initialise the term.
        '''
        is_not = is_not if is_not is not None else False
        source = source if source is not None else '?'
        # Check the source is something we can enumerate, so can understand it
        # in the long term...
        if source in SOURCE_INT_TO_STR:
            self.source = SOURCE_STR_TO_INT[source]
        else:
            raise ValueError('Source unknown.', source)

        self.ont = ont

        # Save term
        self.id = id_

        # Backup this.
        self.is_not = is_not

        # Alpha HAS to be defined. It is determined either in the parser or
        # straight from the annotations file.
        self.alpha = alpha

        # Initialise the gene IDs that have contributed to this term...
        self.relevant_genes = defaultdict(set)

    def __eq__(self, other):
        '''
            Returns true if the two AnnotationTerms are equal.
        '''
        return (isinstance(other, AnnotationTerm) and
                self.id == other.id and
                self.source == other.source and
                self.is_not == other.is_not)

    def __neq__(self, other):
        '''
            Returns true if the AnnotationTerms are not equal.
        '''
        return not self.__eq__(other)

    def __str__(self):
        '''
            Returns identifier, etc.
        '''
        return '{:s} {:s}({:f})'.format(str(self.id),
                                        ('[NOT] ' if self.is_not else ''),
                                        self.alpha)

    def __hash__(self):
        '''
            Returns a unique hash of the element. This is why the equality
            testing above is important!
        '''
        return hash(repr(self))

    def add_relevant_gene(self, i, source=None):
        self.relevant_genes[source].add(i)

    def update_relevant_genes(self, s):
        for k in s.keys():
            self.relevant_genes[k].update(s[k])

    def set_relevant_genes(self, *s):
        self.relevant_genes = defaultdict(set)
        for z in s:
            self.add_relevant_gene(*z)

    def get_belief(self):
        '''
            Returns a level of belief in the annotation.
        '''
        return self.alpha

    def set_source(self, source):
        '''
            Sets the source to a new one.
        '''
        self.source = SOURCE_STR_TO_INT[source]

    def decay_belief(self, decay_rate=0.85):
        '''
            Decays the belief in this term by some rate (default==0.85)
        '''
        self.alpha *= decay_rate

    def add_belief(self, alpha_dt):
        '''
            Add belief to this term by some value.
        '''
        self.alpha += alpha_dt

    def set_belief(self, alpha):
        '''
            Set belief of this term to some value.
        '''
        self.alpha = alpha

    def get_source(self):
        '''
            Retrieves the source of the annotation.
        '''
        return SOURCE_INT_TO_STR[self.source]
