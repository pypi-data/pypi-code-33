HTML_HEADER = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="defaultLanguage" content="en">
    <meta name="availableLanguages" content="en">
    <meta name="description" content="PDF Text Outline">
    <title>PDF Text Outline</title>
    <style>
      body {
        font-size: 12px;
        font-family: Arial,Helvetica,sans-serif;
        text-align: center;
        cursor: default;
      }
      #document {
        position: absolute;
        padding: 5px;
        top: 0pt;
        left: 0pt;
      }
      .page-info {
        margin: 2px 2px 12px 2px;
        background-color: #F3F3F3;
        border: 0.5px solid #AAA;
        text-align: left;
        font-family: monospace;
        box-shadow: 3px 3px #C3C3C3;
      }
      pre.page-info-text {
         margin: 5px;
         padding: 5px;
         font-family: Consolas, Menlo, Monaco, monospace;
         font-size: 12px;
      }
      pre.page-info-header {
         font-family: Consolas, Menlo, Monaco, monospace;
         font-size: 16px;
         font-weight: bold;
      }
      .page {
        position: relative;
        border: 1px solid #C3C3C3;
        margin: 0px 2px 10px 2px;
        box-shadow: 3px 3px #DDD;
      }
      .text-block {
        font-size: 8px;
        text-align: left;
        vertical-align: middle;
        position: absolute;
        border: 1px solid #F6EDED;
      }
      .text-block span.tooltip {
        display: none;
      }
      span.tooltip-text {
        background: #FBD57A;
      }
      span.tooltip pre {
        font-size: 10px;
        color: red;
      }
      .text-block:hover span.tooltip {
        display: block;
        padding: 5px;
        position: absolute;
        font-size: 10px;
        font-family: monospace;
        left: 10%;
        top: 90%;
        z-index: 800;
        box-shadow: 3px 3px rgba(192,193,194,0.5);
        border: 1px solid #E0D39B;
        background-color: #FFF2C7;
      }
      .text-block:hover {
        background-color: #E7E6E6;
        border: 0.5px solid #FEC157;
        z-index: 500;
        cursor: arrow;
      }
      .text {
        padding: 3px;
        float: inline-start;
      }
      table {
        border-collapse: collapse;
        margin: 0px 0px 8px 8px;
      }
      td {
        font-family: Consolas, Menlo, Monaco, monospace;
        font-size: 14px;
        vertical-align: middle;
        padding: 2px 3px;
        text-align: left;
      }
      td.number {
         text-align: right;
      }
      td.label {
        text-align: right;
        padding-right: 26px;
      }
      td.col1 {
        padding-left: 15px;
      }
    </style>
  </head>
  <body>
    <div id="document" class="document">

"""


HTML_FOOTER = """

    </div>
  </body>
</html>
"""


HTML_TABLE = """
<table>
  <tr>
    <td>Page Width:</td>
    <td class="number">{page_width: 7.2f}pt</td>
    <td></td>
    <td class="col1">Line Overlap:</td>
    <td class="number">{line_overlap: 7.2f}</td>
  </tr>
  <tr>
    <td>Page Height:</td>
    <td class="number">{page_height: 7.2f}pt</td>
    <td></td>
    <td class="col1">Character Margin:</td>
    <td class="number">{char_margin: 7.2f}</td>
  </tr>
  <tr>
    <td>Selected Region</td>
    <td></td>
    <td></td>
    <td class="col1">Line Margin:</td>
    <td class="number">{line_margin: 7.2f}</td>
  </tr>
  <tr>
    <td class="label">x0:</td>
    <td class="number">{region.x0: 7.2f}pt</td>
    <td></td>
    <td class="col1">Word Margin:</td>
    <td class="number">{word_margin: 7.2f}</td>
  </tr>
  <tr>
    <td class="label">y0:</td>
    <td class="number">{region.y0: 7.2f}pt</td>
    <td></td>
    <td class="col1">Box Flow:</td>
    <td class="number">{boxes_flow: 7.2f}</td>
  </tr>
  <tr>
    <td class="label">x1:</td>
    <td class="number">{region.x1: 7.2f}pt</td>
    <td></td>
    <td class="col1">Collapse Lines:</td>
    <td class="number">{collapse_lines}</td>
  </tr>
  <tr>
    <td class="label">y1:</td>
    <td class="number">{region.y1: 7.2f}pt</td>
    <td></td>
    <td class="col1"></td>
    <td class="number"></td>
  </tr>
</table>
"""


class HTMLDocument:
    def __init__(self, doc_name):
        self.doc_name = doc_name
        self.elements = []
        self.text_count = 0
        self.page_height = 0

    def start_page(
        self,
        pdf_page,
        region,
        line_overlap,
        char_margin,
        line_margin,
        word_margin,
        boxes_flow,
        collapse_lines,
    ):
        div = (
            '<div id="page-info-{page_cnt}" class="page-info" style="width:{width}pt">'
            '<pre class="page-info-text page-info-header">'
            "{doc}</br>"
            "Page: {page_cnt}"
            "</pre>"
            "{table}"
            "</div>"
            '<div id="page-{page_cnt}" class="page" '
            'style="width:{width}pt;'
            'height:{height}pt;">'
        )
        self.page_height = pdf_page.height
        table = HTML_TABLE.format(
            region=region,
            page_width=pdf_page.width,
            page_height=pdf_page.height,
            line_overlap=line_overlap,
            char_margin=char_margin,
            line_margin=line_margin,
            word_margin=word_margin,
            boxes_flow=boxes_flow,
            collapse_lines=str(collapse_lines).lower(),
        )
        self.elements.append(
            div.format(
                doc=self.doc_name,
                page_cnt=pdf_page.pageid,
                width=pdf_page.width,
                height=pdf_page.height,
                table=table,
            )
        )

    def end_page(self):
        self.elements.append("</div>")

    def add_text_block(self, txt):
        div = (
            '<div id="txt-{text_cnt}" class="text-block" '
            'style="width:{width}pt;'
            "height:{height}pt;"
            "top:{top}pt;"
            'left:{left}pt;">'
            '<span class="text">{text}</span>'
            "{title}"
            "</div>"
        )

        self.text_count += 1
        text_text = txt.get_text()

        title_text = (
            '<span class="tooltip">'
            f'<span class="tooltip-text">{text_text}</span></br>'
            "<pre>"
            f"x0: {txt.x0:7.2f}   x1: {txt.x1:7.2f}  width:  {txt.width:7.2f}</br>"
            f"y0: {txt.y0:7.2f}   y1: {txt.y1:7.2f}  height: {txt.height:7.2f}"
            "</pre>"
            "</span>"
        )

        self.elements.append(
            div.format(
                text_cnt=self.text_count,
                width=txt.width,
                height=txt.height,
                top=self.page_height - (txt.y0 + txt.height),
                left=txt.x0,
                title=title_text,
                text=text_text,
            )
        )

    def _inner_html(self):
        return "\n".join(self.elements)

    def __str__(self):
        return HTML_HEADER + self._inner_html() + HTML_FOOTER

    def save_to(self, filepath):
        with filepath.open(mode="w") as fh_:
            fh_.write(str(self))
