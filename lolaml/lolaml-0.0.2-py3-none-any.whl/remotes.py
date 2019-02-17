from dataclasses import dataclass
from pathlib import Path

import log

from lolaml.data import RunData


@dataclass
class RemoteStorage:
    """
    Store all artifacts in a remote bucket.

    Currently only google storage and local storage are supported.

    The local `<ARTIFACT_PATH>` is stored under
    `<REMOTE_BUCKET>/<PROJECT>/<RUN_ID>/<ARTIFACT_PATH>`

    TODO more docs
    """

    remote_location: str
    remote_credentials: str

    @staticmethod
    def from_spec(remote: str, remote_credentials: str):
        if not remote:
            return None

        remote = str(remote)
        if remote.startswith("gs://"):
            if remote_credentials:
                return RemoteStorage(remote, remote_credentials)
            else:
                raise ValueError("Remote_credentials not set")
        else:
            return RemoteStorage(remote, remote_credentials)

        log.debug(
            "Set `remote` and `remote_credentials` to save data on a remote server"
        )
        return None

    def _get_container(self):
        if self.remote_location.startswith("gs://"):
            from cloudstorage.drivers.google import GoogleStorageDriver

            _protocol, container_name = self.remote_location.split("://")
            container_name = container_name.strip("/")
            storage = GoogleStorageDriver(self.remote_credentials)
            container = storage.get_container(container_name)

        else:
            from cloudstorage.drivers.local import LocalDriver

            tmp = Path(self.remote_location)
            loc, name = str(tmp.parent), str(tmp.name)
            container = LocalDriver(loc).get_container(name)

        return container

    def upload(self, data: RunData):
        container = self._get_container()
        artifacts = list(data.artifacts.keys())
        log.info(f"# Starting uploading of {len(artifacts)} artifact(s)...")
        for artifact_path in artifacts:
            log.debug(f" * Uploading {artifact_path}")
            dst = self.artifact_destination(artifact_path, data.run_id, data.project)
            container.upload_blob(artifact_path, blob_name=dst)

    @staticmethod
    def artifact_destination(artifact_path: str, run_id: str, project: str):
        """
        Create the remote artifact destination.

        Examples:
            >>> artifact_path = "/tmp/lolaml/73epbsfm/6caf409f-8e27-4d4c-80db-1b05d510601e/lola_run_6caf409f-8e27-4d4c-80db-1b05d510601e.json"
            >>> run_id = "6caf409f-8e27-4d4c-80db-1b05d510601e"
            >>> project = "default"
            >>> RemoteStorage.artifact_destination(artifact_path, run_id, project)
            'default/6caf409f-8e27-4d4c-80db-1b05d510601e/lola_run_6caf409f-8e27-4d4c-80db-1b05d510601e.json'

        """
        return str(Path(project) / artifact_path[artifact_path.find(run_id) :])
