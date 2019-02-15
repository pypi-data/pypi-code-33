from django.conf import settings
from django.utils.timezone import now

from negative_i18n.models import StringTranslation
from django.db import IntegrityError, OperationalError, ProgrammingError
from django.utils.functional import lazy


from django.core.cache import cache
from modeltranslation.utils import get_language


def translate(string):
    lang = get_language()

    cache_key = 'translations_{}'.format(lang)

    collect = getattr(settings, 'COLLECT_I18N_STATS', True)

    if collect:
        StringTranslation.objects.filter(key=string).update(last_used=now())

    trans_map = cache.get(cache_key, None)
    if not trans_map:
        try:
            trans_map = {x.key: getattr(x, 'translation_{}'.format(lang)) or x.translation for x in StringTranslation.objects.all()}

            cache.set(cache_key, trans_map)
        except (ProgrammingError, OperationalError, AttributeError):
            return string

    # if key exist
    if string in trans_map:
        result = trans_map[string]
    else:
        try:
            StringTranslation(key=string).save()
        except IntegrityError as e:
            print('Insert failed: {}'.format(e))
        trans_map[string] = string

        cache.set(cache_key, trans_map)

        result = string

    if not isinstance(result, str):
        return string

    return result


translate_lazy = lazy(translate, str)
_ = translate_lazy




