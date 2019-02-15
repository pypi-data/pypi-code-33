import polib
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.translation import get_language
from modeltranslation.admin import TabbedTranslationAdmin as TranslatableModelAdmin
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname

from negative_i18n.models import StringTranslation

from .translation import translator


def get_model_ct_tuple(model):
    # Deferred models should be identified as if they were the underlying model.
    model_name = model._meta.concrete_model._meta.model_name \
        if hasattr(model, '_deferred') and model._deferred else model._meta.model_name
    return (model._meta.app_label, model_name)


def get_model_ct(model):
    return "%s.%s" % get_model_ct_tuple(model)


def get_trans_fields(languages):
    fields = [f"translation_{lang_code}" for lang_code, lang in languages]

    return tuple(fields)


from django import forms


def validate_file_extension(value):
    if not value.name.endswith('.po'):
        raise ValidationError('Only .po files allowed')


class UploadFileForm(forms.Form):
    update_empty = forms.BooleanField(
        label='Copy missing strings',
        required=False
    )
    file = forms.FileField(
        label="Select .po file to import", validators=[validate_file_extension],
        widget=forms.FileInput(attrs={'accept': '.po'})
    )


class StringTranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'translation',) + get_trans_fields(settings.LANGUAGES)
    list_editable = get_trans_fields(settings.LANGUAGES)
    list_filter = ('context',)

    change_list_template = 'negative-i18n/i18n_change_list.html'

    actions = [delete_selected]


    def get_list_display(self, request):
        return ('key', 'last_used',) + get_trans_fields(settings.LANGUAGES)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                print('File uploaded!')
                print(request.FILES['file'])

                po = polib.pofile(request.FILES['file'].read().decode())

                extra_context['po_result'] = self.apply_po_file(po,
                                                                fix_empty_db_strings=form.cleaned_data['update_empty'])

                # handle_uploaded_file()
                # return HttpResponseRedirect('/success/url/')

        extra_context['po_form'] = UploadFileForm()

        po_files = []
        for lang, name in settings.LANGUAGES:
            po_file = self.collect_po_file(lang)
            po_files.append({
                'lang': lang,
                'name': name,
                'percent': po_file.percent_translated(),
                'items': len(po_file),
                'translated': len(po_file.translated_entries())
            })

        extra_context['po_files'] = po_files

        return super().changelist_view(request, extra_context=extra_context)

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if hasattr(settings, 'GOOGLE_TRANSLATE_KEY'):
    #         actions += translate
    #     return actions

    #
    #
    def get_urls(self):
        urls = super(StringTranslationAdmin, self).get_urls()
        my_urls = [
            url(r'^strings_(?P<lang>\w+).po$', self.admin_site.admin_view(self.render_po_file)),
        ]
        return my_urls + urls

    def render_po_file(self, request, lang):

        all_langs = dict(settings.LANGUAGES)

        if not lang in all_langs:
            lang = get_language()

        po = self.collect_po_file(lang)

        response = HttpResponse(content=str(po).encode(), content_type='text/plain; charset=utf-8')

        response['Content-Disposition'] = 'attachment; filename="strings_{}.po"'.format(lang)

        return response

    def apply_po_file(self, po: polib.POFile, fix_empty_db_strings=False):
        string_entries = {}
        model_entries = {}
        for entry in po:
            for kind, identity in entry.occurrences:
                if kind == 'strings':
                    string_entries[entry.msgid] = (entry.msgid, entry.msgstr)
                else:
                    model_entries['{}:{}'.format(kind, identity)] = (entry.msgid, entry.msgstr)

        lang = po.metadata['Language']

        strings_updated = 0
        for key, val in string_entries.items():
            for obj in StringTranslation.objects.filter(key=key):
                localized_fieldname = build_localized_fieldname('translation', lang)

                msgid, msgstr = string_entries[key]

                if not msgstr:
                    if fix_empty_db_strings:
                        msgstr = msgid
                    else:
                        continue

                if getattr(obj, localized_fieldname) != msgstr:
                    setattr(obj, localized_fieldname, msgstr)
                    strings_updated += 1
                    obj.save()

        models = translator.get_registered_models(abstract=False)

        model_entries_updated = 0
        for model in models:
            if model is StringTranslation:
                continue
            opts = translator.get_options_for_model(model)

            fields_to_copy = []
            for field_name in opts.fields.keys():
                fields_to_copy.append(
                    (field_name, build_localized_fieldname(field_name, lang))
                )

            for obj in model.objects.all():
                model_updated = False
                for field_name, field_name_local in fields_to_copy:
                    key = '{}:{}:{}'.format(get_model_ct(model), field_name, obj.id)

                    if key in model_entries:
                        localized_fieldname = build_localized_fieldname(field_name, lang)

                        msgid, msgstr = model_entries[key]

                        if not msgstr:
                            if fix_empty_db_strings:
                                msgstr = msgid
                            else:
                                continue

                        if getattr(obj, localized_fieldname) != msgstr:
                            setattr(obj, localized_fieldname, msgstr)
                            model_updated = True
                            model_entries_updated += 1

                if model_updated:
                    obj.save()

        return {
            'lang': lang,
            'strings_updated': strings_updated,
            'model_entries_updated': model_entries_updated,
        }

    def collect_po_file(self, lang):
        po = polib.POFile()
        po.metadata = {
            'Language': lang,
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }

        def append_item(msgid, msgstr, occurrences):
            entry = po.find(msgid)
            if not entry:
                po.append(
                    polib.POEntry(msgid=msgid, msgstr=msgstr, occurrences=occurrences)
                )
            else:
                entry.occurrences += occurrences

        for string in StringTranslation.objects.all():
            if string.key and len(string.key) > 0:
                append_item(
                    msgid=string.key,
                    msgstr=getattr(string, 'translation_{}'.format(lang)) or '',
                    occurrences=[('strings', str(string.id))]
                )
        models = translator.get_registered_models(abstract=False)
        for model in models:

            if 'products' in str(model):
                continue

            if model is StringTranslation:
                continue
            opts = translator.get_options_for_model(model)

            fields_to_copy = []
            for field_name in opts.fields.keys():
                fields_to_copy.append(
                    (field_name, build_localized_fieldname(field_name, lang))
                )

            for obj in model.objects.all():
                for field_name, field_name_local in fields_to_copy:
                    try:
                        msgid = obj.__dict__[field_name]
                    except KeyError:
                        msgid = None

                    if msgid and msgid != '':
                        if len(msgid) < 300:
                            append_item(
                                msgid=msgid,
                                msgstr=getattr(obj, field_name_local) or '',
                                occurrences=[('{}:{}'.format(get_model_ct(model), field_name), str(obj.id))]
                            )
                        else:
                            print("WARN: text too long for msgid. Model: {} Field: {}".format(model, field_name))
        return po


admin.site.register(StringTranslation, StringTranslationAdmin)
