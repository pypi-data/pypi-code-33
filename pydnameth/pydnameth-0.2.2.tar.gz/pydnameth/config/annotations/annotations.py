from pydnameth.config.common import CommonTypes


class Annotations:

    def __init__(self,
                 name='annotations',
                 exclude=CommonTypes.any.value,
                 cross_reactive=CommonTypes.any.value,
                 snp=CommonTypes.any.value,
                 chr=CommonTypes.any.value,
                 gene_region=CommonTypes.any.value,
                 geo=CommonTypes.any.value,
                 probe_class=CommonTypes.any.value
                 ):
        self.name = name
        self.exclude = exclude
        self.cross_reactive = cross_reactive
        self.snp = snp
        self.chr = chr
        self.gene_region = gene_region
        self.geo = geo
        self.probe_class = probe_class

    def __str__(self):
        return 'ex(' + self.exclude + ')' + '_' + \
               'CR(' + self.cross_reactive + ')' + '_' + \
               'SNP(' + self.snp + ')' + '_' + \
               'chr(' + self.chr + ')' + '_' + \
               'gene(' + self.gene_region + ')' + '_' + \
               'geo(' + self.geo + ')' + '_' + \
               'class(' + self.probe_class + ')'

