import contextlib
import gettext
import os

import babel
import babel.support
import six
import speaklater

from morphi.libs import packages


class Manager(object):
    """Manages translations"""

    def __init__(self, dirname=None, locales=None, domain=None, package_name=None):
        self._locales = None
        self.translations = None

        self.dirname = dirname
        self.domain = domain
        self.package_name = package_name

        # `locales` has a setter that depends on the other values, so needs to be
        # initialized last
        self.locales = locales

    @property
    def locales(self):
        return self._locales

    @locales.setter
    def locales(self, value):
        if (
                value is not None and
                not isinstance(value, (tuple, list))
        ):
            value = [value]

        if (
                value != self._locales or
                self.translations is None
        ):
            self._locales = value

            # now that we've updated the locale, we need to load the new translations
            self.translations = self._translations_loader(self.dirname, self.locales,
                                                          self.domain, self.package_name)

    def gettext(self, string, **variables):
        translations = self.translations

        # translate string
        translated_string = (
            string
            if translations is None
            else translations.gettext(string)
        )

        return (
            translated_string
            if not variables
            else translated_string.format(**variables)
        )

    def lazy_gettext(self, string, **variables):
        return speaklater.make_lazy_string(self.gettext, string, **variables)

    def lazy_ngettext(self, singular, plural, num, **variables):
        return speaklater.make_lazy_string(self.ngettext, singular, plural, num, **variables)

    def _mo_finder(self, domain=None, localedir=None, languages=None, all=False,
                   package_name=None, extension='mo'):
        if domain is None:
            domain = self.domain

        if languages is None:
            languages = self.locales

        if package_name is None:
            package_name = self.package_name

        return find_mo_filename(
            domain=domain,
            localedir=localedir,
            languages=languages,
            all=all,
            package_name=package_name,
            extension=extension
        )

    def ngettext(self, singular, plural, num, **variables):
        variables.setdefault('num', num)

        string_to_translate = (
            singular
            if num == 1
            else plural
        )
        return self.gettext(string_to_translate, **variables)

    def _translations_loader(self, *args, **kwargs):
        return load_translations(*args, **kwargs)


def find_mo_filename(domain=None, localedir=None, languages=None, all=False,  # noqa: C901
                     package_name=None, extension='mo'):
    """
    Search the filesystem and package for an appropriate .mo file, and return the path
    (or `None`, if not found)
    """
    if languages is not None:
        if not isinstance(languages, (list, tuple)):
            languages = [languages]

        languages = [str(language) for language in languages]

    for attempted_domain in (None, domain, package_name):
        if not attempted_domain:
            attempted_domain = babel.support.Translations.DEFAULT_DOMAIN

        for attempted_package_name in (
                None,
                package_name
        ):
            filename = None

            attempted_dirnames = [localedir]
            if package_name:
                attempted_dirnames.extend([
                    'locale',
                    'i18n'
                ])

            for attempted_dirname in attempted_dirnames:
                path_exists = (
                    packages.enclose_package_path_exists(package_name)
                    if attempted_package_name is not None
                    else None
                )
                filename = gettext_find(attempted_domain, attempted_dirname, languages,
                                        all, path_exists=path_exists, extension=extension)
                if filename:
                    break

            if filename:
                break

        if filename:
            break

    # `filename` could be an empty string or an empty list; if so, normalize it to `None`
    if not filename:
        return None

    return filename


def get_mo_data(dirname=None, locales=None, domain=None, package_name=None):
    """
    Finds the .mo data for the specified parameters, and returns the binary data.
    If the .mo file cannot be found or read, returns `None`
    """
    mo_filename = find_mo_filename(localedir=dirname, languages=locales,
                                   domain=domain, package_name=package_name)

    if mo_filename is None:
        return None

    openers = []

    if package_name is not None:
        openers.append({
            'opener': packages.package_open,
            'args': (package_name, mo_filename)
        })

    openers.append({
        'opener': open,
        'args': (mo_filename, 'rb')
    })

    resource_data = None
    for config in openers:
        opener = config['opener']
        opener_args = config['args']

        try:
            with opener(*opener_args) as f:
                resource_data = f.read()

            break

        except NotImplementedError:
            pass

    return resource_data


def gettext_find(domain, localedir=None, languages=None, all=False,  # noqa: C901
                 path_exists=None, extension='mo'):
    """
    Locate a file using the `gettext` strategy.

    This is almost a straight copy of `gettext.find`
    """

    if path_exists is None:
        path_exists = os.path.exists

    # Get some reasonable defaults for arguments that were not supplied
    if localedir is None:
        localedir = gettext._default_localedir
    if languages is None:
        languages = []
        for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            val = os.environ.get(envar)
            if val:
                languages = val.split(':')
                break
        if 'C' not in languages:
            languages.append('C')
    # now normalize and expand the languages
    nelangs = []
    for lang in languages:
        for nelang in gettext._expand_lang(lang):
            if nelang not in nelangs:
                nelangs.append(nelang)
    # select a language
    if all:
        result = []
    else:
        result = None
    for lang in nelangs:
        if lang == 'C':
            break
        mofile = os.path.join(localedir, lang, 'LC_MESSAGES', '%s.%s' % (domain, extension))
        mofile_lp = os.path.join("/usr/share/locale-langpack", lang,
                                 'LC_MESSAGES', '%s.%s' % (domain, extension))

        # first look into the standard locale dir, then into the
        # langpack locale dir

        # standard mo file
        try:
            if path_exists(mofile):
                if all:
                    result.append(mofile)
                else:
                    return mofile

            # langpack mofile -> use it
            if path_exists(mofile_lp):
                if all:
                    result.append(mofile_lp)
                else:
                    return mofile_lp

        except (NotImplementedError, ValueError):
            pass

    return result


def load_translations(dirname=None, locales=None, domain=None, package_name=None):
    """
    Find the .mo data for the specified parameters, and returns the translations.
    If the .mo file cannot be found or read, returns `None`
    """
    mo_data = get_mo_data(dirname, locales, domain, package_name)
    if mo_data is None:
        return babel.support.NullTranslations()

    with contextlib.closing(six.BytesIO(mo_data)) as fp:
        translations = babel.support.Translations(fp=fp,
                                                  domain=domain or package_name)

    return translations
