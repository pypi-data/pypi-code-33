"""Tools for doing tests with a docker image.

This module provides various tools for building and testing a docker image.
See the `DockerTester` class for details.
"""

import traceback
import tempfile
import datetime
import logging
import io
import sys
import os
import subprocess
import json

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


class DockerBuildConf(object):
    """Configuration information for building docker test docker image.
    """

    def __init__(self, img_name, container_name, build_args, build_dir,
                 dports=(), docker_net='bridge', no_cache=False):
        """

        :arg img_name:        String name for docker image to create.

        :arg container_name:  String name of docker container instance to use.

        :arg build_args:      List of strings to use as --build-arg options
                              in building docker image.

        :arg build_dir=None:    Build directory containing Dockerfile, etc.

        :arg dports=():   Sequence of integer ports to expose on docker img.

        :arg docker_net='bridge':  Name of docker network. This is used in
                                   binding the simple http server to serve
                                   secrets if it exists. If this docker network
                                   does not exit, then we omit the --bind
                                   argument when creating the server. Usually,
                                   things can work without this. If you have
                                   problems you can try creating the docker
                                   bridge network and see if it helps.

        :arg no_cache=False:  Optional flag to prevent caching. Generally,
                              you are better off putting a line like
                              ARG build_date=SPECIFY_THIS_ON_BUILD
                              in your Dockerfile and then providing
                              a build arg of the current date to not cache
                              from that point on. But if you want to force a
                              full, clean, rebuild use no_cache=True.

        """
        self.img_name = img_name
        self.container_name = container_name
        self.build_args = build_args
        self.build_dir = build_dir
        self.dports = dports
        self.docker_net = docker_net
        self.no_cache = no_cache

    def pretty(self):
        """Pretty print config info.
        """
        names = ['img_name', 'container_name', 'build_args', 'build_dir',
                 'dports', 'docker_net']
        result = '%s(%s)' % (self.__class__.__name__, ',\n  '.join(
            [getattr(self, n) for n in names]))
        return result

    def get_img_name(self):
        "Return self.img_name"

        return self.img_name

    def __repr__(self):
        return self.pretty()


class DockerTestConf(object):
    """Configuration for docer test.
    """

    def __init__(self, img_logs, tester_log_level=logging.DEBUG):
        """Initializer.

        :arg img_logs:     List of strings specifying log files on docker
                           image we should capture when done.

        :arg tester_log_level=logging.DEBUG:  Optional log level to use
                                              in logging launch_tests.
                                              If None, no logging will be done.
                                              Otherwise we capture the log.

        """
        self.img_logs = img_logs
        self.tester_log_level = tester_log_level

    def get_img_logs(self):
        "Return self.img_logs"

        return self.img_logs

    def get_tester_log_level(self):
        "Return self.tester_log_level"

        return self.tester_log_level


class TestProblem(object):
    """Class to capture a problem occuring in a test.
    """

    def __init__(self, name, description, driver=None):
        """Initializer.

        :arg name:   String name of the test.

        :arg description:    String description of the problem.

        :arg driver=None:  Optional selenium driver used to run the test.
                           If provided, we try to get a screenshot.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:

        """
        self.name = name
        self.description = description
        self.screenshot = None
        self.source = None
        self.grab_screenshot(driver)
        self.grab_source(driver)

    def grab_source(self, driver):
        """If driver is None, grab page source and save it in self.source.
        """
        if driver is None:
            return
        self.source = driver.page_source

    def grab_screenshot(self, driver):
        """If driver is None, grab a screnshot and save it in self.screenshot.
        """
        if driver is None:
            return
        my_temp = tempfile.mktemp(suffix='.png')
        driver.save_screenshot(my_temp)
        self.screenshot = open(my_temp, 'rb').read()
        os.remove(my_temp)

    def dump_screenshot(self, path=None):
        """Dump screenshot to given path.

        :arg path=None:   If this is None, then we try to find a reasonable
                          temp directory and put the screenshot in dump.png
                          in that temporary directory.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:   A string indicating where screenshot was dumped to.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:    Easy way to dump screenshot to a file.

        """
        if path is None:
            options = ['c:/cygwin64/tmp', '/tmp']
            for item in options:
                if os.path.exists(item) and os.path.isdir(item):
                    path = os.path.join(item, 'dump.png')
                    break
        if path is None:
            raise ValueError('No path given and could not auto-choose one')
        open(path, 'wb').write(self.screenshot)
        return 'screen shot saved in <%s>' % path

    def __repr__(self):
        desc = self.description
        if len(desc) > 20:
            desc = desc[:17] + '...'
        return '%s(name=%s, description=%s, screenshot=...)' % (
            self.__class__.__name__, self.name, desc)


class DockerTester(object):
    """Class to build docker image and run tests.

    To create a dockerized test system, you can do the following:

      1. Create a Dockerfile as usual for docker.
      2. Sub-class DockerTester and implement launch_tests.
      3. Create an instance of your DockerTester sub-class.
      4. Call the run method of your instance.

    """

    def __init__(self, build_conf, test_conf):
        """Initializer.

        :arg build_conf:   Instance of DockerBuildConf for configuration info.

        :arg test_conf:    Instance of DockerTestConf.
        """
        self.build_conf = build_conf
        self.test_conf = test_conf

    def start_http_helper(self, port=8090, default_dir=None):
        """Start subprocess for HTTP server in default_dir to serve secrets.

        :arg port=8090:    Default port for server.

        :arg default_dir=None: Directory to serve from (uses os.getenv('HOME')
                               if this is None.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  The subprocess for the HTTP server.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   We need a way to get secrets into the Docker
                   image. One easy way is to start the HTTP server in
                   the HOME directory and let docker connect to that
                   and look at secret files it needs.  The HTTP server
                   will bind to the gateway for the docker network in
                   self.build_conf.docker_net to reduce the chance for
                   unauthorized access, but you should still be
                   careful here.

                   Call hserver.terminate() when done (where hserver is the
                   return value of this function).
        """
        bind = self.get_docker_net_ip()
        cmd_line = ('%s -m http.server %s' % (sys.executable, port))
        if bind:
            cmd_line += ' --bind %s' % bind
        cmd_line = cmd_line.split()
        logging.info('Launching simple HTTP server via: %s', cmd_line)
        hserver = subprocess.Popen(
            cmd_line, cwd=default_dir if default_dir else (
                os.getenv('HOME')))
        return hserver

    def get_docker_net_ip(self):
        """Find the IP for the docker subnet and return it.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  String indicating IP address for docker subnet.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Often docker is tied to a specific subnet. If we want
                   to do networking, we need that subnet. This method
                   tries to get it and return it.
        """
        inspect_key = "'{{ (index .IPAM.Config 0).Gateway}}'"
        cmd_line = ['docker', 'inspect', '-f', inspect_key,
                    self.build_conf.docker_net]
        result = subprocess.check_output(cmd_line)
        if isinstance(result, bytes):
            result = result.decode('utf8')
        result = result.strip().strip("'").strip()
        return result

    def build_docker(self, auto_delete=True):
        """Build the docker image.

        :arg auto_delete=True:  Whether to automatically delete previous image.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:  This will build the docker image.

        """
        image_name = self.build_conf.img_name
        if auto_delete:
            if self.check_dock_obj(image_name):
                logging.debug('Removing existing image %s', image_name)
                subprocess.check_call(['docker', 'rmi', '--force', image_name])
        build_dir = self.build_conf.build_dir
        build_date = datetime.datetime.utcnow().isoformat()
        cmd_line = ['docker', 'build', '.', '--build-arg',
                    'build_date=UTC__%s' % build_date, '-t', image_name]
        for barg in self.build_conf.build_args:
            cmd_line.extend(['--build-arg', barg])
        if self.build_conf.no_cache:
            cmd_line.append('--no-cache')

        logging.info('Building with command line: %s', str(cmd_line))
        dbuilder = subprocess.Popen(cmd_line, cwd=build_dir)
        dbuilder.wait()
        if dbuilder.returncode != 0:
            raise ValueError('Process %s failed with return code %s.' % (
                ' '.join(cmd_line), dbuilder.returncode))

    def create_container(self, auto_delete=True):
        """Create the docker container after the image is built.

        :arg auto_delete=True:    Whether to delete existing container.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  Result of calling subprocess.check_call to create the
                   container.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Create the docker container from the image.

        """
        cname = self.build_conf.container_name
        if auto_delete:
            if self.check_dock_obj(cname):
                logging.debug('Removing existing container %s', cname)
                subprocess.check_call(['docker', 'rm', '--force', cname])

        cmd_line = ['docker', 'create', '--name', cname]
        for my_port in self.build_conf.dports:
            cmd_line.extend(['-p', '%s:%s' % (my_port, my_port)])
        cmd_line.append(self.build_conf.img_name)
        return subprocess.check_call(cmd_line)

    def start_container(self):
        """Start docker container.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  Result of calling subprocess.check_call to start container.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Start the container.

        """
        cmd_line = 'docker start %s' % self.build_conf.container_name
        return subprocess.check_call(cmd_line.split())

    def stop_container(self):
        """Stop docker container.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  Result of calling subprocess.check_call to stop container.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Stop the container.

        """
        cmd_line = 'docker stop %s' % self.build_conf.container_name
        return subprocess.check_call(cmd_line.split())

    def connect_container(self, network_name):
        """Connect container to given network_name.

        :param network_name:     String name of network to connect to.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  Result of calling subprocess.check_call to connect
                   container to given network.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Connect container to a network.

        """
        cmd_line = 'docker network connect %s %s' % (
            network_name, self.build_conf.container_name)
        return subprocess.check_call(cmd_line.split())

    @staticmethod
    def check_dock_obj(object_name, re_raise=False):
        """Get information about given docker object.

        :arg object_name:  Name of docker object to check.

        :arg re_raise=False:   Whether to raise exception if we hit one.
                               Generally we just ignore the exception
                               and return None since it probably means
                               the object does not exist but you can
                               set this to True if you want to see the
                               exception yourself.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  A list representing a JSON array from the docker inspect
                   command for objects with the given object_name.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Get information about existing docker objects (or check if
                   they exist at all).

        """
        cmd_line = 'docker inspect %s' % object_name
        try:
            output = subprocess.check_output(cmd_line.split())
        except subprocess.CalledProcessError as problem:
            if re_raise:
                raise
            else:
                logging.debug('In check_dock_obj ignoring exception %s',
                              problem)
            return None
        info = json.loads(output.decode('UTF8'))
        return info

    def launch_tests(self):
        """Sub-classes must override to conduct desired tests.

        This should return a list of TestProblem instances describing
        any problems that were encountered in testing.
        """
        raise NotImplementedError

    def run(self, email=None, do_stop=True):
        """Main method to run all the tests, report results, etc.

        :arg email=None:     String email address to send results to if
                             desired. If None, then no email is sent.

        :arg do_stop=True:   Stop the container after running tests. You
                             can set this to false if you want to
                             debug and manually call stop_container
                             when you are done if desired.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:   List of TestProblem instances as returned by the
                    launch_tests method.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:    This is the top level entry point to run the tests. It
                    does the following:

           1. Setup HTTP server in home dir to serve secrets to docker.
           2. Build docker image.
           3. Start docker container.
           4. Run tests.
           5. Report test results.
           6. Clean-up and shutdown.

                    The idea is that you can run this function each time you
                    want to do a full build + test of the system.

        """

        problems, test_log = [], []
        try:
            problems.extend(self.raw_run(test_log))
        except Exception as my_exc:  # pylint: disable=broad-except
            kls = getattr(my_exc, '__class__', None)
            ename = getattr(kls, '__name__', 'unknown') if (
                kls is not None) else 'unknown'
            msg = 'Get Exception %s: "%s" in running tester.' % (ename, my_exc)
            my_tb = traceback.format_exc()
            msg += '\nTraceback:\n%s' % my_tb
            logging.error(msg)
            problems.append(TestProblem('Exception', msg))

        logging.info('Reporting results.')
        self.report_test_results(
            problems, email, text_attachments=self.get_logs() + test_log)

        if do_stop:
            self.stop_container()

        return problems

    def raw_run(self, test_log):
        """Low level helper to run the tests.

        :param test_log:     List to append logs to in the form (NAME, TXT)
                             where NAME is the name of the log with TXT as
                             its content.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :return:   List of TestProblem instances indicating any issues.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Intended to be called only from run method to run the
                   tests.

        """
        hserver = self.start_http_helper()
        try:
            self.build_docker()
            self.create_container()
        finally:
            hserver.terminate()
            hserver.wait(timeout=1)
        if not hserver.returncode:
            raise ValueError('HTTP server did not terminate when asked')

        self.start_container()
        if self.test_conf.tester_log_level is not None:
            log_capture_string = io.StringIO()
            capture = logging.StreamHandler(log_capture_string)
            capture.setLevel(logging.DEBUG)
            logging.getLogger('').addHandler(capture)
        problems = self.launch_tests()
        if self.test_conf.tester_log_level is not None:
            logging.getLogger('').removeHandler(capture)
            log_capture_string.seek(0)
            test_log.append(('python-log', log_capture_string.read()))

        return problems

    def get_logs(self):
        """Get specified log files from docker machine.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  List of pairs of the form (name, content) indicating the
                   name of a log file and its content.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Get log data from container.

        """
        result = []
        cname = self.build_conf.container_name
        for name in self.test_conf.img_logs:
            try:
                info = subprocess.check_output([
                    'docker', 'exec', '-i', cname, 'cat', name])
                info = info.decode('utf8')
            except Exception as problem:  # pylint: disable=broad-except
                info = 'Exception: in trying to get log file %s:\n%s\n' % (
                    name, str(problem))
            result.append((name, info))
        return result

    def report_test_results(self, problems, email, text_attachments,
                            name=None):
        """Report the results of running tests.

        :arg problems:    List of TestProblem instances encountered.

        :arg email:       String to email report to. If empty, no email sent.

        :arg text_attachments:  List of pairs of the form (name, content)
                                for text attacments to include.

        :arg name=None:  Optional string name for this test suite. If None,
                         use self.__class__.__name__.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Print results of tests and also email them if desired.

        """
        name = name if name else self.__class__.__name__
        text = ['Finished testing %s at %s' % (name, datetime.datetime.now())]
        if problems:
            text.append('Problems are:\n%s\n' % '\n'.join(map(str, problems)))
            text.extend([
                '\n\nYou may check https://github.com/emin63/oxtest for the\n'
                'README.md to see tips and tricks for running and debugging.'])
        text = '\n'.join(text)

        if email:
            msg = MIMEMultipart()
            msg['FROM'] = email
            msg['TO'] = email
            msg['Subject'] = '%s Test Results: %s' % (name, (
                ('%i problems' % len(problems)) if problems else 'CLEAN!'))
            msg.attach(MIMEText(text))
            for item in problems:
                if item.screenshot:
                    img = MIMEImage(item.screenshot,
                                    name='%s.png' % item.name)
                    msg.attach(img)
                if getattr(item, 'source', None):
                    attachment = MIMEText(item.source)
                    attachment.add_header('Content-Disposition', 'attachment',
                                          filename='%s.html' % item.name)
                    msg.attach(attachment)
            text_attachments = list(text_attachments)
            for item_name, text in (list(text_attachments) + [
                    (item.name + '.txt', item.description)
                    for item in problems]):
                attachment = MIMEText(text)
                attachment.add_header(
                    'Content-Disposition', 'attachment', filename=item_name)
                msg.attach(attachment)
            bytes_body = bytes(msg.as_string(), 'UTF8')
            epipe = subprocess.Popen(["/usr/sbin/sendmail", '-t', '-oi'],
                                     stdin=subprocess.PIPE)
            com_results = epipe.communicate(bytes_body)
            logging.info('Sent email to %s with result %s', email,
                         str(com_results))
        print('Results of test:\n%s\n' % text)
