import pathlib


def get_modified_time(file):
    file = pathlib.Path(file)
    if file.exists():
        return file.stat().st_mtime
    return 0


class Dependencies:
    def __init__(self, *depend_files_name, files=None):
        if files is None:
            files = []

        files.extend(list(depend_files_name))

        self.__dependencies = Dependencies.__resolve_depend(files)

    @staticmethod
    def __resolve_depend(files, deps=None):
        if deps is None:
            deps = {}
        for file in files:
            with open(file) as fp:
                for line in fp.readlines():
                    line = line.split(':')
                    out = line[0].strip()
                    inp = [i.strip() for i in line[1].strip().split(' ')]
                    if out not in deps:
                        deps[out] = []
                    deps[out].extend(inp)
        return deps

    def latest_time(self, output):
        times = [get_modified_time(d) for d in self.depend_files(output)]
        if len(times) == 0:
            return 0
        return max(times)

    def depend_files(self, output):
        if output not in self.__dependencies:
            return []

        deps = self.__dependencies[output]
        for dep in deps:
            deps.extend(self.depend_files(dep))

        return deps
