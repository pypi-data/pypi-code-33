import unittest
import os
import contextlib
import shutil

from scotty import cli


class PerformExperimentParallelTest(unittest.TestCase):
    cli_cmd = 'scotty experiment perform'
    test_script_name = os.path.basename(__file__)
    test_script_name = os.path.splitext(test_script_name)[0]
    experiment_samples_path = 'samples/components/experiment/parallel_workload'
    experiment_tmp_path_root = os.path.join('tmp', test_script_name)
    experiment_tmp_path = os.path.join(experiment_tmp_path_root, experiment_samples_path)

    def setUp(self):
        if os.path.isdir(self.experiment_tmp_path):
            shutil.rmtree(self.experiment_tmp_path)
        shutil.copytree(self.experiment_samples_path, self.experiment_tmp_path)
        self.experiment_scotty_path = os.path.join(self.experiment_tmp_path, '.scotty/')
        self.setUpWorkloadModulePath()
        self.setUpResourceModulePath()

    def setUpWorkloadModulePath(self):
        self.workload_module_path = os.path.join(
            self.experiment_scotty_path,
            'components/workload/demo_workload/workload_gen.py')

    def setUpResourceModulePath(self):
        self.resource_module_path = os.path.join(
            self.experiment_scotty_path,
            'components/resource/demo_resource/resource_gen.py')

    def tearDown(self):
        shutil.rmtree(self.experiment_tmp_path_root)

    def test_perform_experiment_parallel(self):
        self.run_cmd()
        self.assertTrue(os.path.isdir(self.experiment_scotty_path), 'Missing .scotty directory')
        self.assertTrue(os.path.exists(self.workload_module_path), 'Missing demo_workload module')
        self.assertTrue(os.path.exists(self.resource_module_path), 'Missing demo_resource module')
        with open(self._result_file, 'r') as f:
            result_test = f.readline().strip()
        self.assertEqual(result_test, '42.42.42.42')

    @property
    def _result_file(self):
        result_file = os.path.join(self.experiment_scotty_path, 'data/workload/demo_workload/')
        result_file = os.path.join(result_file, 'my_result_file.txt')
        return result_file

    @contextlib.contextmanager
    def cwd(self, path):
        prev_cwd = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(prev_cwd)

    def run_cmd(self):
        with self.cwd(self.experiment_tmp_path):
            cmd_args = self.cli_cmd.split(' ')
            cli.run(cmd_args)
