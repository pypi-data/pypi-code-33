from django.db.models import Manager


class SubscriptionsPackageManager(Manager):
    """Returns the avalaible subscriptions Package."""

    def get_queryset(self):
        from ccc.packages.models import PackageType

        options = {'is_active': True, 'type': PackageType.SUBSCRIPTION}
        return super(SubscriptionsPackageManager, self).get_queryset().filter(**options)


class RechargesPackageManager(Manager):
    """Returns the avalaible recharges packages."""

    def get_queryset(self):
        from ccc.packages.models import PackageType

        options = {'is_active': True, 'type': PackageType.RECHARGE}
        return super(RechargesPackageManager, self).get_queryset().filter(**options)
