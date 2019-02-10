import contextlib
import os
import shutil
import subprocess
import uuid
from argparse import ArgumentTypeError


class Workdir:
    def __init__(self, path):
        self.path = path

    def expand_subpath(self, path):
        return os.path.join(self.path, path)

    def make_release_dir(self):
        name = uuid.uuid4()
        release_dir = f"releases/{name}"
        os.makedirs(self.expand_subpath(release_dir), exist_ok=True)
        return release_dir

    def unpack_release(self, data):
        release_dir = self.make_release_dir()
        subprocess.run(
            ["tar", "x", "-C", self.expand_subpath(release_dir), "-f", "-"],
            stdin=data,
            check=True,
        )
        return release_dir

    def make_link(self, name, target):
        with contextlib.suppress(FileNotFoundError):
            os.unlink(self.expand_subpath(name))
        os.symlink(target, self.expand_subpath(name))

    def prepare_next_deployment(self, data):
        release_dir = self.unpack_release(data)
        self.make_link("next", release_dir)

    def switch_to_next_deployment(self):
        if os.path.exists(self.expand_subpath("current")):
            self.make_link("previous", os.readlink(self.expand_subpath("current")))
        os.replace(self.expand_subpath("next"), self.expand_subpath("current"))

    def clear_previous_deployment(self):
        if os.path.exists(self.expand_subpath("previous")):
            release_dir = os.path.join(
                os.path.dirname(self.expand_subpath("previous")),
                os.readlink(self.expand_subpath("previous")),
            )
            os.unlink(self.expand_subpath("previous"))
            shutil.rmtree(release_dir)

    def deploy(self, data):
        self.prepare_next_deployment(data)
        self.clear_previous_deployment()
        self.switch_to_next_deployment()

    def rollback(self):
        os.replace(self.expand_subpath("previous"), self.expand_subpath("current"))


class WorkdirType:
    def __call__(self, path):
        if not os.path.isdir(path):
            raise ArgumentTypeError(f"'{path}' does not exist")
        return Workdir(path)
