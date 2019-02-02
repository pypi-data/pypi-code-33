from enum import Enum


class AnnotationKey(Enum):
    cpg = 'ID_REF'
    chr = 'CHR'
    map_info = 'MAPINFO'
    Probe_SNPs = 'Probe_SNPs'
    Probe_SNPs_10 = 'Probe_SNPs_10'
    gene = 'UCSC_REFGENE_NAME'
    probe_class = 'Class'
    geo = 'RELATION_TO_UCSC_CPG_ISLAND'
    bop = 'BOP'
    cross_reactive = 'CROSS_R'


class Exclude(Enum):
    cluster = 'cluster'


class CrossReactive(Enum):
    exclude = 'ex'


class SNP(Enum):
    exclude = 'ex'


class Chromosome(Enum):
    non_sex = 'NS'
    X = 'X'
    Y = 'Y'


class GeneRegion(Enum):
    yes = 'yes'
    no = 'no'


class Geo(Enum):
    shores = 'shores'
    shores_s = 'shores_s'
    shores_n = 'shores_n'
    islands = 'islands'
    islands_shores = 'islands_shores'


class ProbeClass(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    A_B = 'A_B'


__all__ = ['AnnotationKey', 'Exclude', 'CrossReactive', 'SNP', 'Chromosome', 'GeneRegion', 'Geo', 'ProbeClass']
