"""
Plotting: PL
============

.. automodule:: scanpy

.. note::

    See the :ref:`settings` section for all important plotting configurations.


Generic
-------

.. autosummary::
   :toctree: .

   pl.scatter
   pl.heatmap
   pl.dotplot
   pl.violin
   pl.stacked_violin
   pl.matrixplot
   pl.clustermap
   pl.ranking


Preprocessing
-------------

Methods for visualizing quality control and results of preprocessing functions.

.. autosummary::
   :toctree: .

   pl.highest_expr_genes
   pl.filter_genes_dispersion


Tools
-----

Methods that extract and visualize tool-specific annotation in an
:class:`~anndata.AnnData` object.  For any method in module ``tl``, there is
a method with the same name in ``pl``.

**PCA**

.. autosummary::
   :toctree: .

   pl.pca
   pl.pca_loadings
   pl.pca_variance_ratio
   pl.pca_overview

**Embeddings**

.. autosummary::
   :toctree: .

   pl.tsne
   pl.umap
   pl.diffmap
   pl.draw_graph
   pl.phate

**Branching trajectories and pseudotime, clustering**

Visualize clusters using one of the embedding methods passing ``color='louvain'``.

.. autosummary::
   :toctree: .

   pl.dpt_groups_pseudotime
   pl.dpt_timeseries
   pl.paga
   pl.paga_path
   pl.paga_compare

**Marker genes**

.. autosummary::
   :toctree: .

   pl.rank_genes_groups
   pl.rank_genes_groups_violin
   pl.rank_genes_groups_stacked_violin
   pl.rank_genes_groups_heatmap
   pl.rank_genes_groups_dotplot
   pl.rank_genes_groups_matrixplot


**Simulations**

.. autosummary::
   :toctree: .

   pl.sim
"""

from .anndata import scatter, violin, ranking, clustermap, stacked_violin, heatmap, dotplot, matrixplot, tracksplot

from .preprocessing import filter_genes_dispersion, highly_variable_genes

from .tools.scatterplots import pca, diffmap, draw_graph, tsne, phate, umap
from .tools import pca_loadings, pca_scatter, pca_overview, pca_variance_ratio
from .tools.paga import paga, paga_adjacency, paga_compare, paga_path
from .tools import dpt_timeseries, dpt_groups_pseudotime
from .tools import rank_genes_groups, rank_genes_groups_violin
from .tools import rank_genes_groups_dotplot, rank_genes_groups_heatmap, rank_genes_groups_stacked_violin, rank_genes_groups_matrixplot, rank_genes_groups_tracksplot
from .tools import sim

from .rcmod import set_rcParams_scanpy, set_rcParams_defaults
from . import palettes

from .utils import matrix
from .utils import timeseries, timeseries_subplot, timeseries_as_heatmap

from .qc import highest_expr_genes
