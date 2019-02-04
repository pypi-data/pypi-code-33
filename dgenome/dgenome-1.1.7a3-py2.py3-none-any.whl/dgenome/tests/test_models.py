from django.test import TestCase
from .create_data import create_feature, create_transcript, create_genelocation
from .create_data import create_gene, create_genome, create_chromosome

from dgenome.models import Chromosome, Gene, GeneLocation
from dgenome.models import Transcript


class ModelsTestCase(TestCase):
    def setUp(self):
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

    def test_chromosome_gene(self):
        chr = Chromosome.objects.get(name='chr1')
        self.assertEqual(str(chr), 'chr1')
        for g in chr.gene_set.all():
            self.assertEqual(g.name, 'Gen1')

    def test_chromosome_gene_relation(self):
        genes = Gene.objects.filter(chromosome__name='chr1')
        for g in genes:
            self.assertEqual(g.name, 'Gen1')

    def test_gene_chromosome(self):
        gen = Gene.objects.get(name="Gen1")
        self.assertEqual(gen.chromosome.name, 'chr1')
        self.assertEqual(str(gen), 'Gen1')

    def test_gene_location(self):
        gen = Gene.objects.get(name="Gen1")
        self.assertEqual(len(gen.genelocation_set.all()), 2)

    def test_location_gene(self):
        loc = GeneLocation.objects.get(txstart=11)
        self.assertEqual(loc.gene.name, 'Gen1')

    def test_transcript_gene(self):
        trans = Transcript.objects.get(txstart=1)
        self.assertEqual(trans.gene.name, 'Gen1')
        self.assertEqual(str(trans), 'Trans1')

    def test_gene_transcript(self):
        gen = Gene.objects.get(name="Gen1")
        for t in gen.transcript_set.all():
            self.assertEqual(t.name, 'Trans1')
