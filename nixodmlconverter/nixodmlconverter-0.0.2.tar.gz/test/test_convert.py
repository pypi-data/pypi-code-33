import datetime
import os
import shutil
import tempfile
import unittest

import nixio as nix
import odml

from nixodmlconverter import convert

document_attributes = ['author', 'version', 'date', 'repository']
section_attributes = ['name', 'oid', 'definition', 'type', 'reference', 'repository',
                      # 'link', 'include'
                      ]
property_attributes = ['name', 'oid', 'definition', 'value', 'unit', 'reference',
                       'dependency', 'dependency_value', 'dtype', 'value_origin',
                       # the type conversion of the uncertainty is not solved yet.
                       # 'uncertainty',
                       ]


class TestBlock(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp("_odmlnix", "test_", tempfile.gettempdir())

        self.odml_doc = odml.Document(author='me', date=datetime.date.today(),
                                      version='0.0.1', repository='unknown')
        odml.Section(name='first section', definition='arbitrary definition',
                     type='testsection', parent=self.odml_doc, reference='reference 1',
                     repository='also unknown', link='???', include=False)

        odml.Property(name='first property', value=[1, 2, 3],
                      parent=self.odml_doc.sections[0],
                      unit='Volt', uncertainty=3, reference='still unknown',
                      definition='first property recorded', dependency='unknown',
                      dependency_value='also unknown', dtype='int', value_origin='ref 2')

    def tearDown(self):
        # cleanup temporary files and folder
        shutil.rmtree(self.test_dir)

    def test_double_conversion(self):
        nf = os.path.join(self.test_dir, 'tmp.nix')
        of = os.path.join(self.test_dir, 'tmp.odml')
        convert.nixwrite(self.odml_doc, nf, 'overwrite')
        nix_file = nix.File(nf)
        convert.odmlwrite(nix_file, of)
        odml_doc = odml.load(of)

        for attr in document_attributes:
            self.assertEqual(getattr(self.odml_doc, attr), getattr(odml_doc, attr))

        for sec in self.odml_doc.sections:
            sec2 = odml_doc.sections[sec.name]
            for attr in section_attributes:
                self.assertEqual(getattr(sec, attr), getattr(sec2, attr))

            for prop in sec.properties:
                prop2 = sec2.properties[prop.name]
                for attr in property_attributes:
                    self.assertEqual(getattr(prop, attr), getattr(prop2, attr))

        nix_file.close()
