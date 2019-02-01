from transliterate import translit, get_available_language_codes
from transliterate.discover import autodiscover
from transliterate.base import TranslitLanguagePack, registry

autodiscover()


class ExtendedRussianLangPack(TranslitLanguagePack):
    language_code = "ru_ext"
    language_name = "Russian extended"
    mapping = (
        u"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        u"АБЦДЕФГХИЙКЛМНОПКРСТУВВКЫЗ",
    )
    pre_processor_mapping = {
        "SHCH": "Щ",
        "YA": "Я",
        "IA": "Я",
        "YU": "Ю",
        "IU": "Ю",
        "CH": "Ч",
        "SH": "Ш",
        "Y": "Й",
        "X": "КС",
        "ZH": "Ж",
        "TS": "Ц",
        "KH": "X"
    }
    reversed_specific_pre_processor_mapping = {
        'В': 'V',
        "Ё": "E",
        "Ж": "ZH",
        "Й": "I",
        'К': 'K',
        "Х": "KH",
        "Ц": "TS",
        "Ч": "CH",
        "Ш": 'SH',
        'Щ': 'SHCH',
        'Ъ': '',
        'Ы': 'Y',
        'Ь': '',
        'Э': 'E',
        'Ю': 'IU',
        'Я': 'IA'
    }


registry.register(ExtendedRussianLangPack, force=True)
