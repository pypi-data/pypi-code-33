#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains a parser for the UniProt-GOA
    GAF files and yields dictionaries.

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
from .._utils import auto_open
from ..OBOParser import OBO
from Bio.UniProt.GOA import GAF10FIELDS, GAF20FIELDS
from enum import Enum
from functools import partial
from property_manager import lazy_property
from tqdm import tqdm
import pandas as pd
import re


# GOA things
GOA_VERSION_PATTERN = re.compile('!gaf-version: (?P<version>\d.\d)')
GOA_CHUNKSIZE = int(1e6)


# Hard-coded information
SOURCE = 'UNIPROT-GOA'
GO_EXP_EV_CODES = frozenset(['EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP'])
GO_IEA_TRUSTED_REF_CODES = frozenset([2, 3, 4, 23, 37, 38, 39, 40, 42, 45, 46])
GO_PAINT_EV_CODES = frozenset(['IBA', 'IBD'])
SUPPORTED_ONTOLOGIES = frozenset(['go'])
EXPERIMENTAL_BELIEF = 1.0
TRUSTED_BELIEF = 0.95


class Belief(Enum):
    EXPERIMENTAL = 1
    TRUSTED = 2


def get_belief(belief_type):
    if belief_type is Belief.TRUSTED:
        return TRUSTED_BELIEF
    elif belief_type is Belief.EXPERIMENTAL:
        return EXPERIMENTAL_BELIEF
    else:
        raise ValueError('Unknown belief encountered')


class OntologyError(Exception):
    pass


def add_arguments(arg_parser):
    '''
        Adds arguments to overall program's parser.
    '''
    arg_parser.add_argument('--go_annots', default=None,
                            help='Path to the UniProt-GOA annotations file '
                                 'in GAF format.')
    arg_parser.add_argument('--go_obo', default=None,
                            help='Path to the GO OBO definition.')
    arg_parser.add_argument('--go_annotfilter', default='experimental',
                            choices=[x for (x, y) in GOFilters.__dict__.items()
                                     if type(y) == classmethod],
                            help='Filter for annotations from input GAF')


def process_arguments(args, arg_parser):
    '''
        Post-processes arguments to the program.
    '''
    if args.go_annots is not None:
        if args.go_obo is None:
            arg_parser.error('GO OBO not defined.')

        setattr(args, 'go_ontology', OBO(args.go_obo,
                                         store_as_int=True,
                                         ontology_name='go'))

        # Check that the OBO file given is the Gene Ontology
        if args.go_ontology.name.lower() not in SUPPORTED_ONTOLOGIES:
            raise OntologyError('GAF annotation reader only supports: {}'
                                .format(SUPPORTED_ONTOLOGIES))


def _parse_gaf_chunk(chunk, ontology=None, terms=None, filter_func=None,
                     id_mapping=None, relevant_genes=None, relevant_terms=None):
    def split_field(chunk, f):
        f = chunk.keys()[f]
        chunk[f] = chunk[f].apply(lambda x: (x.split('|') if type(x) is str
                                             else []))

    for f in [3, 5, 7, 10, 12]:
        split_field(chunk, f)
    if len(chunk.keys()) > 15:
        for f in [15, 16]:
            split_field(chunk, f)

    if id_mapping is not None:
        # Map these using the table passed.
        chunk.rename(columns={'DB_Object_ID': 'xref'}, inplace=True)
        chunk = pd.merge(chunk, id_mapping,
                         left_on='xref', right_index=True,
                         how='inner', copy=False)
        chunk.drop('xref', axis=1, inplace=True)
        chunk.rename(columns={'oma': 'DB_Object_ID'}, inplace=True)

    if terms is not None:
        chunk = chunk[chunk['GO_ID'].isin(terms)]

    filter_func = (filter_func if filter_func is not None else
                   getattr(GOFilters, 'all'))

    if len(chunk) > 0:
        chunk['belief'] = chunk.apply(filter_func, axis=1)
        chunk = chunk[~chunk['belief'].isnull()]

    if ontology is not None and ontology._store_as_int:
        chunk['GO_ID'] = chunk['GO_ID'].apply(ontology._id_to_int)

    # Filter to the relevant terms
    if relevant_terms is not None:
        chunk = chunk[chunk['GO_ID'].isin(relevant_terms)]

    return chunk


def gaf_parser(fn, ontology=None, **kwargs):
    '''
        Parser for a GAF file, making use of the BioPython gafiterator and
        pre-filtering using a filter function if required.
    '''
    with auto_open(fn, 'rt') as fp:
        for (i, line) in enumerate(fp):
            m = GOA_VERSION_PATTERN.match(line)
            if m is not None:
                version = float(m['version'])
                break

            if i > 1000:
                raise ValueError('GOA file doesn\'t contain version line in top'
                                 ' 1000 lines.')
    # Filtering set for valid terms
    terms = None if ontology is None else set(map(str, ontology))

    # This is currently as limited as BioPython reader.
    header = GAF10FIELDS if version < 2 else GAF20FIELDS
    for chunk in pd.read_csv(fn, sep='\t', comment='!', names=header,
                             chunksize=GOA_CHUNKSIZE, dtype=str):
        yield from map(lambda x: x[1], _parse_gaf_chunk(chunk,
                                                        ontology=ontology,
                                                        terms=terms,
                                                        **kwargs).iterrows())


class GOFilters(object):
    @classmethod
    def experimental(cls, annot):
        '''
            Filter function for GO experimental annotations.
        '''
        return (None if not (annot['Evidence'].upper() in GO_EXP_EV_CODES) else
                Belief.EXPERIMENTAL)

    @classmethod
    def all(cls, annot):
        ev_code = annot['Evidence'].upper()
        return (Belief.TRUSTED if ev_code not in GO_EXP_EV_CODES else
                Belief.EXPERIMENTAL)

    @classmethod
    def all_exceptiea(cls, annot):
        '''
            Filter function for all GO annotations except IEA.
        '''
        ev_code = annot['Evidence'].upper()
        if ev_code == 'IEA':
            return None
        elif ev_code != 'NR':
            return (Belief.TRUSTED if ev_code not in GO_EXP_EV_CODES else
                    Belief.EXPERIMENTAL)
        else:
            return None

    @classmethod
    def all_onlyieatrusted(cls, annot):
        '''
            Filter function for all GO annotations, except for untrusted IEA.
        '''
        ev_code = annot['Evidence'].upper()
        ref_codes = [ref.upper().split(':') for ref in annot['DB:Reference']]

        if ev_code != 'NR':
            if ev_code == 'IEA':
                return (None if not any(ref_code[0] == 'GO_REF' and
                                        int(ref_code[1]) in
                                        GO_IEA_TRUSTED_REF_CODES
                                        for ref_code in ref_codes) else
                        Belief.TRUSTED)
            else:
                return (Belief.TRUSTED if ev_code not in GO_EXP_EV_CODES else
                        Belief.EXPERIMENTAL)
        else:
            return None

    @classmethod
    def trusted(cls, annot):
        '''
            Filter function for GO experimental and "trusted" annotations.
            Takes some "trusted" IEA reference codes, plus some TAS codes.
        '''
        ev_code = annot['Evidence'].upper()
        ref_codes = [ref.upper().split(':') for ref in annot['DB:Reference']]

        is_iea_trusted = (ev_code == 'IEA' and
                          any(ref_code[0] == 'GO_REF' and
                              int(ref_code[1]) in GO_IEA_TRUSTED_REF_CODES
                              for ref_code in ref_codes))
        is_reactome = (ev_code == 'TAS' and
                       any(ref_code[0] == 'REACTOME'
                           for ref_code in ref_codes))
        is_exp = (ev_code in GO_EXP_EV_CODES)

        if not (is_iea_trusted or is_reactome or is_exp):
            return None
        elif not is_exp:
            return Belief.TRUSTED
        else:
            return Belief.EXPERIMENTAL

    @classmethod
    def trusted_plus_paint(cls, annot):
        '''
            Filter function for GO experimental and "trusted" annotations.
            Takes some "trusted" IEA reference codes, plus some TAS codes.

            This also takes those inferred by PAINT.
        '''
        ev_code = annot['Evidence'].upper()
        ref_codes = [ref.upper().split(':') for ref in annot['DB:Reference']]

        is_iea_trusted = (ev_code == 'IEA' and
                          any(ref_code[0] == 'GO_REF' and
                              int(ref_code[1]) in GO_IEA_TRUSTED_REF_CODES
                              for ref_code in ref_codes))
        is_reactome = (ev_code == 'TAS' and
                       any(ref_code[0] == 'REACTOME'
                           for ref_code in ref_codes))
        is_paint = (ev_code in GO_PAINT_EV_CODES and
                    any(ref_code[0] == 'GO_REF' and
                        int(ref_code[1]) == 33
                        for ref_code in ref_codes))
        is_exp = (ev_code in GO_EXP_EV_CODES)

        if not (is_iea_trusted or is_reactome or is_paint or is_exp):
            return None
        elif not is_exp:
            return Belief.TRUSTED
        else:
            return Belief.EXPERIMENTAL


class AnnotationParser(object):
    '''
        This defines the annotation parser for GAF based annotations.
        TODO: generalise this so that it will definitely work for ontologies
        other than the GO.
    '''
    def __init__(self, **kwargs):
        '''
            Initialise the AnnotationParser.
        '''
        # Backup required arguments
        self.species = kwargs['species']

        self.annots = kwargs['go_annots']
        self.ontology = kwargs['go_ontology']
        self.annot_filter = kwargs['go_annotfilter']

        self.relevant_genes = kwargs.get('relevant_genes', None)
        self.annot_map = kwargs.get('annot_map', None)

        self.resolve_xref = partial(self.species.resolve_xref, _extra=False)

    @lazy_property
    def relevant_terms(self):
        if self.annot_map is not None:
            return set(self.annot_map['go'].keys())
        else:
            return None

    @lazy_property
    def id_mapping(self):
        if not hasattr(self.species, '_extra_xrefs'):
            return None
        tab = self.species._extra_xrefs
        tab['entry_num'] = tab['oma'].apply(self.resolve_xref)
        if self.relevant_genes is not None:
            tab = tab[tab['entry_num'].isin(self.relevant_genes)]
        return tab

    def __call__(self):
        '''
            This yields entries, based on parsed annotations from a Uniprot GOA
            file.
        '''
        filter_func = getattr(GOFilters, self.annot_filter)
        for annot in tqdm(gaf_parser(self.annots,
                                     filter_func=filter_func,
                                     id_mapping=self.id_mapping,
                                     ontology=self.ontology,
                                     relevant_genes=self.relevant_genes,
                                     relevant_terms=self.relevant_terms),
                          desc='Loading GO Annotations',
                          unit=' entries',
                          miniters=0,
                          mininterval=1):
            i = (annot['entry_num'] if 'entry_num' in annot else
                 self.resolve_xref(annot['DB_Object_ID']))
            if i is not None:
                yield {'entry_num': i,
                       'alpha': get_belief(annot['belief']),
                       'annot_id': annot['GO_ID'],
                       'is_not': ('not' in
                                  {q.lower() for q in annot['Qualifier']}),
                       'source': SOURCE}
