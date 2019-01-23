import docker
from robot.api import logger
from docker.types import Mount

class Robodirs3arch(object):

    def __init__(self):
        self.client = docker.from_env()
        self.dirs3arch_docker = "dirs3arch"

    def run_dirs3arch(self, url, extensions, wordlist, results_path):
        self.url = url
        self.extensions = extensions
        self.wordlist = wordlist
        self.results_path = results_path
        results_mount = Mount("/dirs3arch_results", self.results_path, type="bind")
        wordlist_mount = Mount("/wordlist.txt", self.wordlist, type="bind")
        mounts = [results_mount, wordlist_mount]
        command = '-u {0} -e {1} -w {2} --json-report=/dirs3arch_results/dirs3arch_results.json'.format(self.url, self.extensions, '/wordlist.txt')
        self.client.containers.run(self.dirs3arch_docker, mounts=mounts, command=command)
        logger.trace("Successfully ran dirs3arch against the target URL {0}. Please find the *.json output in the results directory".format(self.url))
