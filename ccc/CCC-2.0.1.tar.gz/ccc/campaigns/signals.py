def signal_send_sms(sender, instance, created, **kwargs):
    """Send a SMS, asyncrhon..."""
    from ccc.campaigns.cloud_tasks import task_send_sms
    if created:
        if instance.countdown:
            if instance.campaign:
                task_send_sms(output_sms_id=instance.id).execute(
                    timezone=instance.campaign.user.time_zone,
                    trigger_date=instance.sms_campaign_trigger_date,
                    seconds=instance.countdown
                )
            else:
                task_send_sms(output_sms_id=instance.id).execute(seconds=instance.countdown)
        else:
            task_send_sms(output_sms_id=instance.id).execute()


def omms_post_save(sender, instance, created, **kwargs):
    from ccc.campaigns.cloud_tasks import send_mms

    if instance.status == 'created':
        if instance.countdown:
            if instance.campaign:
                user_timezone = instance.campaign.user.time_zone
                campaign_trigger_date = instance.mms_campaign_trigger_date

                # Send async MMS message
                send_mms(omms_id=instance.id).execute(
                    timezone=user_timezone,
                    trigger_date=campaign_trigger_date,
                    seconds=instance.coutdown
                )
            else:
                send_mms(omms_id=instance.id).execute(seconds=instance.coutdown)
        else:
            send_mms(omms_id=instance.id).execute()


def fu_campaign_pre_delete(sender, instance, using, **kwargs):
    if instance.recur:
        instance.unschedule_from_celery()


def campaign_followup_post_save(sender, instance, created, **kwargs):
    if instance.is_follow_up and created:
        from ccc.campaigns.models import FollowUpDetail
        FollowUpDetail.objects.create(campaign=instance)
