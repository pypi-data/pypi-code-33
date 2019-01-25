from django.contrib import admin
from django import forms
from .models import ProjectRole, ProjectPermission, Project, ProjectUserRole, \
    ProjectMetadata, ExperimentType, Experiment, \
    ExperimentMetadata, Sample, SampleMetadata, Condition, ConditionMetadata


class ProjectRoleAdminForm(forms.ModelForm):
    class Meta:
        model = ProjectRole
        fields = '__all__'


class ProjectRoleAdmin(admin.ModelAdmin):
    form = ProjectRoleAdminForm
    list_display = ['name', 'created', 'last_updated']


admin.site.register(ProjectRole, ProjectRoleAdmin)


class ProjectPermissionAdminForm(forms.ModelForm):
    class Meta:
        model = ProjectPermission
        fields = '__all__'


class ProjectPermissionAdmin(admin.ModelAdmin):
    form = ProjectPermissionAdminForm
    list_display = ['name', 'created', 'last_updated']


admin.site.register(ProjectPermission, ProjectPermissionAdmin)


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ['name', 'created', 'last_updated', 'description', 'status', 'completed']


admin.site.register(Project, ProjectAdmin)


class ProjectUserRoleAdminForm(forms.ModelForm):
    class Meta:
        model = ProjectUserRole
        fields = '__all__'


class ProjectUserRoleAdmin(admin.ModelAdmin):
    form = ProjectUserRoleAdminForm
    list_display = ['project', 'user', 'role']


admin.site.register(ProjectUserRole, ProjectUserRoleAdmin)


class ProjectMetadataAdminForm(forms.ModelForm):
    class Meta:
        model = ProjectMetadata
        fields = '__all__'


class ProjectMetadataAdmin(admin.ModelAdmin):
    form = ProjectMetadataAdminForm
    list_display = ['key', 'created', 'last_updated', 'value']
    readonly_fields = ['key', 'created', 'last_updated', 'value']


admin.site.register(ProjectMetadata, ProjectMetadataAdmin)


class ExperimentTypeAdminForm(forms.ModelForm):
    class Meta:
        model = ExperimentType
        fields = '__all__'


class ExperimentTypeAdmin(admin.ModelAdmin):
    form = ExperimentTypeAdminForm
    list_display = ['name', 'created', 'last_updated']


admin.site.register(ExperimentType, ExperimentTypeAdmin)


class ExperimentAdminForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = '__all__'


class ExperimentAdmin(admin.ModelAdmin):
    form = ExperimentAdminForm
    list_display = ['name', 'created', 'last_updated', 'description']


admin.site.register(Experiment, ExperimentAdmin)


class ExperimentMetadataAdminForm(forms.ModelForm):
    class Meta:
        model = ExperimentMetadata
        fields = '__all__'


class ExperimentMetadataAdmin(admin.ModelAdmin):
    form = ExperimentMetadataAdminForm
    list_display = ['key', 'created', 'last_updated', 'value']


admin.site.register(ExperimentMetadata, ExperimentMetadataAdmin)


class SampleAdminForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = '__all__'


class SampleAdmin(admin.ModelAdmin):
    form = SampleAdminForm
    list_display = ['name', 'created', 'last_updated']


admin.site.register(Sample, SampleAdmin)


class SampleMetadataAdminForm(forms.ModelForm):
    class Meta:
        model = SampleMetadata
        fields = '__all__'


class SampleMetadataAdmin(admin.ModelAdmin):
    form = SampleMetadataAdminForm
    list_display = ['key', 'created', 'last_updated', 'value']


admin.site.register(SampleMetadata, SampleMetadataAdmin)


class ConditionAdminForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = '__all__'


class ConditionAdmin(admin.ModelAdmin):
    form = ConditionAdminForm
    list_display = ['name', 'created', 'last_updated', 'description']


admin.site.register(Condition, ConditionAdmin)


class ConditionMetadataAdminForm(forms.ModelForm):
    class Meta:
        model = ConditionMetadata
        fields = '__all__'


class ConditionMetadataAdmin(admin.ModelAdmin):
    form = ConditionMetadataAdminForm
    list_display = ['key', 'created', 'last_updated', 'value']


admin.site.register(ConditionMetadata, ConditionMetadataAdmin)
