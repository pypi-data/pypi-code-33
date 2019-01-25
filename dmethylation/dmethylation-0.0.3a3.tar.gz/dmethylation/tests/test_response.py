from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from dgenome.tests.create_data import create_feature, create_transcript, create_genelocation
from dgenome.tests.create_data import create_gene, create_genome, create_chromosome
from .create_data import create_superuser
from .create_data import create_region, create_cpg
from .create_data import create_cpghastranscriptregions


class ResponseViewTest(TestCase):
    '''
    Tests for Region
    '''

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(username='admin',
                                     password='admin',
                                     email='admin@example.com')
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

    def test_health(self):
        response = self.client.get(reverse('dmethylation:health'))
        self.assertEqual(response.status_code, 200)

    def test_region_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dmethylation:region-list'),
                                   {'name': 'TSS1500'}, format='json')
        self.assertEqual(response.status_code, 200)
        for o in response.json():
            self.assertEqual(o['name'], 'TSS1500')

    def test_cpg_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dmethylation:cpg-list'),
                                   {'name': 'cg00035864'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['chr'], 'Y')
            self.assertEqual(o['mapinfo'], 8553009)

    def test_mapinfo_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dmethylation:cpg-list'),
                                   {'chr': 'Y', 'mapinfo': 8553009}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'cg00035864')
