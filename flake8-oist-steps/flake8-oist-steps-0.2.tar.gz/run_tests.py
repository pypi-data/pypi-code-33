# -*- coding: utf-8 -*-
import ast
import unittest

from flake8_oist_steps import IdChecker


class TestBuiltins(unittest.TestCase):
    def assert_codes(self, ret, codes):
        self.assertEqual(len(ret), len(codes))
        for item, code in zip(ret, codes):
            self.assertTrue(item[2].startswith(code + ' '))

    def test_mesh_findTetByPoint(self):
        tree = ast.parse(
            'import steps.utilities.meshio as smeshio\n\n'
            'mesh = smeshio.loadMesh("/path/to/mesh")\n'
            'tet = mesh.findTetByPoint([0, 0, 0])\n'
            'if tet == -1:\n'
            '    print("boundary")\n'
        )
        checker = IdChecker(tree, '/home/script.py')
        ret = [c for c in checker.run()]
        self.assert_codes(ret, ['E421'])
