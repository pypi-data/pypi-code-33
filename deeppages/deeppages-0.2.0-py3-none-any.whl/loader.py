from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader

from .models import Template


class Loader(BaseLoader):
    ''' Custom template loader that loads templates from database and is
    managed by model Page.
    '''
    def get_contents(self, origin):
        try:
            template = Template.objects.get(pk=origin.name)
        except Template.DoesNotExist:
            raise TemplateDoesNotExist(origin)
        else:
            return template.content

    def get_template_sources(self, template_name):
        """
        Return an Origin object pointing to an absolute path in each directory
        in template_dirs. For security reasons, if a path doesn't lie inside
        one of the template_dirs it is excluded from the result set.
        """
        template = Template.objects.filter(name=template_name).exists()

        if template:
            yield Origin(
                name=template.pk,
                template_name=template_name,
                loader=self
            )
