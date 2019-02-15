import jinja2
from pathlib import Path


class FGSummary(object):
    def __init__(self, output, params):
        if output.type != "summary":
            raise TypeError(f'Expected a summary file but got "{output.type}"')
        self.output = output.path
        self.params = params
        self.footnote = self.summary_footnote()
        self.template = None

    def summary_footnote(self):
        footnote = "\n### Parameters\n"
        for name, param in self.params.parameter.items():
            if param.type == str:
                value = f'"{param.value}"'
            else:
                value = param.value
            footnote += f"* __{name}__ = `{value}`  _({param.description})_\n"
        return footnote

    def render_template(self, temp_file, **kwargs):
        summary = temp_file.read_text() + self.footnote
        temp = jinja2.Template(summary, undefined=jinja2.StrictUndefined)
        return temp.render(kwargs)

    def write(self, **kwargs):
        if self.template is None:
            raise AttributeError(
                "Please specify the template before calling `write` by setting the `template` parameter."
            )

        template = Path(self.template)
        if not template.exists():
            raise FileNotFoundError(
                f'Could not find the summary template under "{template}".  You can change the template location by modifying the `template` argument.'
            )
        summary = self.render_template(template, **kwargs)
        self.output.write_text(summary)
