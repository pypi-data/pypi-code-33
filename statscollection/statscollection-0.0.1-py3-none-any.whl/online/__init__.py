#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=================
The online module
=================

.. currentmodule:: statscollection.online 


The following classes are available for online computations on data streams, i.e. any iterable object in Python.

Table of contents
-----------------

Online algorithmsm for summary statistics.

.. autosummary::
   :nosignatures:

   ~statscollection.online.classes.Mean
   ~statscollection.online.classes.Min
   ~statscollection.online.classes.Min
   
   
Online algorithmsm for sampling.

.. autosummary::
   :nosignatures:

   ~statscollection.online.sampling.Sample
   

The API
-------

The classes in this module share a common api, illustrated in the following example.

.. doctest::

    >>> from statscollection.online import Mean
    >>> mean = Mean().fit(2.0)  # Fit a single item
    >>> print(mean.evaluate())
    2.0
    >>> mean = mean.fit(iter([5.0, 2.0]))  # Fit an iterable object
    >>> print(mean.evaluate())
    3.0

It's possible to...

.. doctest::

    >>> for result in Mean().yield_from(iter([1.0, 3.0, 5.0])):
    ...     print(result)
    1.0
    2.0
    3.0












End of example.

.. code-block:: python
   :linenos:

   # Create a stream of data. This could be an array, data from a file, etc...
   import random
   stream = (random.random() for i in range(1000000))

   mean = Mean()

   # Fit a single element, or several elements
   mean.fit(next(stream))


Now a doctest.

.. doctest::

   >>> from statscollection.online import Mean
   >>> mean = Mean().fit(2.0)
   >>> print(mean.evaluate())
   2.0




Start of test.
>>> 1 + 1
2


End of api.

test
----

Start of todo.




TODO

- :class:`~statscollection.online.classes.Mean` : Compute the mean.


.. autoclass:: statscollection.online.classes.Mean
   :no-members:

TODO


.. autofunction:: statscollection.online.classes.Mean


TODO.

.. automodule:: statscollection.online.classes
   :members:
   :inherited-members:
       
       
.. automodule:: statscollection.online.sampling
   :members:
   :inherited-members:
       
       
.. automodule:: statscollection.online.abstract_classes
   :members:
   :inherited-members:



"""
from .classes import Mean, Max, Min
from .sampling import Sample

Mean = Mean
Max = Max
Min = Min
Sample = Sample
