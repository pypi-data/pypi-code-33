#!/usr/bin/python

"""Tests for abstract module"""
# vim: set expandtab ts=4 sw=4:

from os.path import join

import h5py

from numpy.testing import assert_array_equal

from ..test import anamtestpath, AnamTestBase

# This will raise if it can't find the test data directory
DATADIR = anamtestpath()

# Tests that involve writing are grouped in a class

from ..abstract import AbstractAnam, register_class  # noqa: F402


class TestDictWriter(AbstractAnam):

    hdf5_outputs = ['ddat']

    def __init__(self, setvals=None):
        AbstractAnam.__init__(self)

        self.ddat = setvals


register_class(TestDictWriter)


class TestListWriter(AbstractAnam):

    hdf5_outputs = ['ldat']

    def __init__(self, setvals=None):
        AbstractAnam.__init__(self)

        self.ldat = setvals


register_class(TestListWriter)


class TestWriter(AbstractAnam):

    hdf5_outputs = ['dat']

    def __init__(self, setvals=None):
        AbstractAnam.__init__(self)

        self.dat = setvals


register_class(TestWriter)


class TestArrayContainer(AbstractAnam):

    hdf5_outputs = ['data1', 'data2']

    def __init__(self, data1=None, data2=None):
        AbstractAnam.__init__(self)

        self.data1 = data1
        self.data2 = data2

    def __lt__(self, other):
        # This isn't a proper test, it just sorts
        # by object ID for test purposes
        return id(self) < id(other)

    def __eq__(self, other):
        # This isn't a proper test, it just compares
        # by object ID for test purposes
        return id(self) == id(other)


register_class(TestArrayContainer)


class AbstractWritingTest(AnamTestBase):
    def write_it(self, filename, dat):
        import h5py

        f = h5py.File(join(self.tempdir, filename), 'w')
        g = f.create_group('test')
        dat.to_hdf5(g)
        f.close()

    def read_it(self, filename, cls):
        import h5py

        f = h5py.File(join(self.tempdir, filename), 'r')
        blah = cls.from_hdf5(f['test'])
        f.close()
        return blah

    def array_checker(self, val, expected):
        a = TestWriter(val)
        self.write_it('test.hdf5', a)
        b = self.read_it('test.hdf5', TestWriter)
        assert((expected == b.dat).all())

    def scalar_checker(self, val, expected):
        a = TestWriter(val)
        self.write_it('test.hdf5', a)
        b = self.read_it('test.hdf5', TestWriter)
        assert((expected == b.dat))

    def test_write_extra_data(self):
        """Check that we can save and restore extra data"""
        a = TestWriter('nothing')
        a.extra_data['foo'] = 1
        self.write_it('test.hdf5', a)
        b = self.read_it('test.hdf5', TestWriter)
        assert('foo' in b.extra_data)
        assert(b.extra_data['foo'] == 1)

    def test_write_array_int8(self):
        """Check that we can save and restore a int8 numpy array"""
        from numpy import array, int8
        a = array([[1, 2], [3, 4]], dtype=int8)
        self.array_checker(a, a)

    def test_write_array_int16(self):
        """Check that we can save and restore a int16 numpy array"""
        from numpy import array, int16
        a = array([[1, 2], [3, 4]], dtype=int16)
        self.array_checker(a, a)

    def test_write_array_int32(self):
        """Check that we can save and restore a int32 numpy array"""
        from numpy import array, int32
        a = array([[1, 2], [3, 4]], dtype=int32)
        self.array_checker(a, a)

    def test_write_array_int64(self):
        """Check that we can save and restore a int64 numpy array"""
        from numpy import array, int64
        a = array([[1, 2], [3, 4]], dtype=int64)
        self.array_checker(a, a)

    def test_write_array_uint8(self):
        """Check that we can save and restore a uint8 numpy array"""
        from numpy import array, uint8
        a = array([[1, 2], [3, 4]], dtype=uint8)
        self.array_checker(a, a)

    def test_write_array_uint16(self):
        """Check that we can save and restore a uint16 numpy array"""
        from numpy import array, uint16
        a = array([[1, 2], [3, 4]], dtype=uint16)
        self.array_checker(a, a)

    def test_write_array_uint32(self):
        """Check that we can save and restore a uint32 numpy array"""
        from numpy import array, uint32
        a = array([[1, 2], [3, 4]], dtype=uint32)
        self.array_checker(a, a)

    def test_write_array_uint64(self):
        """Check that we can save and restore a uint64 numpy array"""
        from numpy import array, uint64
        a = array([[1, 2], [3, 4]], dtype=uint64)
        self.array_checker(a, a)

    def test_write_array_float32(self):
        """Check that we can save and restore a float32 numpy array"""
        from numpy import array, float32
        a = array([[1.0, 2.0], [3.0, 4.0]], dtype=float32)
        self.array_checker(a, a)

    def test_write_array_float64(self):
        """Check that we can save and restore a float64 numpy array"""
        from numpy import array, float64
        a = array([[1.0, 2.0], [3.0, 4.0]], dtype=float64)
        self.array_checker(a, a)

    def test_write_array_complex64(self):
        """Check that we can save and restore a complex64 numpy array"""
        from numpy import array, complex64
        a = array([[1.0, 2.0], [3.0, 4.0]], dtype=complex64)
        self.array_checker(a, a)

    def test_write_array_complex128(self):
        """Check that we can save and restore a complex128 numpy array"""
        from numpy import array, complex128
        a = array([[1.0, 2.0], [3.0, 4.0]], dtype=complex128)
        self.array_checker(a, a)

    def test_write_array_bool(self):
        """Check that we can save and restore a bool numpy array"""
        from numpy import array
        a = array([[False, True], [True, False]], dtype=bool)
        self.array_checker(a, a)

    def test_write_null_array_0d(self):
        """Check that we can save and restore a null numpy array with 0
        dimensions (float64)"""
        from numpy import zeros, float64
        a = zeros((), dtype=float64)
        self.array_checker(a, a)

    def test_write_null_array_1d(self):
        """Check that we can save and restore a null numpy array with 1
        dimension (float64)"""
        from numpy import array, float64
        a = array([], dtype=float64)
        self.array_checker(a, a)

    def test_write_null_array_2d(self):
        """Check that we can save and restore a null numpy array with 2
        dimensions (float64)"""
        from numpy import array, float64
        a = array([[], []], dtype=float64)
        self.array_checker(a, a)

    def test_write_null_array_3d(self):
        """Check that we can save and restore a null numpy array with 3
        dimensions (float32)"""
        from numpy import array, float32
        a = array([[[], [], []], [[], [], []], ], dtype=float32)
        self.array_checker(a, a)

    def test_write_null_array_3d_int16(self):
        """Check that we can save and restore a null numpy array with 3
        dimensions (int16)"""
        from numpy import array, int16
        a = array([[[], [], []], [[], [], []], ], dtype=int16)
        self.array_checker(a, a)

    def test_write_list(self):
        """Check that we can save and restore a list"""
        a = [1, 2, 3, 4]
        self.scalar_checker(a, a)

    def test_write_list_nested1(self):
        """Check that we can save and restore nested lists"""
        a = [1, [1, 2], 3, 4]
        self.scalar_checker(a, a)

    def test_write_list_nested2(self):
        """Check that we can save and restore really nested lists"""
        a = [1, [1, 2, 3], [3, 2, 1], [3, 2, 1], 4]
        self.scalar_checker(a, a)

    def test_write_list_nested3(self):
        """Check that we can save and restore really nested lists with
        objects"""
        a = [1, [TestWriter(), 2], 'a',
             4, TestWriter(), [1, None, 'foo'],
             [], [[]]]
        tw = TestWriter(a)
        self.write_it('test.hdf5', tw)
        b = self.read_it('test.hdf5', TestWriter)
        assert(isinstance(b, TestWriter))
        b = b.dat
        assert(len(b) == 8)
        assert(b[0] == 1)
        assert(isinstance(b[1], list))
        assert(len(b[1]) == 2)
        assert(isinstance(b[1][0], TestWriter))
        assert(b[1][1] == 2)
        assert(b[2] == 'a')
        assert(b[3] == 4)
        assert(isinstance(b[4], TestWriter))
        assert(isinstance(b[5], list))
        assert(len(b[5]) == 3)
        assert(b[5][0] == 1)
        assert(b[5][1] is None)
        assert(b[5][2] == 'foo')
        assert(isinstance(b[6], list))
        assert(len(b[6]) == 0)
        assert(isinstance(b[7], list))
        assert(len(b[7]) == 1)
        assert(isinstance(b[7][0], list))
        assert(len(b[7][0]) == 0)

    def test_write_empty_list(self):
        """Check that we can save and restore an empty list"""
        self.scalar_checker([], [])

    def test_write_list_of_objects(self):
        """Check that we can save and restore a list of objects"""
        l = [TestWriter(1), TestWriter(2), TestWriter(3)]
        a = TestListWriter(l)
        self.write_it('test.hdf5', a)
        b = self.read_it('test.hdf5', TestListWriter)
        assert(isinstance(b, TestListWriter))
        assert(isinstance(b.ldat, list))
        assert(len(b.ldat) == 3)
        for j in range(3):
            assert(isinstance(b.ldat[j], TestWriter))
            assert(b.ldat[j].dat == (j+1))

    def test_reading_list_of_objects_new(self):
        """Check that we can restore a list of objects in the new, sane
        AnamList format"""
        from ..abstract import obj_from_hdf5file
        filename = join(DATADIR, 'test_newlist.hdf5')
        b = obj_from_hdf5file(filename)
        assert(isinstance(b, TestListWriter))
        assert(isinstance(b.ldat, list))
        assert(len(b.ldat) == 3)
        for j in range(3):
            assert(isinstance(b.ldat[j], TestWriter))
            assert(b.ldat[j].dat == (j+1))

    def test_reading_list_of_objects_old(self):
        """Check that we can restore a list of objects in the old LIST
        format"""
        from ..abstract import obj_from_hdf5file
        filename = join(DATADIR, 'test_oldlist.hdf5')
        b = obj_from_hdf5file(filename)
        assert(isinstance(b, TestListWriter))
        assert(isinstance(b.ldat, list))
        assert(len(b.ldat) == 3)
        for j in range(3):
            assert(isinstance(b.ldat[j], TestWriter))
            assert(b.ldat[j].dat == (j+1))

    def test_write_mixed_list(self):
        """Check that we can save and restore a mixed list of python
        built-ins"""
        a = ['a', 'b', 1, 2.0]
        self.scalar_checker(a, a)

    def test_write_empty_dict(self):
        """Check that we can save and restore an empty dictionary"""
        l = {}
        a = TestDictWriter(l)
        self.write_it('test.hdf5', a)
        b = self.read_it('test.hdf5', TestDictWriter)
        assert(isinstance(b, TestDictWriter))
        assert(isinstance(b.ddat, dict))
        assert(len(b.ddat) == 0)

    def test_write_basic_dict(self):
        """Check that we can save and restore a basic dictionary"""
        l = {'A': 1, 'B': 2}
        a = TestDictWriter(l)
        self.write_it('test.hdf5', a)
        b = self.read_it('test.hdf5', TestDictWriter)
        assert(isinstance(b, TestDictWriter))
        assert(isinstance(b.ddat, dict))
        assert(len(b.ddat) == 2)
        assert(b.ddat['A'] == 1)
        assert(b.ddat['B'] == 2)

    def test_write_dict_with_objects(self):
        """Check that we can save and restore a dictionary containing
        objects"""
        l = {'a': TestWriter(1),
             2: TestWriter(2),
             3: TestWriter(3)}
        a = TestDictWriter(l)
        self.write_it('test.hdf5', a)
        b = self.read_it('test.hdf5', TestDictWriter)
        assert(isinstance(b, TestDictWriter))
        assert(isinstance(b.ddat, dict))
        assert(len(b.ddat) == 3)
        assert(b.ddat['a'].dat == 1)
        assert(b.ddat[2].dat == 2)
        assert(b.ddat[3].dat == 3)

    def test_write_dict_with_dict(self):
        """Check that we can save and restore a dictionary containing a
        dictionary"""
        l = {'a': TestWriter(1),
             2: {'c': 99, 'd': 100, 'e': TestWriter('blah')},
             3: TestWriter(3)}
        a = TestDictWriter(l)
        self.write_it('test.hdf5', a)
        b = self.read_it('test.hdf5', TestDictWriter)

        assert(isinstance(b, TestDictWriter))
        assert(isinstance(b.ddat, dict))

        assert(len(b.ddat) == 3)

        assert(b.ddat['a'].dat == 1)
        assert(isinstance(b.ddat[2], dict))
        assert(b.ddat[2]['c'] == 99)
        assert(b.ddat[2]['d'] == 100)
        assert(b.ddat[2]['e'].dat == 'blah')
        assert(b.ddat[3].dat == 3)

    def test_write_string(self):
        """Check that we can save and restore a string"""
        a = 'fijdafijdsaifjdsaifjdsaifjadsiofjasdoifjasdf'
        self.scalar_checker(a, a)

    def test_simple_object(self):
        """Check that we can save and restore a simple object"""
        from ..store import Store
        a = Store()
        self.scalar_checker(a, a)

    def test_objfromhdf5file_1(self):
        """Check that we can use obj_from_hdf5file without an explicit name"""
        from ..abstract import obj_from_hdf5file
        from ..store import Store

        s = obj_from_hdf5file(join(DATADIR, 'simplestore.hdf5'))
        assert(isinstance(s, Store))
        assert(s.extra_data['foo'] == 1)

    def test_objfromhdf5file_2(self):
        """Check that we can use obj_from_hdf5file with the correct explicit
        name"""
        from ..abstract import obj_from_hdf5file
        from ..store import Store

        s = obj_from_hdf5file(join(DATADIR, 'simplestore.hdf5'), 'store')
        assert(isinstance(s, Store))
        assert(s.extra_data['foo'] == 1)

    def test_from_hdf5file(self):
        """Check that we can use from_hdf5file properly"""
        from ..store import Store

        s = Store.from_hdf5file(join(DATADIR, 'simplestore.hdf5'), 'store')
        assert(isinstance(s, Store))
        assert(s.extra_data['foo'] == 1)

    def test_objfromhdf5file_wrongexplicitclass(self):
        """Check that we can't use obj_from_hdf5file with a the wrong explicit
        name"""
        from ..abstract import obj_from_hdf5file

        self.assertRaises(KeyError, obj_from_hdf5file,
                          join(DATADIR, 'simplestore.hdf5'), 'wrongname')

    def test_objfromhdf5file_badclassname_infile(self):
        """Check that we can't use obj_from_hdf5file with a bad class in the
        file"""
        from ..abstract import obj_from_hdf5file

        self.assertRaises(RuntimeError, obj_from_hdf5file, join(DATADIR,
                          'badclassname.hdf5'))

    def test_objfromhdf5group_1(self):
        """Check that we can use obj_from_hdf5group"""
        from ..abstract import obj_from_hdf5group
        from ..store import Store

        h = h5py.File(join(DATADIR, 'simplestore.hdf5'), 'r')
        s = obj_from_hdf5group(h['store'])
        h.close()

        assert(isinstance(s, Store))
        assert(s.extra_data['foo'] == 1)

    def test_objfromhdf5group_badclassname_ingroup(self):
        """Check that we can't use obj_from_hdf5group with a bad class in the
        group"""
        from ..abstract import obj_from_hdf5group

        h = h5py.File(join(DATADIR, 'badclassname.hdf5'), 'r')

        try:
            self.assertRaises(RuntimeError, obj_from_hdf5group, h['store'])
        finally:
            h.close()

    def test_parsehdf5value_badclassname(self):
        """Check that parse_hdf5_value fails with a bad class name"""
        from ..abstract import parse_hdf5_value

        h = h5py.File(join(DATADIR, 'badclassname.hdf5'), 'r')

        try:
            self.assertRaises(RuntimeError, parse_hdf5_value, h, 'store',
                              'store', h['store'])
        finally:
            h.close()

    def test_parsehdf5value_pythonobject(self):
        """Check that parse_hdf5_value works with a python object"""
        from ..abstract import parse_hdf5_value

        # We fake the input for this test up
        s = parse_hdf5_value(None, None, None, 'blah')
        assert(s == 'blah')

    def test_classname(self):
        """Check that we correctly check alias names"""
        from ..abstract import AbstractAnam

        class AliasNameTest(AbstractAnam):
            hdf5_aliases = ['test.this.is.an.alias']

        a = AliasNameTest()
        assert(a.check_classname('test.this.is.an.alias'))
        assert(not a.check_classname('test.this.is.not.an.alias'))


class AbstractCollectionTest(AnamTestBase):
    def write_it(self, filename, dat):
        import h5py

        f = h5py.File(join(self.tempdir, filename), 'w')
        g = f.create_group('test')
        dat.to_hdf5(g)
        f.close()

    def read_it(self, filename, cls):
        import h5py

        f = h5py.File(join(self.tempdir, filename), 'r')
        blah = cls.from_hdf5(f['test'])
        f.close()
        return blah

    def test_create_hdf5collection(self):
        """Check that we can create an empty AnamCollection"""
        from ..abstract import AnamCollection

        n = AnamCollection()
        assert(isinstance(n.members, list))
        assert(len(n.members) == 0)
        assert(len(n._cache) == 0)

    def test_create_hdf5collection_from_single_item(self):
        """Check that we can create a AnamCollection from a single item"""
        from ..abstract import AnamCollection

        item = TestArrayContainer()
        n = AnamCollection(item)

        assert(isinstance(n.members, list))
        assert(len(n.members) == 1)

    def test_create_hdf5collection_from_list(self):
        """Check that we can create a AnamCollection from a list"""
        from ..abstract import AnamCollection

        item1 = TestArrayContainer()
        item2 = TestArrayContainer()

        n = AnamCollection([item1, item2])

        assert(isinstance(n.members, list))
        assert(len(n.members) == 2)

    def test_create_hdf5collection_from_empty_list(self):
        """Check that we can create a AnamCollection from an empty list"""
        from ..abstract import AnamCollection

        n = AnamCollection([])

        assert(isinstance(n.members, list))
        assert(len(n.members) == 0)

    def test_save_restore_emptyhdf5collection(self):
        """Check that we can store and restore an empty AnamCollection"""
        from ..abstract import AnamCollection

        n = AnamCollection()
        self.write_it('test.hdf5', n)
        new = self.read_it('test.hdf5', AnamCollection)

        assert(isinstance(new.members, list))
        assert(len(new.members) == 0)
        assert(isinstance(new.anam_combine, list))
        assert(len(new.anam_combine) == 0)
        assert(len(new._cache) == 0)

    def test_save_restore_single_item_collection(self):
        """Check that we can store and restore a AnamCollection with a single
        item"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2 = arange(10, 30)

        item = TestArrayContainer(data1, data2)
        n = AnamCollection(item)

        self.write_it('test.hdf5', n)
        new = self.read_it('test.hdf5', AnamCollection)

        assert(isinstance(new.members, list))
        assert(len(new.members) == 1)
        assert(new.members[0].data1.shape == (10, ))
        assert(new.members[0].data2.shape == (20, ))

    def test_save_restore_multiple_item_collection(self):
        """Check that we can store and restore a AnamCollection with multiple
        items"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2 = arange(10, 30)

        item1 = TestArrayContainer(data1, data2)
        item2 = TestArrayContainer(data1, data2)
        n = AnamCollection([item1, item2])

        self.write_it('test.hdf5', n)
        new = self.read_it('test.hdf5', AnamCollection)

        assert(isinstance(new.members, list))
        assert(len(new.members) == 2)
        assert(new.members[0].data1.shape == (10, ))
        assert(new.members[0].data2.shape == (20, ))
        assert(new.members[1].data1.shape == (10, ))
        assert(new.members[1].data2.shape == (20, ))

    def test_update_cache_empty(self):
        """Check that we can update our cache on an empty object with no
        combine attributes"""
        from ..abstract import AnamCollection

        n = AnamCollection()
        n.update_cache()
        assert(isinstance(n._cache, dict))
        assert(len(n._cache) == 0)

    def test_update_cache_empty_with_attr(self):
        """Check that we can update our cache on an empty object with combine
        attributes"""
        from ..abstract import AnamCollection

        n = AnamCollection()
        n.anam_combine = ['testcomb']
        n.update_cache()
        assert(isinstance(n._cache, dict))
        assert(len(n._cache) == 1)
        assert('testcomb' in n._cache)
        assert(n._cache['testcomb'] is None)

    def test_clear_cache(self):
        """Check that we can clear our cache"""
        from ..abstract import AnamCollection

        n = AnamCollection()
        n.anam_combine = ['testcomb']
        n.update_cache()
        assert(isinstance(n._cache, dict))
        assert(len(n._cache) == 1)
        assert('testcomb' in n._cache)
        assert(n._cache['testcomb'] is None)
        n.clear_cache()
        assert(len(n._cache) == 0)
        assert(not ('testcomb' in n._cache))

    def test_update_cache_with_one_member(self):
        """Check that we can update our cache on a collection with one item"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2 = arange(10, 30)

        item = TestArrayContainer(data1, data2)
        n = AnamCollection(item)
        n.anam_combine = ['data1', 'data2']

        n.update_cache()

        assert(isinstance(n.members, list))
        assert(len(n.members) == 1)
        assert(n.members[0].data1.shape == (10, ))
        assert(n.members[0].data2.shape == (20, ))
        assert('data1' in n._cache)
        assert('data2' in n._cache)
        assert(n._cache['data1'].shape == (10, 1))
        assert(n._cache['data2'].shape == (20, 1))
        assert(len(list(n.keys())) == 2)
        assert('data1' in list(n.keys()))
        assert('data2' in list(n.keys()))

    def test_update_cache_with_multiple_members(self):
        """Check that we can update our cache on a collection with multiple
        items"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1a = arange(10)
        data1b = arange(10, 20)
        data2a = arange(10, 30)
        data2b = arange(20, 40)

        item1 = TestArrayContainer(data1a, data2a)
        item2 = TestArrayContainer(data1b, data2b)
        n = AnamCollection([item1, item2])
        n.anam_combine = ['data1', 'data2']

        n.update_cache()

        assert(isinstance(n.members, list))
        assert(len(n.members) == 2)
        assert(n.members[0].data1.shape == (10, ))
        assert(n.members[0].data2.shape == (20, ))
        assert(n.members[1].data1.shape == (10, ))
        assert(n.members[1].data2.shape == (20, ))
        assert('data1' in n._cache)
        assert('data2' in n._cache)
        assert(n._cache['data1'].shape == (10, 2))
        assert(n._cache['data2'].shape == (20, 2))
        assert_array_equal(n._cache['data1'][:, 0], data1a)
        assert_array_equal(n._cache['data1'][:, 1], data1b)
        assert_array_equal(n._cache['data2'][:, 0], data2a)
        assert_array_equal(n._cache['data2'][:, 1], data2b)

    def test_update_cache_with_scalars(self):
        """Check that we can update our cache on a collection when using
        scalars"""
        from ..abstract import AnamCollection

        data1a = 1.0
        data1b = 2.0
        data2a = 3
        data2b = 4

        item1 = TestArrayContainer(data1a, data2a)
        item2 = TestArrayContainer(data1b, data2b)
        n = AnamCollection([item1, item2])
        n.anam_combine = ['data1', 'data2']

        n.update_cache()

        assert(isinstance(n.members, list))
        assert(len(n.members) == 2)
        assert(n._cache['data1'].shape == (2, ))
        assert(n._cache['data2'].shape == (2, ))
        assert(n._cache['data1'][0] == 1.0)
        assert(n._cache['data1'][1] == 2.0)
        assert(n._cache['data2'][0] == 3)
        assert(n._cache['data2'][1] == 4)

    def test_update_cache_missing_attribute(self):
        """Check that we raise if an attribute is missing"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2 = arange(10, 30)

        item = TestArrayContainer(data1, data2)
        del item.data2
        n = AnamCollection(item)
        n.anam_combine = ['data1', 'data2']

        self.assertRaises(AttributeError, n.update_cache)

    def test_update_cache_missing_attribute_later_member(self):
        """Check that we raise if an attribute is missing in a later member"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2 = arange(10, 30)

        item1 = TestArrayContainer(data1, data2)
        item2 = TestArrayContainer(data1, data2)
        del item2.data2
        n = AnamCollection([item1, item2])
        n.anam_combine = ['data1', 'data2']

        self.assertRaises(AttributeError, n.update_cache)

    def test_update_cache_dtype_mismatch(self):
        """Check that we raise if an attribute mismatches in dtype"""
        from numpy import arange, complex
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2 = arange(10, 30)

        item1 = TestArrayContainer(data1, data2)
        item2 = TestArrayContainer(data1, data2)
        item2.data2 = item2.data2.astype(complex)
        n = AnamCollection([item1, item2])
        n.anam_combine = ['data1', 'data2']

        self.assertRaises(ValueError, n.update_cache)

    def test_update_cache_shape_mismatch(self):
        """Check that we raise if an attribute mismatches in shape and not
        flexible"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2a = arange(10, 30)
        data2b = arange(10, 29)

        item1 = TestArrayContainer(data1, data2a)
        item2 = TestArrayContainer(data1, data2b)
        n = AnamCollection([item1, item2])
        n.anam_combine = ['data1', 'data2']

        self.assertRaises(ValueError, n.update_cache)

    def test_update_cache_shape_mismatch_flexible(self):
        """Check that we don't raise if an attribute mismatches in shape and
        flexible"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2a = arange(10, 30)
        data2b = arange(10, 29)

        item1 = TestArrayContainer(data1, data2a)
        item2 = TestArrayContainer(data1, data2b)
        n = AnamCollection([item1, item2])
        n.anam_combine = ['data1', 'data2']

        n.update_cache(True)

        assert(n.data1.shape == (10, 2))
        assert(n.data2 is None)

    def test_update_cache_not_numpy_attribute(self):
        """Check that we raise if an attribute is not a numpy array"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1 = arange(10)
        data2 = 'test'

        item = TestArrayContainer(data1, data2)
        n = AnamCollection(item)
        n.anam_combine = ['data1', 'data2']

        self.assertRaises(AttributeError, n.update_cache)

    def test_getattr_from_cache(self):
        """Check that we can access cached attributes directly"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1a = arange(10)
        data1b = arange(10, 20)
        data2a = arange(10, 30)
        data2b = arange(20, 40)

        item1 = TestArrayContainer(data1a, data2a)
        item2 = TestArrayContainer(data1b, data2b)
        n = AnamCollection([item1, item2])
        n.anam_combine = ['data1', 'data2']

        # Check that we get a None before the cache is updated
        assert(n.data1 is None)
        n.update_cache()

        assert_array_equal(n.data1[:, 0], data1a)
        assert_array_equal(n.data1[:, 1], data1b)
        assert_array_equal(n.data2[:, 0], data2a)
        assert_array_equal(n.data2[:, 1], data2b)

    def test_list_emulation(self):
        """Check that AnamCollection's list passthrough routines work"""
        from numpy import arange
        from ..abstract import AnamCollection

        data1a = arange(10)
        data1b = arange(20, 30)
        data1c = arange(30, 40)

        data2a = arange(10, 30)
        data2b = arange(20, 40)
        data2c = arange(30, 50)

        item1 = TestArrayContainer(data1a, data2a)
        item2 = TestArrayContainer(data1b, data2b)
        item3 = TestArrayContainer(data1c, data2c)

        n = AnamCollection()
        n.anam_combine = ['data1', 'data2']

        # Test that we start with a length of 0
        assert(len(n) == 0)

        # Test that we raise an IndexError properly
        self.assertRaises(IndexError, n.__getitem__, 0)

        # Add in our first item and test for it
        n.append(item1)
        assert(len(n) == 1)
        assert(n[0] == item1)
        assert(n.count(item1) == 1)
        assert(n.count(item2) == 0)
        assert(n.index(item1) == 0)

        n.extend([item2, item3])
        assert(len(n) == 3)
        assert(n[0] == item1)
        assert(n[1] == item2)
        assert(n[2] == item3)

        assert(n.count(item1) == 1)
        assert(n.count(item2) == 1)

        assert(n.index(item1) == 0)
        assert(n.index(item2) == 1)
        assert(n.index(item3) == 2)

        assert(n.pop(1) == item2)
        assert(len(n) == 2)
        assert(n[0] == item1)
        assert(n[1] == item3)
        assert(n.pop(1) == item3)
        assert(len(n) == 1)
        assert(n[0] == item1)
        assert(n.pop(0) == item1)
        assert(len(n) == 0)

        n.append(item2)
        n.append(item3)
        n.insert(0, item1)
        assert(n[0] == item1)
        assert(n[1] == item2)
        assert(n[2] == item3)

        n.reverse()
        assert(n[0] == item3)
        assert(n[1] == item2)
        assert(n[2] == item1)

        self.assertRaises(ValueError, n.remove, 'test')

        n.remove(item3)
        assert(len(n) == 2)
        assert(n[0] == item2)
        assert(n[1] == item1)

        # Hard to actually test sort as our objects don't have a proper __eq__
        # method so just check that the length stays the same
        n.sort()
        assert(len(n) == 2)

        # Clear our list
        n.pop()
        n.pop()
        assert(len(n) == 0)

        # Test assignment via __setitem__
        n.append(item1)
        n.append(item1)
        n.append(item1)
        n[1] = item2
        assert(n[1] == item2)

        # Test assignment via __setslice__
        n[0:2] = [item2, item1]
        assert(n[0] == item2)
        assert(n[1] == item1)

        # Test getting via __getslice__
        b = n[0:2]
        assert(b[0] == item2)
        assert(b[1] == item1)

        # Test contains
        assert((item1 in n) is True)
        assert((item3 in n) is False)

        # Test deleting via __delitem__
        del n[2]
        assert(len(n) == 2)

        # Test deleting via __delslice__
        del n[0:2]
        assert(len(n) == 0)

        n.append(item1)
        n.append(item2)
        c = 0
        for k in n:
            if c == 0:
                assert(k == item1)
            else:
                assert(k == item2)
            c += 1
        assert(c == 2)


class AnamDictTest(AnamTestBase):
    def test_create_anam_dict(self):
        """Test creation of anam dict"""
        from ..abstract import AnamDict

        d = {1: 1, 2: 2}

        a = AnamDict(d)

        assert(len(list(a.data.keys())) == 2)

    def test_bad_create_anam_dict(self):
        """Test that we fail to create an AnamDict with bad data"""
        from ..abstract import AnamDict

        d = []

        self.assertRaises(ValueError, AnamDict, d)


class AnamListTest(AnamTestBase):
    def test_create_anam_list(self):
        """Test creation of anam list"""
        from ..abstract import AnamList

        d = [1, 2, 3]
        a = AnamList(d)
        assert(len(a.data) == 3)

        d = None
        a = AnamList(d)
        assert(len(a.data) == 0)

        d = 1
        a = AnamList(d)
        assert(len(a.data) == 1)


class AnamNamemapTest(AnamTestBase):
    def test_namemap_read(self):
        """Test use of namemap functionality from existing file"""
        from ..abstract import obj_from_hdf5file
        from .namemap_example import NameMapTestCase

        n = obj_from_hdf5file(join(DATADIR, 'namemap_example.hdf5'))

        assert(isinstance(n, NameMapTestCase))
        assert(n._classvarname == 'foo')

    def test_namemap_readwrite(self):
        """Test use of namemap functionality with new file"""
        import h5py
        from .namemap_example import NameMapTestCase

        n = NameMapTestCase()
        n._classvarname = 'fooblah'

        f = h5py.File(join(self.tempdir, 'testnm.hdf5'), 'w')
        n.to_hdf5(f.create_group('nmtest'))
        f.close()

        f = h5py.File(join(self.tempdir, 'testnm.hdf5'), 'r')
        assert('filevarname' in f['nmtest'].attrs)
        NameMapTestCase.from_hdf5(f['nmtest'])
        f.close()

        assert(isinstance(n, NameMapTestCase))
        assert(n._classvarname == 'fooblah')
