#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch.

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
from . import __copyright__, __version__
from .HOGStore import HOGStore
from .HOGParser_HOGPROP import HOGParser
from .parsers.utils import load_parser, PARSERS
from .QTLs import QTLs
from .strategies.utils import STRATEGY
from timeit import default_timer as timer
import argparse
import logging


LOG = logging.getLogger(__name__)


def parse_args(argv, exe_name, desc, strategy='sum'):
    '''
        Parses the arguments from the terminal.
    '''
    arg_parser = argparse.ArgumentParser(prog=exe_name,
                                         description=desc,
                                         epilog=__copyright__)

    # Add standard arguments
    arg_parser.add_argument('--output_path', default='.',
                            help='[Default is current directory] Path to '
                                 'output directory.')
    arg_parser.add_argument('--nthreads', type=int, default=1,
                            help='When set, at most n threads will be used to'
                                 ' propagate through HOGs')
    arg_parser.add_argument('--oxml', required=True,
                            help='Path to OrthoXML containing the HOGs.')
    arg_parser.add_argument('--is_not_oma', action='store_true',
                            help='Use if HOGs are not from OMA.')
    arg_parser.add_argument('--xref_mappings', nargs='*',
                            help='Paths to files containing mapping of format '
                                 '<HOG protId>[TAB]<Annotation ID>.')
    arg_parser.add_argument('--cache_species', action='store_true',
                            help='Use to cache the HOG species table as a '
                                 'pickle after the first load.')
    arg_parser.add_argument('--hogs_db', default='', type=str,
                            help='Path to HOG DB to save. Can be reused. If '
                                 'not set, temporary file used.')
    arg_parser.add_argument('--create_db_only', action='store_true',
                            help='Use if you only want to create and store '
                                 'the DB.')
    arg_parser.add_argument('--version', '-v', action='version',
                            help='Show version and exit.',
                            version=__version__)

    # QTLs and gene locations
    arg_parser.add_argument('--qtls', nargs='+', required=True,
                            help='List of paths to QTL files. Format: '
                                 '<Term, Chromosome, Start (Mbp), End (Mbp)>')
    arg_parser.add_argument('--gene_locations', nargs='+', required=True,
                            help='List of paths to Gene-Locations files. '
                                 'Format: '
                                 '<ID, Chromosome, Start (bp), End (bp)>')
    arg_parser.add_argument('--dataset_names', nargs='+', default=None,
                            help='List of names of the datasets for '
                                 'identification purposes.')
    # arg_parser.add_argument('--individually', action='store_true',
    #                         help='Use this if you wish to consider every QTL '
    #                              'individually.')
    # arg_parser.add_argument('--traits', nargs='*', type=int,
    #                         help='List of traits to work with in the '
    #                              'non-individual case.')

    # Flag to compute empirical distribution in order to compute p-values.
    arg_parser.add_argument('--with_p', action='store_true',
                            help='Use if desire the empirical distribution '
                                 'to compute p-values. Also set n_replicates.')
    arg_parser.add_argument('--replicates', type=int, default=1000,
                            help='Number of randomisations when observing the '
                                 'empirical distribution to estimate p '
                                 'values.')

    # Annotation types supported
    arg_parser.add_argument('--annotation_map', nargs='+', required=True,
                            help='Mapping from trait in QTL file to '
                                 'annotation IDs (e.g., GO, ChEBI).')

    # Results location
    arg_parser.add_argument('--results', default='./results.tsv',
                            help='Path to results file (TSV). Will print to '
                                 'stdout if not set.')

    for t in PARSERS:
        load_parser(t).add_arguments(arg_parser)

    # Add arguments for strategy
    STRATEGY.set_strategy(strategy)
    STRATEGY.get_strategy().add_arguments(arg_parser)

    # Parse the arguments.
    args = arg_parser.parse_args(argv)
    if args.nthreads < 1:
        setattr(args, 'nthreads', 1)

    # Do some annotation checks
    setattr(args,
            'annot_types',
            list(filter(lambda t: (getattr(args, t + '_annots') is not None),
                        PARSERS)))

    if len(args.annot_types) == 0:
        arg_parser.error('No annotations input.')

    # Process arguments
    for t in args.annot_types:
        load_parser(t).process_arguments(args, arg_parser)

    # Save strategy arguments
    STRATEGY.get_strategy().save_arguments(args)

    return args


def main(argv, exe_name, desc=''):
    t1 = timer()
    args = parse_args(argv, exe_name, desc)

    with HOGParser(is_oma=True,
                   noload_annots=True,
                   **vars(args)) as hog_parser:
        # Load the QTLs object
        qtls = QTLs(hog_parser.species,
                    args.gene_locations,
                    args.qtls,
                    args.dataset_names)

        # Target set
        targets = (qtls.targets if (not args.with_p) else qtls.all_genes)

        # Load HOGs
        hogs = HOGStore(hog_parser, targets,
                        show_progress=True,
                        fn=args.hogs_db,
                        **vars(args))
        if not args.create_db_only:
            # Predict on these HOGs.
            res = qtls.predict(hogs,
                               with_p=args.with_p,
                               replicates=args.replicates,
                               individually=True)
            #                    individually=args.individually,
            #                    traits=args.traits)

            # Write to file.
            res.to_csv(args.results, sep='\t', index=False)

    LOG.info('Time taken {}'.format(timer() - t1))
