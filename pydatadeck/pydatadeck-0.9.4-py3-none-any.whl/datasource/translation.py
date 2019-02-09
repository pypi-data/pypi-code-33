"""Helpers for text translation"""

import gettext


# Global cache for installed gettext object for different locales
_gettext_cache = {}


def get_translator(locale, domain, locale_dir='locales'):
    """
    Gets cached gettext function for translation.

    Args:
        locale (str): locale, e.g. en_US, zh_CN
        domain (str): domain of translation, which affect
            name of translation resources to be loaded
        locale_dir (str, optional): directory to locate
            translation message resources

    Returns:
        [type]: [description]
    """

    translation = _gettext_cache.get(locale)
    if not translation:
        lang = gettext.translation(domain,
                                   localedir=locale_dir,
                                   languages=[locale])
        lang.install()
        translation = lang.gettext
        _gettext_cache[locale] = translation

    return translation
