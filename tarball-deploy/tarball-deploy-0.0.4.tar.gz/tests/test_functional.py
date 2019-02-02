import itertools
import io
import subprocess
from tarfile import TarFile, TarInfo

import pytest


@pytest.fixture
def tarballs():
    def tarballs_generator():
        count = 0
        while True:
            count += 1
            content = f"foo #{count}".encode()
            tar_bytes = io.BytesIO()
            with TarFile(fileobj=tar_bytes, mode="w") as tarfile:
                tarinfo = TarInfo("foo.txt")
                tarinfo.size = len(content)
                tarfile.addfile(tarinfo, io.BytesIO(content))
            yield tar_bytes.getvalue()

    return tarballs_generator()


@pytest.fixture
def tarball(tarballs):
    return next(tarballs)


def test_deploy_from_stdin(tmp_path, tarball):
    r = subprocess.run(
        f"tarball-deploy --workdir={tmp_path} --from=-", shell=True, input=tarball
    )
    assert r.returncode == 0
    with open(tmp_path / "current/foo.txt") as f:
        assert f.read() == "foo #1"


def test_deploy_from_file(tmp_path, tarball):
    with open(tmp_path / "release.tar", "wb") as f:
        f.write(tarball)
    r = subprocess.run(
        f"tarball-deploy --workdir={tmp_path} --from={tmp_path}/release.tar",
        shell=True,
        input=tarball,
    )
    assert r.returncode == 0
    with open(tmp_path / "current/foo.txt") as f:
        assert f.read() == "foo #1"


def test_repeated_deploys(tmp_path, tarballs):
    for tarball in itertools.islice(tarballs, 3):
        r = subprocess.run(
            f"tarball-deploy --workdir={tmp_path} --from=-", shell=True, input=tarball
        )
        assert r.returncode == 0
    with open(tmp_path / "current/foo.txt") as f:
        assert f.read() == "foo #3"
    with open(tmp_path / "previous/foo.txt") as f:
        assert f.read() == "foo #2"


def test_rollback(tmp_path, tarballs):
    for tarball in itertools.islice(tarballs, 2):
        subprocess.run(
            f"tarball-deploy --workdir={tmp_path} --from=-", shell=True, input=tarball
        )
    r = subprocess.run(f"tarball-deploy --workdir={tmp_path} --rollback", shell=True)
    assert r.returncode == 0
    with open(tmp_path / "current/foo.txt") as f:
        assert f.read() == "foo #1"
