"""
Support for scaling forecasting out to multiple cores, CPUs and machines. 
Currently supported methods only include the local thread and process clusters and can be used in notebooks.

Experimental stage facilities are provided for BatchAI.

"""

from .compute_base import (ComputeStrategyMixin, ComputeBase)
from .scale_up_compute import (JoblibParallelCompute, ConcurrentFuturesCompute)
from .scale_out_compute import DaskDistributedCompute
from .aml_compute import AMLBatchAICompute
from .scheduler import Scheduler
