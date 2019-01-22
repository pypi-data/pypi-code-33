import os, subprocess
from IPython.core.display import HTML
from IPython.display import SVG
from .d3_lib import *
import xir


here = os.path.dirname(os.path.realpath(__file__))

def viz(nmir, width, height):
    return HTML( 
        set_styles(['force_directed_graph'])+
        '<script src="'+here+'../lib/d3/require.js"></script>'+ 
        '<script>require.config({paths: {d3: "https://d3js.org/d3.v4.min"}});</script>'+ 
        draw_graph('structural', {'data': nmir})+ 
        '<script>require(["d3"], function(d3){ runviz(d3,'+str(width)+','+str(height)+'); });</script>'
)

def show(topo):
    json_filename = "/tmp/%s.json"%xir.label(topo)
    svg_filename = "/tmp/%s.svg"%xir.label(topo)
    with open(json_filename, "w") as f:
        f.write(topo.xir())
    subprocess.run(["vgen", "-file", json_filename], cwd='/tmp')
    return SVG(filename=svg_filename)

def dark():
    style = """
    <style>
        text {
            fill: #ddd;
        }
        circle {
            fill: #0b63fd !important;
        }
        line {
            stroke: #777 !important;
        }
    </style>
    """
    return HTML(style)
