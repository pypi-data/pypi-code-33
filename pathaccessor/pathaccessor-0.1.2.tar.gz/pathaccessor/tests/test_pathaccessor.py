from unittest import TestCase
import re
from pathaccessor.impl import (
    MappingPathAccessor,
    MappedAttrsPathAccessor,
    PathAccessorBase,
    SequencePathAccessor,
)


class BaseMixin (object):
    TargetClass = PathAccessorBase
    Key = 'weapon'
    Elem = 'sword'
    GetItemError = KeyError

    def getValue(self):
        return {
            'weapon': 'sword',
            'armor': 'leather',
            'get': 'got',  # Important case for MappedAttrs
        }

    def setUp(self):
        self.value = self.getValue()
        self.target = self.TargetClass(self.value, 'ROOT')

    def test_del(self):
        startlen = len(self.target)
        del self.target[self.Key]
        endlen = len(self.target)
        self.assertEqual(startlen - 1, endlen)

    def test_len(self):
        self.assertEqual(len(self.value), len(self.target))

    def test_repr(self):
        expected = "<{} ROOT {}>".format(
            self.TargetClass.__name__,
            repr(self.value),
        )
        actual = repr(self.target)
        self.assertEqual(expected, actual)

    def test_getitem(self):
        self.assertEqual(self.Elem, self.target[self.Key])

    def test_setitem(self):
        self.target[self.Key] = 'polyester'
        self.assertEqual('polyester', self.target[self.Key])

    def test_getitem_missing(self):
        self.assertRaisesRegexp(
            self.GetItemError,
            r"^<[A-Za-z]+PathAccessor ROOT [^>]+> has no member 42$",
            self.target.__getitem__,
            42,
        )


class MappingPathAccessorTests (BaseMixin, TestCase):
    TargetClass = MappingPathAccessor

    def test_keys(self):
        self.assertEqual({'weapon', 'armor', 'get'}, set(self.target.keys()))

    def test_get(self):
        self.assertEqual('sword', self.target.get('weapon'))
        self.assertEqual(None, self.target.get('hat'))
        self.assertEqual('gru', self.target.get('sidekick', 'gru'))

    def test_update(self):
        self.target.update({'hat': 'wizard', 'belt': 'cowboy'})
        expectedkeys = {'weapon', 'armor', 'get', 'hat', 'belt'}
        self.assertEqual(expectedkeys, set(self.target.keys()))


class MappedAttrsPathAccessorTests (BaseMixin, TestCase):
    TargetClass = MappedAttrsPathAccessor

    def test_attribute_access_versus_getitem(self):
        self.assertEqual('leather', self.target.armor)
        self.assertEqual('leather', self.target['armor'])

    def test_tricky_attribute_access(self):
        thing1 = self.target.get
        thing2 = self.target['get']
        self.assertEqual('got', thing1)
        self.assertEqual(thing1, thing2)

    def test_setattr_versus_setitem(self):
        self.target.hat = 'wizard'
        self.assertEqual('wizard', self.target.hat)
        self.assertEqual('wizard', self.target['hat'])

        self.target['hat'] = 'tophat'
        self.assertEqual('tophat', self.target.hat)
        self.assertEqual('tophat', self.target['hat'])

    def test_mapa_to_mapping_interface(self):
        # If you need a Mapping interface use this API:
        mpa = MappingPathAccessor.fromMappedAttrs(self.target)
        self.assertEqual('leather', mpa.get('armor'))
        self.assertEqual('got', mpa.get('get'))
        self.assertEqual('banana', mpa.get('fruit', 'banana'))


class SequencePathAccessorTests (BaseMixin, TestCase):
    TargetClass = SequencePathAccessor
    Key = 1
    Elem = 'b'
    GetItemError = IndexError

    def getValue(self):
        return ['a', 'b', 'c']

    def test_insert(self):
        self.target.insert(2, 'X')
        self.assertEqual(['a', 'b', 'X', 'c'], self.value)


class CompoundStructureTests (TestCase):
    def assertRaisesLiteral(self, exc, msg, f, *args, **kw):
        self.assertRaisesRegexp(
            exc,
            '^{}$'.format(re.escape(msg)),
            f,
            *args,
            **kw
        )

    def setUp(self):
        self.structure = {'a': [{"foo": [None, [], 1337]}]}

    def test_mapping_access_success(self):
        mpa = MappingPathAccessor(self.structure, 'ROOT')
        elem = mpa['a'][0]['foo'][2]
        self.assertEqual(1337, elem)

    def test_mappedattrs_access_success(self):
        mpa = MappedAttrsPathAccessor(self.structure, 'ROOT')
        elem = mpa.a[0].foo[2]
        self.assertEqual(1337, elem)

    def test_mapping_access_error(self):
        mpa = MappingPathAccessor(self.structure, 'ROOT')
        child = mpa['a'][0]['foo'][1]
        self.assertRaisesLiteral(
            TypeError,
            ("Index 'bananas' of "
             + "<SequencePathAccessor ROOT['a'][0]['foo'][1] []>"
             + " not an integer"),
            child.__getitem__,
            'bananas',
        )

    def test_mappedattrs_access_error(self):
        mapa = MappedAttrsPathAccessor(self.structure, 'ROOT')
        child = mapa['a'][0].foo[1]
        self.assertRaisesLiteral(
            TypeError,
            ("Index 'bananas' of "
             + "<SequencePathAccessor ROOT['a'][0].foo[1] []>"
             + " not an integer"),
            child.__getitem__,
            'bananas',
        )

    def test_compound_write_mappedattrs(self):
        mapa = MappedAttrsPathAccessor(self.structure, 'ROOT')
        mapa.a[0].bar = 'banana'

        self.assertEqual(
            {
                'a': [{
                    "foo": [None, [], 1337],
                    "bar": 'banana',
                }],
            },
            self.structure,
        )

    def test_compound_write_sequence(self):
        mapa = MappedAttrsPathAccessor(self.structure, 'ROOT')
        mapa.a[0].foo[0] = 'banana'

        self.assertEqual(
            {
                'a': [{
                    "foo": ['banana', [], 1337],
                }],
            },
            self.structure,
        )
