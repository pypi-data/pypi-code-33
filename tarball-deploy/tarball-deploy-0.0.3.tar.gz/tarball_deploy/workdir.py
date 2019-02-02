import contextlib
import os
import subprocess
import uuid


class Workdir:
    def __init__(self, path):
        self.path = path
        if not os.path.isdir(path):
            raise RuntimeError(f'Working directory "{path}" does not exist')

    def expand_subpath(self, path):
        return os.path.join(self.path, path)

    def ensure_subpath(self, path):
        os.makedirs(self.expand_subpath(path), exist_ok=True)

    def new_release_dir(self):
        name = uuid.uuid4()
        subpath = f"releases/{name}"
        self.ensure_subpath(subpath)
        return subpath

    def unpack_new_release(self, data):
        release_dir = self.new_release_dir()
        subprocess.run(
            ["tar", "x", "-C", self.expand_subpath(release_dir), "-f", "-"],
            stdin=data,
            check=True,
        )
        return release_dir

    def update_link(self, name, target):
        with contextlib.suppress(FileNotFoundError):
            os.unlink(self.expand_subpath(name))
        os.symlink(target, self.expand_subpath(name))

    def prepare_deployment(self, data):
        release_dir = self.unpack_new_release(data)
        self.update_link("next", release_dir)

    def switch_to_deployment(self):
        if os.path.exists(self.expand_subpath("current")):
            self.update_link("previous", os.readlink(self.expand_subpath("current")))
        os.replace(self.expand_subpath("next"), self.expand_subpath("current"))

    def deploy(self, data):
        self.prepare_deployment(data)
        self.switch_to_deployment()

    def rollback(self):
        os.replace(self.expand_subpath("previous"), self.expand_subpath("current"))
