from . import models
from . import serializers
from rest_framework import viewsets, permissions

from .permissions import is_object_excluded


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id', None)

        if id:
            self.queryset = self.queryset.filter(pk=id)

        if self.request.user.is_authenticated:
            for p in self.queryset:
                if p.permission.name != 'public' and \
                        is_object_excluded(self.request.user, p, p):
                    self.queryset = self.queryset.exclude(pk=p.pk)
        else:
            self.queryset = self.queryset.filter(permission__name='public')

        return self.queryset


class ProjectMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.ProjectMetadata.objects.all()
    serializer_class = serializers.ProjectMetadataSerializer

    def get_queryset(self):
        project = self.request.query_params.get('project', None)

        if project:
            self.queryset = self.queryset.filter(project__pk=project)
            if self.request.user.is_authenticated:
                for p in self.queryset:
                    if p.project.permission.name != 'public' and \
                            is_object_excluded(self.request.user, p.project, p.project):
                        self.queryset = self.queryset.exclude(pk=p.pk)
            else:
                self.queryset = self.queryset.filter(project__permission__name='public')
            return self.queryset

        raise permissions.exceptions.PermissionDenied


class ExperimentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.Experiment.objects.all()
    serializer_class = serializers.ExperimentSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        ids = self.request.query_params.getlist('ids', None)

        if id:
            self.queryset = self.queryset.filter(pk=id)
        elif ids:
            self.queryset = self.queryset.filter(pk__in=ids)

        if self.request.user.is_authenticated:
            for e in self.queryset:
                if e.permission.name != 'public' and \
                        is_object_excluded(self.request.user, e.project, e):
                    self.queryset = self.queryset.exclude(pk=e.pk)
        else:
            self.queryset = self.queryset.filter(permission__name='public')

        return self.queryset


class ExperimentMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.ExperimentMetadata.objects.all()
    serializer_class = serializers.ExperimentMetadataSerializer

    def get_queryset(self):
        experiment = self.request.query_params.get('experiment', None)

        if experiment:
            self.queryset = self.queryset.filter(experiment__pk=experiment)
            if self.request.user.is_authenticated:
                for e in self.queryset:
                    if e.experiment.permission.name != 'public' and \
                            is_object_excluded(self.request.user,
                                               e.experiment.project,
                                               e.experiment):
                        self.queryset = self.queryset.exclude(pk=e.pk)
            else:
                self.queryset = self.queryset.filter(experiment__permission__name='public')
            return self.queryset

        raise permissions.exceptions.PermissionDenied


class SampleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.Sample.objects.all()
    serializer_class = serializers.SampleSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        ids = self.request.query_params.getlist('ids', None)

        if id:
            self.queryset = self.queryset.filter(pk=id)
        elif ids:
            self.queryset = self.queryset.filter(pk__in=ids)

        if self.request.user.is_authenticated:
            for e in self.queryset:
                if e.permission.name != 'public' and \
                        is_object_excluded(self.request.user, e.experiment.project, e):
                    self.queryset = self.queryset.exclude(pk=e.pk)
        else:
            self.queryset = self.queryset.filter(permission__name='public')

        return self.queryset


class SampleMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.SampleMetadata.objects.all()
    serializer_class = serializers.SampleMetadataSerializer

    def get_queryset(self):
        sample = self.request.query_params.get('sample', None)

        if sample:
            self.queryset = self.queryset.filter(sample__pk=sample)
            if self.request.user.is_authenticated:
                for e in self.queryset:
                    if e.sample.permission.name != 'public' and \
                            is_object_excluded(self.request.user,
                                               e.sample.experiment.project,
                                               e.sample):
                        self.queryset = self.queryset.exclude(pk=e.pk)
            else:
                self.queryset = self.queryset.filter(sample__permission__name='public')
            return self.queryset

        raise permissions.exceptions.PermissionDenied


class ConditionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.Condition.objects.all()
    serializer_class = serializers.ConditionSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id', None)
        ids = self.request.query_params.getlist('ids', None)

        if id:
            self.queryset = self.queryset.filter(pk=id)
        elif ids:
            self.queryset = self.queryset.filter(pk__in=ids)

        if self.request.user.is_authenticated:
            for e in self.queryset:
                if e.permission.name != 'public' and \
                        is_object_excluded(self.request.user, e.experiment.project, e):
                    self.queryset = self.queryset.exclude(pk=e.pk)
        else:
            self.queryset = self.queryset.filter(permission__name='public')

        return self.queryset


class ConditionMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.ConditionMetadata.objects.all()
    serializer_class = serializers.SampleMetadataSerializer

    def get_queryset(self):
        condition = self.request.query_params.get('condition', None)

        if condition:
            self.queryset = self.queryset.filter(sample__pk=condition)
            if self.request.user.is_authenticated:
                for e in self.queryset:
                    if e.condition.permission.name != 'public' and \
                            is_object_excluded(self.request.user,
                                               e.condition.experiment.project,
                                               e.condition):
                        self.queryset = self.queryset.exclude(pk=e.pk)
            else:
                self.queryset = self.queryset.filter(condition__permission__name='public')
            return self.queryset

        raise permissions.exceptions.PermissionDenied
