from __future__ import print_function
from __future__ import absolute_import

import os
import glob
import json
import time
from collections import OrderedDict

from .sample_data import sample_nodes, sample_links

def rst(s, *repls): 
    '''Really stupid templates
       Yeah, so templates might be better. Meh.'''
    for name, value in repls:
        s = s.replace('${'+name+'}', str(value))
    return s

def _resolve_file(filename, search_dir=None):
    '''Resolve a path
       For absolute paths, do nothing, otherwise search in "search_dir"
       and then in this file's directory
       Raise an error if the file cannot be resolved'''
    package_dir = os.path.dirname(os.path.abspath(__file__))
    for d in ['', search_dir, package_dir]:
        if d is None:
            continue
        f = os.path.join(d, filename)
        if os.path.exists(f):
            return f
    raise IOError("File {} cannot be located".format(filename))

def rst_file_basic(filename, *repls):
    '''Run rst on a file'''
    with open(_resolve_file(filename)) as fid:
        s = fid.read()
    return rst(s, *repls)

def include_rst_files(filename, search_dir=None):
    '''RST's import/include system
       This uses traditional inclusion (like the c pre-processor)
       and not template inheritance (like Jinja, Mako, etc.)
       Searches out all instances of ${file=*} and
       replaces them with the contents in that file
       Runs recursively'''
    filename = _resolve_file(filename, search_dir)
    d = os.path.dirname(filename)
    with open(filename) as fid:
        s = fid.read()
    ss = s.split('${file=')
    main = ss[:1]
    for i in ss[1:]:
        fn, rest = i.split('}', 1)
        main += [include_rst_files(fn, d), rest]
    return ''.join(main)

def rst_file(filename, *repls):
    '''Run rst on a file after including any referenced files'''
    return rst(include_rst_files(filename), *repls)

def render_d3_fdg(dat,
                  title='A Force-Directed Graph',
                  scale=1,
                  force_scale=1,
                  default_size=5,
                  expand_scale=3,
                  neighbor_scale=1.5,
                  shrink_scale=1,
                  show_labels=False,
                  canvas_wh=(800, 800),
                  slider_init_x=0.4,
                  save_freq='null',
                  move_new_nodes_to_centroid=True,
                  click_function='click_function_focus_node',
                  connections_html_function='indented_list',
                  zooming_code='enable_zoom()',
                  zoom_in=0.1,
                  zoom_out=10,
                  html_filename='fdg_base.html.template',
                  custom_repls=()):
    move_new_nodes_to_centroid = 'true' if move_new_nodes_to_centroid else 'false'
    f = '/tmp/index.html'
    w, h = canvas_wh
    s = rst_file(html_filename,
                 ('title', title),
                 ('scale', scale),
                 ('force_scale', force_scale),
                 ('default_size', default_size),
                 ('expand_scale', expand_scale),
                 ('neighbor_scale', neighbor_scale),
                 ('shrink_scale', shrink_scale),
                 ('show_labels', 'true' if show_labels else 'false'),
                 ('canvasw', w),
                 ('canvash', h),
                 ('slider_init_x', slider_init_x),
                 ('save_freq', save_freq),
                 ('move_new_nodes_to_centroid', move_new_nodes_to_centroid),
                 ('click_function', click_function),
                 ('connections_html_function', connections_html_function),
                 ('zooming_code', zooming_code), # Make sure this comes first...
                 ('zoom_in', zoom_in),
                 ('zoom_out', zoom_out),
                 ('graph', json.dumps(dat)),
                 *custom_repls
                )
    with open(f, 'w') as fid:
        fid.write(s)
    
    os.system('xdg-open '+f)

def fdg(nodes, links, **kwds):
    """High-level wrapper around render_d3_fdg

    nodes is a list of 2-tuples of strings like: (id, group)
    links is a list of 2-tuples of strings like: (source, target, value)

    source and target should be id's found in nodes

    all kwds are passed to render_d3_fdg
    """
    d = OrderedDict([
        ("nodes", [OrderedDict([("id", _id), ("group", group)])
                  for _id, group in nodes]),
        ("links", [OrderedDict([("source", source), ("target", target), ("value", value)])
                  for source, target, value in links]),
    ])
    return render_d3_fdg(d, **kwds)

def do_cmd(cmd):
    print(cmd)
    return os.system(cmd)

def file_stem(filename):
    return os.path.splitext(os.path.split(filename)[-1])[0]

def string_between(s, before, after):
    return s.split(before)[1].split(after)[0]

def _generate_pngs(svg_base, dout, out_base, png_wh):
    w, h = png_wh
    for fin in glob.glob(svg_base):
        f = file_stem(fin)
        f = 'newesttree (0)' if f == 'newesttree' else f # For consistency
        i = int(string_between(f, '(', ')'))
        fout = os.path.join(dout, '{}_{:03d}.png'.format(out_base, i))
        do_cmd('inkscape -z -e "{fout}" -w {w} -h {h} "{fin}" -y=1'
               .format(fin=fin, fout=fout, w=w, h=h))

def _generate_gif(dout, out_base, animation_delay=20, display=True):
    pngs = os.path.join(dout, out_base+ '_*.png')
    gif = os.path.join(dout, 'animation.gif')
    do_cmd('convert -delay {delay} -loop 0 {pngs} {gif}'.format(delay=animation_delay,
                                                                pngs=pngs, gif=gif))
    if display:
        do_cmd('eog {}'.format(gif))

def _handle_save_freq_options(save_freq, total_steps=300):
    '''Handle multiple string options for save_freq (see docs for fdg_plus_images)
       total_steps is the number of time steps d3 seems to takes in the sim (always 300?)
       Returns:
       save_freq: JS-friendly format (integer or 'null')
       ignore_first: boolean flag that controls which svgs get processed to images'''
    ignore_first = (save_freq == 'last')
    sf_dict = {None: 'null',
               'first_last': total_steps-1,
               'last': total_steps-1,
               'first': 10000000,
               'all': 1,
               -1: total_steps-1, # ??
              }
    save_freq = sf_dict[save_freq] if save_freq in sf_dict else save_freq
    return save_freq, ignore_first

def fdg_plus_images(nodes, links,
                    save_freq='last',
                    png_wh=(1200, 1200),
                    sleep_time=10,
                    out_base='out',
                    dout='/tmp/',
                    clean_downloads=True,
                    clean_tmp=True,
                    animate=True,
                    animation_delay=20,
                    display=True,
                    **kwds
                   ):
    '''Render a D3 graph, save svg's at various points, and then use
       inkscape and ImageMagick (convert) to create pngs and then an
       animated gif
       Input kwd args:
       save_freq: Control the number of svg's saved from the simulation
                  one of: None or 'null', 'last' (default), 'first', 'first_last', 'all'
                          or any integer
       png_wh: Canvas size of output pngs, default (1200, 1200)
       sleep_time: Time to wait before starting the png conversion, default 10s
       out_base: name of the output png files default 'out'
       dout: output directory, default '/tmp/'
       clean_downloads: When True (default), clear the Downloads folder of names like newesttree*.svg
       clean_tmp: When True (default), clear the output directory of names matching the output pattern
       animate: When True (default), create an animated gif from the generated pngs
       display: When True (default), open the gif with eog
       
       All other **kwds get passed to render_d3_fdg thru fdg'''
    svg_base = os.path.expanduser('~/Downloads/newesttree*.svg')
    save_freq, ignore_first = _handle_save_freq_options(save_freq)
    if clean_downloads:
        do_cmd('rm '+ svg_base)
    if clean_tmp:
        do_cmd('rm {}_*.png'.format(os.path.join(dout, out_base)))
    if ignore_first:
        svg_base = svg_base.replace('*', ' (*)')
    fdg(nodes, links, save_freq=save_freq, **kwds)
    
    if save_freq != 'null':
        time.sleep(sleep_time)
        _generate_pngs(svg_base, dout, out_base, png_wh)
        
        if animate:
            _generate_gif(dout, out_base, animation_delay=animation_delay, display=display)

if __name__ == '__main__':
    #fdg(sample_nodes, sample_links, save_freq=60) # version that auto-DL's svgs
    #fdg_plus_images(sample_nodes, sample_links, save_freq=20) # version that auto-DL's svg's AND converts to pngs and animated gif
    #fdg_plus_images(sample_nodes, sample_links) # saves just the image of the final render
    vals = sorted({i[2] for i in sample_links})
    sample_links = [(i, j, vals.index(k) * 1. / len(vals)) for i, j, k in sample_links]
    fdg_plus_images(sample_nodes, sample_links, title='Shakespeare characters',
                    save_freq=None, html_filename='fdg_base.html.template') # disabled saving, best for testing
    
