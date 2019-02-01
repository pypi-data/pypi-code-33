"""
Package that simplifies Azure deployment (creating forecasting web services).

Forecasters are created as AzureML web services. These utilities automate 
the data scientist's tasks involved in building web services from 
forecasting pipelines. 
"""
from .score_context import ScoreContext
from .score_script_helper import execute_pipeline_operation
from .dnnscorecontext import DnnScoreContext
from .storage_context import (StorageContext, LocalStorageContext,
                              AzureBlobStorageContext)
