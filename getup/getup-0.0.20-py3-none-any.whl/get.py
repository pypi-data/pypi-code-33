import attr

def manual_setup(conf):
    """
    If configuration is meant to happen from scripts &c
    conf is supposed to be dictionary to override defaults
    """
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            **attr.asdict(conf, retain_collection_types=True, recurse=True)
        )
        import django

        django.setup()
