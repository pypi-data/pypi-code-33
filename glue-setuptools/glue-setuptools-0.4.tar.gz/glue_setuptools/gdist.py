import errno
import os
import re
import shutil
import zipfile

from distutils import log
from distutils.errors import DistutilsPlatformError, DistutilsInternalError, DistutilsSetupError, DistutilsOptionError
from setuptools import Command
from subprocess import Popen, PIPE


def validate_glue_entrypoint(dist, attr, value):
    if not re.compile('^([a-zA-Z0-9_]+\.)*[a-zA-Z0-9_]+:[a-zA-Z0-9_]+$').match(value):
        raise DistutilsSetupError('{} must be in the form of \'my_package.some_module:some_function\''.format(attr))


class GDist(Command):

    description = 'build a AWS Glue compatible distribution'
    user_options = [
        ('include-version=', None, 'Include the version number on the glue distribution name')
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        setattr(self, 'include_version', None)

    def finalize_options(self):
        inc_ver = getattr(self, 'include_version')
        if inc_ver is None or \
                inc_ver == '' or \
                inc_ver == 'True' or \
                inc_ver == 'true' or \
                inc_ver == 'Yes' or \
                inc_ver == 'yes':
            setattr(self, 'include_version', True)
        elif inc_ver == 'False' or \
                inc_ver == 'false' or \
                inc_ver == 'No' or \
                inc_ver == 'no':
            setattr(self, 'include_version', False)
        else:
            raise DistutilsOptionError('include-version must be True, true, Yes, yes, False, false, No, no or absent')

    def run(self):
        # We must create a distribution to install first
        # This is a short-cut to working with the actual build
        # directory, or to using the 'install' command, which
        # will generally only install a zipped egg
        self.run_command('bdist_wheel')
        setattr(self, '_dist_dir', self.get_finalized_command('bdist_wheel').dist_dir)

        # Install the package built by bdist_wheel
        # (or bdist, or bdist_wheel, depending on how the user called setup.py
        self._install_dist_package()

        # Create Glue Job entry point function
        self._create_glue_entrypoint()

        # Now build the glue package
        self._build_glue_package()

    def _build_glue_package(self):
        dist_name = '{}-glue-{}.zip'.format(self.distribution.get_name(), self.distribution.get_version()) \
            if getattr(self, 'include_version') \
            else '{}-glue.zip'.format(self.distribution.get_name())
        dist_path = os.path.join(self._dist_dir, dist_name)

        script_name = '{}-{}-script.py'.format(self.distribution.get_name(), self.distribution.get_version()) \
            if getattr(self, 'include_version') \
            else '{}-script.py'.format(self.distribution.get_name())
        script_path = os.path.join(self._dist_dir, script_name)

        if os.path.exists(dist_path):
            os.remove(dist_path)
        if os.path.exists(script_path):
            os.remove(script_path)

        log.info('creating {}'.format(dist_path))
        with zipfile.ZipFile(dist_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            abs_src = os.path.abspath(self._glue_build_dir)
            for root, _, files in os.walk(self._glue_build_dir):
                for filename in files:
                    if root == self._glue_build_dir and filename == 'entrypoint.py':
                        continue
                    absname = os.path.abspath(os.path.join(root, filename))
                    arcname = absname[len(abs_src) + 1:]
                    log.debug('zipping {} as {}'.format(os.path.join(root, filename), arcname))
                    zf.write(absname, arcname)
        # Set the resulting distribution file path for downstream command use
        setattr(self, 'gdist_name', dist_name)
        setattr(self, 'gdist_path', dist_path)

        log.info('copying {}'.format(script_path))
        shutil.copy(os.path.join(self._glue_build_dir, "entrypoint.py"), script_path)
        setattr(self, 'gdist_script_name', script_name)
        setattr(self, 'gdist_script_path', script_path)

    def _install_dist_package(self):
        # Get the name of the package that we just built
        package_name = self.distribution.get_name()
        # Get the dist directory that bdist_wheel put the package in
        # Create the glue build dir
        self._glue_build_dir = os.path.join('build', 'gdist-'+package_name)
        try:
            if os.path.exists(self._glue_build_dir):
                shutil.rmtree(self._glue_build_dir)
            log.info('creating {}'.format(self._glue_build_dir))
            os.makedirs(self._glue_build_dir)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(self._glue_build_dir):
                pass
            else:
                raise DistutilsInternalError('{} already exists and is not a directory'.format(self._glue_build_dir))
        log.info('installing package {} from {} into {}'.format(package_name,
                                                                self._dist_dir,
                                                                self._glue_build_dir))
        pip = Popen(['pip', 'install',
                     '-f', self._dist_dir,
                     '-t', self._glue_build_dir, package_name],
                    stdout=PIPE, stderr=PIPE)
        stdout, stderr = pip.communicate()
        log.debug("pip stdout: {}".format(stdout))
        log.debug("pip stderr: {}".format(stderr))

        if pip.returncode is not 0:
            raise DistutilsPlatformError('pip returned unsuccessfully')

    def _create_glue_entrypoint(self):
        glue_entrypoint = getattr(self.distribution, 'glue_entrypoint', None)
        if not glue_entrypoint:
            return
        components = glue_entrypoint.split(':')
        module = components[0]
        function = components[1]
        function_lines = [
            'import {}\n'.format(module),
            '\n',
            '\n',
            '{}.{}()\n'.format(module, function)
        ]
        function_path = os.path.join(self._glue_build_dir, 'entrypoint.py')
        log.info('creating {}'.format(function_path))
        with open(function_path, 'w') as py:
            py.writelines(function_lines)

