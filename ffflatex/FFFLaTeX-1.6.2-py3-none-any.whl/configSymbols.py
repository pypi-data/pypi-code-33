#  -*- coding: utf-8 -*-
from typing import Union

from bs4 import NavigableString, Tag

from FFFLaTeX.parserutil import generate_latex_from_element, sanitize_string


def generate_latex_from_children(element: Union[Tag, NavigableString],
                                 payload: dict):
    if isinstance(element, Tag):
        for c in element.children:
            payload["TeX"] += generate_latex_from_element(c, payload)
    else:
        payload["TeX"] += generate_latex_from_element(element, payload)
    return payload


def discover_dimensions(element: Union[Tag, NavigableString], payload: dict):
    count_rows, count_cells = 0, 0
    for c in element.descendants:
        if c.name in ["tr", "th"]:
            count_rows += 1
        if c.name in ["td"]:
            count_cells += 1
    payload["tableSize"] = count_cells // count_rows
    return payload


def table_size_str(element: Union[Tag, NavigableString], payload: dict):
    payload = discover_dimensions(element, payload)
    payload["TeX"] = (payload["tableSize"] - 1) * "c|" + "c"
    return payload


def table_flag_set(element: Union[Tag, NavigableString], payload: dict):
    payload["inTable"] = True
    payload["first_row"] = True
    return payload


def table_flag_clear(element: Union[Tag, NavigableString], payload: dict):
    del payload["inTable"]
    return payload


def generate_table_cell_latex(element: Union[Tag, NavigableString],
                              payload: dict):
    i = 0
    for c in element.children:
        if c.name == "td":
            if payload["first_row"]:
                payload["TeX"] += "\\bfseries "
            payload["TeX"] += generate_latex_from_element(c, payload)
            i += 1
            if (i < payload["tableSize"]):
                payload["TeX"] += '&'

    payload["TeX"] += "\\\\\\hline\n"
    payload["first_row"] = False
    return payload


def stripped_text(element: Union[Tag, NavigableString], payload: dict):
    payload["TeX"] += sanitize_string(element)
    for c in element.children:
        payload["TeX"] += generate_latex_from_element(c, payload)
    return payload


def sanitize_text(element: Union[Tag, NavigableString], payload: dict):
    payload["TeX"] = sanitize_string(element)
    return payload


def add_video(element: Union[Tag, NavigableString], payload: dict):
    if (payload["__img_ext"][element.attrs["src"]] == ".webm"):
        return payload

    payload["TeX"] += """
\\begin{figure}[H]\n
    \\centering
    \\includemedia[
        width=0.88\\linewidth,
        height=0.5\\linewidth, 
        attachfiles, 
        transparent,
        activate=pagevisible,
        noplaybutton, 
        passcontext,
        flashvars={
            source="""

    payload["TeX"] += payload["__img_names"][element.attrs["src"]]
    payload["TeX"] += payload["__img_ext"][element.attrs["src"]]
    payload["TeX"] += """
            &autoPlay=true 
            &loop=true 
            &scaleMode=letterbox }, 
        addresource="""
    payload["TeX"] += payload["__img_names"][element.attrs["src"]]
    payload["TeX"] += payload["__img_ext"][element.attrs["src"]]
    payload["TeX"] += """]
    {{\\color{gray} Loading Video }}
    {VPlayer9.swf}\n
\\end{figure}\n"""
    return payload


def add_image(element: Union[Tag, NavigableString], payload: dict):
    if payload["__img_ext"][element.attrs["src"]] == ".gif":
        return add_video(element, payload)

    figure = "inTable" not in payload.keys()
    if figure:
        payload["TeX"] += "\\begin{figure}[H]\n\\centering"
    payload["TeX"] += "\\" + payload["__img_names"][element.attrs["src"]]
    if figure:
        payload["TeX"] += "\\end{figure}\n"
    return payload


def add_link(element: Union[Tag, NavigableString], payload: dict):
    payload["TeX"] += "\\href{" + element.attrs[
        "href"] + "}{" + sanitize_string(element) + "}"
    return payload


def fff_url(element: Union[Tag, NavigableString], payload: dict):
    payload["TeX"] += payload["__url"]
    return payload


def fff_num(element: Union[Tag, NavigableString], payload: dict):
    payload["TeX"] += str(payload["__num"])
    return payload


def fff_title(element: Union[Tag, NavigableString], payload: dict):
    payload["TeX"] += str(payload["__title"])
    return payload


def fff_date(element: Union[Tag, NavigableString], payload: dict):
    payload["TeX"] += str(payload["__date"])
    return payload


def fff_authors(element: Union[Tag, NavigableString], payload: dict):
    payload["TeX"] += str(payload["__authors"])
    return payload


symbols = {
    "@table_size_str":               table_size_str,
    "@generate_latex_from_children": generate_latex_from_children,
    "@generate_table_cell_latex":    generate_table_cell_latex,
    "@table_flag_set":               table_flag_set,
    "@table_flag_clear":             table_flag_clear,
    "@stripped_text":                stripped_text,
    "@sanitize_text":                sanitize_text,
    "@add_video":                    add_video,
    "@add_image":                    add_image,
    "@add_link":                     add_link,
    "@fff_url":                      fff_url,
    "@fff_num":                      fff_num,
    "@fff_title":                    fff_title,
    "@fff_date":                     fff_date,
    "@fff_authors":                  fff_authors
}