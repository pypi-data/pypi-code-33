# To migrate the data from the defunct database
import os

from boto3.dynamodb.conditions import Key, Attr
from metagenomi.db import (olddb, testdb, dbconn)
from metagenomi.helpers import (to_int, to_decimal)
from metagenomi.helpers import in_db
from metagenomi.tasks.mapping import Mapping
from metagenomi.tasks.assemblystats import AssemblyStats
from metagenomi.tasks.prodigal import Prodigal


from metagenomi.models.assembly import Assembly
from metagenomi.helpers import download_file

import pandas as pd
import numpy as np


def get_sequence_parameters(sp):
    '''
    Return pandas dataframe of top 10 sequences and their parameters
    '''

    df = pd.DataFrame(sp)
    df['length'] = pd.to_numeric(df["length"])
    df['gc'] = pd.to_numeric(df["G+C"])
    df['non_ns'] = pd.to_numeric(df["Non-Ns"])
    df['sequence'] = df.index

    df = df.drop(columns=['G+C', 'Non-Ns'])

    return df.reset_index(drop=True)


def get_longest_contig(sp):
    df = get_sequence_parameters(sp)
    name = df['length'].idxmax()
    value = df['length'][name]
    return (name, value)


def get_end(s, sp):
    ls = s.split('-')
    # Last item in range
    if ls[1] == '':
        return get_longest_contig(sp)[1]
    else:
        return(int(ls[1]))


def get_length_distribution(ld, sp, as_df=True):
    '''
    Return pandas dataframe of length distributions
    '''

    if as_df:
        df = pd.DataFrame(ld)
        df['start'] = [int(i.split('-')[0]) for i in df['range']]
        df['end'] = [get_end(i, sp) for i in df['range']]

        cols = df.columns
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

        df = df.drop(columns=['range'])
        return df


def fix_prey_assembly(a, db=testdb):
    newd = {}
    newd['s3path'] = a['s3-path']
    newd['mgid'] = a['mg-identifier']
    newd['associated'] = {'sequencing': a['associated']['read']}

    assembly = Assembly(**newd, db=db)

    # Extras: Mappings
    if 'mapping' in a:
        newmappings = []
        for i in a['mapping']:
            newtask = {}
            newtask['cmd_run'] = i['cmd_run']
            newtask['jobid'] = 'None'

            newtask['aligned_mapq_greaterequal_10'] = to_int(i['aligned_mapq_greaterequal_10'])
            newtask['aligned_mapq_less_10'] = to_int(i['aligned_mapq_less_10'])
            newtask['percent_pairs'] = to_decimal(i['percent_pairs'])
            newtask['reads_per_sec'] = to_int(i['reads_per_sec'])
            newtask['seed_size'] = to_int(i['seed_size'])
            newtask['time_in_aligner_seconds'] = to_int(i['time_in_aligner_seconds'])
            newtask['too_short_or_too_many_nns'] = to_int(i['too_short_OR_too_many_NNs'])
            newtask['total_bases'] = to_int(i['total_bases'])
            newtask['total_reads'] = to_int(i['total_reads'])
            newtask['unaligned'] = to_int(i['unaligned'])
            newtask['reads_mapped'] = {'fwd': i['reads_mapped'][0],
                                       'rev': i['reads_mapped'][1]}
            newtask['reference'] = i['ref']

            newmappings.append(Mapping(assembly.mgid, **newtask))

        assembly.mappings = newmappings

    # AssemblyStats
    if 'megahit_metadata' in a:
        i = a['megahit_metadata']
        newtask = {}
        newtask['cmd_run'] = i['cmds_run']
        newtask['jobid'] = 'None'
        newtask['total_seqs'] = i['total_seqs']
        newtask['total_bps'] = i['total_bps']
        newtask['n50'] = i['n50']
        newtask['avg_sequence_len'] = i['avg_seq_len']
        newtask['assembler'] = 'megahit'

        sp = i['Sequence parameters']
        ld = i['Length distribution']

        newtask['sequence_parameters'] = get_sequence_parameters(sp).replace([np.nan, ''],
                                                   'None')
        newtask['length_distribution'] = get_length_distribution(ld, sp).replace([np.nan, ''],
                                                   'None')

        assembly.assembly_stats = AssemblyStats(assembly.mgid, **newtask)

    # Try to predict the prodigal stuff
    faa = f'{assembly.s3path}.genes.faa'
    ctgs = assembly.s3path.split('_min1000')[0]+'.fa'

    localfaa = download_file(faa, os.getcwd())
    localctgs = download_file(ctgs, os.getcwd())
    localpullseqctgs = download_file(assembly.s3path, os.getcwd())

    proteins_predicted = len([1 for line in open(localfaa) if line.startswith(">")])
    contigs_above_cutoff = len([1 for line in open(localpullseqctgs) if line.startswith(">")])
    all_contigs = len([1 for line in open(localctgs) if line.startswith(">")])

    os.remove(localfaa)
    os.remove(localctgs)
    os.remove(localpullseqctgs)

    newtask = {}
    newtask['cmd_run'] = 'None'
    newtask['jobid'] = 'None'
    newtask['mode'] = 'meta'
    newtask['pullseq_contigs'] = assembly.s3path
    newtask['protein_file'] = faa
    newtask['min_sequence_length'] = 1000
    newtask['proteins_predicted'] = proteins_predicted
    newtask['contigs_above_cutoff'] = contigs_above_cutoff
    newtask['contigs_below_cutoff'] = all_contigs - contigs_above_cutoff

    assembly.s3path = ctgs
    assembly.prodigal = Prodigal(assembly.mgid, **newtask)
    return assembly


def fix_prey_sample():
    pass


def main(project='PREY', db=testdb):
    preyitems = scan(olddb, filter_key='mg-identifier', filter_value=project)

    for i in preyitems[:2]:
        if 'assm' in i['mg-identifier']:
            if not in_db(i['mg-identifier'], db):
                print(i['mg-identifier'])
                newd = fix_prey_assembly(i, db=db)
                print(newd.db.table)
                newd.write(force=True, ignore_exceptions=True)
            # print(newd.db.table)


    # Step 1: pull everything from the old database in
    # project wise or object wise?
    # Should I do this in python???

    # Check if it

    # Step 2: for each project, munge the data

    # Step 3: Try to validate, check errors

    # Step 4:

def scan(db, filter_key=None, filter_value=None, comparison='contains'):
    """
    not currently in use
    """

    if filter_key and filter_value:
        if comparison == 'equals':
            filtering_exp = Key(filter_key).eq(filter_value)
        elif comparison == 'contains':
            filtering_exp = Attr(filter_key).contains(filter_value)

        response = db.table.scan(
            FilterExpression=filtering_exp)

    else:
        response = db.table.scan()

    items = response['Items']
    while True:
        print(len(response['Items']))
        if response.get('LastEvaluatedKey'):
            response = db.table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                FilterExpression=filtering_exp
                )
            items += response['Items']
        else:
            break

    return items

if __name__ == '__main__':
    main()
