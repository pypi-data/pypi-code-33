import matplotlib.pyplot as plt
from matplotlib import patches
import pickle
import os
import numpy  as np
from svg_to_axes import FigureLayout
import imp
from optparse import OptionParser

def clear_fifidata(fifidatafile, figure, axis):
    '''
    Clear out all matplotlib calls from the figure, axis
    '''

    fifidata_file = open(fifidatafile, 'r')
    fifidata = pickle.load(fifidata_file)
    fifidata_file.close()

    try:
        fifidata[figure][axis] = []
    except:
        return

    fifidata_file = open(fifidatafile, 'w')
    pickle.dump(fifidata, fifidata_file)
    fifidata_file.close()

def __save_fifidata__(package, function, 
                      layout, figure, axis, 
                      fifidatafile, title, description, 
                      *args, **kwargs):
    
    # load
    if os.path.exists(fifidatafile):
        fifidata_file = open(fifidatafile, 'r')
        fifidata = pickle.load(fifidata_file)
        fifidata_file.close()
    else:
        fifidata = {}
    if figure not in fifidata.keys():
        fifidata[figure] = {}
    if axis not in fifidata[figure].keys():
        fifidata[figure][axis] = [] # want to preserve order that things are called in

    # new figure action (e.g. mpl call)
    new_figure_action = {'package': package,
                         'function': function,
                         'title': title,
                         'description': description,
                         'args': args,
                         'kwargs': kwargs}

    # delete duplicate entries
    idx = []
    if 1:
        for i, action in enumerate(fifidata[figure][axis]):
            if action['title'] == title:
                idx.append(i)
        if len(idx) > 0:
            for i in sorted(idx, reverse=True):
                del fifidata[figure][axis][i]

    if len(idx) > 0:
        fifidata[figure][axis].insert(np.min(idx), new_figure_action)
    else:
        fifidata[figure][axis].append(new_figure_action)

    # save
    fifidata_file = open(fifidatafile, 'w')
    pickle.dump(fifidata, fifidata_file)
    fifidata_file.close()

def load_custom_function(package_name, function_name):
    try:
        f, filename, description = imp.find_module(package_name)
    except:
        if '.' in package_name:
            raise ValueError('Use the basename for the module, and include all submodules in the function name. e.g. package_name: figurefirst, function_name: mpl_function.adjust_spines')
        else:
            raise ValueError('Could not find package: ' + package_name + ', maybe you need to install it?')
    package = imp.load_module(package_name, f, filename, description)
    
    nest = function_name.split('.')
    function = package
    for attr in nest:
        function = getattr(function, attr)

    return function

def custom(package, function,
           layout, figure, axis, 
           fifidatafile, title, description, 
           *args, **kwargs):
    '''
    Function must be of the form: def foo(ax, *args, **kwargs)
    '''
    __custom_plot__(package, function, layout, figure, axis, *args, **kwargs)
    __save_fifidata__(package, function, 
                      layout, figure, axis, 
                      fifidatafile, title, description, 
                      *args, **kwargs)
def __custom_plot__(package, function, layout, figure, axis, *args, **kwargs):
    ax = layout.axes[figure, axis]
    f = load_custom_function(package, function)
    f(ax, *args, **kwargs)

def mpl(function,              
        layout, figure, axis, 
        fifidatafile, title, description, 
        *args, **kwargs):
    '''
    function - string name for a matplotlib function
    layout - figurefirst layout object
    figure - figurefirst name for figure in layout
    axis - figurefirst name for axis in figure in layout
    
    fifidatafile - fifidata filename, which points to a pickled dict object, with the following format:
                   fifidata[figure][axis][figure_action_1, figure_action_2, ...]
                                          where figure_action is a dict object, with the following format:
                                          figure_action = {'title': title string,
                                                           'description': dict with description for each arg,
                                                           'args': args,
                                                           'kwargs': kwargs}      
    title - string name for the figure action (eg '95 percent confidence interval')
    description - list of names for each of the args 
    cleardata - if True, will search for an entry in layout[figure][axis] with the same exact title and replace it                                                              
    args - the args passed to the matplotlib function
    kwargs - the kwargs passed to the matplotlib function
    '''
    __mpl_plot__(function, layout, figure, axis, *args, **kwargs)
    __save_fifidata__('mpl', function, 
                      layout, figure, axis, 
                      fifidatafile, title, description, 
                      *args, **kwargs)
def __mpl_plot__(function, layout, figure, axis, *args, **kwargs):
    ax = layout.axes[figure, axis]
    f = getattr(ax, function)
    f(*args, **kwargs)

def mpl_patch(patchname, layout, figure, axis, fifidatafile, title, description, *args, **kwargs):
    '''
    Patchname - something like "Rectangle" (e.g. matplotlib.patches.Rectangle)
    '''
    __mpl_patch_plot__(patchname, layout, figure, axis, *args, **kwargs)
    __save_fifidata__('mpl.patches', patchname, 
                      layout, figure, axis, 
                      fifidatafile, title, description, 
                      *args, **kwargs)
def __mpl_patch_plot__(patchname, layout, figure, axis, *args, **kwargs):
    patch = getattr(patches, patchname)(*args, **kwargs)
    ax = layout.axes[figure, axis]
    ax.add_artist(patch)

def __replot_figure__(layout, figure, fifidatafile):
    layout.clear_fflayer(figure)

    fifidata_file = open(fifidatafile, 'r')
    fifidata = pickle.load(fifidata_file)
    fifidata_file.close()

    if figure not in fifidata.keys():
        return 0

    print()
    print('===================================================')
    print(figure)
    print('===================================================')
    for axis, actions in fifidata[figure].items():
        print(axis)
        print('-------------------------')
        for action in actions:
            package = action['package']
            function = action['function']
            args = action['args']
            args_size = []
            args_type = []
            for arg in args:
                try:
                    L = len(arg)
                    args_size.append(L)
                    args_type.append(str(type(arg)))
                except:
                    pass
            if len(args_size) > 0:
                string = ''
                for i, s in enumerate(args_size):
                    try:
                        d = action['description'][i]
                        if len(d) > 20:
                            d = d[0:20]+'...'
                        string += d + ': ' + str(s) + '(' + args_type[i] + ')' + ', '
                    except:
                        pass # missing description
                if len(string) > 0:
                    t = action['title']
                    if len(t) > 15:
                        t = t[0:15]+'...'
                    print(t + ': ' + package+'.'+function + ' ===> ' + 'Size of args: ' + string)
            kwargs = action['kwargs']
            if package == 'mpl':
                __mpl_plot__(function, layout, figure, axis, *args, **kwargs)
            elif package == 'mpl.patches':
                __mpl_patch_plot__(function, layout, figure, axis, *args, **kwargs)
            else:
                __custom_plot__(package, function, layout, figure, axis, *args, **kwargs)

    return 1

def replot(layoutsvgfile, outputfile, fifidatafile):
    layout = FigureLayout(layoutsvgfile)
    layout.make_mplfigures()

    for figure in layout.figures.keys():
        fig = __replot_figure__(layout, figure, fifidatafile)
        if fig:
            layout.append_figure_to_layer(layout.figures[figure], figure, cleartarget=True)
    
    layout.write_svg(outputfile)

def compress(fifidatafile, max_length=500):
    '''
    Attempt to downsize (via interpolation) large arguments. Very experimental. 
    Searches for arguments that are:
        1. A np.ndarray of length > max_length
        2. A list of np.ndarrays where each element of the list is identical in length, and that length > max_length
    '''
    fifidata_file = open(fifidatafile, 'r')
    fifidata = pickle.load(fifidata_file)
    fifidata_file.close()

    for figure in fifidata.keys():
        for axis in fifidata[figure].keys():
            for action in fifidata[figure][axis]:
                args = action['args']
                new_args = []
                for i, arg in enumerate(args):
                    new_arg = arg
                    if type(arg) == np.ndarray:
                        if len(arg) > max_length:
                            xp = np.linspace(0, 1, len(arg))
                            x = np.linspace(0, 1, max_length)
                            new_arg = np.interp(x, xp, arg)
                    elif type(arg) == list and len(arg) > 0:
                        print action
                        print
                        if type(arg[0]) == np.ndarray:
                            lengths = [len(a) for a in arg]
                            if len(np.unique(lengths)) == 1: # all same length
                                if lengths[0] > max_length: # too long
                                    new_arg = []
                                    for a in arg:
                                        xp = np.linspace(0, 1, len(a))
                                        x = np.linspace(0, 1, max_length)
                                        n = np.interp(x, xp, a)
                                        new_arg.append(n)

                    new_args.append(new_arg)
                action['args'] = new_args

    compressed_fifidatafile = fifidatafile.split('.pickle')[0] + '_compressed.pickle'
    fifidata_file = open(compressed_fifidatafile, 'w')
    pickle.dump(fifidata, fifidata_file)
    fifidata_file.close()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--layout", type="str", dest="layout", default='',
                        help="path to layout svg")
    parser.add_option("--output", type="str", dest="output", default='',
                        help="path to output svg")
    parser.add_option("--data", type="str", dest="data", default='',
                        help="path to fifi data file (a pickle file)")
    (options, args) = parser.parse_args()  
    
    replot(options.layout, options.output, options.data)