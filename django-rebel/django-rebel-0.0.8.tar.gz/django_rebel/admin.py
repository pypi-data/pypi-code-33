from django.conf import settings
from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.utils.html import format_html

from django_rebel.paginator import LargeListPaginator
from .models import Mail, MailContent, Event, MailLabel


class LargeListAdminMixin:
    max_num_pages = 100
    paginator = LargeListPaginator
    show_full_result_count = False

    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return self.paginator(self.max_num_pages, queryset, per_page, orphans, allow_empty_first_page)


class EventInlineAdmin(admin.StackedInline):
    model = Event
    can_delete = False
    extra = 0
    readonly_fields = ("name", "created_at", "extra_data")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MailContentInline(admin.StackedInline):
    model = MailContent
    readonly_fields = ("subject", "body_text", "html_content")
    exclude = ("body_plain", "body_html")

    def html_content(self, obj: MailContent):
        if obj:
            return format_html("<a href='{url}' target='_blank'>Show Mail Content</a>", url=obj.get_content_url())

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MailLabelFilter(admin.SimpleListFilter):
    title = "Label"
    parameter_name = "label_slug"

    def lookups(self, request, model_admin):
        labels = MailLabel.objects.all()

        return (
            (label.slug, label.name) for label in labels
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                label__slug=self.value()
            )

        return queryset.all()


class BaseMailEventFilter(admin.SimpleListFilter):
    event_name: str = None
    event_query_param = None

    def __init__(self, *args, **kwargs):
        self.parameter_name = self.event_name
        self.title = self.event_name.title()

        super(BaseMailEventFilter, self).__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        return (
            ("yes", self.event_name.title()),
            ("no", "Not %s" % self.event_name.title()),
        )

    def queryset(self, request, queryset):
        if self.value() in ["yes", "no"]:
            value = True if self.value() == "yes" else False

            return queryset.filter(
                **{self.event_query_param: value}
            )

        return queryset.all()


class HasDeliveredEventFilter(BaseMailEventFilter):
    event_name = "delivered"
    event_query_param = "has_delivered"


class HasOpenedEventFilter(BaseMailEventFilter):
    event_name = "opened"
    event_query_param = "has_opened"


class HasClickedEventFilter(BaseMailEventFilter):
    event_name = "clicked"
    event_query_param = "has_clicked"


class ProfileFilter(admin.SimpleListFilter):
    title = "Profile"
    parameter_name = "profile"

    def lookups(self, request, model_admin):
        profiles = settings.REBEL["EMAIL_PROFILES"].keys()

        return (
            (profile, profile.title()) for profile in profiles
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                profile=self.value()
            )

        return queryset.all()


class MailAdmin(LargeListAdminMixin, admin.ModelAdmin):
    list_display = ("id", "label", "owner_link", "email_to", "created_at", "tags", "profile",
                    "has_delivered", "has_opened", "has_clicked")
    search_fields = ("email_from__exact", "email_to__exact",)
    inlines = [EventInlineAdmin, MailContentInline]
    readonly_fields = ("message_id", "email_from", "email_to", "profile", "label", "tags",
                       "created_at", "has_delivered", "has_opened", "has_clicked", "storage_url")
    exclude = ("owner_id", "owner_type")
    list_select_related = ("content", "label",)
    list_filter = [ProfileFilter, MailLabelFilter, HasDeliveredEventFilter, HasOpenedEventFilter, HasClickedEventFilter]

    def owner_display(self, obj: Mail):
        return obj.owner_object.__str__()

    def subject(self, obj: Mail):
        if hasattr(obj, "content"):
            return obj.content.subject

        return "-"

    def has_delivered(self, obj: Mail):
        return _boolean_icon(obj.has_delivered)

    has_delivered.admin_order_field = "has_delivered"

    def has_opened(self, obj: Mail):
        return _boolean_icon(obj.has_opened)

    has_opened.admin_order_field = "has_opened"

    def has_clicked(self, obj: Mail):
        return _boolean_icon(obj.has_clicked)

    has_clicked.admin_order_field = "has_clicked"

    def owner_link(self, obj: Mail):
        if obj.owner_object:
            url = obj.owner_object.get_admin_view_link()

            return format_html("<a href='{url}'>{owner_type}: {content}</a>",
                               url=url,
                               owner_type=obj.owner_type.name.title(),
                               content=str(obj.owner_object.__str__()))

    def get_queryset(self, request):
        qs = super(MailAdmin, self).get_queryset(request)

        return qs.with_event_status().prefetch_related("owner_object")

    def get_search_fields(self, request):
        fields = super().get_search_fields(request)

        fields = list(fields) + settings.REBEL["SEARCH_FIELDS"]

        return fields


class MailLabelAdmin(admin.ModelAdmin):
    search_fields = ("slug", "name")
    list_display = ("name", "slug")


admin.site.register(Mail, MailAdmin)
admin.site.register(MailLabel, MailLabelAdmin)
