from pathlib import Path
import chevron
import pyquilted


DATA_PATH = str(Path(pyquilted.__file__).resolve().parent)


class TemplateRender:
    @staticmethod
    def render_mustache(template, data):
        with open(template) as f:
            html = chevron.render(
                    template=f,
                    data=data,
                    partials_path=DATA_PATH + '/templates')
        return html
