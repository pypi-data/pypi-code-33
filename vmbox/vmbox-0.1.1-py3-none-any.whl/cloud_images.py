import os

import click
import requests
from bs4 import BeautifulSoup
from ruamel.yaml import safe_load


class LinuxDistro(object):
    def __init__(self, name):
        self.name = name

        with open("repositories.yaml", "r") as f:
            self.distros = safe_load(f).get("distros")

    @property
    def data(self):
        return self.distros.get(self.name)

    @property
    def releases(self):
        return list(map(str, self.data.get("releases")))

    @property
    def repo_link(self):
        return self.data.get("repo")

    @property
    def img_format(self):
        return self.data.get("format")

    def release_url(self, release=None):
        if not release:
            release = self.releases[-1]

        if self.name == "centos":
            return "{repo}/centos/{rel}/images".format(repo=self.repo_link, rel=release)
        elif self.name == "fedora":
            return "{repo}/pub/fedora/linux/releases/{rel}/Cloud/x86_64/images".format(
                repo=self.repo_link, rel=release
            )
        elif self.name == "cirros":
            return "{repo}/{rel}".format(repo=self.repo_link, rel=release)
        elif self.name == "debian":
            return "{repo}/cdimage/cloud/OpenStack/archive/{rel}".format(
                repo=self.repo_link, rel=release
            )
        elif self.name == "ubuntu":
            return "{repo}/releases/{rel}/release".format(repo=self.repo_link, rel=release)
        else:
            click.echo("No release URL available for {}".format(self.name))

    def images(self, release=None, release_url=None, ssl_verify=False):
        """All available cloud remote images"""
        if not release_url:
            release_url = self.release_url(release=release)
        page = requests.get(release_url, verify=ssl_verify).text
        soup = BeautifulSoup(page, "html.parser")
        return [
            node.get("href")
            for node in soup.find_all("a")
            if node.get("href").endswith(self.img_format)
        ]

    def download(self, image, release=None, path=None):
        """Download image with click progress bar
        Args:
            url: cloud image url
            release: release number
            path: Image download to local path
        """
        if not path:
            path = os.path.join(os.environ["HOME"], "Downloads")

        click.echo("Download request for: {img}".format(img=image))
        url = os.path.join(self.release_url(release=release), image)
        r = requests.get(url, stream=True)

        if r.status_code != requests.codes.ok:
            click.echo("Unable to connect {url}".format(url=url))
            r.raise_for_status()

        total_size = int(r.headers.get("Content-Length"))
        local_img_path = os.path.join(path, image)

        with click.progressbar(r.iter_content(1024), length=total_size) as bar, open(
            local_img_path, "wb"
        ) as file:
            for chunk in bar:
                file.write(chunk)
                bar.update(len(chunk))
