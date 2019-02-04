import re
from django.db.models import Q

from dgenome.models import Gene, Transcript, Feature


def get_coordinates_chr(term):
    chr_query = False
    start = False
    end = False
    m = re.search('chr(\\d+):(\\d+)(-(\\d+))?', term)
    if m:
        start = int(m.group(2))
        if m.group(4):
            end = int(m.group(4))
        if start <= 0:
            start = 1
        chr_query = 'chr' + m.group(1)
    return chr_query, start, end


def get_coordinates_gene(term):
    chr_query = False
    start = False
    end = False
    queryset = Gene.objects.filter(name=term.upper())
    if queryset:
        g = queryset.first()
        location = g.genelocation_set.first()
        start = location.start_pos
        end = location.end_pos
        chr_query = g.chr
    return chr_query, start, end


def get_coordinates(term):
    chr_query, start, end = get_coordinates_chr(term)
    return chr_query, start, end


def get_genes(term):
    chr_query, txstart, txend = get_coordinates(term)
    if chr_query and txstart and txstart:
        return Gene.objects.filter(Q(chromosome__name=chr_query),
                                   Q(genelocation__txend__lte=txend,
                                     genelocation__txend__gte=txstart) |
                                   Q(genelocation__txstart__lte=txend,
                                     genelocation__txstart__gte=txstart) |
                                   Q(genelocation__txstart__lte=txstart,
                                     genelocation__txend__gte=txend)).distinct()
    return Gene.objects.filter(name=term.upper())


def transcript_queryset_to_list(queryset):
    transcripts = []
    for t in queryset:
        transcripts.append(t.id)
    return transcripts


def find_tss1500(chr, mapinfo):
    queryset = Transcript.objects.filter(
        Q(strand='+', gene__chromosome__name=chr,
          tss1500start__lte=mapinfo, tss200start__gt=mapinfo) |
        Q(strand='-', gene__chromosome__name=chr,
          tss200start__lt=mapinfo, tss1500start__gte=mapinfo))
    return transcript_queryset_to_list(queryset)


def find_tss200(chr, mapinfo):
    queryset = Transcript.objects.filter(
        Q(strand='+', gene__chromosome__name=chr,
          tss200start__lte=mapinfo, txstart__gt=mapinfo) |
        Q(strand='-', gene__chromosome__name=chr,
          txend__lt=mapinfo, tss200start__gte=mapinfo))
    return transcript_queryset_to_list(queryset)


def find_body(chr, mapinfo):
    queryset = Transcript.objects.filter(gene__chromosome__name=chr,
                                         txstart__lte=mapinfo, txend__gte=mapinfo)
    return transcript_queryset_to_list(queryset)


def find_5utr(chr, mapinfo):
    queryset = Transcript.objects.filter(
        Q(strand='+', gene__chromosome__name=chr,
          txstart__lte=mapinfo, cdsstart__gt=mapinfo, has_coding=True) |
        Q(strand='-', gene__chromosome__name=chr,
          cdsend__lt=mapinfo, txend__gte=mapinfo, has_coding=True))
    return transcript_queryset_to_list(queryset)


def find_3utr(chr, mapinfo):
    queryset = Transcript.objects.filter(
        Q(strand='+', gene__chromosome__name=chr,
          cdsend__lt=mapinfo, txend__gte=mapinfo, has_coding=True) |
        Q(strand='-', gene__chromosome__name=chr,
          txstart__lte=mapinfo, cdsstart__gt=mapinfo, has_coding=True))
    return transcript_queryset_to_list(queryset)


def find_1exon(chr, mapinfo):
    transcripts = []
    feats = Feature.objects.filter(transcript__gene__chromosome__name=chr,
                                   feat_type='exon', start__lte=mapinfo,
                                   end__gte=mapinfo)
    for f in feats:
        if (f.transcript.strand == '+' and f.transcript.feature_set.first() == f) or (
                f.transcript.strand == '-' and f.transcript.feature_set.last() == f):
            transcripts.append(f.transcript.id)
    return transcripts
