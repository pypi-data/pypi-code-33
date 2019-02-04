from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from .create_data import create_superuser
from .create_data import create_feature, create_transcript, create_genelocation
from .create_data import create_gene, create_genome, create_chromosome


class ViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser(username='admin',
                                     password='admin',
                                     email='admin@example.com')
        genome = create_genome(organism='human', chromosomes=22,
                               assembly='hg19', source='UCSC')
        chr = create_chromosome(name="chr1", genome=genome)
        gen = create_gene(name="Gen1", chromosome=chr)
        create_genelocation(txstart=1, txend=10, cdsstart=3, cdsend=7, gene=gen)
        create_genelocation(txstart=12, txend=22, cdsstart=14, cdsend=18, gene=gen)
        trans = create_transcript(name="Trans11", strand='-', tss1500start=1707,
                                  tss200start=207, txstart=1, txend=20, cdsstart=3,
                                  cdsend=7, gene=gen)
        create_feature(feat_type='exon', start=1, end=5, transcript=trans)
        create_feature(feat_type='intron', start=6, end=8, transcript=trans)
        create_feature(feat_type='exon', start=9, end=10, transcript=trans)

        gen = create_gene(name="Gen2", chromosome=chr)
        create_genelocation(txstart=6, txend=23, cdsstart=8, cdsend=18, gene=gen)
        trans = create_transcript(name="Trans21", strand='-', tss1500start=1707,
                                  tss200start=207, txstart=6, txend=23, cdsstart=8,
                                  cdsend=18, gene=gen)
        create_feature(feat_type='exon', start=6, end=9, transcript=trans)
        create_feature(feat_type='intron', start=10, end=15, transcript=trans)
        create_feature(feat_type='exon', start=16, end=23, transcript=trans)

    def test_health(self):
        response = self.client.get(reverse('dgenome:health'))
        self.assertEqual(response.status_code, 200)

    def test_chromosome_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dgenome:chromosome-list'),
                                   {'assembly': 'hg19'}, format='json')
        self.assertEqual(response.status_code, 200)
        for o in response.json():
            self.assertEqual(o['name'], 'chr1')

    def test_chromosome_name(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dgenome:chromosome-list'),
                                   {'assembly': 'hg19', 'name': 'chr1'}, format='json')
        self.assertEqual(response.status_code, 200)
        for o in response.json():
            self.assertEqual(o['name'], 'chr1')

    def test_gene_get_no_assembly(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dgenome:gene-list'),
                                   {'name': 'Gen1'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_gene_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dgenome:gene-list'),
                                   {'assembly': 'hg19', 'name': 'Gen1'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'Gen1')

    def test_gene_get_by_pos(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dgenome:gene-list'),
                                   {'assembly': 'hg19', 'chr': 'chr1:4-12'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        for o in response.json():
            f = False
            if o['name'] == 'Gen1':
                f = True
                self.assertEqual(len(o['genelocations']), 2)
            if o['name'] == 'Gen2':
                f = True
                self.assertEqual(len(o['genelocations']), 1)
            self.assertEqual(f, True)

    def test_transcripts_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dgenome:transcript-list'),
                                   {'assembly': 'hg19', 'name': 'Trans11'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for o in response.json():
            self.assertEqual(o['name'], 'Trans11')
