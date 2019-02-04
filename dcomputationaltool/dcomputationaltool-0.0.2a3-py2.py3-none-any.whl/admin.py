from django.contrib import admin
from django import forms
from .models import ComputationalTool, ComputationalToolCWLImport
from .models import ComputationalToolInput, ComputationalToolInputType
from .models import ComputationalWF, ComputationalWFCWLImport
from .models import ComputationalWFStep, ComputationalWFStepInput


class ComputationalToolAdminForm(forms.ModelForm):
    class Meta:
        model = ComputationalTool
        fields = '__all__'


class ComputationalToolAdmin(admin.ModelAdmin):
    form = ComputationalToolAdminForm
    list_display = ['name', 'created', 'last_updated',
                    'description', 'cwl']


admin.site.register(ComputationalTool, ComputationalToolAdmin)


class ComputationalToolCWLImportAdminForm(forms.ModelForm):
    class Meta:
        model = ComputationalToolCWLImport
        fields = '__all__'


class ComputationalToolCWLImportAdmin(admin.ModelAdmin):
    form = ComputationalToolCWLImportAdminForm
    list_display = ['computationaltool', 'name', 'version', 'created', 'last_updated', 'cwl']


admin.site.register(ComputationalToolCWLImport, ComputationalToolCWLImportAdmin)


class ComputationalToolInputAdminForm(forms.ModelForm):
    class Meta:
        model = ComputationalToolInput
        fields = '__all__'


class ComputationalToolInputAdmin(admin.ModelAdmin):
    form = ComputationalToolInputAdminForm
    list_display = ['computationaltool', 'name', 'computationaltoolinputtype',
                    'created', 'last_updated', 'option',
                    'value', 'array', 'optional', 'doc']


admin.site.register(ComputationalToolInput, ComputationalToolInputAdmin)


class ComputationalToolInputTypeAdminForm(forms.ModelForm):
    class Meta:
        model = ComputationalToolInputType
        fields = '__all__'


class ComputationalToolInputTypeAdmin(admin.ModelAdmin):
    form = ComputationalToolInputTypeAdminForm
    list_display = ['type', 'created', 'last_updated']


admin.site.register(ComputationalToolInputType, ComputationalToolInputTypeAdmin)


class ComputationalWFAdminForm(forms.ModelForm):
    class Meta:
        model = ComputationalWF
        fields = '__all__'


class ComputationalWFAdmin(admin.ModelAdmin):
    form = ComputationalWFAdminForm
    list_display = ['name', 'created', 'last_updated', 'description', 'cwl']


admin.site.register(ComputationalWF, ComputationalWFAdmin)


class ComputationalWFCWLImportAdminForm(forms.ModelForm):
    class Meta:
        model = ComputationalWFCWLImport
        fields = '__all__'


class ComputationalWFCWLImportAdmin(admin.ModelAdmin):
    form = ComputationalWFCWLImportAdminForm
    list_display = ['name', 'created', 'last_updated', 'cwl']


admin.site.register(ComputationalWFCWLImport, ComputationalWFCWLImportAdmin)


class ComputationalWFStepAdminForm(forms.ModelForm):
    class Meta:
        model = ComputationalWFStep
        fields = '__all__'


class ComputationalWFStepAdmin(admin.ModelAdmin):
    form = ComputationalWFStepAdminForm
    list_display = ['computationalwf', 'computationaltool',
                    'computationalwfstep', 'name', 'created',
                    'last_updated', 'order', 'description']


admin.site.register(ComputationalWFStep, ComputationalWFStepAdmin)


class ComputationalWFStepInputAdminForm(forms.ModelForm):
    class Meta:
        model = ComputationalWFStepInput
        fields = '__all__'


class ComputationalWFStepInputAdmin(admin.ModelAdmin):
    form = ComputationalWFStepInputAdminForm
    list_display = ['computationalwfstep', 'computationaltoolinput', 'created',
                    'last_updated', 'value']


admin.site.register(ComputationalWFStepInput, ComputationalWFStepInputAdmin)
