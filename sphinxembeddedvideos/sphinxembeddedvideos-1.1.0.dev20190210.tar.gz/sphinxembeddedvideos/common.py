import re

from docutils.parsers.rst import directives, Directive


def get_size(d, key):
    if key not in d:
        return None
    m = re.match("(\d+)(|%|px)$", d[key])
    if not m:
        raise ValueError("invalid size %r" % d[key])
    return int(m.group(1)), m.group(2) or "px"


def css(d):
    return "; ".join(sorted("%s: %s" % kv for kv in d.items()))


def visit_embedded_node(self, node, alias, url, control_height):
    aspect = node["aspect"]
    width = node["width"]
    height = node["height"]

    if aspect is None:
        aspect = 16, 9

    div_style = {}
    if (height is None) and (width is not None) and (width[1] == "%"):
        div_style = {
            "padding-top": "%dpx" % control_height,
            "padding-bottom": "%f%%" % (width[0] * aspect[1] / aspect[0]),
            "width": "%d%s" % width,
            "position": "relative",
        }
        style = {
            "position": "absolute",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "border": "0",
        }
    else:
        if width is None:
            if height is None:
                width = 560, "px"
            else:
                width = height[0] * aspect[0] / aspect[1], "px"
        if height is None:
            height = width[0] * aspect[1] / aspect[0], "px"
        style = {
            "width": "%d%s" % width,
            "height": "%d%s" % (height[0] + control_height, height[1]),
            "border": "0",
        }
    attrs = {
        "src": url % node["id"],
        "style": css(style),
    }
    attrs["allowfullscreen"] = "true"
    div_attrs = {
        "CLASS": alias + "_wrapper",
        "style": css(div_style),
    }
    self.body.append(self.starttag(node, "div", **div_attrs))
    self.body.append(self.starttag(node, "iframe", **attrs))
    self.body.append("</iframe></div>")


class EmbeddedVideo(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "width": directives.unchanged,
        "height": directives.unchanged,
        "aspect": directives.unchanged,
    }

    def run(self):
        if "aspect" in self.options:
            aspect = self.options.get("aspect")
            m = re.match("(\d+):(\d+)", aspect)
            if m is None:
                raise ValueError("invalid aspect ratio %r" % aspect)
            aspect = tuple(int(x) for x in m.groups())
        else:
            aspect = None
        width = get_size(self.options, "width")
        height = get_size(self.options, "height")
        return [self.embeddedfunction(id=self.arguments[0], aspect=aspect,
                                      width=width, height=height)]
