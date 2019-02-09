# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import jinja2
import upt


class NixPackage(object):
    def __init__(self, upt_pkg):
        self.upt_pkg = upt_pkg

    def __getattribute__(self, name):
        if name in ['homepage', 'name', 'summary', 'version']:
            return self.upt_pkg.__getattribute__(name)
        else:
            return object.__getattribute__(self, name)

    @property
    def licenses(self):
        spdx_to_nix = {
            'AFL-2.1': 'licenses.afl21',
            'AFL-3.0': 'licenses.afl3',
            'AGPL-3.0': 'licenses.agpl3',
            'APSL-2.0': 'licenses.apsl20',
            'Artistic-1.0': 'licenses.artistic1',
            'Artistic-2.0': 'licenses.artistic2',
            'Apache-2.0': 'licenses.asl20',
            'BSL-1.0': 'licenses.boost',
            'Beerware': 'licenses.beerware',
            '0BSD': 'licenses.bsd0',
            'BSD-2-Clause': 'licenses.bsd2',
            'BSD-3-Clause': 'licenses.bsd3',
            'BSD-4-Clause': 'licenses.bsdOriginal',
            'ClArtistic': 'licenses.clArtistic',
            'CC0-1.0': 'licenses.cc0',
            'CC-BY-NC-SA-2.0': 'licenses.cc-by-nc-sa-20',
            'CC-BY-NC-SA-2.5': 'licenses.cc-by-nc-sa-25',
            'CC-BY-NC-SA-3.0': 'licenses.cc-by-nc-sa-30',
            'CC-BY-NC-SA-4.0': 'licenses.cc-by-nc-sa-40',
            'CC-BY-ND-3.0': 'licenses.cc-by-nd-30',
            'CC-BY-SA-2.5': 'licenses.cc-by-sa-25',
            'CC-BY-3.0': 'licenses.cc-by-30',
            'CC-BY-SA-3.0': 'licenses.cc-by-sa-30',
            'CC-BY-4.0': 'licenses.cc-by-40',
            'CC-BY-SA-4.0': 'licenses.cc-by-sa-40',
            'CDDL-1.0': 'licenses.cddl',
            'CECILL-2.0': 'licenses.cecill20',
            'CECILL-B': 'licenses.cecill-b',
            'CECILL-C': 'licenses.cecill-c',
            'CPL-1.0': 'licenses.cpl10',
            'DOC': 'licenses.doc',
            'EFL-1.0': 'licenses.efl10',
            'EFL-2.0': 'licenses.efl20',
            'EPL-1.0': 'licenses.epl10',
            'EPL-2.0': 'licenses.epl20',
            'EUPL-1.1': 'licenses.eupl11',
            'GFDL-1.2': 'licenses.fdl12',
            'GFDL-1.3': 'licenses.fdl13',
            'GPL-1.0': 'licenses.gpl1',
            'GPL-1.0+': 'licenses.gpl1Plus',
            'GPL-2.0': 'licenses.gpl2',
            'GPL-2.0+': 'licenses.gpl2Plus',
            'GPL-3.0': 'licenses.gpl3',
            'GPL-3.0+': 'licenses.gpl3Plus',
            'HPND': 'licenses.hpnd',
            'IJG': 'licenses.ijg',
            'IPA': 'licenses.ipa',
            'IPL-1.0': 'licenses.ipl10',
            'ISC': 'licenses.isc',
            'LGPL-2.0': 'licenses.lgpl2',
            'LGPL-2.0+': 'licenses.lgpl2Plus',
            'LGPL-2.1': 'licenses.lgpl21',
            'LGPL-2.1+': 'licenses.lgpl21Plus',
            'LGPL-3.0': 'licenses.lgpl3',
            'LGPL-3.0+': 'licenses.lgpl3Plus',
            'Libpng': 'licenses.libpng',
            'libtiff': 'licenses.libtiff',
            'LPPL-1.2': 'licenses.lppl12',
            'LPPL-1.3c': 'licenses.lppl13c',
            'LPL-1.02': 'licenses.lpl-102',
            'MIT': 'licenses.mit',
            'MPL-1.0': 'licenses.mpl10',
            'MPL-1.1': 'licenses.mpl11',
            'MPL-2.0': 'licenses.mpl20',
            'MS-PL': 'licenses.mspl',
            'NCSA': 'licenses.ncsa',
            'NPOSL-3.0': 'licenses.nposl3',
            'OFL-1.1': 'licenses.ofl',
            'OLDAP-2.8': 'licenses.openldap',
            'OpenSSL': 'licenses.openssl',
            'OSL-2.1': 'licenses.osl21',
            'OSL-3.0': 'licenses.osl3',
            'PHP-3.01': 'licenses.php301',
            'PostgreSQL': 'licenses.postgresql',
            'Python-2.0': 'licenses.psfl',
            'QPL-1.0': 'licenses.qpl',
            'Ruby': 'licenses.ruby',
            'SGI-B-2.0': 'licenses.sgi-b-20',
            'Sleepycat': 'licenses.sleepycat',
            'TCL': 'licenses.tcltk',
            'Unlicense': 'licenses.unlicense',
            'Vim': 'licenses.vim',
            'VSL-1.0': 'licenses.vsl10',
            'Watcom-1.0': 'licenses.watcom',
            'W3C': 'licenses.w3c',
            'WTFPL': 'licenses.wtfpl',
            'WXwindows': 'licenses.wxWindows',
            'Zlib': 'licenses.zlib',
            'ZPL-2.0': 'licenses.zpl20',
            'ZPL-2.1': 'licenses.zpl21',
        }

        return [spdx_to_nix.get(upt_license.spdx_identifier, 'XXX')
                for upt_license in self.upt_pkg.licenses]

    @staticmethod
    def _to_nix_name(name):
        return name

    def _get_build_inputs(self, phase):
        return [self._to_nix_name(req.name)
                for req in self.upt_pkg.requirements.get(phase, [])]

    @property
    def native_build_inputs(self):
        native_build_inputs = self._get_build_inputs('test')
        native_build_inputs.extend(self._get_build_inputs('build'))
        return native_build_inputs

    @property
    def propagated_build_inputs(self):
        return self._get_build_inputs('run')

    @property
    def url(self):
        """Return the URL of the source (usually a tar.gz file)."""
        try:
            archive = self.upt_pkg.get_archive()
            return archive.url
        except (upt.ArchiveUnavailable, upt.HashUnavailable):
            return 'TODO'

    @property
    def sha256(self):
        """Return the SHA256 of the source (usually a tar.gz file)."""
        try:
            archive = self.upt_pkg.get_archive()
            return archive.sha256
        except (upt.ArchiveUnavailable, upt.HashUnavailable):
            return 'TODO'

    def render(self):
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('upt_nix', 'templates'),
            trim_blocks=True,
        )
        env.filters['urlformat'] = self.urlformat
        template = env.get_template(self.template)
        return template.render(pkg=self)

    def urlformat(self, url):
        """Format a source URL."""
        return url


class NixPythonPackage(NixPackage):
    template = 'python.nix'

    @staticmethod
    def _to_nix_name(name):
        return name.lower()


class NixPerlPackage(NixPackage):
    template = 'perl.nix'

    @staticmethod
    def _to_nix_name(name):
        return name.replace('::', '')

    def urlformat(self, url):
        return url.replace('https://cpan.metacpan.org', 'mirror://cpan')


class NixBackend(upt.Backend):
    name = 'nix'

    def create_package(self, upt_pkg, output=None):
        pkg_classes = {
            'pypi': NixPythonPackage,
            'cpan': NixPerlPackage,
        }

        try:
            pkg_cls = pkg_classes[upt_pkg.frontend]
        except KeyError:
            raise upt.UnhandledFrontendError(self.name, upt_pkg.frontend)

        print(pkg_cls(upt_pkg).render())
