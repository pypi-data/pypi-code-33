"""``Run`` is the main interface to log information about an experiment."""
import getpass
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import log

from lolaml.config import load_lola_config
from lolaml.data import RunData
from lolaml.remotes import RemoteStorage
from lolaml.storage import JSONStorage
from lolaml.utils import ls_files


class Run:
    """
    `Run` is the main interface to log information about an experiment.

    Use it as a context manager to start/stop the run
    (or instanciate it directly).
    Then use the ``log_*`` functions to log everything that is important for
    your experiment.

    Attributes:
        run_id: The id of the run.
        data (lolaml.data.RunData): The actual data that is being logged.

    Args:
        project: The name of the project this run belongs to
            (default project name is `default`).
        path_prefix: Where to store the artifacts.
            The run_id is prepended to the `path_prefix`.
            If not specified, Lola will generate a temp path automatically.
        log_git: Log git sha, status and diff if ``True``.
        log_call_info: Log general call info (``__file__`` and ``argv``) if ``True``.
        remote_location: Specify the remote bucket to upload the artifacts to.
            Don't upload anything if not specified.
        remote_credentials: The path to the credentials for the remote location.
        ignore_config: Don't read the `.lola.toml` if ``True``.

    Example:
        >>> import lolaml as lola
        >>> with lola.Run(ignore_config=True) as run:  # doctest:+ELLIPSIS
        ...     run.log_param("lr", 0.1)
        ...     run.log_tags("WIP", "RNN")
        ...     run.log_metric("loss", .56, step=1)

    """

    def __init__(
        self,
        project: str = "default",
        path_prefix: Optional[str] = None,
        log_git: bool = True,
        log_call_info: bool = True,
        remote_location: Optional[str] = None,
        remote_credentials: Optional[str] = None,
        ignore_config=False,
    ):
        run_id = str(uuid.uuid4())
        log.info(f"# Starting run '{run_id}'")

        _user_config = {}
        if remote_credentials is not None:
            _user_config["remote_credentials"] = remote_credentials
        if remote_location is not None:
            _user_config["remote_location"] = remote_location
        config = load_lola_config(_user_config, ignore_config=ignore_config)

        self._storage = JSONStorage
        self._remote_storage = RemoteStorage.from_spec(
            config["remote_location"], config["remote_credentials"]
        )

        if path_prefix is None:
            path_prefix = tempfile.mktemp(prefix=f"lolaml/{project}/")
            log.debug(
                f" * No path_prefix set. Storing artifacts under '{path_prefix}'."
            )
        _path = Path(path_prefix) / str(run_id)
        _path.mkdir(parents=True, exist_ok=True)
        path: str = str(_path)

        data = RunData(
            project=project,
            run_id=run_id,
            status="running",
            start_time=_now(),
            path=path,
            user=getpass.getuser(),
        )

        if log_git:
            data.git = {
                "sha": get_git_sha(),
                "status": get_git_status(),
                "diff": get_git_diff(),
            }

        if log_call_info:
            data.call_info = {"__file__": __file__, "argv": list(sys.argv)}

        self.data = data

    @property
    def path(self) -> str:
        return self.data.path

    @property
    def run_id(self) -> str:
        return self.data.run_id

    def log_metric(self, name: str, value: Any, *, step: Optional[int] = None) -> None:
        """
        Log a metric (key/value) with an optional step.

        Additionally the current time is logged.
        """
        self.data.metrics.append(
            {"name": name, "value": value, "step": step, "ts": _now()}
        )

    def log_tag(self, tag: str) -> None:
        """Log a tag."""
        self.data.tags = list(set([*self.data.tags, tag]))

    def log_tags(self, *tags) -> None:
        """Log many tags."""
        for tag in tags:
            self.log_tag(tag)

    def log_param(self, name: str, value: Any) -> None:
        """Log the parameter (key/value)."""
        self.data.params[name] = value

    def log_params(self, params: Dict[str, Any]) -> None:
        """Log many parameters (dict)."""
        for k, v in params.items():
            self.log_param(k, v)

    def _log_artifact(self, path: str) -> None:
        """Log the artifacts under the given `path`."""
        # TODO calc md5/sha/hashes
        # TODO mark special artifacts like images
        _path = Path(path)
        artifact_info: Dict[str, Any] = {}
        if _path.is_file():
            stat = _path.stat()
            artifact_info = {
                "type": "file",
                "st_size": stat.st_size,
                "st_atime": stat.st_atime_ns,
                "st_mtime": stat.st_mtime_ns,
                "st_ctime": stat.st_ctime_ns,
            }
            self.data.artifacts[str(path)] = artifact_info
        elif _path.is_dir():
            log.debug(f"Skipping {path}")
        else:
            self.data.artifacts[str(path)] = {}

    def _log_all_artifacts(self) -> None:
        """Log all artifacts under the current path."""
        for p in ls_files(self.path):
            self._log_artifact(str(p))

    def _finish(self) -> None:
        """Finish a successful run and write to disk."""
        self.data.status = "done"
        self.data.end_time = _now()
        self._write()

    def _write(self):
        """Write the current json representation to disk (and upload all artifacts)."""
        self._log_all_artifacts()
        self._log_artifact(self._storage.log_file_path(self.path, self.run_id))

        self._storage.write(self.data)
        if self._remote_storage:
            self._remote_storage.upload(self.data)

    # Context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            # record error and write log
            self.data.status = "error"
            self.data.end_time = _now()
            self._write()
        else:
            self._finish()


def run(**kwargs):
    return Run(**kwargs)


########################################################################################
# HELPERS
def _now() -> str:
    return str(datetime.now())


def _git_cmd(*args):
    try:
        return subprocess.check_output(args).strip().decode("utf-8")
    except subprocess.CalledProcessError as e:
        log.warning("Git error:", e)
        return str(e)
    except FileNotFoundError as e:
        log.warning("FileNotFoundError:", e)
        return str(e)


def get_git_sha():
    return _git_cmd("git", "rev-parse", "HEAD")


def get_git_status():
    return _git_cmd("git", "status")


def get_git_diff():
    return _git_cmd("git", "diff")
