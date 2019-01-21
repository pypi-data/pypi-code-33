# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['another_linked_list',
 'another_linked_list.fns',
 'another_linked_list.fns.decorators',
 'another_linked_list.fns.internal']

package_data = \
{'': ['*']}

install_requires = \
['all_purpose_set>=0.1.3,<0.2.0', 'ordered_set>=3.1,<4.0', 'wrapt>=1.10,<2.0']

setup_kwargs = {
    'name': 'another-linked-list',
    'version': '0.1.0',
    'description': 'A linked list with an api and documentation more to my liking',
    'long_description': '# Another Linked List\n\n*Note: This document is best viewed [on github](https://github.com/olsonpm/py_another-linked-list).\nPypi\'s headers are all caps which presents inaccurate information*"\n\n\n<br>\n\n<!-- START doctoc generated TOC please keep comment here to allow auto update -->\n<!-- DON\'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->\n**Table of Contents**\n\n- [What is it?](#what-is-it)\n- [Why create it?](#why-create-it)\n- [Simple usage](#simple-usage)\n- [Api](#api)\n  - [class LinkedList([a list of elements])](#class-linkedlista-list-of-elements)\n    - [Attributes](#attributes)\n    - [Methods](#methods)\n  - [node](#node)\n- [Test](#test)\n\n<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n\n<br>\n\n### What is it?\n\n- An incomprehensive implementation of a doubly-linked list\n\n<br>\n\n### Why create it?\n\n- I didn\'t like the api or documentation of other linked lists.  I\'m also new\n  to python so this was a good way to learn.\n\n<br>\n\n### Simple usage\n\n```py\nfrom another_linked_list import LinkedList\n\n# create a list with three nodes\nll = LinkedList(["a", "b", "d"])\n\n# get the node with element "b"\nbNode = ll.findFirstNode("b")\n\n# insert "c" after bNode\nll.insertAfter(bNode, "c")\n\nprint(list(ll))\n# prints [\'a\', \'b\', \'c\', \'d\']\n```\n\n<br>\n\n### Api\n\n#### class LinkedList([a list of elements])\n- the linked list holds a list of [nodes](#node).  Each node holds an element\n  (the value) along with pointers to the previous and next nodes.  For the most\n  part the methods are intended to allow you to work with the elements moreso\n  than the nodes because that was my use-case.  This design decision may change\n  in the future to be more focused around the nodes.\n- all methods return `self` unless specified otherwise\n- all methods which take a list argument also accept an instance of LinkedList\n- in all code examples below, assume `ll` starts with `LinkedList(["a", "c"])`\n- the internal methods implemented are\n  - \\_\\_copy\\_\\_\n  - \\_\\_iter\\_\\_ (iterates over the elements, **not** the nodes)\n  - \\_\\_len\\_\\_\n  - \\_\\_reversed\\_\\_\n\n<br>\n\n#### Attributes\n\n##### firstNode: [node](#node)\n```py\nprint(ll.firstNode.element) # a\n```\n##### lastNode: [node](#node)\n```py\nprint(ll.lastNode.element) # c\n```\n\n<br>\n\n#### Methods\n\n##### append(element)\n```py\nll.append(\'d\')\nprint(list(ll)) # [\'a\', \'c\', \'d\']\n```\n\n##### copy() => LinkedList\n\n##### appendAll(list)\n```py\nll.appendAll([\'d\', \'e\'])\nprint(list(ll)) # [\'a\', \'c\', \'d\', \'e\']\n```\n\n##### findFirstNode(element) => [node](#node)\n```py\ncNode = ll.findFirstNode([\'c\'])\nprint(cNode.element) # c\n```\n\n##### insertAfter([node](#node), element)\n```py\nll.insertAfter(ll.firstNode, \'b\')\nprint(list(ll)) # [\'a\', \'b\', \'c\']\n```\n\n##### insertAllAfter([node](#node), list)\n```py\nll.insertAllAfter(ll.firstNode, [\'b\', \'d\'])\nprint(list(ll)) # [\'a\', \'b\', \'d\', \'c\']\n```\n\n##### insertAllBefore([node](#node), list)\n```py\nll.insertAllBefore(ll.lastNode, [\'b\', \'d\'])\nprint(list(ll)) # [\'a\', \'b\', \'d\', \'c\']\n```\n\n##### insertBefore([node](#node), element)\n```py\nll.insertBefore(ll.lastNode, \'b\')\nprint(list(ll)) # [\'a\', \'b\', \'c\']\n```\n\n##### prepend(element)\n```py\nll.prepend(\'z\')\nprint(list(ll)) # [\'z\', \'a\', \'c\']\n```\n\n##### prependAll(list)\n```py\nll.prependAll([\'y\', \'z\'])\nprint(list(ll)) # [\'y\', \'z\', \'a\', \'c\']\n```\n\n##### removeFirstElement(element)\n```py\nll.removeFirstElement(\'c\')\nprint(list(ll)) # [\'a\']\n```\n\n##### removeNode([node](#node))\n```py\nll.removeNode(ll.firstNode)\nprint(list(ll)) # [\'c\']\n```\n\n<br>\n\n#### node\n- a node is just an instance of SimpleNamespace with three attributes\n  - **element**: &lt;can be anything&gt;\n  - **next_**: node\n  - **previous**: node\n\n```py\nprint(ll.firstNode.element) # a\nprint(ll.firstNode.next_.element) # c\nprint(ll.lastNode.previous.element) # a\nprint(ll.firstNode.previous is None) # True\n```\n\n<br>\n\n### Test\n\n```sh\n#\n# you must have poetry installed\n#\n$ poetry shell\n$ poetry install\n$ python runTests.py\n```\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_another-linked-list',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
