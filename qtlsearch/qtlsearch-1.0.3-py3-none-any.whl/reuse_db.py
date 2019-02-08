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
from argparse import ArgumentParser
import os

from . import __copyright__
from .main import main as main_inner
from .download import get_inner_arguments


def parse_arguments(argv, exe_name, desc):
    parser = ArgumentParser(prog=exe_name,
                            description=desc,
                            epilog=__copyright__)

    parser.add_argument('--data_path',
                        default='./data',
                        help='Path to store downloaded data.')

    parser.add_argument('--species',
                        nargs='+', required=True,
                        help='Species to build DB for. Input as UniProt '
                             'species codes. Same order as --qtl.')
    parser.add_argument('--qtl', nargs='+', required=True,
                        help='List of paths to QTL files. Format: '
                             '<Term, Chromosome, Start (Mbp), End (Mbp)>.'
                             ' Same order as --species.')

    parser.add_argument('--db', required=True, default='./qtlsearch.db',
                        help='Path to QTLSearch DB.')

    # Flag to compute empirical distribution in order to compute p-values.
    parser.add_argument('--with_p', action='store_true',
                        help='Use if desire the empirical distribution '
                             'to compute p-values. Also set n_replicates.')
    parser.add_argument('--replicates', type=int, default=1000,
                        help='Number of randomisations when observing the '
                             'empirical distribution to estimate p '
                             'values.')

    # Results location
    parser.add_argument('--results', default='./results.tsv',
                        help='Path to results file (TSV).')

    return parser.parse_args(argv)


def main(argv, exe_name, desc=''):
    args = parse_arguments(argv, exe_name, desc)

    main_inner(get_inner_arguments(args, db_only=False, results=args.results),
               exe_name,
               desc)
