# glue code for calling the bonsai analyzer from python
import subprocess, yaml
import xir

def shortest_path(topo, x, y):
    json_filename = "/tmp/%s.json"%xir.label(topo)
    svg_filename = "/tmp/%s.svg"%xir.label(topo)
    with open(json_filename, "w") as f:
        f.write(topo.xir())
    out = subprocess.run(["bonsai", "spath", json_filename, x, y], cwd='/tmp', 
                   capture_output=True).stderr

    return yaml.load(out)

