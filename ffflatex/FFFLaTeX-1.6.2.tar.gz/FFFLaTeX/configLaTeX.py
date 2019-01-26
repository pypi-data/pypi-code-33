#  -*- coding: utf-8 -*-

tagTex = {
    "documentHeader": """
\\documentclass{article}

\\usepackage[utf8]{inputenc}
\\usepackage{graphicx}
\\usepackage{media9}
\\usepackage[OT1]{fontenc}
\\usepackage{tabularx}
\\usepackage{float}
\\usepackage{pgfplotstable}
\\usepackage[hidelinks]{hyperref}
\\usepackage[french]{babel}
\\usepackage{colortbl}

%color theme
\\usepackage{wallpaper}
\\usepackage{xcolor}

\\definecolor{factoText}{HTML}{C8C8C8}
\\definecolor{factoLink}{HTML}{FF7200}

%font theme

\\usepackage[scaled]{helvet}
\\renewcommand\\familydefault{\\sfdefault} 
\\usepackage[T1]{fontenc}

%page theme
\\usepackage{fancyhdr}

\\write18{wget -N https://factorio.com/static/img/factorio-logo.png -P 
../out/pics/ -O 
logo.png }
\\write18{wget -N https://factorio.com/static/img/stressed_linen_texture.png 
-P ../out/pics/ -O 
background.png }

""",
    "documentTitle":  """
\\title{\\includegraphics[width=0.8\\textwidth]{logo.png} \\\\
\\Large \\bfseries \\href{ @fff_url }{\\color{factoLink} @fff_title }}
\\author{ @fff_authors }
\\date{ @fff_date }
""",
    "documentBegin":  """
\\begin{document}
    \\pagestyle{empty}
    \\color{factoText}
	\\TileWallPaper{\paperheight}{\paperwidth}{background.png}
    
    \\maketitle
    \\pagestyle{empty}
""",
    "documentEnd":    """
\\end{document}
""",
    "ul":             """
\\begin{itemize} 
    @generate_latex_from_children 
\\end{itemize}
""",
    "table":          """
\\begin{figure}[H]
    \\resizebox{\\textwidth}{!}{
    \\arrayrulecolor{factoText}
    @table_flag_set
    \\begin{tabular}{ @table_size_str }
        
        @generate_latex_from_children 
        
    \\end{tabular}}
    @table_flag_clear
\\end{figure}
""",
    "tbody":          """
@generate_latex_from_children
""",
    "tr":             """
@generate_table_cell_latex
""",
    "td":             """
\color{factoText} @generate_latex_from_children 
""",
    "li":             """
\\item @sanitize_text
""",
    "p":              """
\\paragraph{}
@generate_latex_from_children
""",

    "h2":             """
\\section*{ @sanitize_text }
""",
    "h3":             """
\\subsection*{ @sanitize_text }
""",
    "h4":             """
\\subsubsection*{ @sanitize_text }
""",
    "video":          """
@generate_latex_from_children
""",
    "source":         """
@add_video
""",
    "img":            """
@add_image
""",
    "a":              """
{\\color{factoLink} @add_link }
""",
    "i":              """
\\textit{ @sanitize_text }
""",
    "em":             """
\\textbf{ @sanitize_text }
""",
    "div":            """
@generate_latex_from_children
"""
}
