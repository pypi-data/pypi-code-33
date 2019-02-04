from django.apps import AppConfig


class StaffConfig(AppConfig):
    name = "staff"

    def ready(self):
        from staff import signals  # noqa
