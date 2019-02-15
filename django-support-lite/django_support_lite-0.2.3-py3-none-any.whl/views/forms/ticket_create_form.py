import datetime
import json

import pytz
from django import forms

from django_support_lite.forms.fields.multiple_file_field import MultipleFileField
from django_support_lite.forms.inputs.multiple_file_input import MultipleFileInput
from django_support_lite.forms.validators.file_content_validator import FileContentValidator


class TicketCreateForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput({
            "class": "form-control",
        }),
        label="Title",
        help_text="Ticket subject.",
        max_length=300
    )

    text = forms.CharField(
        widget=forms.Textarea({
            "class": "form-control",
            "rows": 5,
        }),
        label="Text",
        help_text="Ticket message.",
        max_length=100000
    )

    images = MultipleFileField(
        widget=MultipleFileInput({
            "class": "form-control",
        }),
        validators=[
            FileContentValidator(content_restrictions=[
                {
                    "extensions": [
                        "jpg",
                        "jpeg",
                        "gif",
                        "png",
                    ],
                    "content_types": [
                        "image/jpeg",
                        "image/jpeg",
                        "image/pjpeg",
                        "image/png",
                        "image/gif",
                    ],
                },
            ]),
        ],
        label="Images",
        help_text="Up to 5 images. Format jpg, png, gif.",
        max_count=5,
        required=False
    )
