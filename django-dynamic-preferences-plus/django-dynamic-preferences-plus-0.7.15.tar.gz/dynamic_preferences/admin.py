# !/usr/bin/env python
# encoding:UTF-8

import operator
from django.contrib import admin
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel
from django import forms
from dynamic_preferences.types import FilePreference
from django.db import models
from django.contrib.admin.util import lookup_needs_distinct
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


class PreferenceChangeListForm(forms.ModelForm):
    """
    A form that integrate dynamic-preferences into django.contrib.admin
    """
    # Me must use an acutal model field, so we use raw_value. However, 
    # instance.value will be displayed in form.
    raw_value = forms.CharField()

    def is_multipart(self):
        """
        Returns True if the form needs to be multipart-encoded, i.e. it has
        FileInput. Otherwise, False.
        """
        for section in self.instance.registry:
            for pref in self.instance.registry[section]:
                if isinstance(self.instance.registry[section][pref], FilePreference):
                    return True
        return False

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')
        super(PreferenceChangeListForm, self).__init__(*args, **kwargs)
        self.fields['raw_value'] = self.instance.preference.setup_field()

    def save(self, *args, **kwargs):
        ikargs = {}
        if isinstance(self.instance.preference, FilePreference):
            ikargs['delete_filename'] = self.initial['raw_value']
        self.cleaned_data['raw_value'] = self.instance.preference.serializer.serialize(self.cleaned_data['raw_value'],
                                                                                       **ikargs)
        return super(PreferenceChangeListForm, self).save(*args, **kwargs)


class GlobalPreferenceChangeListForm(PreferenceChangeListForm):
    class Meta:
        model = GlobalPreferenceModel


class UserPreferenceChangeListForm(PreferenceChangeListForm):
    class Meta:
        model = UserPreferenceModel


class DynamicPreferenceAdmin(admin.ModelAdmin):
    changelist_form = PreferenceChangeListForm
    readonly_fields = ('section', 'name', 'value', 'help')
    fields = ("raw_value",)
    list_display = ['section', 'name', 'raw_value', 'help']
    list_display_links = ['name', ]
    list_editable = ('raw_value',)
    search_fields = ['section', 'name', 'help']
    list_filter = ('section',)
    ordering = ('section', 'name')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return []

    def get_changelist_form(self, request, **kwargs):
        return self.changelist_form

    def get_search_results(self, request, queryset, search_term):

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        initial_queryset = queryset
        use_distinct = False
        if self.search_fields and search_term:
            orm_lookups = [construct_search(str(search_field)) for search_field in self.search_fields]
            for bit in search_term.split():
                or_queries = [models.Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
                queryset = queryset.filter(reduce(operator.or_, or_queries))
            if not use_distinct:
                for search_spec in orm_lookups:
                    if lookup_needs_distinct(self.opts, search_spec):
                        use_distinct = True
                        break
        if not queryset.count():
            queryset = initial_queryset
            if search_term != '':
                self.message_user(request,
                                  _('No results found for \'%(search_term)s\'') % {'search_term': search_term},
                                  messages.INFO)
        return queryset, use_distinct


class GlobalPreferenceAdmin(DynamicPreferenceAdmin):
    form = GlobalPreferenceChangeListForm
    changelist_form = GlobalPreferenceChangeListForm


admin.site.register(GlobalPreferenceModel, GlobalPreferenceAdmin)


class UserPreferenceAdmin(DynamicPreferenceAdmin):
    form = UserPreferenceChangeListForm
    changelist_form = UserPreferenceChangeListForm
    list_display = ['user'] + DynamicPreferenceAdmin.list_display
    search_fields = ['user__username'] + DynamicPreferenceAdmin.search_fields


admin.site.register(UserPreferenceModel, UserPreferenceAdmin)
