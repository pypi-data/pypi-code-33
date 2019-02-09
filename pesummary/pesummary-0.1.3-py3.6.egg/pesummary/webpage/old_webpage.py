# Copyright (C) 2018  Charlie Hoy <charlie.hoy@ligo.org>
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import socket
import os

import pesummary
from pesummary.utils import utils
import sys
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

__HEADER__ = """<!DOCTYPE html>
<head>
  <title></title>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css'>
  <script src='https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>
  <script src='https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js'></script>
  <script src='https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js'></script>
  <stylesheet>
</head>
<body style='background-color:#F8F8F8'>
"""

def _check_line_format(line):
    """Check at the end of each line there is \n

    Parameters
    ----------
    line: str
        A string that you are checking
    """
    if line != "" and not line[-1] == "\n":
        line += "\n"
    return line

def _write_lines_to_file(html_file, lines):
    """Write multiple lines to a file

    Parameters
    ----------
    html_file: 
        open html file that you wish to add content to
    lines:
        list of lines that you would like added to the html file
    """
    checked_lines = [_check_line_format(i) for i in lines]
    html_file.writelines(checked_lines)

def make_html(web_dir, pages=None, title="Summary Pages", stylesheets=[]):
    """Make the initial html page.

    Parameters
    ----------
    web_dir: str
        path to the location where you would like the html file to be saved
    title: str, optional
        header title of html page
    pages: list
        list of pages that you would like to be created
    stylesheets: list, optional
        list of stylesheets to including in the html page. It is assumed all
        stylesheets are located in the `css` in the root of the summary pages.
        This should be provided as basenames without extension that is assumed
        to be `.css`.
    """
    for i in pages:
        if i != "home":
            i = "html/" + i
        f = open("{}/{}.html".format(web_dir, i), "w")
        header = __HEADER__.split("\n")
        header[2] = "  <title>{}</title>".format(title)
        header[-4] = ''.join([
            "  <link rel='stylesheet' href='../css/{0:s}.css'>\n".format(s)
            for s in stylesheets])
        _write_lines_to_file(f, header)
        f.close()

def open_html(web_dir, html_page):
    """Open html page ready so you can manipulate the contents

    Parameters
    ----------
    web_dir: str
        path to the location where you would like the html file to be saved
    html_page: str
        name of the html page that you would like to edit
    """
    try:
        if html_page[-5:] == ".html":
            html_page = html_page[:-5]
    except:
        pass
    if html_page == "home.html" or html_page == "home":
        f = open(web_dir+"/home.html", "a")
    else:
        f = open(web_dir+"/html/"+html_page+".html", "a")
    return page(f, web_dir)

class page():
    """Class to generate and manipulate an html page.
    """
    def __init__(self, html_file, web_dir):
        self.html_file = html_file
        self.web_dir = web_dir

    @property
    def user(self):
        """Determine the user that ran the job
        """
        try:
            user = os.environ["USER"]
        except:
            user = "albert.einstein"
        return user

    @property
    def host(self):
        """Determine the host that ran the job
        """
        return socket.getfqdn()

    @property
    def base_url(self):
        """Grab the base_url associated with the web_dir
        """
        return utils.guess_url(self.web_dir, self.host, self.user)

    def close(self):
        """Close the opened html file.
        """
        self.html_file.close()

    def add_content(self, content):
        """Add content to the html page

        Parameters
        ----------
        content: str, optional
            list of strings that you want to html page
        """
        _write_lines_to_file(self.html_file, content)

    def add_badge(self, badge_info):
        """Add a badge to your html page
        """
        BADGE="<h4><span class='badge badge-info'>" + \
              "Code Version: {}</span></h4>".format(badge_info)
        self.add_content([BADGE])

    def _header(self, title, colour, approximant):
        """Add the header content to the html file
        """
        HEADER="""
        <div class='jumbotron text-center' style='background-color: {}; margin-bottom:0'>
        <h1 id={}>{}</h1>
        """.format(colour, approximant, title)
        header = HEADER.split("\n")
        self.add_content(header)
        self.add_badge(pesummary.__version__)
        self.add_content(["</div>"])

    def make_header(self, title="Parameter Estimation Summary Pages",
                    background_colour="#eee", approximant="IMRPhenomPv2"):
        """Make header for document in bootstrap format.

        Parameters
        ----------
        title: str, optional
            header title of html page
        background_color: str, optional
            string of the haxademical colour that you would like for the
            background colour of your header
        approximant: str, optional
            the approximant that you are analysing
        """
        self._header(title, background_colour, approximant)

    def _footer(self, user, rundir):
        """Add the footer content to the html file
        """
        command= ""
        for i in sys.argv:
            command+=" {}".format(i)
        FOOTER="""<div class='jumbotron text-center' style='margin-bottom:0'>
        <p>Simulation run by {}. Run directories found at {}</p>
        <p>Command line: {}</p>
        </div>""".format(user, rundir, command)
        footer = FOOTER.split("\n")
        self.add_content(footer)

    def make_footer(self):
        """Make footer for document in bootstrap format.
        """
        self._footer(self.user, self.web_dir)

    def _setup_navbar(self):
        """Add the html to the html file needed to generate a navbar
        """
        NAVBAR="""<script src='{}/js/variables.js'></script>
        <script src='{}/js/grab.js'></script>
        <script src='{}/js/multi_dropbar.js'></script>
        <nav class='navbar navbar-expand-sm navbar-dark bg-dark'>
        <a class='navbar-brand' href='#'>Navbar</a>
        <button class='navbar-toggler' type='button' data-toggle='collapse' data-target='#collapsibleNavbar'>
        <span class='navbar-toggler-icon'></span>
        </button> """.format(self.base_url, self.base_url, self.base_url)
        navbar = NAVBAR.split("\n")
        self.add_content(navbar)

    def make_navbar(self, links=None, search=True):
        """Make a navigation bar in boostrap format.

        Parameters
        ----------
        links: list, optional
            list giving links that you want to include in your navbar.
            Sublinks and subsublinks can also be given. They should be of the form,

                links=[corner, [1d_histograms, [mass1, mass2, mchirp]]]

             here "mass1, mass2, mchirp" are all sublink of "1d_histograms" and
             "corner" has no sublinks.
        search: bool, optional
            if True, search bar will be given in navbar
        """
        self._setup_navbar()
        if links == None:
            raise Exception ("Please specify links for use with navbar")
        NAVBAR="""<div class='collapse navbar-collapse' id='collapsibleNavbar'>
        <ul class='navbar-nav'>
        """
        for i in links:
            if type(i) == list:
                NAVBAR+="""<li class='nav-item'>
                <li class='nav-item dropdown'>
                <a class='nav-link dropdown-toggle' href='#' """ + \
                "id='navbarDropdown' role='button' " + \
                "data-toggle='dropdown' aria-haspopup='true' " + \
                """aria-expanded='false'>
                {}
                </a>
                <ul class='dropdown-menu' aria-labelledby='dropdown1'>
                """.format(i[0])
                for j in i:
                    if type(j) == list:
                        if len(j) > 1:
                            if type(j[1]) == list:
                                NAVBAR+="""<li class='dropdown-item dropdown'>
                                <a class='dropdown-toggle' id='%s' """ %(j[0]) + \
                                "data-toggle='dropdown' aria-haspopup='true' " + \
                                "aria-expanded='false'>%s</a>" %(j[0])
                                NAVBAR+="""
                                <ul class='dropdown-menu' aria-labelledby='%s'>
                                """ %(j[0])
                                for k in j[1]:
                                    NAVBAR+="<li class='dropdown-item' href='#' " + \
                                            "onclick='grab_html(\"%s\")'>" %(k) + \
                                            "<a>%s</a></li>\n" %(k)
                                NAVBAR+="</ul>\n"
                                NAVBAR+="</li>\n"
                            else:
                                for k in j:
                                    NAVBAR+="<li class='dropdown-item' href='#' " + \
                                            "onclick='grab_html(\"%s\")'>" %(k) + \
                                            "<a>%s</a></li>\n" %(k)
                        else:
                            NAVBAR+="<li class='dropdown-item' href='#' " + \
                                    "onclick='grab_html(\"{}\")'>" + \
                                    "<a>{}</a></li>\n".format(j[0], j[0])
                NAVBAR+="""</ul>
                </li>
                """ 
            else:
                NAVBAR+="<li class='nav-item'>\n"
                if i == "home":
                    NAVBAR+="<a class='nav-link' href='%s/%s.html'>%s</a>\n" %(self.base_url,i,i)
                else:
                    NAVBAR+="<a class='nav-link' href='#' " + \
                            "onclick='grab_html(\"%s\")'>%s</a>\n" %(i,i)
                NAVBAR+="</li>"
        NAVBAR+="</ul>\n"
        NAVBAR+="</div>\n"
        navbar = NAVBAR.split("\n")
        self.add_content(navbar)

    def make_table_of_numbers(self, headings=None, contents=None,
                              heading_span=1, colors=None):
        """Generate a table in bootstrap format.

        Parameters
        ----------
        headings: list, optional
            list of headings
        contents: list, optional
            nd list giving the contents of the table.
        heading_span: int, optional
            width of the header cell. By default it will span a single column
        colors: list, optional
            list of colors for the table columns
        """
        TABLE="""<div class='container' style='margin-top:5em'>
        <div class='table-responsive'>
        """
        if heading_span > 1:
            TABLE+="<table class='table table-sm'>\n"
        else:
            TABLE+="<table class='table table-striped table-sm'>\n"
        TABLE+="""<thead>
        <tr>
        """
        for i in headings:
            TABLE+="<th colspan='%s'>%s</th>\n" %(heading_span, i)
        TABLE+="""</tr>
        <tbody>
        """
        for num, i in enumerate(contents):
            TABLE+="<tr>\n"
            if heading_span == 2:
                for j, col in zip(i, ["#ffffff"]+colors*(len(i)-1)):
                    TABLE+="<td style='background-color: %s'>%s</td>\n" %(col,j)
                TABLE+="</tr>\n"
            else:
                for j in i:
                    TABLE+="<td>%s</td>\n" %(j)
                TABLE+="</tr>\n"
        TABLE+="""</tbody>
        </table>
        </div>
        </div>
        """
        table = TABLE.split("\n")
        self.add_content(table)

    def make_table_of_images(self, contents=None):
        """Generate a table of images in bootstrap format.

        Parameters
        ----------
        headings: list, optional
            list of headings
        contents: list, optional
            nd list giving the contents of the table.
        """
        TABLE="""<script type='text/javascript' src='../js/modal.js'></script>
        <link rel='stylesheet' href='../css/image_styles.css'>
        <div class='container' style='margin-top:5em; margin-bottom:5em;"""
        TABLE+="background-color:#FFFFFF; box-shadow: 0 0 5px grey;'>\n"
        ind = 0
        for i in contents:
            TABLE+="<div class='row justify-content-center'>\n"
            for num, j in enumerate(i):
                TABLE+="""<div class='column'>
                <a href='#demo' data-slide-to='{}'>
                <img src='{}' alt='No image available' style='width:{}px;' """ + \
                """id='{}' onclick='modal(\"{}\")'>
                </a>
                </div>
                """.format(ind, self.base_url+"/plots/"+j.split("/")[-1],
                           1050./len(i), j.split("/")[-1][:-4], j.split("/")[-1][:-4])
                ind += 1
            TABLE+="</div>\n"
        TABLE+="</div>\n"
        table = TABLE.split("\n")
        self.add_content(table)

    def make_code_block(self, language=None, contents=None):
        """Generate a code block hightlighted using pigments.

        Parameters
        ----------
        language: str, optional
            The lanaguge of the configuration file to use for syntax
            highlighting.
        contents: str, optional
            String containing the contents of the config file.

        Returns
        -------
        style: str
            The styles used to highlight the rendered contents.
        """
        lexer = get_lexer_by_name(language)
        formatter = HtmlFormatter(style='manni')
        render = highlight(contents, lexer, formatter)
        self.add_content([render])
        styles = formatter.get_style_defs('.highlight')
        styles += ".highlight {margin: 20px; padding: 20px;}"
        return styles

    def insert_image(self, path):
        """Generate an image in bootstrap format.

        Parameters
        ----------
        path: str, optional
            path to the image that you would like inserted
        """
        IMAGE="<div class='container' style='margin-top:5em; margin-bottom:5em;" + \
              "background-color:#FFFFFF; box-shadow: 0 0 5px grey;'>\n"
        IMAGE+="<img src='{}' alt='No image available' style='align-items:center;" + \
               " width:700px;' class='max-auto d-block'".format(path)
        IMAGE+="""</p>
        <div style='clear: both;'></div>
        </div>
        """
        image = IMAGE.split("\n")
        self.add_content(image)

    def make_accordian(self, headings=None, content=None):
        """Generate an accordian in bootstrap format with images as content.

        Parameters
        ----------
        headings: list, optional
            list of headings that you want your accordian to have
        content: nd list, optional
            n dimensional list where n is the number of rows. The content
            of each list should be the path to the location of the image
        """
        ACCORDIAN="""<div class='row justify-content-center'>
        <div class='accordian' id='accordian' style='width:70%'>
        """
        for num, i in enumerate(headings):
            ACCORDIAN+="""<div class='card' style='border: 0px solid black'>
            <div class='card-header' id='{}'>
            <h5 class='mb-0'>
            <button class='btn btn-link collapsed' type='button' """ + \
            """data-toggle='collapse' data-target='#collapse{}' """ + \
            """aria-expanded='false' aria-controls='collapse{}'>
            {}\n"
            </button>
            </h5>
            </div>
            <div id='collapse{}' class='collapse' aria-labelledby='{}' data-parent='#accordian'>
            <div class='card-body'>
            <img src='{}' alt='No image available' style='width:700px;' """ + \
            """class='mx-auto d-block'>
            </div>
            </div>
            </div>
            """.format(i,i,i,i,i,i,content[num])
        ACCORDIAN+="""</div>
        </div>"""
        accordian = ACCORDIAN.split("\n")
        self.add_content(accordian)

    def make_search_bar(self, popular_options=None, code="combine"):
        """Generate a search bar to combine the corner plots
        javascript.

        Parameters
        ----------
        popular_options: list, optional
            a list of popular options for your search bar
        """
        ids = "canvas" if code == "combine" else code
        SEARCH="""<link rel='stylesheet' href='../css/side_bar.css'>
        <script type='text/javascript' src='../js/combine_corner.js'></script>
        <script type='text/javascript' src='../js/side_bar.js'></script>
        <script type='text/javascript' src='../js/multiple_posteriors.js'></script>
        <div class='w3-sidebar w3-bar-block w3-border-right sidenav' style='display:none' id='mySidebar'>
        <button onclick='side_bar_close()' class='close'>&times;</button>
        """
        corner_parameters = ["luminosity_distance", "dec", "a_2",
                             "a_1", "geocent_time", "phi_jl", "psi", "ra", "phase",
                             "mass_2", "mass_1", "phi_12", "tilt_2", "iota",
                             "tilt_1", "chi_p", "chirp_mass", "mass_ratio",
                             "symmetric_mass_ratio", "total_mass", "chi_eff"]
        for i in corner_parameters:
            SEARCH+="<input type='checkbox' name='type' value='{}' id='{}' " + \
                    "style='text-align: center; margin: 0 5px 0;'>{}<br>\n".format(i,i,i)
        SEARCH+="""</div>
        <div class='row justify-content-center'>
        <p style='margin-top:2.5em'> Input the parameter names that you would like to compare</p>
        </div>
        <div class='row justify-content-center'>
        <input type='text' placeholder='search' id='corner_search'>
        <button type='submit' onclick='{}()'>Submit</button>
        <button class='w3-button w3-teal w3-xlarge' onclick='side_bar_open()'>&times</button>
        </div>
        <div class='row justify-content-center'>
        """.format(code)
        if popular_options:
            for i in popular_options:
                SEARCH+="<button type='button' class='btn btn-info' " + \
                        "onclick='{}(\"{}\")' style='margin-left:0.25em; " + \
                        "margin-right:0.25em; margin-top: 1.0em'>{}</button>\n".format(code, i, i)
        SEARCH+="""</div>
        <div class='container' style='margin-top:5em; margin-bottom:5em; """ + \
        """background-color:#FFFFFF; box-shadow: 0 0 5px grey;'>
        <div class='row justify-content-center' id='corner_plot'>
        <canvas id='{}' width='600' height='600'></canvas>
        </div>
        </div>
        """.format(ids)

    def make_modal_carousel(self, images=None):
        """Make a pop up window that appears on top of the home page showing
        images in a carousel.

        Parameters
        ----------
        images: list
            list of image locations that you would like included in the
            carousel
        """
        MODAL="<div class='modal fade bs-example-modal-lg' tabindex='-1' " + \
              "role='dialog' aria-labelledby='myLargeModalLabel' " + \
              "aria-hidden='true' id='myModel' style='margin-top: 200px;'>\n"
        MODAL+="""<div class='modal-dialog modal-lg' style='width:90%'>
        <div class='modal-content'>
        <div id='demo' class='carousel slide' data-ride='carousel'>
        <ul class='carousel-indicators'>
        """
        for num, i in enumerate(images):
            if num == 0:
                MODAL+="<li data-target='#demo' data-slide-to-'{}' " + \
                       "class='active'></li>\n".format(num)
            MODAL+="<li data-target='#demo' data-slide-to-'{}'></li>\n".format(num)
        MODAL+="""<li data-target='#demo' data-slide-to='0' class='active'></li>
        <li data-target='#demo' data-slide-to='1'></li>
        <li data-target='#demo' data-slide-to='2'></li>
        </ul>
        <div class='carousel-inner'>
        """
        for num, i in enumerate(images):
            if num == 0:
                MODAL+="<div class='carousel-item active'>\n"
            else:
                MODAL+="<div class='carousel-item'>\n"
            MODAL+="<img src={} style='align-items:center;' class='mx-auto d-block'>\n".format(i)
            MODAL+="</div>\n"
        MODAL+="""</div>
        <a class='carousel-control-prev' href='#demo' data-slide='prev'>
        <span class='carousel-control-prev-icon'></span>
        </a>
        <a class='carousel-control-next' href='#demo' data-slide='next'>
        <span class='carousel-control-next-icon'></span>
        </a>
        </div>
        </div>
        </div>
        """
        modal = MODAL.split("\n")
        self.add_content(modal)
