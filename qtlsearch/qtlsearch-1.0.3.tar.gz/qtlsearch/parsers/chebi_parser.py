#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains a parser for the ChEBI cross
    reference file and yields dictionaries.

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
from ..OBOParser import OBO
from property_manager import lazy_property
from tqdm import tqdm
import pandas as pd


# Hard-coded information
SOURCE = 'CHEBI'
SUPPORTED_ONTOLOGIES = frozenset(['chebi'])
BELIEF = 1.0


class OntologyError(Exception):
    pass


def add_arguments(arg_parser):
    '''
        Adds arguments to overall program's parser.
    '''
    arg_parser.add_argument('--chebi_annots', default=None,
                            help='Path to the UniProt-GOA annotations file '
                                 'in GAF format.')
    arg_parser.add_argument('--chebi_obo', default=None,
                            help='Path to the GO OBO definition.')


def process_arguments(args, arg_parser):
    '''
        Post-processes arguments to the program.
    '''
    if args.chebi_annots is not None:
        if args.chebi_obo is None:
            arg_parser.error('ChEBI OBO not defined.')

        setattr(args, 'chebi_ontology', OBO(args.chebi_obo,
                                            store_as_int=True,
                                            ontology_name='chebi'))

        # Check that the OBO file given is the Gene Ontology
        if args.chebi_ontology.name.lower() not in SUPPORTED_ONTOLOGIES:
            raise OntologyError('ChEBI annotation reader only supports: {}'
                                .format(SUPPORTED_ONTOLOGIES))


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

        self.annots = kwargs['chebi_annots']
        self.ontology = kwargs['chebi_ontology']
        self.relevant_genes = kwargs.get('relevant_genes', None)

    @lazy_property
    def id_mapping(self):
        tab = self.species._extra_xrefs
        if self.relevant_genes is not None:
            z = set(map(self.species.get_xref, self.relevant_genes))
            return tab[tab['oma'].isin(z)]
        else:
            return tab

    def __call__(self):
        '''
            This yields entries, based on parsed annotations from a Uniprot GOA
            file.
        '''
        pbar_entries = tqdm(desc='Loading ChEBI xrefs', unit=' entries',
                            miniters=0, mininterval=1)

        # This is the reference.tsv.gz file. Header needs to be declared, as in
        # original file.
        try:
            df = pd.read_csv(self.annots, sep='\t')
        except UnicodeDecodeError:
            df = pd.read_csv(self.annots, sep='\t', encoding='ISO-8859-1')

        # Filter to UniProt
        df = df[df['REFERENCE_DB_NAME'] == 'UniProt'][['COMPOUND_ID',
                                                       'REFERENCE_ID']]
        df.rename(columns={'REFERENCE_ID': 'xref'}, inplace=True)
        df = pd.merge(df, self.id_mapping, left_on='xref', right_index=True,
                      how='inner', copy=False)

        for (_, r) in df.iterrows():
            annot_id = self.species.resolve_xref(r['oma'], _extra=None)
            chebi_id = r['COMPOUND_ID']

            if annot_id is not None and (self.ontology is None or chebi_id in
                                         self.ontology):
                # Valid entry - checked that GO ID is in the OBO.
                entry = {}
                if self.ontology is not None:
                    entry['annot_id'] = self.ontology._id_to_int(chebi_id)
                else:
                    entry['annot_id'] = chebi_id
                
                entry['entry_num'] = annot_id
                entry['is_not'] = False
                entry['alpha'] = BELIEF
                entry['source'] = SOURCE
                yield entry

                pbar_entries.update()

        # Finish progress bar for entries
        pbar_entries.close()
