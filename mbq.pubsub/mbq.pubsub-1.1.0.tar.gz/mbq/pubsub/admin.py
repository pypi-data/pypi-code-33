import json

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

import boto3
from botocore.exceptions import ClientError
from mbq.pubsub import models, utils


def get_name_from_topic_arn(arn):
    return arn.split(":")[-1]


class SNSTopicListFilter(admin.SimpleListFilter):
    title = "topic"
    parameter_name = "topic_arn"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request).order_by("topic_arn")
        topic_arns = qs.values_list("topic_arn", flat=True).distinct()
        for arn in topic_arns:
            yield (arn, get_name_from_topic_arn(arn))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(topic_arn=self.value())
        return queryset


def replay_messages(model_admin, request, queryset):
    sqs = boto3.client("sqs")
    queue_urls = {}

    for message in queryset:
        if message.queue not in queue_urls:
            url = sqs.get_queue_url(QueueName=utils.construct_full_queue_name(message.queue))
            queue_urls[message.queue] = url["QueueUrl"]

        try:
            sqs.send_message(QueueUrl=queue_urls[message.queue], MessageBody=message.payload)
            message.delete()
        except ClientError as e:
            model_admin.message_user(
                request, f"Message {message.id} failed to replay: {e.response}"
            )


replay_messages.short_description = "Replay messages"


class UndeliverableMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "message_timestamp", "message_type", "queue")

    list_filter = ("message_type", "queue")

    fields = ("id", "created_at", "message_timestamp", "message_type", "queue", "topic_arn")

    readonly_fields = (
        "id",
        "created_at",
        "message_timestamp",
        "message_type",
        "queue",
        "topic_arn",
    )

    def has_delete_permission(self, *args):
        return True

    def has_add_permission(self, request):
        return False

    def admin_topic(self, message):
        return get_name_from_topic_arn(message.topic_arn)

    admin_topic.short_description = "topic"

    list_display = list_display + ("admin_topic",)
    list_filter = list_filter + (SNSTopicListFilter,)

    def admin_papertrail_link(self, message):
        papertrail_link = settings.PUBSUB.get("PAPERTRAIL_URL")
        if papertrail_link:
            message_id = json.loads(message.payload)["MessageId"]
            url = f"{papertrail_link}/events?q={message_id}"
            return format_html('<a href="{url}" target="_blank">{text}</a>', url=url, text=url)
        else:
            return "To see a papertrai link, add the 'PAPERTRAIL_URL' setting to your ranch config"

    admin_papertrail_link.short_description = "papertrail"

    def admin_payload(self, message):
        try:
            payload = json.loads(message.payload)
            data = json.loads(payload["Message"])
            payload["Message"] = data
            payload_str = json.dumps(payload, indent=4)
            return format_html("<br/><pre>{}</pre>", payload_str)
        except Exception:
            return format_html("<br/><pre>{}</pre>", message.payload)

    admin_payload.short_description = "payload"

    fields = fields + ("admin_payload", "admin_papertrail_link")
    readonly_fields = readonly_fields + ("admin_payload", "admin_papertrail_link")

    actions = [replay_messages]


admin.site.register(models.UndeliverableMessage, UndeliverableMessageAdmin)
