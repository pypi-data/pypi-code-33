from datetime import timedelta

from django.conf import settings
from django.db import models

# Create your models here.
from django.urls import reverse


class Episode(models.Model):
    name = models.CharField(max_length=100)
    begin = models.DateField()
    end = models.DateField()

    application_path = models.CharField(
        max_length=100,
        null=True,
        help_text="Pfad in Dropbox zu Anmeldungen, z.B. /WRD 2019/Anmeldungen/Hauptsaison",
    )
    certificate_path = models.CharField(
        max_length=100,
        null=True,
        help_text="Pfad in Dropbox zu Nachweisen, z.B. /WRD 2019/Nachweise",
    )
    guard_order_path = models.CharField(
        max_length=100,
        null=True,
        help_text="Pfad in Dropbox zu Wachaufträgen, z.B. /WRD 2019/Wachaufträge/1 Vorsaison",
    )

    @property
    def days(self):
        delta = self.end - self.begin
        return delta.days

    def day_list(self):
        return [self.begin + timedelta(days=i) for i in range(0, self.days + 1)]

    def day_list_ct(self):
        applications = self.applications.all()

        return [
            (d, sum([1 if d in a.day_list() else 0 for a in applications]))
            for d in self.day_list()
        ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["begin", "name"]
        verbose_name = "Episode"
        verbose_name_plural = "Episoden"


class Application(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="applications"
    )
    episode = models.ForeignKey(
        Episode, on_delete=models.PROTECT, related_name="applications"
    )

    arrival = models.DateField("Anreise")
    departure = models.DateField("Abreise")

    APPLICATION_STATUS_LIST = [
        (0, "🌥 Interesse"),
        (1, "🌤 Angemeldet"),
        # (2, "🌤 ZWRD-K beworben"),
        (3, "☀️ Wachauftrag liegt vor"),
    ]

    application_status = models.IntegerField(choices=APPLICATION_STATUS_LIST, default=0)

    ROLES = [
        ("RS", "Rettungsschwimmer/in"),
        ("WR", "Wasserretter/in"),
        ("BF", "Bootsführer/in"),
        ("WF", "Wachführer"),
    ]

    role = models.CharField("Einsatz als", max_length=2, choices=ROLES, default="RS")

    eh_ok = models.BooleanField(
        "EH-Nachweis", help_text="Gültiger EH-Nachweis liegt vor", default=False
    )
    drsa_ok = models.BooleanField(
        "DRSA-Nachweis", help_text="Gültiger DRSA-Nachweis liegt vor", default=False
    )

    @property
    def days(self):
        delta = self.departure - self.arrival
        return delta.days

    def day_list(self):
        return [self.arrival + timedelta(days=i) for i in range(0, self.days + 1)]

    def application_attachments(self):
        return self.attachments.filter(
            attachment_type=ApplicationAttachment.ATTACHMENT_TYPE_APPLICATION
        )

    def certificate_attachments(self):
        return self.attachments.filter(
            attachment_type=ApplicationAttachment.ATTACHMENT_TYPE_CERTIFICATE
        )

    def guard_order_attachments(self):
        return self.attachments.filter(
            attachment_type=ApplicationAttachment.ATTACHMENT_TYPE_GUARD_ORDER
        )

    comment = models.TextField("Kommentar", blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} @ {self.episode}"

    def get_admin_url(self):
        return reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=(self.pk,),
        )

    def get_absolute_url(self):
        return reverse("application-detail", args=(self.pk,))

    class Meta:
        ordering = ["episode", "-application_status", "user"]
        verbose_name = "Anmeldung"
        verbose_name_plural = "Anmeldungen"


# https://dropbox-sdk-python.readthedocs.io/en/stable/
class DropboxFile(models.Model):

    # I think they are mostly 25 chars long, but who knows...
    # Dropbox API documentation contains no information on this
    file_id = models.CharField(max_length=32)

    # https://www.dropbox.com/developers/reference/content-hash
    content_hash = models.CharField(max_length=64)

    # filename in Dropbox
    name = models.CharField(max_length=250)

    path_display = models.CharField(max_length=1000)

    # https://dropbox-sdk-python.readthedocs.io/en/stable/moduledoc.html#dropbox.files.FileMetadata.server_modified
    server_modified = models.DateTimeField()

    def __str__(self):
        return self.path_display

    class Meta:
        verbose_name = "Dropbox-Datei"
        verbose_name_plural = "Dropbox-Dateien"


class ApplicationAttachment(models.Model):

    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="attachments"
    )
    dropbox_file = models.ForeignKey(
        DropboxFile, on_delete=models.CASCADE, related_name="attachments"
    )

    ATTACHMENT_TYPE_UNKNOWN = 0
    ATTACHMENT_TYPE_APPLICATION = 1
    ATTACHMENT_TYPE_CERTIFICATE = 2
    ATTACHMENT_TYPE_GUARD_ORDER = 3
    ATTACHMENT_TYPES = [
        (ATTACHMENT_TYPE_UNKNOWN, "Unbekannt"),
        (ATTACHMENT_TYPE_APPLICATION, "Anmeldung"),
        (ATTACHMENT_TYPE_CERTIFICATE, "Nachweis"),
        (ATTACHMENT_TYPE_GUARD_ORDER, "Wachauftrag"),
    ]
    attachment_type = models.IntegerField(
        choices=ATTACHMENT_TYPES, default=ATTACHMENT_TYPE_UNKNOWN
    )

    def __str__(self):
        return self.dropbox_file.path_display

    class Meta:
        verbose_name = "Anhang"
        verbose_name_plural = "Anhänge"
