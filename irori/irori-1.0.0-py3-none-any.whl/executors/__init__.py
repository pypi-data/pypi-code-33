import subprocess


class Executor:
    def __init__(self, concurrency_count=1):
        self.__processes = []
        self.__concurrency_count = concurrency_count
        self.__running = True

    def start_process(self, command: str):
        if not self.__running:
            return None
        if len(self.__processes) >= self.__concurrency_count:
            pass
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.__processes.append(process)
        return process

    @property
    def concurrency_count(self):
        return self.__concurrency_count

    @staticmethod
    def __process_failed(proc: subprocess.Popen):
        stdout, _ = proc.communicate()
        print(proc.args)
        print(stdout.decode(encoding='utf-8'))

    def wait(self):
        while True:
            for proc in self.__processes:
                ret = proc.poll()
                if ret is not None:
                    self.__processes.remove(proc)
                    if ret != 0:
                        self.__running = False
                        Executor.__process_failed(proc)
                        self.wait_all()
                        exit(1)

    def wait_all(self):
        for proc in self.__processes:
            proc.wait()
            if proc.returncode != 0:
                self.__running = False
                Executor.__process_failed(proc)
        self.__processes = []
