#!python

import pandas
import django
import argparse

django.setup()

from dmethylation.models import Region, CpGHasTranscriptRegions

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Export CpG locations to TSV')
    parser.add_argument('-o', help='Output TSV file', required=True)
    parser.add_argument('-r', help='Region name', required=True)

    args = parser.parse_args()
    tsv_file = args.o
    region_name = args.r

    data = []
    region = Region.objects.get(name=region_name)
    i = 0
    for c in CpGHasTranscriptRegions.objects.filter(region__pk=region.pk):
        data.append([region.name, c.cpg.name, c.transcript.gene.name])
        if i % 1000 == 0:
            print("%d" % (i), end='\r')
        i += 1
    print('CpGs in the region: ' + str(i))
    df = pandas.DataFrame(data, columns=['Region', 'cpg', 'Gene'])
    df = df.drop_duplicates()
    df.to_csv(tsv_file, sep='\t', header=True, index=False)
