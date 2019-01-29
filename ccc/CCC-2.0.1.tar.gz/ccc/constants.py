import pytz

TIMEZONES = pytz.common_timezones[-2:] + pytz.common_timezones[:-2]
TIMEZONE_CHOICES = [(tz, tz) for tz in TIMEZONES]

DURATION_CHOICES = (
    ('4', 'Seconds'),
    ('3', 'Minutes'),
    ('1', 'Days'),
    ('2', 'Hours'),
)

DURATION_MAPPING = {
    '4': 'seconds',
    '3': 'minutes',
    '1': 'days',
    '2': 'hours',
}

LOGO_PLACE = (
    ("top-left", "Top Left"),
    ("top-right", "Top Right"),
    ("top-middle", "Top Middle"),
    ("middle-left", "Middle Left"),
    ("middle-middle", "Middle Middle"),
    ("middle-right", "Middle Right"),
    ("bottom-left", "Bottom Left"),
    ("bottom-middle", "Bottom Middle"),
    ("bottom-right", "Bottom Right"),
)

EMIAL_TYPE = (('basic', 'Basic'), ('premium', 'Premium'))

schedular_mapping = {'voice_schedular_step': 'voice_campaign_trigger_date',
                     'mms_schedular_step': 'mms_campaign_trigger_date',
                     'sms_schedular_step': 'sms_campaign_trigger_date',
                     'email_schedular_step': 'email_campaign_trigger_date'}

step_duration_date = (('voice_schedular_step', 'voice_schedular_duration', 'voice_campaign_trigger_date', 'voice_delay'),
                      ('mms_schedular_step', 'mms_schedular_duration', 'mms_campaign_trigger_date', 'mms_delay'),
                      ('sms_schedular_step', 'sms_schedular_duration', 'sms_campaign_trigger_date', 'sms_delay'),
                      ('email_schedular_step', 'email_schedular_duration', 'email_campaign_trigger_date', 'email_delay'))

initial_web_template_data = {
    "page": {
        "title": "",
        "description": "",
        "template": {
            "name": "template-base",
            "type": "basic",
            "version": "0.0.1"
        },
        "body": {
            "type": "mailup-bee-page-proprerties",
            "container": {
                "style": {
                    "background-color": "#FFFFFF"
                }
            },
            "content": {
                "style": {
                    "font-family": "Arial, 'Helvetica Neue', Helvetica, sans-serif",
                    "color": "#000000"
                },
                "computedStyle": {
                    "linkColor": "#0068A5",
                    "messageBackgroundColor": "transparent",
                    "messageWidth": "500px"
                }
            }
        },
        "rows": [
            {
                "type": "one-column-empty",
                "container": {
                    "style": {
                        "background-color": "transparent"
                    }
                },
                "content": {
                    "style": {
                        "background-color": "transparent",
                        "color": "#000000",
                        "width": "500px"
                    }
                },
                "columns": [
                    {
                        "grid-columns": 12,
                        "modules": [
                            {
                                "type": "mailup-bee-newsletter-modules-empty",
                                "descriptor": {}
                            }
                        ],
                        "style": {
                            "background-color": "transparent",
                            "padding-top": "5px",
                            "padding-right": "0px",
                            "padding-bottom": "5px",
                            "padding-left": "0px",
                            "border-top": "0px dotted transparent",
                            "border-right": "0px dotted transparent",
                            "border-bottom": "0px dotted transparent",
                            "border-left": "0px dotted transparent"
                        }
                    }
                ]
            }
        ]
    }
}
