import pytest
from conficus.structs import ListNode, DoubleLinkedDict


@pytest.fixture
def node_list():
    node = ListNode('first', 0)
    node2 = ListNode('second', 1)
    node3 = ListNode('three', 2)

    node.append(node2).append(node3)

    return (node, node2, node3)


def test_list_node_init():
    node = ListNode('first', 0)
    assert node.name == 'first'
    assert node.content == 0
    assert node.previous is None
    assert node.next is None
    assert node.is_root is False
    assert node.is_tail is False
    assert node.unlinked


def test_list_node_append():
    node = ListNode('first', 0)
    node2 = ListNode('second', 1)
    node.append(node2)

    assert node.previous is None
    assert node.is_root
    assert node.is_tail is False
    assert node.unlinked is False
    assert node.next is node2

    assert node2.previous is node
    assert node2.next is None
    assert node2.is_tail
    assert node2.is_root is False
    assert node2.unlinked is False

    node3 = ListNode('beta', 10)
    node.append(node3)

    assert node.next is node3
    assert node2.previous is node3


def test_list_node_prepend():
    node = ListNode('first', 0)
    node2 = ListNode('second', 1)
    node.prepend(node2)

    assert node.previous is node2
    assert node.is_root is False
    assert node.is_tail
    assert node.unlinked is False
    assert node.next is None

    assert node2.previous is None
    assert node2.next is node
    assert node2.is_tail is False
    assert node2.is_root is True
    assert node2.unlinked is False


def test_list_node_replace():
    node = ListNode('first', 0)
    node2 = ListNode('second', 1)

    node.replace(node2)

    assert node.name == node2.name
    assert node.content == node2.content
    assert node == node2
    assert node is not node2


def test_list_node_remove_unlinked():
    node = ListNode('first', 0)
    assert node.unlinked
    node.remove()
    assert node.unlinked


def test_list_node_list(node_list):
    node, node2, node3 = node_list

    assert node.is_root
    assert node2.is_root is False
    assert node2.is_tail is False
    assert node3.is_tail


def test_list_node_remove_root(node_list):
    node, node2, node3 = node_list

    node.remove()

    assert node.unlinked
    assert node2.is_root
    assert node3.is_tail


def test_list_node_remove_tail(node_list):
    node, node2, node3 = node_list

    node3.remove()

    assert node3.unlinked
    assert node2.is_tail
    assert node.is_root


def test_list_node_remove_middle(node_list):
    node, node2, node3 = node_list

    node2.remove()

    assert node.is_root
    assert node3.is_tail

    assert node.next is node3
    assert node3.previous is node


@pytest.fixture
def dld():
    return DoubleLinkedDict(('first', 0), ('second', 1), ('third', 2))


def test_double_linked_dict():
    dld = DoubleLinkedDict()
    assert len(dld) == 0


def test_double_linked_dict_init(dld):
    assert len(dld) == 3
    assert dld.root.name == 'first'
    assert dld.tail.name == 'third'


def test_double_linked_dict_append(dld):
    dld.append('fourth', 3)

    assert len(dld) == 4
    assert dld.tail.name == 'fourth'
    assert dld.tail.previous.name == 'third'


def test_double_linked_dict_prepend(dld):
    dld.prepend('alpha', -1)

    assert len(dld) == 4
    assert dld.root.name == 'alpha'
    assert dld.root.next.name == 'first'

    dld2 = DoubleLinkedDict()

    dld2.prepend('one', 2)

    assert dld2.tail is dld2['one']
    assert dld2['one'].is_tail is False


def test_double_linked_dict_insert_before(dld):
    dld.insert_before('first', 'alpha', -1)

    assert len(dld) == 4
    assert dld.root.name == 'alpha'
    assert dld.root.next.name == 'first'

    assert dld['alpha'].name == 'alpha'
    assert dld['alpha'].is_root

    assert dld['first'].is_root is False

    dld.insert_before('third', 'beta', 10)

    dld['second'].next is dld['beta']
    dld['third'].previous is dld['beta']


def test_double_linked_dict_insert_after(dld):
    dld.insert_after('third', 'beta', 10)

    assert len(dld) == 4
    assert dld.tail.name == 'beta'
    assert dld.tail.previous.name == 'third'

    assert dld['beta'].name == 'beta'
    assert dld['beta'].is_tail is True
    assert dld['third'].is_tail is False

    dld.insert_after('third', 'delta', 20)
    assert dld['third'].next is dld['delta']
    assert dld['beta'].previous is dld['delta']


def test_double_linked_dict_replace(dld):

    node = dld['second']

    assert dld['second'].content == 1
    assert dld['second'] is node

    dld.replace('second', 500)

    assert dld['second'].content == 500
    assert dld['second'] is node


def test_double_linked_dict_iter_names(dld):
    dld.prepend('alpha', -1)
    dld.append('omega', 100)
    dld.insert_after('second', 'beta', 10)

    names = [a for a in dld.iter_names()]

    assert names == ['alpha',
                     'first',
                     'second',
                     'beta',
                     'third',
                     'omega']


def test_double_linked_dict_iter_values(dld):
    dld.prepend('alpha', -1)
    dld.append('omega', 100)
    dld.insert_after('second', 'beta', 10)

    values = [a for a in dld.iter_values()]

    assert values == [-1, 0, 1, 10, 2, 100]


def test_list_node_repr():
    node = ListNode('name', 1)
    assert repr(node) == '<ListNode "name">'
