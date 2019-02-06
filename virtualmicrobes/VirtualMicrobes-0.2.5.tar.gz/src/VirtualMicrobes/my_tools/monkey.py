'''
Created on Feb 17, 2016

@author: thocu
'''

def monkeypatch_class(name, bases, namespace):
    '''
    https://mail.python.org/pipermail/python-dev/2008-January/076194.html
    
    
    WHOOOHHHAAAAA this is a Monkey Patch. Eat that, unreliable package developers!
    '''
    assert len(bases) == 1, "Exactly one base class required"
    base = bases[0]
    for name, value in namespace.iteritems():
        if name != "__metaclass__":
            setattr(base, name, value)
    return base

#To use:

from matplotlib.artist import Artist

class MyArtist(Artist):
    __metaclass__ = monkeypatch_class
    def __setstate__(self, odict):
        Artist.__init__(self)
        self.__dict__.update(odict)


from matplotlib.figure import Figure
class MyFigure(Figure):
    __metaclass__ = monkeypatch_class
    def __setstate__(self, state):
        restore_to_pylab = state.pop('_restore_to_pylab', False)

        super(Figure,self).__setstate__(state)    
        self.__dict__.update(state)

        # re-initialise some of the unstored state information
        self._axobservers = []
        self.canvas = None

        if restore_to_pylab:
            # lazy import to avoid circularity
            import matplotlib.pyplot as plt
            import matplotlib._pylab_helpers as pylab_helpers
            allnums = plt.get_fignums()
            num = max(allnums) + 1 if allnums else 1
            mgr = plt._backend_mod.new_figure_manager_given_figure(num, self)

            # XXX The following is a copy and paste from pyplot. Consider
            # factoring to pylab_helpers

            if self.get_label():
                mgr.set_window_title(self.get_label())

            # make this figure current on button press event
            def make_active(event):
                pylab_helpers.Gcf.set_active(mgr)

            mgr._cidgcf = mgr.canvas.mpl_connect('button_press_event',
                                                 make_active)

            pylab_helpers.Gcf.set_active(mgr)
            self.number = num

            plt.draw_if_interactive()
        self.stale = True
        
from matplotlib.transforms import TransformWrapper, WeakValueDictionary
class MyTransformWrapper(TransformWrapper):
    __metaclass__ = monkeypatch_class

    def __setstate__(self, state):
        # re-initialise the TransformWrapper with the state's child
        self._init(state['child'])
        # The child may not be unpickled yet, so restore its information.
        self.input_dims = state.get('input_dims', None)
        self.output_dims = state.get('output_dims', None)
        # turn the normal dictionary back into a WeakValueDictionary
        self._parents = WeakValueDictionary(state.get('parents',dict()) )
