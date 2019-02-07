# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from collections import defaultdict
import logging
import os
import shutil

import arrow
from pkginfo import UnpackedSDist
import requests

from swh.core import tarball
from swh.model import hashutil

from .converters import info, author

try:
    from swh.loader.pypi._version import __version__
except ImportError:
    __version__ = 'devel'


def _to_dict(pkginfo):
    """Given a pkginfo parsed structure, convert it to a dict.

    Args:
        pkginfo (UnpackedSDist): The sdist parsed structure

    Returns:
        parsed structure as a dict

    """
    m = {}
    for k in pkginfo:
        m[k] = getattr(pkginfo, k)
    return m


def _project_pkginfo(dir_path):
    """Given an uncompressed path holding the pkginfo file, returns a
       pkginfo parsed structure as a dict.

       The release artifact contains at their root one folder. For example:
       $ tar tvf zprint-0.0.6.tar.gz
       drwxr-xr-x root/root         0 2018-08-22 11:01 zprint-0.0.6/
       ...

    Args:

        dir_path (str): Path to the uncompressed directory
                        representing a release artifact from pypi.

    Returns:
        the pkginfo parsed structure as a dict if any or None if
        none was present.

    """
    # Retrieve the root folder of the archive
    project_dirname = os.listdir(dir_path)[0]
    pkginfo_path = os.path.join(dir_path, project_dirname, 'PKG-INFO')
    if not os.path.exists(pkginfo_path):
        return None
    pkginfo = UnpackedSDist(pkginfo_path)
    return _to_dict(pkginfo)


class PyPIClient:
    """PyPI client in charge of discussing with the pypi server.

    Args:
        base_url (str): PyPI instance's base url
        temp_directory (str): Path to the temporary disk location used
                              for uncompressing the release artifacts

        cache (bool): Use an internal cache to keep the archives on
                      disk. Default is not to use it.
        cache_dir (str): cache's disk location (relevant only with
                        `cache` to True)

        Those last 2 parameters are not for production use.

    """
    def __init__(self, base_url='https://pypi.org/pypi',
                 temp_directory=None, cache=False, cache_dir=None):
        self.version = __version__
        self.base_url = base_url
        self.temp_directory = temp_directory

        self.do_cache = cache
        if self.do_cache:
            self.cache_dir = cache_dir
            self.cache_raw_dir = os.path.join(cache_dir, 'archives')
            os.makedirs(self.cache_raw_dir, exist_ok=True)
        self.session = requests.session()
        self.params = {
            'headers': {
                'User-Agent': 'Software Heritage PyPI Loader (%s)' % (
                    __version__
                )
            }
        }

    def _save_response(self, response, project=None):
        """Log the response from a server request to a cache dir.

        Args:
            response (Response): full server response
            cache_dir (str): system path for cache dir

        Returns:
            nothing

        """
        import gzip
        from json import dumps
        datepath = arrow.utcnow().isoformat()
        name = '%s.gz' % datepath if project is None else '%s-%s.gz' % (
            project, datepath)
        fname = os.path.join(self.cache_dir, name)
        with gzip.open(fname, 'w') as f:
            f.write(bytes(
                dumps(response.json()),
                'utf-8'
            ))

    def _save_raw(self, filepath):
        """In cache mode, backup the filepath to self.cache_raw_dir

        Args:
            filepath (str): Path of the file to save

        """
        _filename = os.path.basename(filepath)
        _archive = os.path.join(self.cache_raw_dir, _filename)
        shutil.copyfile(filepath, _archive)

    def _get_raw(self, filepath):
        """In cache mode, we try to retrieve the cached file.

        """
        _filename = os.path.basename(filepath)
        _archive = os.path.join(self.cache_raw_dir, _filename)
        if not os.path.exists(_archive):
            return None
        shutil.copyfile(_archive, filepath)
        return filepath

    def _get(self, url, project=None):
        """Get query to the url.

        Args:
            url (str): Url

        Raises:
            ValueError in case of failing to query

        Returns:
            Response as dict if ok

        """
        response = self.session.get(url, **self.params)
        if response.status_code != 200:
            raise ValueError("Fail to query '%s'. Reason: %s" % (
                url, response.status_code))

        if self.do_cache:
            self._save_response(response, project=project)

        return response.json()

    def info(self, project_url, project=None):
        """Given a metadata project url, retrieve the raw json response

        Args:
            project_url (str): Project's pypi to retrieve information

        Returns:
            Main project information as dict.

        """
        return self._get(project_url, project=project)

    def release(self, project, release):
        """Given a project and a release name, retrieve the raw information
           for said project's release.

        Args:
            project (str): Project's name
            release (dict): Release information

        Returns:
            Release information as dict

        """
        release_url = '%s/%s/%s/json' % (self.base_url, project, release)
        return self._get(release_url, project=project)

    def prepare_release_artifacts(self, project, version, release_artifacts):
        """For a given project's release version, fetch and prepare the
           associated release artifacts.

        Args:
            project (str): PyPI Project
            version (str): Release version
            release_artifacts ([dict]): List of source distribution
                                        release artifacts

        Yields:
            tuple (artifact, filepath, uncompressed_path, pkginfo) where:

            - artifact (dict): release artifact's associated info
            - release (dict): release information
            - filepath (str): Local artifact's path
            - uncompressed_archive_path (str): uncompressed archive path
            - pkginfo (dict): package information or None if none found

        """
        for artifact in release_artifacts:
            release = {
                'name': version,
                'message': artifact.get('comment_text', ''),
            }
            artifact = {
                'sha256': artifact['digests']['sha256'],
                'size': artifact['size'],
                'filename': artifact['filename'],
                'url': artifact['url'],
                'date': artifact['upload_time'],
            }
            yield self.prepare_release_artifact(project, release, artifact)

    def prepare_release_artifact(self, project, release, artifact):
        """For a given release project, fetch and prepare the associated
           artifact.

        This:
        - fetches the artifact
        - checks the size, hashes match
        - uncompress the artifact locally
        - computes the swh hashes
        - returns the associated information for the artifact

        Args:
            project (str): Project's name
            release (dict): Release information
            artifact (dict): Release artifact information

        Returns:
            tuple (artifact, filepath, uncompressed_path, pkginfo) where:

            - release (dict): Release information (name, message)
            - artifact (dict): release artifact's information
            - filepath (str): Local artifact's path
            - uncompressed_archive_path (str): uncompressed archive path
            - pkginfo (dict): package information or None if none found

        """
        version = release['name']
        logging.debug('Release version: %s' % version)
        path = os.path.join(self.temp_directory, project, version)
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, artifact['filename'])
        logging.debug('Artifact local path: %s' % filepath)

        cache_hit = None
        if self.do_cache:
            cache_hit = self._get_raw(filepath)

        if cache_hit:
            h = hashutil.MultiHash.from_path(filepath)
        else:  # no cache hit, we fetch from pypi
            url = artifact['url']
            r = self.session.get(url, **self.params, stream=True)
            status = r.status_code
            if status != 200:
                if status == 404:
                    raise ValueError("Project '%s' not found" % url)
                else:
                    msg = "Fail to query '%s'\nCode: %s\nDetails: %s" % (
                        url, r.status_code, r.content)
                    raise ValueError(msg)

            length = int(r.headers['content-length'])
            if length != artifact['size']:
                raise ValueError('Error when checking size: %s != %s' % (
                    artifact['size'], length))

            h = hashutil.MultiHash(length=length)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=None):
                    h.update(chunk)
                    f.write(chunk)

        hashes = h.hexdigest()

        actual_digest = hashes['sha256']
        if actual_digest != artifact['sha256']:
            raise ValueError(
                '%s %s: Checksum mismatched: %s != %s' % (
                    project, version, artifact['sha256'], actual_digest))

        if not cache_hit and self.do_cache:
            self._save_raw(filepath)

        uncompress_path = os.path.join(path, 'uncompress')
        os.makedirs(uncompress_path, exist_ok=True)
        nature = tarball.uncompress(filepath, uncompress_path)
        artifact['archive_type'] = nature
        artifact.update(hashes)
        pkginfo = _project_pkginfo(uncompress_path)
        return release, artifact, filepath, uncompress_path, pkginfo


class PyPIProject:
    """PyPI project representation

    This allows to extract information for a given project:
    - either its latest information (from the latest release)
    - either for a given release version
    - uncompress associated fetched release artifacts

    This also fetches and uncompresses the associated release
    artifacts.

    """
    def __init__(self, client, project, project_metadata_url, data=None):
        self.client = client
        self.project = project
        self.project_metadata_url = project_metadata_url
        if data:
            self.data = data
        else:
            self.data = client.info(project_metadata_url, project)

        self.last_version = self.data['info']['version']
        self.cache = {
            self.last_version: self.data
        }

    def _data(self, release_name=None):
        """Fetch data per release and cache it.  Returns the cache retrieved
           data if already fetched.

        """
        if release_name:
            data = self.cache.get(release_name)
            if not data:
                data = self.client.release(self.project, release_name)
                self.cache[release_name] = data
        else:
            data = self.data
        return data

    def info(self, release_name=None):
        """Compute release information for provided release (or latest one).

        """
        return info(self._data(release_name))

    def _filter_release_artifacts(self, version, releases,
                                  known_artifacts=None):
        """Filter not already known sdist (source distribution) release.

        There can be multiple 'package_type' (sdist, bdist_egg,
        bdist_wheel, bdist_rpm, bdist_msi, bdist_wininst, ...), we are
        only interested in source distribution (sdist), others bdist*
        are binary

        Args:
            version (str): Release name or version
            releases (dict/[dict]): Full release object (or a list of)
            known_artifacts ([tuple]): List of known releases (tuple filename,
                                       sha256)

        Yields:
            an unknown release artifact

        """
        if not releases:
            return []
        if not isinstance(releases, list):
            releases = [releases]

        if not known_artifacts:
            known_artifacts = set()

        for artifact in releases:
            name = artifact['filename']
            sha256 = artifact['digests']['sha256']
            if (name, sha256) in known_artifacts:
                logging.debug('artifact (%s, %s) already seen for release %s, skipping' % (  # noqa
                    name, sha256, version))
                continue
            if artifact['packagetype'] != 'sdist':
                continue
            yield artifact

    def _cleanup_release_artifacts(self, archive_path, directory_path):
        """Clean intermediary files which no longer needs to be present.

        """
        if directory_path and os.path.exists(directory_path):
            logging.debug('Clean up uncompressed archive path %s' % (
                directory_path, ))
            shutil.rmtree(directory_path)

        if archive_path and os.path.exists(archive_path):
            logging.debug('Clean up archive %s' % archive_path)
            os.unlink(archive_path)

    def all_release_artifacts(self):
        """Generate a mapping of releases to their artifacts"""
        ret = defaultdict(list)
        for version, artifacts in self.data['releases'].items():
            for artifact in self._filter_release_artifacts(version, artifacts):
                ret[version].append((artifact['filename'],
                                     artifact['digests']['sha256']))

        return ret

    def default_release(self):
        """Return the version number of the default release,
           as would be installed by `pip install`"""
        return self.data['info']['version']

    def download_new_releases(self, known_artifacts):
        """Fetch metadata/data per release (if new release artifact detected)

        For new release artifact, this:
        - downloads and uncompresses the release artifacts.
        - yields the (release info, author info, release, dir_path)
        - Clean up the intermediary fetched artifact files

        Args:
            known_artifacts (tuple): artifact name, artifact sha256 hash

        Yields:
            tuple (version, release_info, release, uncompressed_path) where:

            - project_info (dict): release's associated version info
            - author (dict): Author information for the release
            - artifact (dict): Release artifact information
            - release (dict): release metadata
            - uncompressed_path (str): Path to uncompressed artifact

        """
        releases_dict = self.data['releases']
        for version, releases in releases_dict.items():
            releases = self._filter_release_artifacts(
                version, releases, known_artifacts)
            releases = self.client.prepare_release_artifacts(
                self.project, version, releases)
            for release, artifact, archive, dir_path, pkginfo in releases:
                if pkginfo is None:  # fallback to pypi api metadata
                    msg = '%s %s: No PKG-INFO detected, skipping' % (  # noqa
                            self.project, version)
                    logging.warn(msg)
                    continue
                yield pkginfo, author(pkginfo), release, artifact, dir_path
                self._cleanup_release_artifacts(archive, dir_path)
