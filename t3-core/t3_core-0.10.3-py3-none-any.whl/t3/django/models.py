"""Basic Django Models."""
from django.db import models
from django_prometheus.models import model_inserts, model_updates, model_deletes


class PrometheusModelBase(object):
    # Force create the labels for this model in the counters. This
    # is not necessary but it avoids gaps in the aggregated data.
    def __init__(self, *args, **kwargs):
        self.model_name = self._meta.db_table
        model_inserts.labels(self.model_name)
        model_updates.labels(self.model_name)
        model_deletes.labels(self.model_name)
        super().__init__(*args, **kwargs)

    def _do_insert(self, *args, **kwargs):
        model_inserts.labels(self.model_name).inc()
        return super()._do_insert(*args, **kwargs)

    def _do_update(self, *args, **kwargs):
        model_updates.labels(self.model_name).inc()
        return super()._do_update(*args, **kwargs)

    def delete(self, *args, **kwargs):
        model_deletes.labels(self.model_name).inc()
        return super().delete(*args, **kwargs)


class T3Model(PrometheusModelBase, models.Model):
    """Basic Django Model that exports monitoring metrics for Prometheus."""

    class Meta:
        abstract = True
