from edc_constants.constants import YES, NO
from edc_notification import GradedEventNotification
from edc_notification import register
from edc_notification.notification import ModelNotification


@register()
class AeInitialG3EventNotification(GradedEventNotification):

    name = "g3_aeinitial"
    display_name = "a grade 3 initial event has occurred"
    grade = 3
    model = "ambition_ae.aeinitial"


@register()
class AeFollowupG3EventNotification(GradedEventNotification):

    name = "g3_aefollowup"
    display_name = "a grade 3 followup event has occurred"
    grade = 3
    model = "ambition_ae.aefollowup"


@register()
class AeInitialG4EventNotification(GradedEventNotification):

    name = "g4_aeinitial"
    display_name = "a grade 4 initial event has occurred"
    grade = 4
    model = "ambition_ae.aeinitial"


@register()
class AeFollowupG4EventNotification(GradedEventNotification):

    name = "g4_aefollowup"
    display_name = "a grade 4 followup event has occurred"
    grade = 4
    model = "ambition_ae.aefollowup"


@register()
class AeSusarNotification(ModelNotification):

    name = "ae_susar"
    display_name = "a SUSAR report is due"
    model = "ambition_ae.aeinitial"

    email_body_template = (
        "\n\nDo not reply to this email\n\n"
        "{test_body_line}"
        "A report is due for a suspected unexpected serious adverse reaction "
        "submitted for patient {instance.subject_identifier} "
        "at site {instance.site.name} which requires attention.\n\n"
        "Title: {display_name}\n\n"
        "You received this message because you are subscribed to receive these "
        "notifications in your user profile.\n\n"
        "{test_body_line}"
        "Thanks."
    )

    def notify_on_condition(self, instance=None, **kwargs):
        """Returns True if initially, or has been updated to,
        susar=YES and susar_reported=NO.
        """
        notify_on_condition = False
        history = [obj for obj in instance.history.all().order_by("-history_date")]
        if history:
            response = (history[0].susar, history[0].susar_reported)
            try:
                previous_response = (history[1].susar, history[1].susar_reported)
            except IndexError:
                notify_on_condition = response == (YES, NO)
            else:
                if response != previous_response and response == (YES, NO):
                    notify_on_condition = True
        return notify_on_condition
