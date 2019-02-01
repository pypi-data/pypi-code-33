# vim: set expandtab ts=4 sw=4:

# A set of old hints which are used when initialising ClassRegister
_OLD_HINTS = {
    'naf.meg.abstracttransforms.FourByFourTransform':
        'naf.meg.transforms.FourByFourTransform',
    'naf.meg.abstracttransforms.AsciiFourByFourTransform':
        'naf.meg.transforms.AsciiFourByFourTransform',
    'naf.meg.abstracttransforms.NiftiTransform':
        'naf.meg.transforms.NiftiTransform',
    'naf.meg.abstracttransforms.AffineCoordSet':
        'naf.meg.transforms.AffineCoordSet',
    'naf.meg.beamformers.BeamformerMetric':
        'naf.meg.beamformeranalyses.BeamformerMetric',
    'naf.meg.beamformers.NAI':
        'naf.meg.beamformeranalyses.NAI',
    'naf.meg.beamformers.BFWeights':
        'naf.meg.beamformeranalyses.BFWeights',
    'naf.meg.beamformers.BFTimeSeries':
        'naf.meg.beamformeranalyses.BFTimeSeries',
    'naf.meg.beamformers.BFTimeSeriesMetric':
        'naf.meg.beamformeranalyses.BFTimeSeriesMetric',
    'naf.meg.beamformers.BFTimeSeriesMeanVar':
        'naf.meg.beamformeranalyses.BFTimeSeriesMeanVar',
    'naf.meg.beamformers.BFTimeSeriesT2':
        'naf.meg.beamformeranalyses.BFTimeSeriesT2',
    'naf.meg.beamformers.NonRadOrientBase':
        'naf.meg.orientselectors.NonRadOrientBase',
    'naf.meg.beamformers.NonRadOrientSekihara':
        'naf.meg.orientselectors.NonRadOrientSekihara',
    'naf.meg.beamformers.NonRadOrientVanVeen':
        'naf.meg.orientselectors.NonRadOrientVanVeen',
    'naf.meg.beamformers.NonRadOrientPower':
        'naf.meg.orientselectors.NonRadOrientPower',
    'naf.meg.beamformers.NonRadOrientSekiBrute':
        'naf.meg.orientselectors.NonRadOrientSekiBrute',
    'naf.meg.beamformers.NonRadOrientVanVeenBrute2D':
        'naf.meg.orientselectors.NonRadOrientVanVeenBrute2D',
    'naf.meg.beamformers.NonRadOrientVanVeenBrute1D':
        'naf.meg.orientselectors.NonRadOrientVanVeenBrute1D',
    'naf.meg.beamformers.NonRadOrientPowerBrute':
        'naf.meg.orientselectors.NonRadOrientPowerBrute',
    'naf.meg.beamformers.FreeOrientBase':
        'naf.meg.orientselectors.FreeOrientBase',
    'naf.meg.beamformers.FreeOrientSekihara':
        'naf.meg.orientselectors.FreeOrientSekihara',
    'naf.meg.beamformers.FreeOrientVanVeen':
        'naf.meg.orientselectors.FreeOrientVanVeen',
    'naf.meg.beamformers.FreeOrientPower':
        'naf.meg.orientselectors.FreeOrientPower',
    'naf.meg.coils.CoilGroup':
        'naf.meg.channels.ChannelGroup',
    'naf.meg.coils.CoilSet':
        'naf.meg.channels.ChannelSet',
    'naf.meg.coils.CoilType':
        'naf.meg.channels.ChannelType',
    'naf.meg.coils.CoilName':
        'naf.meg.channels.ChannelName',
    'naf.meg.coils.DictCoilDefiner':
        'naf.meg.channels.DictChannelDefiner',
    'naf.meg.btireaders.BTICoilName':
        'naf.meg.btireaders.BTIChannelName'}


class ClassRegister(object):
    __shared_state = {}

    def __init__(self, *args, **kwargs):
        # Quick way of implementing a singleton
        self.__dict__ = self.__shared_state

        if not getattr(self, 'initialised', False):
            self.initialised = True
            self.class_register = {}

            # For historical reasons, we allow naf and ourselves
            self.permitted_prefixes = ['naf', 'anamnesis']

            # For further historical reasons, we load some of the
            # old NAF aliases by default to ease the transition to
            # the broken out, general anamnesis library
            self.hints = _OLD_HINTS.copy()

    def add_permitted_prefix(self, prefix):
        """
        Adds a permitted prefix to the automatic class finder
        """
        self.permitted_prefixes.append(prefix)

    def check_permitted_prefix(self, cname):
        """
        Checks whether a class name starts with a permitted prefix

        :param cname: class name to check
        :returns: True or False
        """
        for pp in self.permitted_prefixes:
            if cname.startswith(pp):
                return True

        return False

    def add_hint(self, oldname, newname):
        """
        Adds a "hint" to the system.

        This is useful if you have renamed a class and need to ensure
        that old serialisation files will still load.  The loading code
        will automatically substitute the old name found in the file
        with the new name given here

        :param oldname: The old full name of the class as a string (e.g.
        'naf.meg.abstracttransforms.FourByFourTransform'
        :param newname: The new full name of the class as a string (e.g.
        'naf.meg.transforms.FourByFourTransform'
        """
        self.hints[oldname] = newname

    def check_hint(self, cname):
        """
        Looks up any hinted class name for the given input name.

        :param cname: Class name to look for a hint for
        :returns: None if not found or full class name of replacement class if
        available
        """
        return self.hints.get(cname, None)


def register_class(cls, name=None):
    c = ClassRegister()

    if name is None:
        name = '.'.join([cls.__module__, cls.__name__])

    if name in c.class_register:
        raise Exception('Name %s already registered' % name)
    c.class_register[name] = cls

    for aname in getattr(cls(), 'hdf5_aliases', []):
        if aname in c.class_register:
            raise Exception('Alias name %s already registered' % aname)
        c.class_register[aname] = cls


def find_class(name):
    c = ClassRegister()
    cls = c.class_register.get(name, None)

    if cls is not None:
        return cls

    # Try our best to find and import it whilst not being entirely insecure
    if isinstance(name, bytes):
        name = name.decode()

    nc = name.split('.')

    cnt = len(nc)
    while cnt > 0:
        try:
            cname = '.'.join(nc[0:cnt])
            # A vague attempt at preventing people abusing this to cause random
            # modules to load.
            if not c.check_permitted_prefix(cname):
                return None
            __import__(cname)
            # Try to find it again
            cls = c.class_register.get(name, None)
            if cls is not None:
                break
        except ImportError:
            # Walk backwards for Christmas
            pass

        cnt -= 1

    if cls is not None:
        return cls

    # If we still haven't found it, look up our hints
    hint = c.check_hint(name)
    if hint is not None:
        return find_class(hint)

    return None


__all__ = ['register_class', 'find_class']
