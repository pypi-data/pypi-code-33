"""Render WTForms using Bootstrap 3.

Inspired by https://github.com/carlnewton/bootstrap-wtf

TODO:
* Don't depend on glyphicons. Maybe take an option for glyphicons, fontawesome,
	or none? We just need it for the close icon. We could fall back on an X.
	Icons depend on FontAwesome, should we just assume that?
* Help text aria-describedby
	https://getbootstrap.com/docs/3.3/css/#forms-help-text
* Disabled & Readonly
	https://getbootstrap.com/docs/3.3/css/#forms-control-disabled
	https://getbootstrap.com/docs/3.3/css/#forms-control-readonly
* Check types using inheritance instead of checking type names
* Rename TEXT_FIELD_TYPES to reflect that it is checking
	textual <input>, <textarea>, and <select> not just text fields
* Add support for static control "fields"
	https://getbootstrap.com/docs/3.3/css/#forms-controls-static
"""
from typing import Dict, Sequence, Union, Mapping, Any, Optional

from flask import Markup
from wtforms import Form, Field, FieldList, HiddenField


TEXT_FIELD_TYPES = frozenset((
	'DateField',
	'DateTimeField',
	'DecimalField',
	'FloatField',
	'IntegerField',
	'PasswordField',
	'SelectField',
	'SelectMultipleField',
	'StringField',
	'TextAreaField',
	'TextField',
	'SearchField',
	'TelField',
	'URLField',
	'EmailField',
	'TimeField',
	'DateTimeLocalField',
	'IntegerRangeField',
	'DecimalRangeField',
	'QuerySelectField',
	'QuerySelectMultipleField',
	))
OTHER_FIELD_TYPES = frozenset((
	'BooleanField',
	'FileField',
	'RadioField',
	'SubmitField',
	))
KNOWN_FIELD_TYPES = TEXT_FIELD_TYPES & OTHER_FIELD_TYPES
FIELD_TYPE_ICONS = {
	'EmailField': '@',
	'DateField': '<span class="fa fa-calendar"></span>',
	'DateTimeField': '<span class="fa fa-calendar"></span>',
	'TelField': '<span class="fa fa-phone"></span>',
	'TimeField': '<span class="fa fa-clock-o"></span>',
	'PasswordField': '<span class="fa fa-key"></span>',
	'URLField': '<span class="fa fa-link"></span>',
	}
ERROR_ICON = (
	'<span class="glyphicon glyphicon-remove form-control-feedback" '
	'aria-hidden="true"></span><span class="sr-only">(error)</span>'
	)


def _space_join_cond(names_conditions: Mapping[Optional[str], Any]) -> str:
	"""Return a space joined string based on mapped conditions."""
	return ' '.join(k for k, v in names_conditions.items() if (k and v))


def _col(text: str, width: int, size: str = 'sm', offset: int = None) -> str:
	"""Wrap text in a column with width."""
	classes = _space_join_cond({
		f'col-{size}-{width}': True,
		f'col-{size}-offset-{offset}': offset,
		})
	return f'<div class="{classes}">{text}</div>'


def bootstrap_field(
	field: Field,
	form_group: bool = True,
	placeholder: Union[bool, str] = True,
	label: bool = True,
	errors: bool = True,
	horizontal: bool = False,
	inline: bool = False,
	btn_color: str = 'default',
	icon: Union[bool, str] = False,
	**kwargs
	) -> Markup:
	"""Render a WTForms Field with Bootstrap markup.

	Args:
		field: The field to render.
		form_group: Whether or not to make it a form-group.
		placeholder: The string to display as a placeholder, True to display the
			default placeholder and something falsey to display nothing.
		label: Whether or not to display the field label.
		errors: Whether or not to display errors.
		horizontal: Whether to display the field horizontally.
		icon:
		inline: Whether to display the field inline.
		btn_color: The color name to pass as the button color.
	"""
	# TODO respect inline
	if isinstance(field, HiddenField):
		# Handles CSRFTokenFields
		return Markup(str(field))

	is_text_field = field.type in TEXT_FIELD_TYPES
	field_classes = _space_join_cond({
		'form-control': is_text_field,
		'btn btn-' + btn_color: field.type == 'SubmitField',
		})
	if placeholder is True and field.type in TEXT_FIELD_TYPES:
		placeholder = 'Enter %s' % field.label.text
	html_str = field(
		class_=field_classes,
		placeholder=placeholder,
		**kwargs
		)
	html_str = _insert_icon(html_str, field, icon, is_text_field)

	horizontal_field_offset = 2
	label_html = ''
	if horizontal and field.errors:
		html_str += ERROR_ICON
	if field.type == 'BooleanField':
		html_str = (
			f'<div class="checkbox"><label>{html_str} {field.label.text}'
			'</label></div>'
			)
	elif field.type != 'SubmitField' and label:
		label_html = field.label(class_=_space_join_cond({
			'control-label': True,
			'col-sm-2': horizontal
			}))
		horizontal_field_offset = 0
	if horizontal:
		html_str = label_html + _col(html_str, 10, offset=horizontal_field_offset)
	else:
		html_str = label_html + html_str
		if form_group and field.errors:
			html_str += ERROR_ICON

	if form_group:
		form_group_classes = _space_join_cond({
			'form-group': True,
			'has-error has-feedback': field.errors,
			'required': field.flags.required,
			})
		html_str = f'<div class="{form_group_classes}">{html_str}</div>'

	html_str += _field_description(field, horizontal)
	html_str += _field_errors(field, errors, horizontal)

	return Markup(html_str)


def _insert_icon(
	html_str: str,
	field: Field,
	icon: Union[str, bool, None],
	is_text_field: bool,
	) -> str:
	"""Insert an icon into a bootstrap input field."""
	if icon and is_text_field:
		if icon is True:
			icon = FIELD_TYPE_ICONS.get(field.type)
		if icon:
			html_str = (
				f'<div class="input-group"><span class="input-group-addon">'
				f'{icon}</span>{html_str}</div>'
				)
	return html_str


def _field_description(field, horizontal):
	description_html = ''
	if field.description:
		description_html = f'<p class ="help-block">{field.description}</p>'
		if horizontal:
			description_html = _col(description_html, 10, offset=2)
	return description_html


def _field_errors(field, errors, horizontal):
	error_html = ''
	if field.errors and errors:
		if len(field.errors) == 1:
			error_html = f'<p class="text-danger">{field.errors[0]}</p>'
		else:
			error_html = ''.join(
				f'<li class="text-danger">{error}</li>'
				for error in field.errors
				)
			error_html = f'<ul>{error_html}</ul>'
		if horizontal:
			error_html = _col(error_html, 10, offset=2)
	return error_html


def _gen_fields(obj: Union[Form, Sequence[Field], FieldList]):
	"""Recursively generate all of the fields in obj."""
	for field in obj:
		if field.type == 'FieldList':
			yield from _gen_fields(field)
		else:
			yield field


def bootstrap_form(
	form: Form,
	action: str = None,
	*,
	method: str = 'POST',
	form_groups: bool = True,
	placeholders: bool = True,
	labels: bool = True,
	errors: bool = True,
	horizontal: bool = False,
	inline: bool = False,
	icons: bool = True,
	id_: str = None,
	class_: str = None,
	field_args: Dict[str, Dict] = None,
	) -> Markup:
	"""Render a WTForms Form with Bootstrap markup.

	Args:
		form: The form to render.
		action: The action of the form.
		method: The method of the form.
		form_groups: Whether to render form groups.
		placeholders: Whether to display placeholders.
		labels: Whether to display labels.
		errors: Whether to display errors.
		horizontal: Render horizontal Bootstrap form.
		inline: Render inline Bootstrap form.
		icons: Whether to display icons in the input.
		id_: An HTML id for the form.
		class_: Classes to add to the form.
		field_args: A mapping of field names to additional arguments to pass
			to each field.
	"""
	if horizontal and inline:
		raise ValueError
	field_args = field_args or {}

	file_upload = any(field.type == 'FileField' for field in _gen_fields(form))
	form_classes = _space_join_cond({
		'form-horizontal': horizontal,
		'form-inline': inline,
		class_: class_,
		})
	form_attrs = _space_join_cond({
		'id="%s"' % id_: id_,
		'method="%s"' % method: method,
		'action="%s"' % action: action,
		'enctype=multipart/form-data': file_upload,
		'class="%s"' % form_classes: form_classes,
		})

	field_values = []
	for field in _gen_fields(form):
		extra_args = field_args.get(field.name, {})
		field_values.append(bootstrap_field(
			field,
			form_group=form_groups,
			placeholder=placeholders,
			label=labels,
			errors=errors,
			horizontal=horizontal,
			inline=inline,
			icon=icons,
			**extra_args
			))
	fields_html = ''.join(field_values)
	html = f'<form {form_attrs}>{fields_html}</form>'
	return Markup(html)
