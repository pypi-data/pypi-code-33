# vim: set expandtab ts=4 sw=4:

import numpy
import h5py
from numbers import Number

from .register import find_class, register_class

from .mpihandler import MPIHandler

__all__ = []


###################################################################
# Generic HDF5 routines
###################################################################
def obj_from_hdf5group(group):
    cls = find_class(group.attrs['class'])
    if cls is None:
        raise RuntimeError("Cannot find class %s" % group.attrs['class'])
    ret = cls.from_hdf5(group)
    return ret


__all__.append('obj_from_hdf5group')


def obj_from_hdf5file(filename, group=None):
    hfile = h5py.File(filename, 'r')
    # Take the first key out of the dictionary.  This is random ordering, but
    # sometimes useful if you know that the file will only have one key.
    if not group:
        group = list(hfile.keys())[0]

    cls = find_class(hfile[group].attrs['class'])
    if cls is None:
        raise RuntimeError("Cannot find class %s" %
                           hfile[group].attrs['class'])
    ret = cls.from_hdf5(hfile[group])
    hfile.close()

    return ret


__all__.append('obj_from_hdf5file')


def write_to_subgroup(subgroup, hname, val):
    try:
        if val is not None:
            if isinstance(val, numpy.ndarray):
                # If we have a null dimension, we need to hack it a bit
                # because the hdf5 library (at the time of writing) doesn't
                # support null dimensions
                if len(val.shape) == 0 or 0 in val.shape:
                    AnamEmptyArray(shape=val.shape,
                                   dtype=val.dtype).to_hdf5(
                        subgroup.create_group(hname))
                else:
                    subgroup.create_dataset(hname, data=val)
            elif isinstance(val, AbstractAnam) or hasattr(val, 'to_hdf5'):
                ssg = subgroup.create_group(hname)
                val.to_hdf5(ssg)
            elif isinstance(val, list):
                # Use AnamList to write the list
                ssg = subgroup.create_group(hname)
                AnamList(val).to_hdf5(ssg)
            elif isinstance(val, dict):
                # Use AnamDict to write the dict
                ssg = subgroup.create_group(hname)
                AnamDict(val).to_hdf5(ssg)
            else:
                # Assume a normal python object
                subgroup.attrs[hname] = val

    # The no cover here is because this catches things we haven't anticipated
    # If we see this happen, we should be anticipating it, not writing a test
    # to see if we still catch it here...
    except Exception as e:  # pragma: no cover
        raise Exception("Error writing subgroup %s [%s]" % (hname, str(e)))

    return subgroup


__all__.append('write_to_subgroup')


def parse_hdf5_value(subgroup, hname, tgtname, value):
    if isinstance(value, h5py.Dataset):
        # Numpy dataset
        # Deal with some common cases; we have problems
        # if we don't do this (for instance the ppc nodes load
        # data as <f8 instead of >f8 which causes problems later)
        if value.dtype.kind == 'f':
            if value.dtype.itemsize == 8:
                return value[...].astype(numpy.float64)
            elif value.dtype.itemsize == 4:
                return value[...].astype(numpy.float32)
        elif value.dtype.kind == 'c':
            if value.dtype.itemsize == 16:
                return value[...].astype(numpy.complex128)
            elif value.dtype.itemsize == 8:
                return value[...].astype(numpy.complex64)
        elif value.dtype.kind == 'i':
            if value.dtype.itemsize == 8:
                return value[...].astype(numpy.int64)
            elif value.dtype.itemsize == 4:
                return value[...].astype(numpy.int32)
            elif value.dtype.itemsize == 2:
                return value[...].astype(numpy.int16)
            elif value.dtype.itemsize == 1:
                return value[...].astype(numpy.int8)
        elif value.dtype.kind == 'u':
            if value.dtype.itemsize == 8:
                return value[...].astype(numpy.uint64)
            elif value.dtype.itemsize == 4:
                return value[...].astype(numpy.uint32)
            elif value.dtype.itemsize == 2:
                return value[...].astype(numpy.uint16)
            elif value.dtype.itemsize == 1:
                return value[...].astype(numpy.uint8)
        elif value.dtype.kind == 'b':
            return value[...].astype(numpy.bool)
        # Hope for the best
        # Again, we nocover this because it's a case we should never hit; if we
        # do, add something to the code above
        return value[...]  # pragma: nocover
    elif isinstance(value, h5py.Group):
        # Subobject
        # Find out which class we need to use
        cls = find_class(subgroup[hname].attrs['class'])
        if cls is None:
            raise RuntimeError("Cannot find class %s" %
                               subgroup[hname].attrs['class'])
        return cls.from_hdf5(subgroup[hname])

    # Assume it's a python object
    return value


__all__.append('parse_hdf5_value')

###################################################################
# End Generic HDF5 routines
###################################################################


###################################################################
# Generic MPI routines
###################################################################

def bcast_value(hname, val, root=0):
    m = MPIHandler()

    m.bcast(hname, root=root)

    if val is not None:
        # Start by checking for AbstractAnam-like objects and prefer to send
        # them this way.  We do this as things with multiple inheritance might
        # otherwise be confused for dicts or lists
        if isinstance(val, AbstractAnam) or \
           (hasattr(val, 'get_hdf5name') and hasattr(val, 'bcast')):
            m.bcast('ANAM', root=root)
            m.bcast(val, root=root)
        elif isinstance(val, list):
            m.bcast('LIST', root=root)
            m.bcast(len(val), root=root)
            for v in val:
                bcast_value('', v, root=root)
        elif isinstance(val, dict):
            m.bcast('DICT', root=root)
            m.bcast(len(list(val.keys())), root=root)
            for k, v in list(val.items()):
                bcast_value(k, v, root=root)
        else:
            m.bcast('NORMAL', root=root)
            m.bcast(val, root=root)
    else:
        m.bcast(None, root=root)

    return (hname, val)


def bcast_recv_value(root=0):
    m = MPIHandler()

    hname = m.bcast(None, root=root)

    t = m.bcast(None, root=root)

    if t is None:
        val = None
    elif t == 'NORMAL' or t == 'ANAM':
        val = m.bcast(None, root=root)
    elif t == 'LIST':
        val = []
        numitems = m.bcast(None, root=root)
        for j in range(numitems):
            h, v = bcast_recv_value(root=root)
            # Ignore name here, it's irrelevant
            val.append(v)
    elif t == 'DICT':
        val = {}
        numitems = m.bcast(None, root=root)
        for j in range(numitems):
            h, v = bcast_recv_value(root=root)
            val[h] = v
    else:
        raise Exception('State machine error in MPI implementation; '
                        'recieved %s, expecting None, ANAM, '
                        'NORMAL, LIST or DICT' % t)

    return (hname, val)


def send_value(hname, val, dest=0, tag=0):
    m = MPIHandler()

    m.send(hname, dest=dest, tag=tag)

    if val is not None:
        # Start by checking for AbstractAnam-like objects and prefer to send
        # them this way.  We do this as things with multiple inheritance might
        # otherwise be confused for dicts or lists
        if isinstance(val, AbstractAnam) or \
           (hasattr(val, 'get_hdf5name') and hasattr(val, 'bcast')):
            m.send('ANAM', dest=dest, tag=tag)
            m.send(val, dest=dest, tag=tag)
        elif isinstance(val, list):
            m.send('LIST', dest=dest, tag=tag)
            m.send(len(val), dest=dest, tag=tag)
            for v in val:
                send_value('', v, dest=dest, tag=tag)
        elif isinstance(val, dict):
            m.send('DICT', dest=dest, tag=tag)
            m.send(len(list(val.keys())), dest=dest, tag=tag)
            for k, v in list(val.items()):
                send_value(k, v, dest=dest, tag=tag)
        else:
            m.send('NORMAL', dest=dest, tag=tag)
            m.send(val, dest=dest, tag=tag)
    else:
        m.send(None, dest=dest, tag=tag)

    return (hname, val)


def recv_value(source=0, tag=0, status=None):
    m = MPIHandler()

    hname = m.recv(None, source=source, tag=tag, status=status)

    t = m.recv(None, source=source, tag=tag, status=status)

    if t is None:
        val = None
    elif t == 'NORMAL' or t == 'ANAM':
        val = m.recv(None, source=source, tag=tag, status=status)
    elif t == 'LIST':
        val = []
        numitems = m.recv(None, source=source, tag=tag, status=status)
        for j in range(numitems):
            h, v = recv_value(source=source, tag=tag, status=status)
            # Ignore name here, it's irrelevant
            val.append(v)
    elif t == 'DICT':
        val = {}
        numitems = m.recv(None, source=source, tag=tag, status=status)
        for j in range(numitems):
            h, v = recv_value(source=source, tag=tag, status=status)
            val[h] = v
    else:
        raise Exception('State machine error in MPI recv implementation; '
                        'recieved %s, expecting None, ANAM, NORMAL, '
                        'LIST or DICT' % t)

    return (hname, val)

###################################################################
# End Generic MPI routines
###################################################################


class AbstractAnam(object):
    def __init__(self):
        if not hasattr(self, 'refs'):
            self.refs = []
            """
            List of papers relevant to this class
            """

        if not hasattr(self, 'shortdesc'):
            self.shortdesc = 'Undescribed class'
            """
            Short description of the class for use in output
            """

        if not hasattr(self, 'hdf5_aliases'):
            self.hdf5_aliases = []
            """
            List of aliased names for the class.  Usually used to cope with
            moving a class from one module to another
            """

        if not hasattr(self, 'hdf5_outputs'):
            self.hdf5_outputs = []
            """
            List of attribute names in the class to save out.  Attributes in
            this list will be set to None if not found when reading the HDF5
            file.

            Understands how to cope with:
             * python objects such as strings, ints, lists etc
             * numpy.ndarrays
             * classes derived from AbstractAnam
            """

        if not hasattr(self, 'hdf5_mapnames'):
            self.hdf5_mapnames = {}
            """
            Dictionary of name mappings to apply when going to/from hdf5.

            Maps names inside the class as the key to the target in the HDF5
            file as the value.
            """

        if not hasattr(self, 'hdf5_defaultgroup'):
            self.hdf5_defaultgroup = 'unknown'

        if not hasattr(self, 'extra_data'):
            self.extra_data = dict()
            """
            Dictionary containing additional data to be saved in and out.  Will
            be stored in the HDF5 file.
            """

        if not hasattr(self, 'extra_bcast'):
            self.extra_bcast = []
            """
            List containing names of addition items to be broadcast for MPI
            which will not be saved in HDF5 files.
            """

    ###################################################################
    # Generic HDF5 methods
    ###################################################################
    @classmethod
    def get_hdf5name(cls):
        name = '.'.join([cls.__module__, cls.__name__])

        return name

    def check_classname(self, name):

        if isinstance(name, bytes):
            name = name.decode('utf-8')

        if name == self.get_hdf5name():
            return True

        # Check aliases
        for aname in self.hdf5_aliases:
            if name == aname:
                return True

        return False

    @classmethod
    def from_hdf5file(cls, filename, group=None):
        if not group:
            group = cls().hdf5_defaultgroup

        f = h5py.File(filename, 'r')
        ret = cls.from_hdf5(f[group])
        f.close()

        return ret

    def to_hdf5(self, subgroup):
        """
        Base implementation of to_hdf5 function which writes things out
        based on the class hdf5_* variables
        """
        # Write class name
        subgroup.attrs['class'] = self.get_hdf5name()

        # Simple setbit implementation so we don't loop forever
        seenit = {}

        # namemaps is stored as an attribute in the hdf5 file to list which
        # subgroups should be loaded as which members of the object
        namemaps = {}

        # Write any compulsory data
        for a in self.hdf5_outputs:
            # Sort out the attribute name and what we map it to in the HDF5
            # file
            if a in list(self.hdf5_mapnames.keys()):
                hname = self.hdf5_mapnames[a]
                namemaps[hname] = a
            else:
                hname = a

            val = getattr(self, a)
            if val is not None:
                if isinstance(val, AbstractAnam):
                    # Implement a simple setbit implementation to avoid
                    # infinite recursion where A wants to write B as a
                    # subobject and B wants to write A as a subobject
                    id_obj = id(val)
                    if id_obj in list(seenit.keys()):  # pragma: nocover
                        raise Exception("Recursion detected in to_hdf5 "
                                        "(object %s)" % a)
                    seenit[id_obj] = 1

            subgroup = write_to_subgroup(subgroup, hname, val)

        # Write any additional data
        for hname, val in list(self.extra_data.items()):
            if val is not None:
                if isinstance(val, AbstractAnam):  # pragma: nocover
                    # Implement a simple setbit implementation to avoid
                    # infinite recursion where A wants to write B as a
                    # subobject and B wants to write A as a subobject
                    id_obj = id(val)
                    if id_obj in list(seenit.keys()):
                        raise Exception("Recursion detected in to_hdf5")
                    seenit[id_obj] = 1

                subgroup = write_to_subgroup(subgroup, hname, val)

        if len(list(namemaps.keys())) > 0:
            towrite = []
            for key, value in namemaps.items():
                towrite.append([key.encode('utf-8'), value.encode('utf-8')])

            subgroup.attrs['namemaps'] = towrite

        return subgroup

    @classmethod
    def from_hdf5(cls, subgroup):
        """
        Base implementation of to_hdf5 function which re-initialises a class
        based on the hdf5_* variables

        This routine also calls init_from_hdf5 after reading the data in
        so that derived classes can hook in and post-process the data
        """

        try:
            ret = cls()
        except Exception as e:  # pragma: nocover
            raise Exception("Failure creating class "
                            "%s (%s)" % (cls.get_hdf5name(), e))

        # Check the class name against the group
        if not ret.check_classname(subgroup.attrs['class']):  # pragma: nocover
            raise ValueError('Subgroup specifies %s '
                             'instead of %s' % (subgroup.attrs['class'].decode('utf-8'),
                                                ret.get_hdf5name()))

        # Read a namemap if we have one
        namemaps = {}
        if 'namemaps' in list(subgroup.attrs.keys()):
            nm = subgroup.attrs['namemaps']
            for row in range(nm.shape[0]):
                key = nm[row, 0].decode('utf-8')
                val = nm[row, 1].decode('utf-8')
                namemaps[key] = val

        # Deal with old-fashioned lists
        lists = []
        if 'LISTS' in list(subgroup.attrs.keys()):
            lists = subgroup.attrs['LISTS']

        # Quickly build up a dictionary of values we're expecting and mark that
        # we haven't seen them
        honames = {}
        for hname in ret.hdf5_outputs:
            honames[hname] = False

        # Read any data in; starting with attributes
        for hname, value in list(subgroup.attrs.items()):
            # Common things we use
            if hname == 'class' or hname.startswith('LIST'):
                continue

            # If we see a byte array, we want a unicode string This is defined
            # in the file format - if the user wants a real byte array, they
            # need to use a numpy array
            if isinstance(value, bytes):
                value = value.decode('utf-8')

            # Apply the name map if necessary
            tgtname = namemaps.get(hname, hname)

            if tgtname.startswith('LIST_'):
                continue
            elif tgtname in list(honames.keys()):
                setattr(ret, tgtname, value)
                honames[tgtname] = True
            else:
                ret.extra_data[tgtname] = value

        # Read any data from the subgroup itself
        for hname, value in list(subgroup.items()):
            # Apply the name map if necessary
            tgtname = namemaps.get(hname, hname)
            if tgtname.startswith('LIST_'):
                continue
            elif tgtname in list(honames.keys()):
                setattr(ret, tgtname, parse_hdf5_value(subgroup, hname,
                                                       tgtname, value))
                honames[tgtname] = True
            else:
                ret.extra_data[tgtname] = parse_hdf5_value(subgroup, hname,
                                                           tgtname, value)

        # Ensure that any compulsory attributes are set to None if we haven't
        # seen them
        for hname, val in list(honames.items()):
            if not val:
                setattr(ret, hname, None)

        # Now read any old-style lists in.
        # This is for backwards compatibility only
        for l in lists:
            if isinstance(l, bytes):
                l = l.decode('utf-8')
            hname = 'LIST_' + l
            setattr(ret, l, AnamList.from_oldstyle_hdf5(subgroup, hname))

        # Tell the object to sort itself out if a Anam object
        if isinstance(ret, AbstractAnam):
            ret.init_from_hdf5()

        return ret

    ###################################################################
    # End generic HDF5 methods
    ###################################################################

    ###################################################################
    # Start subclassable HDF5 methods
    ###################################################################

    def init_from_hdf5(self):
        """Routine called by from_hdf5 after setting data members and attributes
        when initialising from an hdf5 subgroup"""
        pass

    ###################################################################
    # End subclassable HDF5 methods
    ###################################################################

    ###################################################################
    # Start generic MPI routines
    ###################################################################

    def bcast(self, root=0):
        m = MPIHandler()

        # Write class name to confirm we're doing the right thing
        m.bcast(self.get_hdf5name(), root=root)

        m.bcast('DATA', root=root)
        m.bcast(len(self.hdf5_outputs) + len(list(self.extra_data.keys())),
                root=root)

        # Broadcast our data
        for hname in self.hdf5_outputs:
            val = getattr(self, hname)
            bcast_value(hname, getattr(self, hname), root=root)

        # Broadcast any extra data
        for hname, val in list(self.extra_data.items()):
            bcast_value(hname, val, root=root)

        # Broadcast any additional data
        m.bcast('ADDDATA', root=root)
        m.bcast(len(self.extra_bcast), root=root)
        for hname in self.extra_bcast:
            bcast_value(hname, getattr(self, hname), root=root)

        return self

    @classmethod
    def bcast_recv(cls, root=0):
        """
        """
        m = MPIHandler()

        clsname = m.bcast(None, root=root)

        # Check the class name against the group
        # TODO: Deal with class aliases
        if clsname != cls.get_hdf5name():
            raise ValueError('MPI specifies %s '
                             'instead of %s' % (clsname,
                                                cls.get_hdf5name()))

        ret = cls()

        # Quickly build up a dictionary of values we're expecting and mark that
        # we haven't seen them
        honames = {}
        for hname in ret.hdf5_outputs:
            honames[hname] = False

        check = m.bcast(None, root=root)
        if check != 'DATA':  # pragma: nocover
            raise Exception('State machine error in MPI implementation; '
                            'recieved %s, expecting DATA' % check)

        # Read core data in
        numdata = m.bcast(None, root=root)
        for n in range(numdata):
            tgtname, value = bcast_recv_value(root=root)

            if tgtname in list(honames.keys()):
                setattr(ret, tgtname, value)
                honames[tgtname] = True
            else:
                ret.extra_data[tgtname] = value

        # Ensure that any compulsory attributes are set to None if we haven't
        # seen them
        for hname, val in list(honames.items()):
            if not val:
                setattr(ret, hname, None)

        # Read any additional data
        check = m.bcast(None, root=root)
        if check != 'ADDDATA':  # pragma: nocover
            raise Exception('State machine error in MPI implementation; '
                            'recieved %s, expecting ADDDATA' % check)

        numdata = m.bcast(None, root=root)
        for n in range(numdata):
            tgtname, value = bcast_recv_value(root=root)
            setattr(ret, tgtname, value)

        # Tell the object to sort itself out
        ret.init_from_hdf5()

        return ret

    def send(self, dest=0, tag=0):
        m = MPIHandler()

        # Write class name to confirm we're doing the right thing
        m.send(self.get_hdf5name(), dest=dest, tag=tag)

        m.send('DATA', dest=dest, tag=tag)
        m.send(len(self.hdf5_outputs) + len(list(self.extra_data.keys())),
               dest=dest, tag=tag)

        # Send our data
        for hname in self.hdf5_outputs:
            val = getattr(self, hname)
            send_value(hname, getattr(self, hname), dest=dest, tag=tag)

        # Send any extra data
        for hname, val in list(self.extra_data.items()):
            send_value(hname, val, dest=dest, tag=tag)

        # Send any additional data
        m.send('ADDDATA', dest=dest, tag=tag)
        m.send(len(self.extra_bcast), dest=dest, tag=tag)
        for hname in self.extra_bcast:
            send_value(hname, getattr(self, hname), dest=dest, tag=tag)

        return self

    @classmethod
    def recv(cls, source=0, tag=0, status=None):
        """
        """
        m = MPIHandler()

        clsname = m.recv(None, source=source, tag=tag, status=status)

        # Check the class name against the group
        # TODO: Deal with class aliases
        if clsname != cls.get_hdf5name():  # pragma: nocover
            raise ValueError('MPI specifies %s '
                             'instead of %s' % (clsname,
                                                cls.get_hdf5name()))

        ret = cls()

        # Quickly build up a dictionary of values we're expecting and mark that
        # we haven't seen them
        honames = {}
        for hname in ret.hdf5_outputs:
            honames[hname] = False

        check = m.recv(None, source=source, tag=tag, status=status)
        if check != 'DATA':
            raise Exception('State machine error in MPI recv '
                            'implementation; recieved %s, '
                            'expecting DATA' % check)

        # Read core data in
        numdata = m.recv(None, source=source, tag=tag, status=status)
        for n in range(numdata):
            tgtname, value = recv_value(source=source, tag=tag, status=status)

            if tgtname in list(honames.keys()):
                setattr(ret, tgtname, value)
                honames[tgtname] = True
            else:
                ret.extra_data[tgtname] = value

        # Ensure that any compulsory attributes are set to None if we haven't
        # seen them
        for hname, val in list(honames.items()):
            if not val:
                setattr(ret, hname, None)

        # Read any additional data
        check = m.recv(None, source=source, tag=tag, status=status)
        if check != 'ADDDATA':
            raise Exception('State machine error in MPI recv '
                            'implementation; recieved %s, '
                            'expecting ADDDATA' % check)

        numdata = m.recv(None, source=source, tag=tag, status=status)
        for n in range(numdata):
            tgtname, value = recv_value(source=source, tag=tag, status=status)
            setattr(ret, tgtname, value)

        # Tell the object to sort itself out
        ret.init_from_hdf5()

        return ret

    ###################################################################
    # End generic MPI routines
    ###################################################################

    ###################################################################
    # Generic reporting routines
    ###################################################################
    def to_report_text(self, report, page, hdrlevel):
        """
        Generic routine to produce an RST-style report.

        Will simply append the class string representation in
        a literal text block
        """
        s = '::\n\n'
        s += '    ' + str(self).replace('\n', '\n    ')
        s += '\n'
        page.text += s

        if self.refs is not None:
            page.add_ref(self.refs)

        return report, page


__all__.append('AbstractAnam')


class AnamEmptyArray(AbstractAnam):
    def __init__(self, shape=(0, ), dtype=numpy.float32):
        self.shape = shape
        self.dtype = dtype

    def to_hdf5(self, subgroup):
        # Write class name
        subgroup.attrs['class'] = self.get_hdf5name()

        # Write out a numpy array containing the dimensions
        if len(self.shape) > 0:
            s = numpy.array(self.shape, dtype=numpy.int64)
            subgroup = write_to_subgroup(subgroup, 'shape', s)

        # Write out a 1 array just containing the dtype
        d = numpy.array((1, 1), dtype=self.dtype)
        subgroup = write_to_subgroup(subgroup, 'dtype', d)

        return subgroup

    @classmethod
    def from_hdf5(cls, subgroup):
        arr = cls()

        # Check the class name against the group
        if not arr.check_classname(subgroup.attrs['class']):  # pragma: nocover
            raise ValueError('Subgroup specifies %s '
                             'instead of %s' % (subgroup.attrs['class'],
                                                arr.get_hdf5name()))

        # Read the shape and dtype
        if 'shape' in list(subgroup.keys()):
            s = parse_hdf5_value(subgroup, 'shape', None, subgroup['shape'])
        else:
            s = ()

        d = parse_hdf5_value(subgroup, 'dtype', None, subgroup['dtype'])

        return numpy.zeros(tuple(s), dtype=d.dtype)


__all__.append('AnamEmptyArray')
register_class(AnamEmptyArray)


class AnamList(AbstractAnam):
    """
    Class whose sole purpose in life is to allow us to easily serialise
    and unserialise nested lists
    """
    def __init__(self, data=None):
        if data is None:
            self.data = []
        elif not isinstance(data, list):
            self.data = [data]
        else:
            self.data = data

    def to_hdf5(self, subgroup):
        # Write class name
        subgroup.attrs['class'] = self.get_hdf5name()

        # Save number of elements
        subgroup.attrs['count'] = len(self.data)

        cur = 0
        # Write out subgroups containing each element
        hname = 'LIST_item'

        for element in self.data:
            # Name for new subgroup if necessary
            thisname = hname + str(cur)
            write_to_subgroup(subgroup, thisname, element)
            cur += 1

        return subgroup

    @staticmethod
    def from_oldstyle_hdf5(subgroup, name):
        """
        This is a convenience routine which loads the old LIST_* style lists
        from when we used the hdf5_lists methods.

        It's simply in this class for code-neatness reasons.

        Note that this only ever supported lists of AbstractAnam derived
        classes and never nested lists.  The new implementation is heavily
        preferred.  We now only have read support for this format.
        """
        ret = []

        if not subgroup.attrs[name + '_count']:  # pragma: nocover
            raise Exception("Malformed old-style list: "
                            "missing %s" % (name + '_count'))

        count = subgroup.attrs[name + '_count']
        for n in range(count):
            sg = subgroup.get(name + str(n), None)
            cls = find_class(sg.attrs['class'])
            if not cls:  # pragma: nocover
                raise Exception("Class %s missing reading item "
                                "%d for old-style list %s" %
                                (sg.attrs['class'], n, name))
            item = cls.from_hdf5(sg)
            ret.append(item)

        return ret

    @classmethod
    def from_hdf5(cls, subgroup):
        arr = cls()
        ret = []

        # Check the class name against the group
        if not arr.check_classname(subgroup.attrs['class']):  # pragma: nocover
            raise ValueError('Subgroup specifies %s instead '
                             'of %s' % (subgroup.attrs['class'],
                                        arr.get_hdf5name()))

        # Get number of elements
        if 'count' not in subgroup.attrs:  # pragma: nocover
            raise ValueError('Number of element missing')

        cnt = subgroup.attrs['count']

        for j in range(cnt):
            hname = 'LIST_item%d' % j
            # If we have an attribute, it was just a python object
            if hname in list(subgroup.attrs.keys()):
                ret.append(subgroup.attrs[hname])
            elif hname in list(subgroup.keys()):
                # Use parse_hdf5
                ret.append(parse_hdf5_value(subgroup, hname,
                           None, subgroup[hname]))
            else:
                # We use the absence of an item to indicate None (see
                # write_to_subgroup)
                ret.append(None)

        return ret


__all__.append('AnamList')
register_class(AnamList)


class AnamDict(AbstractAnam):
    """
    Class whose sole purpose in life is to allow us to easily serialise
    and unserialise nested dictionaries.
    """
    def __init__(self, data=None):
        if data is None:
            data = {}
        elif not isinstance(data, dict):
            raise ValueError("AnamDict requires a dictionary")
        self.data = data

    def to_hdf5(self, subgroup):
        # Write class name
        subgroup.attrs['class'] = self.get_hdf5name()

        # Save number of elements
        subgroup.attrs['count'] = len(list(self.data.keys()))

        # We serialise as two lists so that we can deal with the datatypes
        # of keys
        write_to_subgroup(subgroup, 'dictkeys', list(self.data.keys()))
        write_to_subgroup(subgroup, 'dictdata', list(self.data.values()))

        return subgroup

    @classmethod
    def from_hdf5(cls, subgroup):
        arr = cls()

        # Check the class name against the group
        if not arr.check_classname(subgroup.attrs['class']):  # pragma: nocover
            raise ValueError('Subgroup specifies %s '
                             'instead of %s' % (subgroup.attrs['class'],
                                                arr.get_hdf5name()))

        # Get number of elements
        if 'count' not in subgroup.attrs:  # pragma: nocover
            raise ValueError('Number of elements missing')

        cnt = subgroup.attrs['count']

        # Get number of elements
        if 'dictkeys' not in list(subgroup.keys()):  # pragma: nocover
            raise ValueError('Dictionary keys missing')

        if 'dictdata' not in list(subgroup.keys()):  # pragma: nocover
            raise ValueError('Dictionary data missing')

        keys = parse_hdf5_value(subgroup, 'dictkeys',
                                None, subgroup['dictkeys'])

        items = parse_hdf5_value(subgroup, 'dictdata',
                                 None, subgroup['dictdata'])

        if len(keys) != cnt:  # pragma: nocover
            raise ValueError("Incorrect number of keys found "
                             "(%d vs %d)" % (len(keys), cnt))

        if len(items) != cnt:  # pragma: nocover
            raise ValueError("Incorrect number of items found "
                             "(%d vs %d)" % (len(items), cnt))

        # Create our dictionary
        return dict(list(zip(keys, items)))


__all__.append('AnamDict')
register_class(AnamDict)


################################################################
# AnamCollection
################################################################

class AnamCollection(AbstractAnam):
    """
    AbstractAnamCollection is designed to allow collections of similar Anam
    objects to be easily stored and retrieved together.

    The object behaves like a normal python list, but also provides for a level
    of "caching" and easy access to common attributes (currently limited to
    numpy arrays) across the multiple objects.

    Users can access the objects in the list using the usual append, insert,
    pop, count and [idx] syntax.

    Subclasses of AnamCollection can provide the anam_combine member variable.
    This is a list of variable names from the stored subclass which should be
    made available via the top level collection.  At the moment, these
    variables must be numpy arrays.  When numpy arrays are collated for
    returning, an extra dimension will be added to the end of the overall array
    which will index the member object from which the data came.

    At the moment, "caching" will only be used if update_cache() is explicitly
    called.  Note that clear_cache() must be called if objects stored in the
    list change.

    At the moment, no sanity checking is performed to ensure that only
    appropriate objects are added into the collection - this must be performed
    by users or subclasses.  This may be changed in future versions.
    """

    hdf5_outputs = ['members']

    def __init__(self, data=None):
        AbstractAnam.__init__(self)

        if not hasattr(self, 'members'):
            self.members = []
            """
            A list of member objects - must be of same type
            """

        if not hasattr(self, 'anam_combine'):
            self.anam_combine = []
            """
            Attributes of member objects to combine into single arrays when
            using the cache.
            """

        if not hasattr(self, '_cache'):
            self._cache = {}

        if data is not None:
            if isinstance(data, list):
                self.members = data
            else:
                self.members = [data]

    def __getattr__(self, name):
        """Override getattr so that cached entries can be accessed directly"""
        if name == 'anam_combine':
            return self.__getattribute__('anam_combine')

        if name in self.anam_combine:
            return self._cache.get(name, None)

        return AbstractAnam.__getattr__(self, name)

    # Map all of the list functions through to the members list
    def __getitem__(self, key):
        return self.members.__getitem__(key)

    def __getslice__(self, *args, **kwargs):
        return self.members.__getslice__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.members.__setitem__(*args, **kwargs)

    def __setslice__(self, *args, **kwargs):
        return self.members.__setslice__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self.members.__delitem__(*args, **kwargs)

    def __delslice__(self, *args, **kwargs):
        return self.members.__delslice__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.members.__iter__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self.members.__contains__(*args, **kwargs)

    def __len__(self):
        return self.members.__len__()

    def append(self, *args, **kwargs):
        return self.members.append(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self.members.count(*args, **kwargs)

    def extend(self, *args, **kwargs):
        return self.members.extend(*args, **kwargs)

    def index(self, *args, **kwargs):
        return self.members.index(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.members.insert(*args, **kwargs)

    def pop(self, *args, **kwargs):
        return self.members.pop(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.members.remove(*args, **kwargs)

    def reverse(self, *args, **kwargs):
        return self.members.reverse(*args, **kwargs)

    def sort(self, *args, **kwargs):
        return self.members.sort(*args, **kwargs)

    # It's quite helpful to be able to ask what the cache keys are too
    def keys(self):
        return self.anam_combine

    # Caching logic
    def update_cache(self, flexible=False):
        """Update our cached collection data.

        In flexible mode, we don't raise if the data for an element is not
        conformable, instead, we set the key to None"""
        self._cache = {}

        num_members = len(self.members)

        # No need to do anything if we have no members
        if num_members < 1:
            for attr in self.anam_combine:
                self._cache[attr] = None
        else:
            # Only update the cache if we fully succeed
            newcache = {}
            for attr in self.anam_combine:
                # Need to figure out the relevant size of the matrix should be
                scalar = False

                if not hasattr(self.members[0], attr):
                    raise AttributeError("%s does not exist in member." % attr)
                try:
                    if isinstance(getattr(self.members[0], attr), Number):
                        sh = ()
                        dt = type(getattr(self.members[0], attr))
                        scalar = True
                    else:
                        sh = getattr(self.members[0], attr).shape
                        dt = getattr(self.members[0], attr).dtype
                except AttributeError as e:
                    raise AttributeError("%s does not have shape/dtype "
                                         "attribute - is it a numpy array? "
                                         "(%s)" % (attr, e))

                # Raise an error if the matrices aren't conformable
                newcache[attr] = numpy.zeros((sh + (num_members,)), dt)

                for midx in range(num_members):
                    if not hasattr(self.members[midx], attr):
                        raise AttributeError("%s does not exist in "
                                             "member." % attr)

                    dat = getattr(self.members[midx], attr)

                    if scalar:
                        newcache[attr][midx] = dat
                        continue

                    # Deal with array case
                    if dat.dtype != dt:
                        raise ValueError("datatypes for %s do not "
                                         "match across members" % (attr))
                    if dat.shape != sh:
                        # In flexible mode, we simply don't collate the data
                        if flexible:
                            newcache[attr] = None
                            continue
                        else:
                            raise ValueError("shapes for %s do not "
                                             "match across members" % (attr))

                    newcache[attr][..., midx] = dat

            # We're good
            self._cache = newcache

    def clear_cache(self):
        """Clear our cached collection data"""
        self._cache = {}


__all__.append('AnamCollection')
register_class(AnamCollection)
