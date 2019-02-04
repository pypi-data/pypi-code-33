import os
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from .create_data import create_user
from .create_data import create_computationaltool
from ..lib.computationaltools import insert_computationaltool_inputs


class ViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(username='admin',
                                password='admin',
                                email='admin@example.com')
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

    def test_health(self):
        response = self.client.get(reverse('dcomputationaltool:health'))
        self.assertEqual(response.status_code, 200)

    def test_computationaltool(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]
        self.assertEqual(len(comptool['imports']), 0)
        self.assertEqual(len(comptool['inputs']), 25)

    def test_computationaltool_input_stdout(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'out_stdout':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'string')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], False)
                self.assertEqual(c['option'], '')
                self.assertEqual(c['doc'], '')
        self.assertEqual(i, 1)

    def test_computationaltool_input_threads(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'threads':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], False)
                self.assertEqual(c['option'], '--runThreadN')
                self.assertEqual(c['doc'], '')
        self.assertEqual(i, 1)

    def test_computationaltool_input_readFilesCommand(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'readFilesCommand':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'string')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--readFilesCommand')
                self.assertEqual(c['doc'], '')
        self.assertEqual(i, 1)

    def test_computationaltool_input_genomeDir(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'genomeDir':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'Directory')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], False)
                self.assertEqual(c['option'], '--genomeDir')
                self.assertEqual(c['doc'], '')
        self.assertEqual(i, 1)

    def test_computationaltool_input_readFilesIn(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'readFilesIn':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'File')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], False)
                self.assertEqual(c['option'], '--readFilesIn')
                self.assertEqual(c['doc'], 'string(s): paths to files that '
                                           'contain input read1 '
                                           '(and, if needed,  read2)')
        self.assertEqual(i, 1)

    def test_computationaltool_input_readFilesIn_2(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'readFilesIn_2':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'File')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '')
                self.assertEqual(c['doc'], 'string(s): paths to files that contain input '
                                           'read1 (and, if needed,  read2)')
        self.assertEqual(i, 1)

    def test_computationaltool_input_outFileNamePrefix(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outFileNamePrefix':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'string')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], False)
                self.assertEqual(c['option'], '--outFileNamePrefix')
                self.assertEqual(c['doc'], 'string: output files name'
                                           ' prefix (including full or relative '
                                           'path). Can only be defined'
                                           ' on the command line.')
        self.assertEqual(i, 1)

    def test_computationaltool_input_limitOutSJcollapsed(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'limitOutSJcollapsed':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--limitOutSJcollapsed')
                self.assertEqual(c['doc'], '1000000 int>0: max number of collapsed junctions')
        self.assertEqual(i, 1)

    def test_computationaltool_input_limitSjdbInsertNsj(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'limitSjdbInsertNsj':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--limitSjdbInsertNsj')
                self.assertEqual(c['doc'], '1000000 int>=0: maximum number of '
                                           'junction to be inserted to the '
                                           'genome on the fly at the mapping '
                                           'stage, including those from '
                                           'annotations and those detected in '
                                           'the 1st step of the 2-pass run')
        self.assertEqual(i, 1)

    def test_computationaltool_input_outFilterMultimapNmax(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outFilterMultimapNmax':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--outFilterMultimapNmax')
                self.assertEqual(c['doc'], '100 int: read alignments '
                                           'will be output only if the read maps '
                                           'fewer than this value, '
                                           'otherwise no alignments will be output')
        self.assertEqual(i, 1)

    def test_computationaltool_input_outFilterMismatchNmax(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outFilterMismatchNmax':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--outFilterMismatchNmax')
                self.assertEqual(c['doc'], '33 int: alignment will be output '
                                           'only if it has fewer mismatches '
                                           'than this value')
        self.assertEqual(i, 1)

    def test_computationaltool_input_outFilterMismatchNoverLmax(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outFilterMismatchNoverLmax':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'float')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--outFilterMismatchNoverLmax')
                self.assertEqual(c['doc'], '0.3 int: alignment will be '
                                           'output only if its ratio of mismatches '
                                           'to *mapped* length is less '
                                           'than this value')
        self.assertEqual(i, 1)

    def test_computationaltool_input_seedSearchStartLmax(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'seedSearchStartLmax':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--seedSearchStartLmax')
                self.assertEqual(c['doc'], '12 int>0: defines the search '
                                           'start point through the read - '
                                           'the read is split into pieces '
                                           'no longer than this value')
        self.assertEqual(i, 1)

    def test_computationaltool_input_alignSJoverhangMin(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'alignSJoverhangMin':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--alignSJoverhangMin')
                self.assertEqual(c['doc'], '15 int>0: minimum overhang'
                                           ' (i.e. block size) for spliced alignments')
        self.assertEqual(i, 1)

    def test_computationaltool_input_alignEndsType(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'alignEndsType':
                i += 1
                self.assertEqual(c['computationaltoolinputtype']['type'], 'string')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--alignEndsType')
                self.assertEqual(c['doc'], 'Local string: type of read ends '
                                           'alignment Local           ... '
                                           'standard local alignment with '
                                           'soft-clipping allowed EndToEnd  '
                                           '      ... force end-to-end read'
                                           ' alignment, do not soft-clip '
                                           'Extend5pOfRead1 ... fully extend '
                                           'only the 5p of the read1, all '
                                           'other ends: local alignment')
        self.assertEqual(i, 1)

    def test_computationaltool_input_outFilterMatchNminOverLread(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outFilterMatchNminOverLread':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'float')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--outFilterMatchNminOverLread')
                self.assertEqual(c['doc'], '0.0 float: outFilterMatchNmin '
                                           'normalized to read length '
                                           '(sum of mates\' lengths for '
                                           'paired-end reads)')
                i += 1
        self.assertEqual(i, 1)

    def test_computationaltool_input_outFilterScoreMinOverLread(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outFilterScoreMinOverLread':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'float')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--outFilterScoreMinOverLread')
                self.assertEqual(c['doc'], '0.3 float: outFilterScoreMin'
                                           ' normalized to read '
                                           'length (sum of mates\' lengths'
                                           ' for paired-end reads)')
                i += 1
        self.assertEqual(i, 1)

    def test_computationaltool_input_winAnchorMultimapNmax(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'winAnchorMultimapNmax':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--winAnchorMultimapNmax')
                self.assertEqual(c['doc'], '50 int>0: max number of '
                                           'loci anchors are allowed to map to')
                i += 1
        self.assertEqual(i, 1)

    def test_computationaltool_input_alignSJDBoverhangMin(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'alignSJDBoverhangMin':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'int')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--alignSJDBoverhangMin')
                self.assertEqual(c['doc'], '3 int>0: minimum overhang '
                                           '(i.e. block size) for annotated '
                                           '(sjdb) spliced alignments')
                i += 1
        self.assertEqual(i, 1)

    def test_computationaltool_input_outFilterType(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outFilterType':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'string')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--outFilterType')
                self.assertEqual(c['doc'], 'Normal string: type of filtering Normal  ... '
                                           'standard filtering using only current alignment '
                                           'BySJout ... keep only those'
                                           ' reads that contain junctions '
                                           'that passed filtering into SJ.out.tab')
                i += 1
        self.assertEqual(i, 1)

    def test_computationaltool_input_limitGenomeGenerateRAM(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'limitGenomeGenerateRAM':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'float')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], True)
                self.assertEqual(c['option'], '--limitGenomeGenerateRAM')
                self.assertEqual(c['doc'], '31000000000 int>0: maximum available RAM '
                                           '(bytes) for genome generation')
                i += 1
        self.assertEqual(i, 1)

    def test_computationaltool_input_twopassMode(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'twopassMode':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'string')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], False)
                self.assertEqual(c['option'], '--twopassMode')
                self.assertEqual(c['doc'], '')
                i += 1
        self.assertEqual(i, 1)

    def test_computationaltool_input_outSAMtype(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outSAMtype':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'string')
                self.assertEqual(c['array'], True)
                self.assertEqual(c['optional'], False)
                self.assertEqual(c['option'], '--outSAMtype')
                self.assertEqual(c['doc'], '')
                i += 1
        self.assertEqual(i, 1)

    def test_computationaltool_input_outStd(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('dcomputationaltool:computationaltool-list'), format='json')
        self.assertEqual(len(response.json()), 1)
        comptool = response.json()[0]['inputs']
        i = 0
        for c in comptool:
            if c['name'] == 'outStd':
                self.assertEqual(c['computationaltoolinputtype']['type'], 'string')
                self.assertEqual(c['array'], False)
                self.assertEqual(c['optional'], False)
                self.assertEqual(c['option'], '--outStd')
                self.assertEqual(c['doc'], '')
                i += 1
        self.assertEqual(i, 1)
