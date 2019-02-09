from pathlib import Path
import pyquilted
from pyquilted.resume_builder import ResumeBuilder
from pyquilted.template_render import TemplateRender
from pyquilted.yaml_loader import YamlLoader


DATA_PATH = str(Path(pyquilted.__file__).resolve().parent)


class ResumeToHtml:
    def resume_to_html(self):
        self._load_yaml()
        self._build_resume()
        self._render_html()

    def _load_yaml(self):
        with open(self.resume_file) as f:
            self.resume_odict = YamlLoader.ordered_load(f)

    def _build_resume(self):
        self.resume_builder = ResumeBuilder(self.resume_odict,
                                            style=self.style,
                                            options=self.options)
        self.resume = self.resume_builder.build_resume()

    def _render_html(self):
        self.html = TemplateRender.render_mustache(
                DATA_PATH + '/templates/base.mustache', self.resume)
