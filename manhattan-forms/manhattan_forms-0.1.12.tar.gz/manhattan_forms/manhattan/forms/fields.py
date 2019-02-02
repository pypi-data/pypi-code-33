from datetime import datetime, date
import json
from _string import formatter_field_name_split
from string import Formatter

from manhattan.formatters.text import slugify
from manhattan.utils.chrono import as_tz, localize_datetime
import wtforms.fields.core
import wtforms.fields.html5
import wtforms.fields.simple
from wtforms.fields import *
from wtforms.fields.core import UnboundField
from wtforms.form import Form
from wtforms.utils import unset_value
from wtforms.validators import InputRequired
from wtforms.widgets import (
    CheckboxInput,
    ListWidget,
    Option,
    Select,
    TextArea,
    TextInput
)

from .utils import to_object_id
from .validators import ErrorMessage, PseudoRequired

import wtforms.validators
from wtforms.validators import *

# WTForm fields are passed through to provide a single access point
__all__ = set(wtforms.fields.core.__all__)
__all__ |= set(wtforms.fields.html5.__all__)
__all__ |= set(wtforms.fields.simple.__all__)
__all__.add('CheckboxField')
__all__.add('DocumentCheckboxField')
__all__.add('DocumentSelectField')
__all__.add('HiddenField')
__all__.add('JSONField')
__all__.add('LatLonField')
__all__.add('PriceField')
__all__.add('SlugField')
__all__.add('StringListField')
__all__.add('TimeField')
__all__.add('YesNoField')
__all__ = tuple(__all__)


class CheckboxField(SelectMultipleField):
    """
    The `Checkbox` field supports for a list of checkboxes within a form, for
    single checkboxes use the `wtforms.fields.BooleanField`.
    """

    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class DateField(DateField):
    """
    The `DateField` is overridden to allow the default format to be set.
    """

    default_format = '%Y-%m-%d'

    def __init__(self, label=None, validators=None, format=None, **kwargs):

        # If no format is provided we'll use the classes default format
        if format is None:

            # If the default format is callable we call it to retrieve the
            # format...
            if callable(DateField.default_format):
                format = DateField.default_format()

            # ...else we simple set it as the format.
            else:
                format = DateField.default_format

        super(DateField, self).__init__(label, validators, format, **kwargs)

    def process_formdata(self, values):
        if len(values) and values[0].strip():
            date_str = values[0].strip()

            # Format strings can contain qualifiers '-' or '#' to indicate that
            # a value shouldn't display a leading zero. However these qualifiers
            # cannot be present when using them to parse a date string and so we
            # strip them.
            #
            # HACK: This has been introduced to allow a date format such as:
            # '%-d %B %Y', without this hack the attempt to parse the date
            # string would always fail due to dash (e.g '%-d'). A longer term
            # solution would be to upgrade the existing date field set
            # (`DateTimeField`, `DateField` and `TimeField`) to support a
            # separation of this logic.
            #
            # ~ Anthony Blackshaw, <ant@getme.co.uk> 9 December 2016
            format = ''
            percent = False
            for c in self.format:
                if c in ['-', '#'] and percent:
                    continue

                if c == '%' and not percent:
                    percent = True
                else:
                    percent = False

                format += c

            try:
                self.data = datetime.strptime(date_str, format).date()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))
        else:
            # If no value has been past to parse set the value of the field
            # to none to represent a blank field
            self.data = None


class DateTimeField(FormField):
    """
    The `DateTimeField` is overridden to support a dual field structure and
    to ensure add timezone support.
    """

    def __init__(
        self,
        labels=None,
        tz=None,
        validators=None,
        separator='-',
        *args,
        **kwargs
    ):

        # The fields label
        self.labels = labels or ['Date', 'Time (24HR)']

        # The timezone the datetime
        self.tz = tz

        # Check to see if any of the validators flag the field as required
        required = False
        for validator in (validators or []):
            if 'required' in getattr(validator, 'field_flags', []):
                required = True
                break

        # Build the date/time form
        class _DateTimeField(Form):

            date = DateField(
                self.labels[0],
                validators=[PseudoRequired()] if required else [],
                render_kw={
                    'data-mh-date-picker': True,
                    'required': False
                }
            )

            time = StringField(
                self.labels[1],
                validators=[PseudoRequired()] if required else [],
                render_kw={
                    'placeholder': 'HH:MM',
                    'required': False
                }
            )

        super(FormField, self).__init__(
            validators=validators,
            *args,
            **kwargs
        )

        self.form_class = _DateTimeField
        self.separator = separator
        self._obj = None
        self._errors = tuple()

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, value):
        self._errors = value

    @property
    def data(self):
        # Check there's a valid date/time to return
        d = self.form.date.data
        t = self.form.time.data
        if d is None and t is None:
            return None

        # Combine the date and time into a single datetime
        try:
            if isinstance(d, date):
                dt = datetime.combine(d, datetime.strptime(t, '%H:%M').time())
            else:
                return None

        except ValueError:
            return None

        # Set the datetime's timezone
        dt = as_tz(dt, self.tz)

        return dt

    def populate_obj(self, obj, name):
        setattr(obj, name, self.data)

    def process(self, formdata, data=unset_value):
        # Check if we should us the default
        if data is unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        # If date is a datetime convert it into a dictionary with date/time
        # key/values.
        if isinstance(data, datetime):

            # Ensure the date/time is local time
            local_dt = localize_datetime(data)

            data = {
                'date': local_dt.date(),
                'time': local_dt.strftime('%H:%M')
            }

        # Populate the date/time fields
        prefix = self.name + self.separator

        if isinstance(data, dict):
            self.form = self.form_class(
                formdata=formdata,
                prefix=prefix,
                **data
            )

        else:
            self.form = self.form_class(
                formdata=formdata,
                obj=data,
                prefix=prefix
            )

    def process_data(self, value):
        # If no value was provided set data to `None` and return
        if value is None:
            self.data = None
            return

        # If we have a value try to coerce to the required type, if we can't set
        # data as `None`
        try:
            self.data = self.coerce(value)
        except (ValueError, TypeError):
            self.data = None

    def validate(self, form, extra_validators=()):
        super(FormField, self).validate(form, extra_validators)

        # Validate individual fields
        d = self.form.date.data
        t = self.form.time.data
        if d or t:
            # If a date or time is provided make sure both are provided

            # Validate date
            if type(d) != date:
                self.date.errors = ['Valid date is missing']

            try:
                datetime.strptime(t, '%H:%M').time()
            except ValueError:
                self.time.errors = ['Valid time is missing']

        # Apply any field errors to the date field
        self.form.date.errors = list(self.form.date.errors) + list(self.errors)

        return (
            len(self.errors) == 0
            and len(self.form.date.errors) == 0
            and len(self.form.time.errors) == 0
        )


class DocumentSelectFieldBase(SelectFieldBase):

    def __new__(cls, *args, **kwargs):
        if '_form' in kwargs and '_name' in kwargs:
            field = super(Field, cls).__new__(cls)

            # Set the form attribute against the field
            field._form = kwargs['_form']

            return field
        else:
            return UnboundField(cls, *args, **kwargs)

    def __init__(self, label=None, frame_cls=None, filter=None, sort=None,
            projection=None, limit=None, id_attr='_id', label_attr=None,
            validators=None, coerce=to_object_id, **kwargs):

        assert frame_cls is not None, \
                'You must specify the `frame_cls` to be used'

        SelectFieldBase.__init__(self, label, validators, **kwargs)
        self.coerce = coerce

        # Arguments used to build the choices
        self._frame_cls = frame_cls
        self._filter = filter
        self._sort = sort
        self._projection = projection
        self._limit = limit
        self._id_attr = id_attr
        self._label_attr = label_attr

    @property
    def choices(self):
        """Build the choices for the field a selection of documents"""

        # Check if the filter is a callable object in which case call it and use
        # the result as the filter.
        filter = self._filter
        if callable(filter):
            filter = filter(self._form, self)

        # Build the filter args
        filter_args = {
            'sort': self._sort,
            'projection': self._projection,
            'limit': self._limit
            }
        filter_args = {k: v for k, v in filter_args.items() if v}

        # Select the documents
        documents = self._frame_cls.many(filter, **filter_args)

        # Build the choices
        return [
            (
                getattr(d, self._id_attr),
                getattr(d, self._label_attr) if self._label_attr else str(d)
            )
            for d in documents]


class DocumentCheckboxField(DocumentSelectFieldBase, CheckboxField):
    """
    The `DocumentCheckboxField` fields supports a list of checkboxes where the
    choices are generated by select documents from the database.
    """


class DocumentSelectField(DocumentSelectFieldBase, SelectField):
    """
    The `DocumentSelectField` fields supports a select field where the options
    are generated by select documents from the database.
    """

    def __init__(self, label=None, frame_cls=None, filter=None, sort=None,
            projection=None, limit=None, id_attr='_id', label_attr=None,
            validators=None, coerce=to_object_id, empty_label='Select...',
            **kwargs):

        super().__init__(label, frame_cls, filter, sort, projection, limit,
                id_attr, label_attr, validators, coerce, **kwargs)

        # If an empty label is specified then the field will display an empty
        # option (with the given label).
        self._empty_label = empty_label

    @property
    def choices(self):
        """Build the choices for the field a selection of documents"""
        choices = super().choices

        # If defined add an empty option to the select
        if self._empty_label is not None:
            choices.insert(0, ('', self._empty_label))

        return choices

    def process_data(self, value):
        # If no value was provided set data to `None` and return
        if value is None:
            self.data = None
            return

        # If we have a value try to coerce to the required type, if we can't set
        # data as `None`
        try:
            self.data = self.coerce(value)
        except (ValueError, TypeError):
            self.data = None

    def pre_validate(self, form):
        # Allow None as a value if an empty label is specified
        if self.data is None and self._empty_label is not None:
            return

        # Check the choice is within the defined choices for the field
        for v, _ in self.choices:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))


class HiddenField(HiddenField):
    """
    A`Hidden` field that supports for value coercion.
    """

    def __init__(self, label=None, validators=None, coerce=None, **kwargs):
        super(HiddenField, self).__init__(label, validators, **kwargs)

        # A function that will be applied to coerce the field's value
        self.coerce = coerce or (lambda x: x)

    def process_formdata(self, values):
        if not values:
            return
        try:
            self.data = self.coerce(values[0])
        except (ValueError, TypeError):
            self.data = None

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            try:
                self.data = self.coerce(self.data)
            except (ValueError, TypeError):
                self.data = None
            return self.data
        else:
            return ''


class JSONField(HiddenField):
    """
    A field that accepts JSON values (typically used in conjunction with
    typeahead/tokenizer fields, or othe JS type fields that set complex data
    structures.
    """

    def _value(self):
        return json.dumps(self.data) if self.data else ''

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except ValueError:
                raise ValueError('This field contains invalid JSON')
        else:
            self.data = None

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError('This field contains invalid JSON')


class LatLonField(FormField):
    """
    A field for setting a latitude and longitude (typically used in
    conjunction with a map JS field).
    """

    def __init__(
        self,
        label=None,
        validators=None,
        order='lonlat',
        *args,
        **kwargs
        ):

        # Store the label
        self.label = Label(None, label)

        # The order that the coordinates will be output in, defaults to
        # 'lonlat' which is the MongoDB requirement (even though the ISO
        # standard appears to be 'latlon').
        self.order = order

        # Prepare the validators for the lat/lon fields
        lat_validators = (validators or []).copy()
        lon_validators = (validators or []).copy()
        if isinstance(validators, dict):
            lat_validators = validators.get('lat', []).copy()
            lon_validators = validators.get('lon', []).copy()

        # Add range validators for lat/lon fields
        lat_validators.append(NumberRange(-90, 90))
        lon_validators.append(NumberRange(-180, 180))

        # Build the lat/lon form
        class _LatLonField(Form):
            lat = FloatField(
                'Latitude',
                validators=lat_validators,
                render_kw={'required': False}
            )
            lon = FloatField(
                'Longitude',
                validators=lon_validators,
                render_kw={'required': False}
            )

        super(LatLonField, self).__init__(_LatLonField, *args, **kwargs)

    @property
    def data(self):
        # Check there's a valid lat/lon to return
        lat = self.form.lat.data
        lon = self.form.lon.data
        if lat is None or lon is None:
            return None

        # Determine the order to return the coordinates in
        if self.order == 'latlon':
            return [lat, lon]
        return [lon, lat]

    def populate_obj(self, obj, name):
        setattr(obj, name, self.data)

    def process(self, formdata, data=unset_value):
        # Check if we should us the default
        if data is unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        # Convert data lists / tuples into a dictionary so it can be used to
        # populate the encapsulated form.
        if isinstance(data, (list, tuple)):
            if self.order == 'latlon':
                data = {'lat': data[0], 'lon': data[1]}
            else:
                data = {'lat': data[1], 'lon': data[0]}

        # Populate the lat/lon fields
        prefix = self.name + self.separator
        if isinstance(data, dict):
            self.form = self.form_class(formdata=formdata, prefix=prefix, **data)
        else:
            self.form = self.form_class(formdata=formdata, obj=data, prefix=prefix)


class PriceField(Field):
    """
    The `PriceField` accepts a price string which it converts to an integer
    representing the price in it's lowest denomination for example pound
    sterling would be convert to pence, dollars and euros to cents.

    Optionally the `denomination_units` argument can be set to change the lowest
    domination, for example setting it to `1` would mean pounds were returned as
    pounds but you'd also need to specify `coerce` as `float` to not lose pence.
    """
    widget = TextInput()

    def __init__(self, label=None, validators=None,
                denomination_units=100, coerce=None, **kwargs):
        super(PriceField, self).__init__(label, validators, **kwargs)

        if coerce is None:
            coerce = self.default_coerce

        self._denomination_units = denomination_units
        self._coerce = coerce

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            return '{:.2f}'.format(self.data / self._denomination_units)
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            value = valuelist[0]
            try:
                value = float(valuelist[0])
                self.data = self._coerce(value * self._denomination_units)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid price value'))

    @staticmethod
    def default_coerce(value):
        return int(round(value))


class SlugField(StringField):
    """
    The `SlugField` accepts a valid slug or will generate a valid slug when no
    value has been provided (for this reason slug fields are typically optional
    (in that you do not need to enter content), and required in that they will
    automically generate a value if one isn't provided.
    """

    def __init__(
            self,
            label=None,
            validators=None,
            template=None,
            allow_paths=False,
            **kwargs
            ):

        super().__init__(label, validators, **kwargs)

        # The template used to generate a slug value if none is provided, can
        # optionally be a function/callable.
        self.template = template

        # Flag indicating if paths are allowed as a value for the slug, e.g:
        # `foo/bar`
        self.allow_paths = allow_paths

        assert self.template, \
                'A `template` must be provided when initializing the slug field'

        # Retain a reference to the form if passed
        if '_form' in kwargs:
            self._form = kwargs['_form']

    def build_slug(self):
        """Return a slug value for the field based on the template value"""

        if callable(self.template):
            return slugify(self.template(self._form, self))
        else:

            # Only extract the data required for the template
            keys = {formatter_field_name_split(n)[0]
                for _, n, _, _ in Formatter().parse(self.template) if n}
            data = {
                k: getattr(getattr(self._form, k), 'data', '') for k in keys
            }

            return slugify(self.template.format(**data))

    def process_formdata(self, values):
        # If a value has been provided then check it's a valid slug...
        if values and ''.join(values).strip():
            self.data = ''.join(values).strip()

            # Check the slug is a valid one...
            paths = [self.data]
            if self.allow_paths:
                paths = [p for p in self.data.split('/')]

            valid = True
            for path in paths:
                if not path or path != slugify(path):
                    valid = False
                    break

            if not valid:
                # ...raise a value error if not
                message = """
Not a valid slug. (Use a-z, 0-1 and '-' characters only)
                    """.strip()

                if self.allow_paths:
                    message = """
Not a valid slug. (Use a-z, 0-1 and '-' or '/' characters only)
                        """.strip()

                message = self.gettext(message)

                raise ValueError(
                    ErrorMessage(message, self, suggestion=self.build_slug())
                )

        # ...if not we generate a default slug.
        elif not self.data:
            self.data = self.build_slug()


class StringListField(Field):
    """
    The `StringListField` supports a list of values being defined as a string.
    """

    widget = TextArea()

    def __init__(self, label='', validators=None, separator='\n',
            remove_blanks=True, remove_duplicates=True, case_sensitive=False,
            coerce=str, sort=False, **kwargs):

        super().__init__(label, validators, **kwargs)

        # The string that separates each value in the string
        self._separator = separator

        # Flags indicating if blank and/or duplicate values should be removed
        self._remove_blanks = remove_blanks
        self._remove_duplicates = remove_duplicates

        # If not case sensitive then duplicates will be removed regardless of
        # differences in case.
        self._case_sensitive = case_sensitive

        # Flag indicating if the values should be sorted
        self._sort = sort

        # A function user to coerce the value to the required format
        self._coerce = coerce

    def _value(self):
        if self.data:
            return self._separator.join(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [v.strip() for v in valuelist[0].split(self._separator)]

            # Remove blanks
            if self._remove_blanks:
                self.data = [v for v in self.data if v]

            # Remove duplicates
            if self._remove_duplicates:
                dataset = set({})
                data = []
                for v in self.data:

                    # Check for a duplicate based on the case sensitive flag
                    if self._case_sensitive:
                        if v in dataset:
                            continue
                        dataset.add(v)

                    else:
                        if v.lower() in dataset:
                            continue
                        dataset.add(v.lower())

                    data.append(v)

                self.data = data

            # Attempt to coerce all values
            try:
                self.data = [self._coerce(d) for d in self.data]
            except:
                self.data = None
                raise ValueError(
                        self.gettext('Not all values in the list are valid'))

            # Sort values
            if self._sort:
                self.data.sort()

        else:
            self.data = []


class TimeField(Field):
    """
    The `TimeField` accepts a time string in 24hr format (by default HH:MM) and
    if valid returns a `datetime.time` instance.
    """

    widget = TextInput()

    def __init__(self, label=None, validators=None, format='%H:%M', **kwargs):
        super().__init__(label, validators, **kwargs)
        self.format = format

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        elif self.data is not None:
            return self.data.strftime(self.format)
        return ''

    def process_formdata(self, values):
        if not values:
            return

        time_str = ' '.join(values)
        try:
            self.data = datetime.strptime(time_str, self.format).time()
        except ValueError:
            self.data = None
            raise ValueError(self.gettext('Not a valid time value.'))


class YesNoField(RadioField):
    """
    The `YesNoField` provides a radio field that requires either a yes or no
    answer and returns a value of True or False respectively.

    The typical use for yes no fields are where you require a user to actively
    answer a question as opposed to using a boolean field where leaving the
    checkbox unticked results in False being returned.

    By default the options presented are 'Yes' and 'No' but these can be
    configured by changing the `choices` argument,
    e.g `choices=[('y', 'OK'), ('n', 'Cancel')]`
    """
    def __init__(self, label=None, validators=None, coerce=None,
            choices=None, **kwargs):

        # By default we use the strings 'y' and 'n' to represent True and
        # False. If these are modified then the `coerce` method also needs to
        # be modified.
        if not choices:
            choices = [('y', 'Yes'), ('n', 'No')]

        if not coerce:
            coerce = lambda x: x if isinstance(x, bool) \
                    else {'y': True, 'n': False}.get(x, None)

        # By default we require the user to choose an option.
        if validators is None:
            validators = [InputRequired()]

        super().__init__(label, validators, choices=choices, coerce=coerce,
                **kwargs)

    def iter_choices(self):
        for value, label in self.choices:
            yield (value, label, self.coerce(value) is self.data)

    def pre_validate(self, form):
        # If the field has a value of `None` then we don't check if it's a
        # valid choice to prevent `None` being flagged as 'Not a valid choice'
        # if the field is not required.
        if self.data is None:
            return

        for v, _ in self.choices:
            if self.data is self.coerce(v):
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))
