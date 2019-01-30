# -*- coding: utf-8 -*-

"""A PyBEL [1]_ extension for building BEL resources with the EBI [2]_ Ontology Lookup Service.

References
----------
.. [1] Hoyt, C. T., *et al.* (2017). `PyBEL: a Computational Framework for Biological Expression Language
       <https://doi.org/10.1093/bioinformatics/btx660>`_. Bioinformatics, 34(December), 1–2.

.. [2] Cote, R., *et al.* (2006). `The Ontology Lookup Service, a lightweight cross-platform tool for controlled
       vocabulary queries <https://doi.org/10.1186/1471-2105-7-97>`_. BMC Bioinformatics, 7, 1–7.

Installation
------------
Get the Latest
~~~~~~~~~~~~~~~
Download the most recent code from `GitHub <https://github.com/pybel/pybel-ols>`_ with:

.. code-block:: sh

   $ pip install git+https://github.com/pybel/pybel-ols.git

For Developers
~~~~~~~~~~~~~~
Clone the repository from `GitHub <https://github.com/pybel/pybel-ols>`_ and install in editable mode with:

.. code-block:: sh

   $ git clone https://github.com/pybel/pybel-ols.git
   $ cd pybel-ols
   $ pip install -e .

"""

from .ols_utils import (
    OlsAnnotationOntology, OlsConstrainedAnnotationOntology, OlsConstrainedNamespaceOntology,
    OlsConstrainedOntology, OlsNamespaceOntology, OlsOntology,
)

__all__ = [
    'OlsOntology',
    'OlsNamespaceOntology',
    'OlsAnnotationOntology',
    'OlsConstrainedOntology',
    'OlsConstrainedNamespaceOntology',
    'OlsConstrainedAnnotationOntology',
]
