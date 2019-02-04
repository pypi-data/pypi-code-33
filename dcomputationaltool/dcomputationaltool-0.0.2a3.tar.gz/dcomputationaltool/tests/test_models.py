import os
from django.test import TestCase
from .create_data import create_computationaltool

from ..lib.computationaltools import insert_computationaltool_inputs
from ..models import ComputationalTool, ComputationalToolInput


class ModelsTestCase(TestCase):
    def setUp(self):
        cwl_location = 'file://' + os.getcwd() + '/dcomputationaltool/tests/cwl/tools/star.cwl'
        comptool = create_computationaltool(name='STAR',
                                            description='Aligner',
                                            cwl=cwl_location,
                                            author_name='Author',
                                            author_identifier='0001',
                                            author_email='author@mail.com',
                                            codeRepository='',
                                            license='https://spdx.org/licenses/OPL-1.0')
        insert_computationaltool_inputs(comptool)

    def test_computationaltool(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        self.assertEqual(str(comptool), 'STAR')
        self.assertEqual(len(comptool.computationaltoolcwlimport_set.all()), 0)
        for i in comptool.computationaltoolcwlimport_set.all():
            self.assertEqual(i.name, 'Docker YML')

    def test_computationaltool_input(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        self.assertEqual(len(comptool.computationaltoolinput_set.all()), 25)

    def test_computationaltool_input_stdout(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='out_stdout', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'string')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, False)
        self.assertEqual(comptoolinput.option, '')
        self.assertEqual(comptoolinput.doc, '')

    def test_computationaltool_input_threads(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='threads', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, False)
        self.assertEqual(comptoolinput.option, '--runThreadN')
        self.assertEqual(comptoolinput.doc, '')

    def test_computationaltool_input_readFilesCommand(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='readFilesCommand', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'string')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--readFilesCommand')
        self.assertEqual(comptoolinput.doc, '')

    def test_computationaltool_input_genomeDir(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='genomeDir', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'Directory')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, False)
        self.assertEqual(comptoolinput.option, '--genomeDir')
        self.assertEqual(comptoolinput.doc, '')

    def test_computationaltool_input_readFilesIn(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='readFilesIn', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'File')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, False)
        self.assertEqual(comptoolinput.option, '--readFilesIn')
        self.assertEqual(comptoolinput.doc,
                         'string(s): paths to files that contain '
                         'input read1 (and, if needed,  read2)')

    def test_computationaltool_input_readFilesIn_2(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='readFilesIn_2', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'File')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '')
        self.assertEqual(comptoolinput.doc,
                         'string(s): paths to files that contain input '
                         'read1 (and, if needed,  read2)')

    def test_computationaltool_input_outFileNamePrefix(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outFileNamePrefix', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'string')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, False)
        self.assertEqual(comptoolinput.option, '--outFileNamePrefix')
        self.assertEqual(comptoolinput.doc,
                         'string: output files name prefix (including full or relative '
                         'path). Can only be defined on the command line.')

    def test_computationaltool_input_limitOutSJcollapsed(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='limitOutSJcollapsed', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--limitOutSJcollapsed')
        self.assertEqual(comptoolinput.doc, '1000000 int>0:'
                                            ' max number of collapsed junctions')

    def test_computationaltool_input_limitSjdbInsertNsj(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='limitSjdbInsertNsj', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--limitSjdbInsertNsj')
        self.assertEqual(comptoolinput.doc, '1000000 int>=0: maximum number '
                                            'of junction to be inserted to the '
                                            'genome on the fly at the mapping '
                                            'stage, including those from '
                                            'annotations and those detected in '
                                            'the 1st step of the 2-pass run')

    def test_computationaltool_input_outFilterMultimapNmax(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outFilterMultimapNmax', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--outFilterMultimapNmax')
        self.assertEqual(comptoolinput.doc, '100 int: read alignments will be '
                                            'output only if the read maps '
                                            'fewer than this value, otherwise '
                                            'no alignments will be output')

    def test_computationaltool_input_outFilterMismatchNmax(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outFilterMismatchNmax', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--outFilterMismatchNmax')
        self.assertEqual(comptoolinput.doc, '33 int: alignment will be output '
                                            'only if it has fewer mismatches '
                                            'than this value')

    def test_computationaltool_input_outFilterMismatchNoverLmax(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outFilterMismatchNoverLmax',
            computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'float')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--outFilterMismatchNoverLmax')
        self.assertEqual(comptoolinput.doc, '0.3 int: alignment will be '
                                            'output only if its ratio of mismatches '
                                            'to *mapped* length is less '
                                            'than this value')

    def test_computationaltool_input_seedSearchStartLmax(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='seedSearchStartLmax', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--seedSearchStartLmax')
        self.assertEqual(comptoolinput.doc, '12 int>0: defines the search start '
                                            'point through the read - '
                                            'the read is split into pieces no '
                                            'longer than this value')

    def test_computationaltool_input_alignSJoverhangMin(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='alignSJoverhangMin', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--alignSJoverhangMin')
        self.assertEqual(comptoolinput.doc, '15 int>0: minimum overhang'
                                            ' (i.e. block size) for spliced alignments')

    def test_computationaltool_input_alignEndsType(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='alignEndsType', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'string')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--alignEndsType')
        self.assertEqual(comptoolinput.doc, 'Local string: type of read ends '
                                            'alignment Local           ... '
                                            'standard local alignment with '
                                            'soft-clipping allowed EndToEnd  '
                                            '      ... force end-to-end read '
                                            'alignment, do not soft-clip '
                                            'Extend5pOfRead1 ... fully extend '
                                            'only the 5p of the read1, all '
                                            'other ends: local alignment')

    def test_computationaltool_input_outFilterMatchNminOverLread(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outFilterMatchNminOverLread',
            computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'float')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--outFilterMatchNminOverLread')
        self.assertEqual(comptoolinput.doc, '0.0 float: outFilterMatchNmin '
                                            'normalized to read length '
                                            '(sum of mates\' lengths for paired-end reads)')

    def test_computationaltool_input_outFilterScoreMinOverLread(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outFilterScoreMinOverLread',
            computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'float')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--outFilterScoreMinOverLread')
        self.assertEqual(comptoolinput.doc, '0.3 float: outFilterScoreMin '
                                            'normalized to read '
                                            'length (sum of mates\' lengths '
                                            'for paired-end reads)')

    def test_computationaltool_input_winAnchorMultimapNmax(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='winAnchorMultimapNmax', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--winAnchorMultimapNmax')
        self.assertEqual(comptoolinput.doc, '50 int>0: max number of '
                                            'loci anchors are allowed to map to')

    def test_computationaltool_input_alignSJDBoverhangMin(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='alignSJDBoverhangMin', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'int')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--alignSJDBoverhangMin')
        self.assertEqual(comptoolinput.doc, '3 int>0: minimum overhang '
                                            '(i.e. block size) for annotated '
                                            '(sjdb) spliced alignments')

    def test_computationaltool_input_outFilterType(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outFilterType', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'string')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--outFilterType')
        self.assertEqual(comptoolinput.doc, 'Normal string: type of '
                                            'filtering Normal  ... '
                                            'standard filtering using '
                                            'only current alignment '
                                            'BySJout ... keep only those '
                                            'reads that contain junctions '
                                            'that passed filtering into SJ.out.tab')

    def test_computationaltool_input_limitGenomeGenerateRAM(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='limitGenomeGenerateRAM', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'float')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, True)
        self.assertEqual(comptoolinput.option, '--limitGenomeGenerateRAM')
        self.assertEqual(comptoolinput.doc, '31000000000 int>0: maximum '
                                            'available RAM '
                                            '(bytes) for genome generation')

    def test_computationaltool_input_twopassMode(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='twopassMode', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'string')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, False)
        self.assertEqual(comptoolinput.option, '--twopassMode')
        self.assertEqual(comptoolinput.doc, '')

    def test_computationaltool_input_outSAMtype(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outSAMtype', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'string')
        self.assertEqual(comptoolinput.array, True)
        self.assertEqual(comptoolinput.optional, False)
        self.assertEqual(comptoolinput.option, '--outSAMtype')
        self.assertEqual(comptoolinput.doc, '')

    def test_computationaltool_input_outStd(self):
        comptool = ComputationalTool.objects.get(name='STAR')
        comptoolinput = ComputationalToolInput.objects.get(
            name='outStd', computationaltool=comptool)
        self.assertEqual(comptoolinput.computationaltoolinputtype.type, 'string')
        self.assertEqual(comptoolinput.array, False)
        self.assertEqual(comptoolinput.optional, False)
        self.assertEqual(comptoolinput.option, '--outStd')
        self.assertEqual(comptoolinput.doc, '')
