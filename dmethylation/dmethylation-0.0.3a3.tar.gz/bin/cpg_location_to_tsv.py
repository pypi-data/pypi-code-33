#!/usr/bin/env python

import pandas
import django
import argparse

django.setup()

from dmethylation.models import CpG

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Export CpG locations to TSV')
    parser.add_argument('-o', help='Output TSV file', required=True)

    args = parser.parse_args()
    tsv_file = args.o

    data = []
    for c in CpG.objects.all():
        data.append([c.ilmnid, c.chr, c.mapinfo, c.name])
    df = pandas.DataFrame(data, columns=['ILMNID', 'CHR', 'MAPINFO', 'cpg'])
    df.to_csv(tsv_file, sep='\t', header=True, index=False)
