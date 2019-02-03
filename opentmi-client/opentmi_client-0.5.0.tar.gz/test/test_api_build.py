import unittest
from opentmi_client.api import Build, Ci, Vcs, Target, Hardware


class TestBuild(unittest.TestCase):
    def test_construct(self):
        build = Build()
        build.name = 'test'
        self.assertIsInstance(build, Build)
        self.assertEqual(build.name, 'test')
        self.assertEqual(build.data, {'name': 'test'})

    def test_type(self):
        build = Build()
        with self.assertRaises(ValueError):
            build.type = 'invalid'
        build.type = 'test'
        self.assertEqual(build.type, 'test')

    def test_compiledBy(self):
        build = Build()
        with self.assertRaises(ValueError):
            build.compiled_by = 'invalid'
        build.compiled_by = 'CI'
        self.assertEqual(build.compiled_by, 'CI')

    def test_ci(self):
        build = Build()
        with self.assertRaises(TypeError):
            build.ci_tool = 'invalid'
        ci = Ci()
        with self.assertRaises(ValueError):
            ci.system = 'invalid'
        build.ci_tool = ci
        build.ci_tool.system = 'Jenkins'
        self.assertEqual(ci.system, 'Jenkins')


    def test_vcs(self):
        build = Build()
        with self.assertRaises(TypeError):
            build.vcs = 'invalid'
        vcs = Vcs()
        build.vcs = [vcs]
        build.vcs[0].name = 'wc'
        self.assertEqual(vcs.name, 'wc')
        vcs.type = 'PR'
        self.assertEqual(vcs.type, 'PR')
        vcs.base_branch = 'base'
        self.assertEqual(vcs.base_branch, 'base')
        vcs.branch = 'master'
        self.assertEqual(vcs.branch, 'master')
        vcs.base_commit = '123'
        self.assertEqual(vcs.base_commit, '123')
        vcs.clean_wa = True
        self.assertTrue(vcs.clean_wa)
        vcs.pr_number = '123'
        self.assertEqual(vcs.pr_number, '123')
        vcs.commit_id = '123'
        self.assertEqual(vcs.commit_id, '123')
        vcs.system = 'git'
        self.assertEqual(vcs.system, 'git')
        vcs.url = 'url'
        self.assertEqual(vcs.url, 'url')

    def test_target(self):
        build = Build()
        with self.assertRaises(TypeError):
            build.target = 'invalid'
        target = Target()
        build.target = target
        target.operating_system = "win32"
        self.assertEqual(build.target.operating_system, 'win32')
        target.type = "hardware"
        self.assertEqual(build.target.type, 'hardware')
        with self.assertRaises(TypeError):
            target.hardware = 'invalid'
        hw = Hardware()
        target.hardware = hw
        hw.model = 'abc'
        self.assertEqual(build.target.hardware.model, 'abc')
        hw.vendor = 'def'
        self.assertEqual(build.target.hardware.vendor, 'def')
        hw.rev = 'qwe'
        self.assertEqual(build.target.hardware.rev, 'qwe')
        hw.meta = 'ooo'
        self.assertEqual(build.target.hardware.meta, 'ooo')

