"""
*hynet* package configuration.

Parameters
----------
GENERAL : dict
    General settings.

    ``parallelize``: (``bool``)
        Enable or disable parallel processing in *hynet*. If True, certain
        procedures (e.g., the construction of constraint matrices for the OPF
        formulation) are parallelized if the system features more than one CPU.

OPF : dict
    Optimal power flow settings.

    ``copper_plate_init``: (``bool``)
        Enable or disable the computation of a copper plate based initial point
        for the solution of the nonconvex QCQP. By default, this is enabled if
        MOSEK is installed and disabled otherwise. For the currently supported
        solvers, only MOSEK provides sufficient performance such that the
        computation of the initial point improves overall performance, i.e.,
        that the reduced number of iterations of the QCQP solver outweighs the
        computational cost for the initial point.
    ``pathological_price_profile_info``: (``bool``)
        Enable or disable the output of information about pathological price
        profiles under the hybrid architecture in the OPF summary. See also
        ``OPFResult`` and ``Scenario.has_hybrid_architecture``.

DISTRIBUTED : dict
    Settings for distributed computation.

    ``default_port``: (``int``)
        Default optimization server TCP port.
    ``default_authkey``: (``str``)
        Default optimization server authentication key.
    ``default_num_workers``: (``int``)
        Default number of worker processes on an optimization client.
    ``ssh_command``: (``str``)
        Command to run SSH on the local machine.
    ``python_command``: (``str``)
        Command to run Python on client machines.
"""

from hynet.utilities.base import validate_mosek_license


GENERAL = {
    'parallelize': True
}

OPF = {
    'copper_plate_init': validate_mosek_license(),
    'pathological_price_profile_info': True
}

DISTRIBUTED = {
    'default_port': 1235,
    'default_authkey': 'hynet',
    'default_num_workers': 1,
    'ssh_command': 'ssh',
    'python_command': 'python'
}
