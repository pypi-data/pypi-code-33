"""
Here all (and only) the signals related with the User module and User Models.
"""
from ccc.users.cloud_tasks import task_send_activation_email, task_send_email_reset_password


def signal_create_user_profile(sender, instance, created, **kwargs):
    """This created extra required data when a new user account is created, first time."""
    if created:
        instance.create_activation_code()


def signal_send_activation_code_email(sender, instance, created, **kwargs):
    """Sending activation instructions to the new customer."""
    if created:
        task_send_activation_email(activation_id=instance.id).execute()


def signal_for_reset_password(sender, instance, created, **kwargs):
    """ResetCode Model. Send the reset email instructions to the user."""
    if created:
        task_send_email_reset_password(reset_code_id=instance.id).execute()
