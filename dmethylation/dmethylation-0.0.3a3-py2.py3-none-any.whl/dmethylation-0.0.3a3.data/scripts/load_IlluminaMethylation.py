#!python

import sys
import pandas
import django
import argparse
import numpy as np

from django.core import management

django.setup()
management.call_command("makemigrations", "dmethylation")
management.call_command("migrate", "dmethylation")

from dgenome.models import Genome
from dgenome.utils import find_tss1500, find_tss200, find_body
from dgenome.utils import find_5utr, find_3utr, find_1exon
from dmethylation.models import Region, CpG
from dmethylation.models import CpGHasTranscriptRegions

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse and insert the Illumina HumanMethylation450k file in the database')
    parser.add_argument('-i', help='Illumina HumanMethylation450 CSV file', required=True)
    parser.add_argument('-b', help='Batch size', required=True)

    args = parser.parse_args()
    anno_file = args.i
    batch_size = int(args.b)

    genome = Genome.objects.all()
    if not genome:
        print('The genome should be inserted first using the load_genome_ucsc_refGenes.py script')
        sys.exit(-1)

    print('Loading CSV file')
    meth_annot = pandas.read_csv(anno_file, skiprows=7, low_memory=False)
    meth_annot = meth_annot.fillna('')
    meth_annot = meth_annot[meth_annot['MAPINFO'] != '']

    regions = ['TSS200', 'TSS1500', '3\'UTR', '5\'UTR', '1stExon', 'Body', 'ISLAND', 'NSHORE', 'SSHORE', 'NSHELF',
               'SSHELF']
    for r in regions:
        Region.objects.create(name=r)
    region_map = {r.name: r.id for r in Region.objects.all()}

    objects = []
    count = 0
    for i, r in meth_annot.iterrows():
        try:
            addressa_id = int(r['AddressB_ID'])
        except:
            addressa_id = np.nan
        try:
            coordinate_36 = int(r['Coordinate_36'])
        except:
            coordinate_36 = np.nan
        probe_snps = '' if 'Probe_SNPs' not in r else r['Probe_SNPs']
        probe_snps_10 = '' if 'Probe_SNPs_10' not in r else r['Probe_SNPs_10']
        phantom = '' if 'Phantom' not in r else r['Phantom']
        enhancer = False if 'Enhancer' not in r else (str(r['Enhancer']).lower() in ['true', '1'])
        dhs = False if 'DHS' not in r else (str(r['DHS']).lower() in ['true', '1'])
        try:
            mapinfo = int(r['MAPINFO'])
            objects.append(
                CpG(
                    ilmnid=r['IlmnID'],
                    name=r['Name'],
                    addressa_id=r['AddressA_ID'],
                    allelea_probeseq=r['AlleleA_ProbeSeq'],
                    addressb_id=addressa_id,
                    alleleb_probeseq=r['AlleleB_ProbeSeq'],
                    infinium_design_type=r['Infinium_Design_Type'],
                    next_base=r['Next_Base'],
                    color_channel=r['Color_Channel'],
                    forward_sequence=r['Forward_Sequence'],
                    genome_build=r['Genome_Build'],
                    chr=r['CHR'],
                    mapinfo=mapinfo,
                    sourceseq=r['SourceSeq'],
                    chromosome_36=r['Chromosome_36'],
                    coordinate_36=coordinate_36,
                    strand=r['Strand'],
                    probe_snps=probe_snps,
                    probe_snps_10=probe_snps_10,
                    random_loci=(str(r['Random_Loci']).lower() in ['true', '1']),
                    methyl27_loci=(str(r['Methyl27_Loci']).lower() in ['true', '1']),
                    ucsc_refgene_name=r['UCSC_RefGene_Name'],
                    ucsc_refgene_accession=r['UCSC_RefGene_Accession'],
                    ucsc_refgene_group=r['UCSC_RefGene_Group'],
                    ucsc_cpg_islands_name=r['UCSC_CpG_Islands_Name'],
                    relation_to_ucsc_cpg_island=r['Relation_to_UCSC_CpG_Island'],
                    phantom=phantom,
                    dmr=r['DMR'],
                    enhancer=enhancer,
                    hmm_island=r['HMM_Island'],
                    regulatory_feature_name=r['Regulatory_Feature_Name'],
                    regulatory_feature_group=r['Regulatory_Feature_Group'],
                    dhs=dhs
                )
            )
            if len(objects) == batch_size:
                try:
                    count += len(objects)
                    print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count), end='\r')
                    CpG.objects.bulk_create(objects)
                    objects.clear()
                except Exception as ex:
                    print('********************************************************************')
                    print(ex)
                    objects.clear()
                    print('********************************************************************')
                    break
        except:
            pass
    if objects:
        try:
            count += len(objects)
            print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count))
            CpG.objects.bulk_create(objects)
        except Exception as ex:
            print('********************************************************************')
            print(ex)
            objects.clear()
            print('********************************************************************')

    objects = []
    count = 0
    for c in CpG.objects.all():
        chr = 'chr' + c.chr
        tss1500 = find_tss1500(chr, c.mapinfo)
        for t in tss1500:
            objects.append(
                CpGHasTranscriptRegions(
                    cpg_id=c.id,
                    region_id=region_map['TSS1500'],
                    transcript_id=t
                )
            )
        tss200 = find_tss200(chr, c.mapinfo)
        for t in tss200:
            objects.append(
                CpGHasTranscriptRegions(
                    cpg_id=c.id,
                    region_id=region_map['TSS200'],
                    transcript_id=t
                )
            )
        trans = []
        utr5 = find_5utr(chr, c.mapinfo)
        trans = trans + list(set(utr5) - set(trans))
        for t in utr5:
            objects.append(
                CpGHasTranscriptRegions(
                    cpg_id=c.id,
                    region_id=region_map['5\'UTR'],
                    transcript_id=t
                )
            )
        utr3 = find_3utr(chr, c.mapinfo)
        trans = trans + list(set(utr3) - set(trans))
        for t in utr3:
            objects.append(
                CpGHasTranscriptRegions(
                    cpg_id=c.id,
                    region_id=region_map['3\'UTR'],
                    transcript_id=t
                )
            )
        exon1 = find_1exon(chr, c.mapinfo)
        trans = trans + list(set(exon1) - set(trans))
        for t in exon1:
            objects.append(
                CpGHasTranscriptRegions(
                    cpg_id=c.id,
                    region_id=region_map['1stExon'],
                    transcript_id=t
                )
            )
        body = find_body(chr, c.mapinfo)
        for t in body:
            if t not in trans:
                objects.append(
                    CpGHasTranscriptRegions(
                        cpg_id=c.id,
                        region_id=region_map['Body'],
                        transcript_id=t
                    )
                )
        if len(objects) >= batch_size:
            try:
                count += len(objects)
                print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count), end='\r')
                CpGHasTranscriptRegions.objects.bulk_create(objects)
                objects.clear()
            except Exception as ex:
                print('********************************************************************')
                print(ex)
                objects.clear()
                print('********************************************************************')
                break
    if objects:
        try:
            count += len(objects)
            print('Inserting ' + str(len(objects)) + ' Total inserted: ' + str(count))
            CpGHasTranscriptRegions.objects.bulk_create(objects)
        except Exception as ex:
            print('********************************************************************')
            print(ex)
            objects.clear()
            print('********************************************************************')

    print('Regions: ' + str(Region.objects.all().count()))
    print('Transcripts: ' + str(CpG.objects.all().count()))
    print('CpGHasTranscriptRegions: ' + str(CpGHasTranscriptRegions.objects.all().count()))
