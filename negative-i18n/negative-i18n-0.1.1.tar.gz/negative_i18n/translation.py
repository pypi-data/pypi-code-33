from negative_i18n.models import StringTranslation
from modeltranslation.translator import translator, TranslationOptions


class StringTranslationOptions(TranslationOptions):
    fields = ('translation',)


translator.register(StringTranslation, StringTranslationOptions)
