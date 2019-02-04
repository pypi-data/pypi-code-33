#!python

import sys
import json
import pandas
import django
import argparse

from django.core import management

django.setup()

from dgenome.models import Genome
from dgenome.models import Chromosome
from dgenome.models import Gene
from dgenome.models import Transcript
from dgenome.models import GeneLocation
from dgenome.models import Feature

from dgenome.serializers import ChromosomeSerializer
from dgenome.serializers import GeneSerializer
from dgenome.serializers import TranscriptSerializer
from dgenome.serializers import GeneLocationSerializer
from dgenome.serializers import FeatureSerializer


def insert_chromosomes(ref, genome, batch_size):
    print('Inserting Chromosome data')
    objects = []
    count = 0
    for c in ref[~ref[2].str.contains('_')][2].unique():
        objects.append(
            Chromosome(name=c, genome_id=genome.pk)
        )
        if len(objects) == batch_size:
            try:
                count += len(objects)
                print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count), end='\r')
                Chromosome.objects.bulk_create(objects)
                objects.clear()
            except:
                print('********************************************************************')
                for o in objects:
                    os = ChromosomeSerializer(o)
                    print(json.dumps(os.data, indent=4))
                    print('********************************************************************')
                sys.exit(-1)
    if objects:
        try:
            count += len(objects)
            print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count))
            Chromosome.objects.bulk_create(objects)
            objects.clear()
        except:
            print('********************************************************************')
            for o in objects:
                os = ChromosomeSerializer(o)
                print(json.dumps(os.data, indent=4))
                print('********************************************************************')
            sys.exit(-1)

    return {c.name: c.id for c in Chromosome.objects.all()}


def insert_genes(ref, chr_map, batch_size):
    print('Inserting Gene data')
    objects = []
    count = 0
    for c in chr_map:
        print('\nProcessing Chromosome: ' + c, end=' ')
        c_ref = ref[ref[2] == c][[12, 3]].drop_duplicates().sort_values(by=[12])
        cc_ref = c_ref.groupby(12, sort=False)[3].apply(''.join)
        cc_ref = cc_ref.to_frame()
        print(len(c_ref))
        for i, r in cc_ref.iterrows():
            objects.append(
                Gene(
                    name=i,
                    strand=r[3],
                    chromosome_id=chr_map[c]
                )
            )
            if len(objects) == batch_size:
                try:
                    count += len(objects)
                    print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count), end='\r')
                    Gene.objects.bulk_create(objects)
                    objects.clear()
                except:
                    print('********************************************************************')
                    for o in objects:
                        os = GeneSerializer(o)
                        print(json.dumps(os.data, indent=4))
                        print('********************************************************************')
                    sys.exit(-1)
    if objects:
        try:
            count += len(objects)
            print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count))
            Gene.objects.bulk_create(objects)
        except:
            print('********************************************************************')
            for o in objects:
                os = GeneSerializer(o)
                print(json.dumps(os.data, indent=4))
                print('********************************************************************')
            sys.exit(-1)

    return {g.chromosome.name + g.name: g.id for g in Gene.objects.all()}


def insert_transcripts(ref, chr_map, gene_map, batch_size):
    print('Inserting Transcript data')
    objects = []
    count = 0
    for c in chr_map:
        print('\nProcessing Chromosme: ' + c)
        c_ref = ref[ref[2] == c]
        for i, r in c_ref.iterrows():
            if r[3] == '+':
                tss200 = r[4] - 200
                tss1500 = tss200 - 1500
            else:
                tss200 = r[5] + 199
                tss1500 = tss200 + 1500
            cdsstart = r[6]
            cdsend = r[7]
            has_coding = False
            if cdsstart == cdsend:
                cdsstart -= 1
                cdsend -= 1
            else:
                cdsend -= 1
                has_coding = True
            objects.append(
                Transcript(
                    name=r[1],
                    strand=r[3],
                    tss1500start=tss1500,
                    tss200start=tss200,
                    txstart=r[4],
                    txend=r[5] - 1,
                    cdsstart=cdsstart,
                    cdsend=cdsend,
                    has_coding=has_coding,
                    gene_id=gene_map[c + r[12]]
                )
            )
            if len(objects) == batch_size:
                try:
                    count += len(objects)
                    print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count), end='\r')
                    Transcript.objects.bulk_create(objects)
                    objects.clear()
                except:
                    print('********************************************************************')
                    for o in objects:
                        os = TranscriptSerializer(o)
                        print(json.dumps(os.data, indent=4))
                        print('********************************************************************')
                    sys.exit(-1)
    if objects:
        try:
            count += len(objects)
            print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count))
            Transcript.objects.bulk_create(objects)
        except:
            print('********************************************************************')
            for o in objects:
                os = TranscriptSerializer(o)
                print(json.dumps(os.data, indent=4))
                print('********************************************************************')
            sys.exit(-1)

    return {t.name: t.id for t in Transcript.objects.all()}


def insert_features(ref, chr_map, trasc_map, batch_size):
    print('Inserting Feature data')
    objects = []
    count = 0
    for c in chr_map:
        print('\nProcessing Chromosme: ' + c)
        c_ref = ref[ref[2] == c]
        for i, r in c_ref.iterrows():
            exon_start = [int(l) for l in r[9].split(',') if l]
            exon_end = [int(l) - 1 for l in r[10].split(',') if l]
            if len(exon_start) != len(exon_end):
                raise ValueError('Different number of exon start and end coordinates')
            for i in range(len(exon_start)):
                objects.append(
                    Feature(
                        feat_type='exon',
                        start=exon_start[i],
                        end=exon_end[i],
                        transcript_id=trasc_map[r[1]]
                    )
                )
                if i < len(exon_start) - 1:
                    start = exon_end[i] + 1
                    end = exon_start[i + 1] - 1
                    objects.append(
                        Feature(
                            feat_type='intron',
                            start=start,
                            end=end,
                            transcript_id=trasc_map[r[1]]
                        )
                    )
                if len(objects) >= batch_size:
                    try:
                        count += len(objects)
                        print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count), end='\r')
                        Feature.objects.bulk_create(objects)
                        objects.clear()
                    except:
                        print('********************************************************************')
                        for o in objects:
                            os = FeatureSerializer(o)
                            print(json.dumps(os.data, indent=4))
                            print('********************************************************************')
                        sys.exit(-1)
    if objects:
        try:
            count += len(objects)
            print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count))
            Feature.objects.bulk_create(objects)
            objects.clear()
        except:
            print('********************************************************************')
            for o in objects:
                os = FeatureSerializer(o)
                print(json.dumps(os.data, indent=4))
                print('********************************************************************')
            sys.exit(-1)


def insert_gene_location(batch_size):
    print('Inserting Gene Location data')
    objects = []
    count = 0
    for g in Gene.objects.all():
        loc = []
        for t in g.transcript_set.all():
            if not loc:
                loc.append({'txstart': t.txstart, 'txend': t.txend,
                            'cdsstart': t.cdsstart, 'cdsend': t.cdsend})
            else:
                append = False
                for l in loc:
                    if t.txend < l['txstart'] or t.txstart > l['txend']:
                        append = True
                    else:
                        l['txstart'] = min(l['txstart'], t.txstart)
                        l['txend'] = max(l['txend'], t.txend)
                        l['cdsstart'] = min(l['cdsstart'], t.cdsstart)
                        l['cdsend'] = max(l['cdsend'], t.cdsend)
                        append = False
                        break
                if append:
                    loc.append({'txstart': t.txstart, 'txend': t.txend,
                                'cdsstart': t.cdsstart, 'cdsend': t.cdsend})
        for l in loc:
            objects.append(
                GeneLocation(
                    txstart=l['txstart'],
                    txend=l['txend'],
                    cdsstart=l['cdsstart'],
                    cdsend=l['cdsend'],
                    gene_id=g.pk
                )
            )
            if len(objects) == batch_size:
                try:
                    count += len(objects)
                    print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count), end='\r')
                    GeneLocation.objects.bulk_create(objects)
                    objects.clear()
                except:
                    print('********************************************************************')
                    for o in objects:
                        os = GeneLocationSerializer(o)
                        print(json.dumps(os.data, indent=4))
                        print('********************************************************************')
                    sys.exit(-1)
    if objects:
        try:
            count += len(objects)
            print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count))
            GeneLocation.objects.bulk_create(objects)
        except:
            print('********************************************************************')
            for o in objects:
                os = GeneLocationSerializer(o)
                print(json.dumps(os.data, indent=4))
                print('********************************************************************')
            sys.exit(-1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse and insert the UCSC GTF file in the database')
    parser.add_argument('-r', help='UCSC refGene.txt', required=True)
    parser.add_argument('-b', help='Batch size', required=True)
    parser.add_argument('-o', help='Organism', required=True)
    parser.add_argument('-c', help='Number of Chromosomes', required=True)
    parser.add_argument('-a', help='Assembly', required=True)
    parser.add_argument('-s', help='Genome source', required=True)

    args = parser.parse_args()
    ref_file = args.r
    batch_size = int(args.b)
    org = args.o
    chrs = int(args.c)
    assembly = args.a
    source = args.s

    management.call_command("makemigrations", "dgenome")
    management.call_command("migrate", "dgenome")

    genome = Genome.objects.create(organism=org, chromosomes=chrs, assembly=assembly, source=source)
    genome.save()

    print('Loading ref')
    ref = pandas.read_csv(ref_file, sep='\t', header=None)

    chr_map = insert_chromosomes(ref, genome, batch_size)
    gene_map = insert_genes(ref, chr_map, batch_size)
    trasc_map = insert_transcripts(ref, chr_map, gene_map, batch_size)
    insert_features(ref, chr_map, trasc_map, batch_size)
    insert_gene_location(batch_size)

    print('Genes: ' + str(Gene.objects.all().count()) + ' Locations: ' + str(GeneLocation.objects.all().count()))
    print('Transcripts: ' + str(Transcript.objects.all().count()))
    print('Features: ' + str(Feature.objects.all().count()))
