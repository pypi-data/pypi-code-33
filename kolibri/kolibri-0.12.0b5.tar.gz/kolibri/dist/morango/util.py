import functools
import logging

from django.db.models import Q
from morango.utils.register_models import _profile_models
from morango.certificates import Filter

logger = logging.getLogger(__name__)


def syncable_model_count(profile, filters=None):
    # create Q objects for filtering by prefixes
    prefix_condition = None
    if filters:
        if not isinstance(filters, Filter):
            filters = Filter(filters)
        prefix_condition = functools.reduce(lambda x, y: x | y, [Q(_morango_partition__startswith=prefix) for prefix in filters])

    # count the number of syncable models for this filter
    models_count = 0
    for klass in _profile_models[profile].values():
        klass_queryset = klass.objects.all()
        if prefix_condition:
                klass_queryset = klass_queryset.filter(prefix_condition)
        models_count += klass_queryset.count()
    return models_count


# taken from https://github.com/FactoryBoy/factory_boy/blob/master/factory/django.py#L256
class mute_signals(object):
    """Temporarily disables and then restores any django signals.
    Args:
        *signals (django.dispatch.dispatcher.Signal): any django signals
    Examples:
        with mute_signals(pre_init):
            user = UserFactory.build()
            ...
        @mute_signals(pre_save, post_save)
        class UserFactory(factory.Factory):
            ...
        @mute_signals(post_save)
        def generate_users():
            UserFactory.create_batch(10)
    """

    def __init__(self, *signals):
        self.signals = signals
        self.paused = {}

    def __enter__(self):
        for signal in self.signals:
            logger.debug('mute_signals: Disabling signal handlers %r',
                         signal.receivers)

            # Note that we're using implementation details of
            # django.signals, since arguments to signal.connect()
            # are lost in signal.receivers
            self.paused[signal] = signal.receivers
            signal.receivers = []

    def __exit__(self, exc_type, exc_value, traceback):
        for signal, receivers in self.paused.items():
            logger.debug('mute_signals: Restoring signal handlers %r',
                         receivers)

            signal.receivers = receivers
            with signal.lock:
                # Django uses some caching for its signals.
                # Since we're bypassing signal.connect and signal.disconnect,
                # we have to keep messing with django's internals.
                signal.sender_receivers_cache.clear()
        self.paused = {}

    def copy(self):
        return mute_signals(*self.signals)

    def __call__(self, callable_obj):
            @functools.wraps(callable_obj)
            def wrapper(*args, **kwargs):
                # A mute_signals() object is not reentrant; use a copy every time.
                with self.copy():
                    return callable_obj(*args, **kwargs)
            return wrapper

# for klass in _profile_models[profile].values():
#     klass_queryset = klass.objects.all()
#     print(klass)
#     print(klass_queryset.count())


