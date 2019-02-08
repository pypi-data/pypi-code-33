#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains functionality to download the
    required files to run QTLSearch.

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
from Bio.UniProt.GOA import GAF10FIELDS, GAF20FIELDS
from property_manager import lazy_property
from urllib.request import urlopen
from tqdm import tqdm
import datetime
import gzip
import logging
import os
import pandas as pd
import tables
import wget

from . import __copyright__
from ._utils import auto_open
from .main import main as main_inner
from .OMARestAPI import Client, ClientException


QTLSEARCH_FNS = {'species': 'species',
                 'hogs': 'oma-hogs.orthoXML.gz',
                 'xref-mapping': 'oma-uniprot.txt.gz',
                 'chebi': 'chebi.obo',
                 'chebi-annots': 'chebi-annots.tsv.gz',
                 'go': 'go.obo',
                 'go-annots': 'uniprot-goa-annots.gaf.gz',
                 'qtlsearch-db': 'qtlsearch.db'}


LOG = logging.getLogger(__name__)


def parse_arguments(argv, exe_name, desc):
    parser = ArgumentParser(prog=exe_name,
                            description=desc,
                            epilog=__copyright__)

    # OMA REST API / Database.
    parser.add_argument('--no_api_cache',
                        action='store_true',
                        help='Boolean whether to disable caching of API '
                             'calls.')
    parser.add_argument('--api_cache_path',
                        default='./api-cache',
                        help='Path to store OMA API cache.')
    parser.add_argument('--oma_version', default=None, type=str,
                        help='OMA version string, e.g. "All.Sep2014", so '
                             'as to enable the use of old releases. This '
                             'will download a VERY LARGE database file '
                             'instead of using the API.')

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
    parser.add_argument('--annotation_map', nargs='+', required=True,
                        help='Mapping from trait in QTL file to '
                             'annotation IDs (e.g., GO, ChEBI).')

    return parser.parse_args(argv)


def main(argv, exe_name, desc=''):
    args = parse_arguments(argv, exe_name, desc)
    os.makedirs(args.data_path, exist_ok=True)

    # Download everything
    download(args)

    main_inner(get_inner_arguments(args, db_only=True),
               exe_name,
               desc)


def get_inner_arguments(args, db_only, results=None):
    # Run
    fns = dict(map(lambda x: (x, os.path.join(args.data_path,
                                              QTLSEARCH_FNS[x])),
                   QTLSEARCH_FNS))
    gene_locs = list(map(lambda sp: os.path.join(fns['species'],
                                                 '{}.tsv.gz'.format(sp)),
                         args.species))

    argv = ['--oxml', fns['hogs'],
            '--xref_mappings', fns['xref-mapping'],
            '--cache_species',
            '--hogs_db', './qtlsearch.db',
            '--qtls', *args.qtl,
            '--gene_locations', *gene_locs,
            '--go_annots', fns['go-annots'],
            '--go_obo', fns['go'],
            '--go_annotfilter', 'trusted_plus_paint',
            '--chebi_annots', fns['chebi-annots'],
            '--chebi_obo', fns['chebi']]
    if db_only:
        argv += ['--annotation_map', *args.annotation_map]
        argv.append('--create_db_only')
    else:
        argv += ['--annotation_map', 'None']

    if results is not None:
        argv += ['--results', results]

    return argv


def download(args):
    with OMADownloader(cached=(not args.no_api_cache),
                       cache_path=args.api_cache_path,
                       data_path=args.data_path,
                       species=args.species,
                       version=args.oma_version) as oma:
        # Download the HOGs
        oma.get_hogs()

        # Get gene co-ordinates for required species
        oma.get_entries()

        # Get OMA x-ref mapping to UniProtKB
        oma.get_xrefs()

        # Download GO / GOA
        go = GODownloader(args.data_path, oma)
        go.download_ontology()
        go.download_annotations()

        # Download ChEBI / ChEBI x-refs to UniProtKB
        chebi = ChEBIDownloader(args.data_path, oma)
        chebi.download_ontology()
        chebi.download_xrefs()


class OMADatabase(object):
    def __init__(self, url, version, cached, cache_path):
        self.db_fn = os.path.join(cache_path,
                                  version + '-OmaServer.h5')
        self.cached = cached
        self.url = url

    @lazy_property
    def db(self):
        # Download the database
        if not os.path.isfile(self.db_fn):
            LOG.info('Downloading OMA Database.')
            wget.download(self.url, out=self.db_fn)
            LOG.info('[Done]')
        else:
            LOG.info('OMA Database already exists.')

        return tables.open_file(self.db_fn)

    def close(self):
        self.db.close()
        if not self.cached:
            os.remove(self.db_fn)

    def __enter__(self):
        return self.db

    def __exit__(self, *args):
        self.close()


class SpeciesError(Exception):
    pass


class OMADownloader(object):
    FNS = {'xref': 'oma-uniprot.txt.gz',
           'hogs': 'oma-hogs.orthoXML.gz',
           'db': 'OmaServer.h5'}

    def __init__(self, cached, cache_path, data_path, species, version=None):
        self.version = version
        self.data_path = data_path
        self._species = species
        self.df = None

        # Setup client. Check if version is the current version if set.
        self.client = Client(cached=cached, cache_path=cache_path)
        if not self.use_api:
            self.db = OMADatabase(self.get_url('db'),
                                  version,
                                  cached,
                                  cache_path)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if not self.use_api:
            self.db.close()

    @lazy_property
    def use_api(self):
        if self.version is None:
            return True
        else:
            return (self.version == self.client.oma_release)

    @lazy_property
    def base_download_url(self):
        if self.version is None:
            return 'https://omabrowser.org/All/'
        else:
            return 'https://omabrowser.org/{}/'.format(self.version)

    def get_url(self, t):
        return self.base_download_url + self.FNS[t]

    @lazy_property
    def species(self):
        if self.use_api:
            # Get the OMA species codes.
            species = set()
            for sp in self._species:
                try:
                    species.add(self.client.genomes.genome(sp).code)
                except ClientException:
                    raise SpeciesError('No such species in OMA: {}'.format(sp))
        else:
            species = set()
            tab = self.db.db.root.Genome
            for sp in self._species:
                x = tab.read_where('UniProtSpeciesCode == {}'
                                   .format(sp.encode('ascii')))
                if len(x) != 1:
                    raise SpeciesError('Species not found' if len(x) == 0
                                       else 'Multiple species matched.')
                species.add(x[0]['UniProtSpeciesCode'].decode('ascii'))
        return species

    def get_entries(self):
        # Download the entries (including co-ordinates)
        LOG.info('Downloading entries (including co-ordinates).')
        for sp in self.species:
            path = os.path.join(self.data_path, QTLSEARCH_FNS['species'])
            os.makedirs(path, exist_ok=True)
            fn = os.path.join(path, '{}.tsv.gz'.format(sp))

            if os.path.isfile(fn):
                LOG.info('{} already downloaded.'.format(sp))
                continue

            if self.use_api:
                df = pd.DataFrame.from_records(
                    ((e.omaid,
                      e.chromosome,
                      e.locus.start,
                      e.locus.end)
                     for e in self.client.genomes.proteins(sp,
                                                           progress=True)
                     if e.is_main_isoform),
                    columns=['id',
                             'chr',
                             'start',
                             'end'])
            else:
                x = self.db.db.root.Genome.read_where('UniProtSpeciesCode == {}'
                                                      .format(sp.encode('ascii')))
                offset = x['EntryOff'][0]
                tot = x['TotEntries'][0]
                ents = self.db.db.root.Protein.Entries[offset:(offset+tot-1)]
                df = pd.DataFrame(ents)

                # Drop alternative splicing variants
                df = df[(df.EntryNr == df.AltSpliceVariant) |
                        (df.AltSpliceVariant == 0)]

                def ent2id(x):
                    return '{}{:05d}'.format(sp, x - offset + 1)
                df['id'] = df.EntryNr.apply(ent2id)
                df = df[['id', 'Chromosome', 'LocusStart', 'LocusEnd']]
                df.rename(columns={'Chromosome': 'chr',
                                   'LocusStart': 'start',
                                   'LocusEnd': 'end'},
                          inplace=True)
                df.chr = df.chr.apply(lambda x: x.decode('ascii'))

            with auto_open(fn, 'wt') as fp:
                df.to_csv(fp, sep='\t', index=False, header=None)

    def get_hogs(self):
        # Download the HOGs
        hog_fn = os.path.join(self.data_path, QTLSEARCH_FNS['hogs'])
        if not os.path.isfile(hog_fn):
            LOG.info('Downloading OMA HOGs.')
            wget.download(self.get_url('hogs'), out=hog_fn)
            LOG.info('[Done]')
        else:
            LOG.info('OMA HOGs already exist.')
        return hog_fn

    @lazy_property
    def mapping_df(self):
        fn = os.path.join(self.data_path, QTLSEARCH_FNS['xref-mapping'])
        return pd.read_csv(fn,
                           sep='\t',
                           names=['oma', 'xref'])

    @lazy_property
    def uniprot_mapped_ids(self):
        return set(self.mapping_df['xref'])

    def get_xrefs(self):
        fn = os.path.join(self.data_path, QTLSEARCH_FNS['xref-mapping'])
        if not os.path.isfile(fn):
            LOG.info('Downloading OMA-UniProtKB mapping.')
            wget.download(self.get_url('xref'), out=fn)
            LOG.info('[Done]')
        else:
            LOG.info('OMA-UniProtKB mapping already exist.')


class GODownloader(object):
    GO_URL = 'http://purl.obolibrary.org/obo/go.obo'
    GOA_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/UNIPROT/' \
              'goa_uniprot_all.gaf.gz'
    GOA_CHUNKSIZE = int(5e6)

    def __init__(self, data_path, oma):
        self.data_path = data_path
        self.oma = oma

    def download_ontology(self):
        fn = os.path.join(self.data_path, QTLSEARCH_FNS['go'])
        if not os.path.isfile(fn):
            LOG.info('Downloading GO.')
            wget.download(self.GO_URL, out=fn)
            LOG.info('[Done]')
        else:
            LOG.info('GO already exists.')
        return fn

    def download_annotations(self):
        # Download and filter to the OMA mapping to cache. This way it can be
        # re-used.
        fn = os.path.join(self.data_path, QTLSEARCH_FNS['go-annots'])
        if not os.path.isfile(fn):
            LOG.info('Downloading and filtering GO annotations. '
                  '(This can take a very long time!)')
            with urlopen(self.GOA_URL) as res, \
                    gzip.GzipFile(fileobj=res, mode='r') as in_fp:
                gaf_version = in_fp.readline()  # TODO: fix for when not GAF2

                with auto_open(fn, 'wt') as out_fp:
                    date = datetime.datetime.now().isoformat()
                    out_fp.writelines([gaf_version.decode('ascii'),
                                       '!oma-filtered {}\n'.format(date)])

                    df_iter = pd.read_csv(in_fp,
                                          names=GAF20FIELDS,
                                          comment='!',
                                          sep='\t',
                                          dtype=str,
                                          chunksize=self.GOA_CHUNKSIZE)

                    with tqdm(desc='Filtering GOA') as pbar:
                        uniprot_ids = self.oma.uniprot_mapped_ids
                        for df in df_iter:
                            # Filter
                            df = df[df.DB_Object_ID.isin(uniprot_ids)]

                            # Write
                            df.to_csv(out_fp,
                                      sep='\t',
                                      header=None,
                                      index=False)

                            pbar.update(self.GOA_CHUNKSIZE)
        else:
            LOG.info('GO annotations already downloaded.')


class ChEBIDownloader(object):
    CHEBI_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo'
    CHEBI_XREF_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/' \
                     'Flat_file_tab_delimited/reference.tsv.gz'

    def __init__(self, data_path, oma):
        self.data_path = data_path
        self.oma = oma

    def download_ontology(self):
        fn = os.path.join(self.data_path, QTLSEARCH_FNS['chebi'])
        if not os.path.isfile(fn):
            LOG.info('Downloading ChEBI.')
            wget.download(self.CHEBI_URL, out=fn)
            LOG.info('[Done]')
        else:
            LOG.info('ChEBI already exists.')
        return fn

    def download_xrefs(self):
        fn = os.path.join(self.data_path, QTLSEARCH_FNS['chebi-annots'])
        if not os.path.isfile(fn):
            LOG.info('Downloading ChEBI xrefs.')
            with urlopen(self.CHEBI_XREF_URL) as res, \
                    gzip.GzipFile(fileobj=res, mode='r') as fp:
                chebi_df = pd.read_csv(fp,
                                       sep='\t',
                                       encoding='ISO-8859-1',
                                       dtype=str)

            # Filter down
            chebi_df = chebi_df[chebi_df.REFERENCE_DB_NAME == 'UniProt']
            uniprot_ids = self.oma.uniprot_mapped_ids
            chebi_df = chebi_df[chebi_df.REFERENCE_ID.isin(uniprot_ids)]

            with auto_open(fn, 'wt') as fp:
                chebi_df.to_csv(fp,
                                sep='\t',
                                index=False,
                                encoding='ISO-8859-1')
            with open('{}.date'.format(fn), 'wt') as fp:
                fp.write(datetime.datetime.now().isoformat() + '\n')
        else:
            LOG.info('ChEBI xrefs already downloaded.')
