# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The hyperdrive package contains the modules supporting hyperparameter tuning.

HyperDrive automates the process of running hyperparameter sweeps for an experiment.  Various sampling methods
are supported in conjunction with a suite of early termination policies allowing poor performing experiment runs
to be cancelled and new ones to be started.
"""
from .policy import BanditPolicy, MedianStoppingPolicy, NoTerminationPolicy, TruncationSelectionPolicy, \
    EarlyTerminationPolicy
from .run import HyperDriveRun, PrimaryMetricGoal
from .sampling import RandomParameterSampling, GridParameterSampling, BayesianParameterSampling, HyperParameterSampling
from .parameter_expressions import choice, randint, uniform, quniform, loguniform, \
    qloguniform, normal, qnormal, lognormal, qlognormal
from .runconfig import HyperDriveRunConfig

__all__ = ["BanditPolicy", "MedianStoppingPolicy", "NoTerminationPolicy", "TruncationSelectionPolicy",
           "EarlyTerminationPolicy", "HyperDriveRun", "HyperDriveRunConfig",
           "RandomParameterSampling", "GridParameterSampling", "BayesianParameterSampling", "HyperParameterSampling",
           "choice", "randint", "uniform", "quniform", "loguniform",
           "qloguniform", "normal", "qnormal", "lognormal", "qlognormal",
           "PrimaryMetricGoal"]
