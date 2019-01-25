from django.test import TestCase
from dmethylation.models import Region, CpG

from dgenome.tests.create_data import create_feature, create_transcript, create_genelocation
from dgenome.tests.create_data import create_gene, create_genome, create_chromosome
from .create_data import create_region, create_cpg
from .create_data import create_cpghastranscriptregions


class ModelViewTest(TestCase):
    '''
    Tests for Region
    '''

    def setUp(self):
        r = create_region(name='TSS1500')
        c = create_cpg(
            ilmnid="cg00035864",
            name="cg00035864",
            addressa_id=31729416,
            allelea_probeseq="AAAACACTAACAATCTTATCCACATAAACCCTTAAATTTATCTCAAATTC",
            addressb_id="",
            alleleb_probeseq="",
            infinium_design_type="II",
            next_base="",
            color_channel="",
            forward_sequence="AATCCAAAGATGATGGAGGAGTGCCCGCTCATGATGTGAAGTACCTGCTCAGCTGGA",
            genome_build="37.0",
            chr="Y",
            mapinfo=8553009,
            sourceseq="AGACACTAGCAGTCTTGTCCACATAGACCCTTGAATTTATCTCAAATTCG",
            chromosome_36="Y",
            coordinate_36=8613009,
            strand="F",
            probe_snps="",
            probe_snps_10="",
            random_loci=False,
            methyl27_loci=False,
            ucsc_refgene_name="TTTY18",
            ucsc_refgene_accession="NR_001550",
            ucsc_refgene_group="TSS1500",
            ucsc_cpg_islands_name="",
            relation_to_ucsc_cpg_island="",
            phantom="",
            dmr="",
            enhancer=True,
            hmm_island="",
            regulatory_feature_name="",
            regulatory_feature_group="",
            dhs=True)

        genome = create_genome(organism='human', chromosomes=22,
                               assembly='hg19', source='USCS')
        chr = create_chromosome(name="chr1", genome=genome)
        gen = create_gene(name="Gen1", chromosome=chr)
        create_genelocation(txstart=1, txend=10, cdsstart=3, cdsend=7, gene=gen)
        create_genelocation(txstart=11, txend=20, cdsstart=13, cdsend=17, gene=gen)
        trans = create_transcript(name="Trans1", strand='-', tss1500start=1707,
                                  tss200start=207, txstart=1, txend=20, cdsstart=3,
                                  cdsend=7, gene=gen)
        create_feature(feat_type='exon', start=1, end=5, transcript=trans)
        create_feature(feat_type='intron', start=6, end=8, transcript=trans)
        create_feature(feat_type='exon', start=9, end=10, transcript=trans)

        create_cpghastranscriptregions(region=r,
                                       cpg=c,
                                       transcript=trans)

    def test_region_model(self):
        region = Region.objects.get(name='TSS1500')
        self.assertEqual(region.name, 'TSS1500')

    def test_cpg_name(self):
        cpg = CpG.objects.get(name='cg00035864')
        self.assertEqual(cpg.ilmnid, 'cg00035864')

    def test_cpg_chr(self):
        cpg = CpG.objects.get(chr='Y', mapinfo=8553009)
        self.assertEqual(cpg.ilmnid, 'cg00035864')

    def test_cpghastranscriptregions(self):
        cpg = CpG.objects.get(chr='Y', mapinfo=8553009)
        cpg_region = cpg.cpghastranscriptregions_set.first()
        self.assertEqual(cpg_region.region.name, 'TSS1500')
        self.assertEqual(cpg_region.transcript.name, 'Trans1')
