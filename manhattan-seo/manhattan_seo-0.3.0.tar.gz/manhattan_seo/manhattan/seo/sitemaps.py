import operator
import pathlib
from xml.etree import ElementTree

from manhattan.formatters.flask import path_to_url

__all__ = [
    'Sitemap',
    'SitemapImage',
    'SitemapIndex',
    'SitemapURL'
]


class Sitemap:
    """
    A sitemap.
    """

    def __init__(self, urls):
        self.urls = urls

    def dump(self, filepath):
        """Save the sitemap to the given filepath"""
        with open(filepath, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(
                ElementTree
                    .tostring(self.to_elm(), encoding='unicode')
                    .replace('<loc>', '\n    <loc>')
                    .replace('<changefreq>', '\n    <changefreq>')
                    .replace('<priority>', '\n    <priority>')
                    .replace('<image:image>', '\n    <image:image>')
                    .replace('</image:image>', '\n    </image:image>')
                    .replace('<image:loc>', '\n        <image:loc>')
                    .replace('<image:title>', '\n        <image:title>')
                    .replace('<image:caption>', '\n        <image:caption>')
                    .replace('<url>', '\n<url>')
                    .replace('</url>', '\n</url>')
                    .replace('</urlset>', '\n</urlset>')
            )

    def to_elm(self):
        urlset_elm = ElementTree.Element('urlset')
        urlset_elm.set(
            'xmlns',
            'http://www.sitemaps.org/schemas/sitemap/0.9'
        )

        urlset_elm.set(
            'xmlns:image',
            'http://www.google.com/schemas/sitemap-image/1.1'
        )

        for url in self.urls:
            urlset_elm.append(url.to_elm())

        return urlset_elm

    @classmethod
    def chunk_urls(cls, urls, max_urls=45000):
        """
        Return a list of sitemaps each containing no more than the maximum
        number of URLs for a sitemap.
        """
        urls.sort(key=operator.attrgetter('url'))
        chunks = [urls[i:i + max_urls] for i in range(0, len(urls), max_urls)]
        return [cls(chunk) for chunk in chunks]


class SitemapImage:
    """
    A sitemap image.
    """

    def __init__(self, url, title=None, caption=None):
        self.url = path_to_url(url) if url.startswith('/') else url
        self.title = title
        self.caption = caption

    def to_elm(self):
        image_elm = ElementTree.Element('image:image')

        # Location
        loc_elm = ElementTree.SubElement(image_elm, 'image:loc')
        loc_elm.text = self.url

        # Title
        if self.title:
            title_elm = ElementTree.SubElement(image_elm, 'image:title')
            title_elm.text = self.title

        # Caption
        if self.caption:
            caption_elm = ElementTree.SubElement(image_elm, 'image:caption')
            caption_elm.text = self.caption

        return image_elm


class SitemapIndex:
    """
    A sitemap index.
    """

    def __init__(self):
        self.sections = {}

    def add_section(self, name, urls, max_urls_per_file=45000):
        """Add a section of URLs to the sitemap index"""
        self.sections[name] = Sitemap.chunk_urls(urls, max_urls_per_file)

    def dump(self, path='nginx_static'):
        """Save the sitemap index to file"""

        # Make sure the save directory exists
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        # Write each sitemap to file
        for name, sitemaps in self.sections.items():
            for i, sitemap in enumerate(sitemaps):

                filepath = '{0}/sitemaps/{1}.xml'.format(path, name)
                if i > 0:
                    filepath = '{0}/sitemaps/{1}-{2}.xml'.format(
                        path,
                        name,
                        i
                    )

                sitemap.dump(filepath)

        # Write the sitemap index to file
        with open('{0}/sitemap.xml'.format(path), 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(
                ElementTree
                    .tostring(self.to_elm(), encoding='unicode')
                    .replace('<sitemap>', '\n<sitemap>')
                    .replace('</sitemapindex>', '\n</sitemapindex>')
            )

    def to_elm(self):
        sitemapindex_elm = ElementTree.Element('sitemapindex')
        sitemapindex_elm.set(
            'xmlns',
            'http://www.sitemaps.org/schemas/sitemap/0.9'
        )

        for name, sitemaps in self.sections.items():
            for i, sitemap in enumerate(sitemaps):

                sitemap_elm = ElementTree.SubElement(
                    sitemapindex_elm,
                    'sitemap'
                )

                path = '/sitemaps/{0}.xml'.format(name)
                if i > 0:
                    path = '/sitemaps/{0}-{1}.xml'.format(name, i)

                loc_elm = ElementTree.SubElement(sitemap_elm, 'loc')
                loc_elm.text = path_to_url(path)

        return sitemapindex_elm


class SitemapURL:
    """
    A sitemap URL.
    """

    def __init__(self, url, priority='0.5', changefreq='monthly'):
        self.url = path_to_url(url) if url.startswith('/') else url
        self.changefreq = changefreq
        self.priority = str(priority)
        self.images = []

    def add_image(self, image):
        """Add an image to the URL"""
        self.images.append(image)

    def to_elm(self):
        url_elm = ElementTree.Element('url')

        # Location
        loc_elm = ElementTree.SubElement(url_elm, 'loc')
        loc_elm.text = self.url

        # Change frequency
        changefreq_elm = ElementTree.SubElement(url_elm, 'changefreq')
        changefreq_elm.text = self.changefreq

        # Priority (only add for the none default value)
        if self.priority != '0.5':
            priority_elm = ElementTree.SubElement(url_elm, 'priority')
            priority_elm.text = self.priority

        # Images
        for image in self.images:
            url_elm.append(image.to_elm())

        return url_elm
