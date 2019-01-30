# !/usr/bin/env python
# encoding:UTF-8

from django import forms
from dynamic_preferences.fields import FieldUpfile
from .registries import global_preferences_registry, user_preferences_registry, site_preferences_registry
from six import string_types
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe, SafeText
from django.utils.translation import ugettext_lazy
from django.utils.html import format_html, force_text
from django.forms.util import flatatt


def preference_form_builder(form_base_class, preferences=(), **kwargs):
    """
    Return a form class for updating preferences
    :param form_base_class: a Form class used as the base. Must have a ``registry` attribute
    :param preferences: a list of :py:class:
    :var section: a section where the form builder will load preferences
    """
    registry = form_base_class.registry
    preferences_obj = []
    if len(preferences) > 0:
        # Preferences have been selected explicitly 
        for pref in preferences:
            if isinstance(pref, string_types):
                preferences_obj.append(registry.get(name=pref))
            elif type(pref) == tuple:
                preferences_obj.append(registry.get(name=pref[0], section=pref[1]))
            else:
                raise NotImplementedError("The data you provide can't be converted to a Preference object")
    else:
        # Try to use section param
        preferences_obj = registry.preferences(section=kwargs.get('section', None))

    fields = {}
    instances = []
    for preference in preferences_obj:
        f = preference.field
        model_kwargs = kwargs.get('model', {})
        instance = preference.to_model(**model_kwargs)
        f.initial = instance.value
        fields[preference.identifier()] = f
        instances.append(instance)

    form_class = type('Custom' + form_base_class.get_name(), (form_base_class,), {})
    form_class.base_fields = fields
    form_class.preferences = preferences_obj
    form_class.instances = instances
    return form_class


def global_preference_form_builder(preferences=(), **kwargs):
    """
    A shortcut :py:func:`preference_form_builder(GlobalPreferenceForm, preferences, **kwargs)`
    """
    return preference_form_builder(GlobalPreferenceForm, preferences, **kwargs)


def user_preference_form_builder(user, preferences=(), **kwargs):
    """
    A shortcut :py:func:`preference_form_builder(UserPreferenceForm, preferences, **kwargs)`
    :param user: a :py:class:`django.contrib.auth.models.User` instance
    :param preferences: preferences
    """
    return preference_form_builder(UserPreferenceForm, preferences, model={'user': user}, **kwargs)


def site_preference_form_builder(preferences=(), **kwargs):
    """
    A shortcut :py:func:`preference_form_builder(SitePreferenceForm, preferences, **kwargs)`
    """
    return preference_form_builder(SitePreferenceForm, preferences, **kwargs)


class PreferenceForm(forms.Form):
    registry = None

    @classmethod
    def get_name(cls):
        return cls.__name__

    def update_preferences(self):
        for instance in self.instances:
            instance.value = self.cleaned_data[instance.preference.identifier()]
            instance.save()


class GlobalPreferenceForm(PreferenceForm):
    registry = global_preferences_registry


class UserPreferenceForm(PreferenceForm):
    registry = user_preferences_registry


class SitePreferenceForm(PreferenceForm):
    registry = site_preferences_registry


class OptimisedClearableFileInput(forms.ClearableFileInput):
    template_with_initial = (
        '<div><div style="width: 50px;max-height: 50px;float: left;margin: 0px 10px 0px 0px;">'
        '<img src="%(initial_url)s" style=" max-width:50px; max-height:50px;" /></div> '
        '<div style="">%(initial_text)s: <a href="%(initial_url)s" target="_blank">%(initial)s</a></div> </div>'
        # '<span class="clear-file"> %(clear_template)s</span> <span>%(input_text)s: %(input)s </span>'
        '<span>%(input)s</span>'
    )
    clear_checkbox_label = ugettext_lazy('Remove this file')
    template_with_clear = '%(clear)s %(clear_checkbox_label)s -'

    @staticmethod
    def is_initial(value):
        """
        Return whether value is considered to be initial value.
        """
        return bool(value)

    @staticmethod
    def get_template_substitution_values(value):
        """
        Return value-related substitutions.
        """
        return {
            'initial': conditional_escape(value),
            'initial_url': FieldUpfile.get_file_url(conditional_escape(value)),
        }

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': 'File name',
            'input_text': 'File',
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(OptimisedClearableFileInput, self).render(name, value, attrs)

        if self.is_initial(value):
            template = self.template_with_initial
            substitutions.update(self.get_template_substitution_values(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = forms.CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions
        return mark_safe(template % substitutions)


class ColorInput(forms.TextInput):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))

        t = "<input id='" + name + "-sp' style='position:relative;left: 5px;width: 80px;' maxlength='7' value='" + \
            value + "' />"
        js_script = "<script type='text/javascript'>"
        js_script = js_script + "document.getElementsByName('" + name + "')[0]" \
                                ".addEventListener('input', function(e){ " \
                                "document.getElementById('" + name + "-sp').value = this.value; });"
        js_script = js_script + "document.getElementById('" + name + "-sp')" \
                                ".addEventListener('input', function(e){ console.log(this.value); " \
                                "document.getElementsByName('" + name + "')[0].value = this.value; });</script>"
        html = format_html('<input{0} style="width:65px;"/>' + t, flatatt(final_attrs)) + SafeText(js_script)
        return html
