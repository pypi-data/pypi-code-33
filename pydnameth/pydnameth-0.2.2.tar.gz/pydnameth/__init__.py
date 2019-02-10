# -*- coding: utf-8 -*-

"""Top-level package for pydnameth."""
# flake8: noqa

__author__ = """Aaron Blare"""
__email__ = 'aaron.blare@mail.ru'
__version__ = '0.2.2'

from .config.config import Config
from .config.common import CommonTypes
from .config.annotations.annotations import Annotations
from .config.annotations.types import AnnotationKey
from .config.annotations.types import Exclude, CrossReactive, SNP, Chromosome, GeneRegion, Geo, ProbeClass
from .config.attributes.attributes import Cells, Observables, Attributes
from .config.data.data import Data
from .config.data.types import DataPath, DataBase
from .config.experiment.experiment import Experiment
from .config.experiment.types import DataType, Task, Method
from pydnameth.scripts.release import \
    cpg_proc_table_linreg, \
    cpg_proc_table_variance_linreg, \
    cpg_proc_table_polygon, \
    cpg_proc_table_z_test_linreg, \
    cpg_proc_clock_linreg, \
    cpg_plot_methylation_scatter, \
    attributes_plot_observables_histogram
from pydnameth.scripts.develop import \
    cpg_proc_table_linreg_dev, \
    cpg_proc_table_variance_linreg_dev, \
    cpg_proc_table_polygon_dev, \
    cpg_proc_table_z_test_linreg_dev, \
    cpg_proc_clock_linreg_dev, \
    cpg_proc_special_clock_linreg_dev, \
    cpg_plot_methylation_scatter_dev, \
    attributes_plot_observables_histogram_dev
from pydnameth.routines.clock.types import ClockExogType
