"""
Calculation of the optimal power flow.
"""

import logging

import numpy as np

from hynet.types_ import hynet_float_, SolverType, SolverStatus
from hynet.solver import AVAILABLE_SOLVERS
from hynet.data.connection import DBConnection
from hynet.data.interface import load_scenario
from hynet.scenario.representation import Scenario
from hynet.model.steady_state import SystemModel
from hynet.qcqp.solver import SolverInterface
from hynet.qcqp.problem import QCQPPoint, QCQP
from hynet.utilities.base import Timer
from hynet.reduction.copper_plate import reduce_to_copper_plate
import hynet.config as config

_log = logging.getLogger(__name__)


def calc_opf(data, scenario_id=0, solver=None, solver_type=None):
    """
    Calculate the optimal power flow.

    This function formulates and solves the optimal power flow (OPF) problem.
    The solver or solver type may be specified explicitly, otherwise an
    appropriate solver is selected automatically.

    **Custom OPF Formulations:** For a customization of the standard OPF
    formulation, please refer to the docstring of ``SystemModel``.

    **Copper Plate Models:** *hynet* supports the simulation of "copper plate
    models", i.e., when the grid model is neglected all injectors and
    loads are connected to a single bus. As such models exhibit the *hybrid
    architecture*, all solver types (QCQP, SDR, and SOCR) are applicable. The
    grid model of a scenario can be reduced to a copper plate using
    ``reduce_to_copper_plate``.

    Parameters
    ----------
    data : DBConnection or Scenario or SystemModel
        Connection to a *hynet* grid database, a ``Scenario`` object, or a
        ``SystemModel`` object.
    scenario_id : .hynet_id_, optional
        Identifier of the scenario. This argument is ignored if ``data`` is a
        ``Scenario`` or ``SystemModel`` object.
    solver : SolverInterface, optional
        Solver for the QCQP problem; the default selects an appropriate
        solver of those available.
    solver_type : SolverType, optional
        Optional solver type for the QCQP problem, i.e., if passed it restricts
        the automatic solver selection to this type. It is ignored if
        ``solver`` is not ``None``.

    Returns
    -------
    result : OPFResult
        Optimal power flow solution.

    See Also
    --------
    hynet.scenario.representation.Scenario
    hynet.opf.result.OPFResult
    hynet.types_.SolverType
    hynet.model.steady_state.SystemModel
    hynet.reduction.copper_plate.reduce_to_copper_plate
    """
    timer = Timer()
    if isinstance(data, SystemModel):
        model = data
    elif isinstance(data, Scenario):
        model = SystemModel(data)
    elif isinstance(data, DBConnection):
        model = SystemModel(load_scenario(data, scenario_id))
    else:
        raise ValueError(("The argument 'data' must be a database file name, "
                          "a Scenario object, or a SystemModel object."))

    if solver is None:
        solver = select_solver(model, solver_type)()
    elif not isinstance(solver, SolverInterface):
        raise ValueError("The solver must be a SolverInterface-derived object.")

    if solver.type == SolverType.SDR and model.dim_v > 500:
        _log.warning("Solving the SDR for this large system potentially "
                     "requires an excessive amount of time.")

    _log.debug("Calculate OPF ~ Loading, verification, and solver selection "
               "({:.3f} sec.)".format(timer.interval()))
    timer.reset()

    qcqp = model.get_opf_problem()

    if solver.type == SolverType.QCQP and model.dim_v > len(model.islands):
        # Support the solver with an appropriate initial point
        if config.OPF['copper_plate_init']:
            qcqp.initial_point = get_copper_plate_initial_point(model, qcqp)

    _log.debug("Calculate OPF ~ QCQP creation ({:.3f} sec.)"
               .format(timer.interval()))

    result = solver.solve(qcqp)
    return model.create_opf_result(result, total_time=timer.total())


def get_relaxation_initial_point(model, qcqp, solver_type):
    """
    Return a relaxation-based initial point for the given OPF QCQP.

    This method returns an initial point for the solution of the OPF QCQP that
    corresponds to a relaxation of the OPF. Especially the second-order cone
    relaxation (SOCR solvers) is typically fast to compute and may be suitable.
    However, in our experience with meshed grids, only in very rare cases the
    SOCR-based initialization turned out to be superior to a copper plate based
    initialization.

    Parameters
    ----------
    model : SystemModel
        Steady-state system model, for which the OPF shall be calculated.
    qcqp : QCQP
        QCQP for the OPF of the given model, for which the initial point
        shall be determined.
    solver_type : SolverType
        Solver type that shall be used to compute the initial point.

    Returns
    -------
    initial_point : QCQPPoint or None
        Relaxation-based initial point for the given OPF QCQP. In case the
        solution failed or no appropriate solver was found, None is returned.
    """
    timer = Timer()
    initial_point = None
    try:
        solver = select_solver(model, solver_type)()
        result = solver.solve(qcqp)
        if result.solver_status != SolverStatus.SOLVED:
            raise RuntimeError("OPF failed with status '"
                               + str(result.solver_status) + "'.")
        initial_point = result.optimizer.scale(qcqp.normalization)
    except RuntimeError as exception:
        _log.warning("{0}-based initialization failed: {1}"
                     .format(solver_type.value, str(exception)))
    _log.debug("{0}-based initial point calculation ({1:.3f} sec.)"
               .format(solver_type.value, timer.total()))
    return initial_point


def get_copper_plate_initial_point(model, qcqp):
    """
    Return a copper plate based initial point for the given OPF QCQP.

    This method returns an initial point for the solution of the OPF QCQP that
    includes the optimal dispatch of the copper plate reduction of the model.
    The copper plate solution is typically fast to compute and can reduce the
    number of iterations required to solve the nonconvex QCQP, i.e., it can
    improve the overall performance when solving the nonconvex problem.

    Parameters
    ----------
    model : SystemModel
        Steady-state system model, for which the OPF shall be calculated.
    qcqp : QCQP
        QCQP for the OPF of the given model, for which the initial point
        shall be determined.

    Returns
    -------
    initial_point : QCQPPoint or None
        Copper plate model based initial point for the given OPF QCQP. In case
        the solution failed or no SOCR solver was found, None is returned.
    """
    timer = Timer()
    initial_point = None
    try:
        cp = SystemModel(reduce_to_copper_plate(model.scenario),
                         verify_scenario=False)
        cp_solver = select_solver(cp, SolverType.SOCR)()
        cp_result = cp_solver.solve(cp.get_opf_problem())
        if cp_result.solver_status != SolverStatus.SOLVED:
            raise RuntimeError("OPF failed with status '"
                               + str(cp_result.solver_status) + "'.")
        initial_point = QCQPPoint(v=0.35 * qcqp.lb.v + 0.65 * qcqp.ub.v,
                                  f=np.zeros(qcqp.dim_f, dtype=hynet_float_),
                                  s=cp_result.optimizer.s * qcqp.normalization.s,
                                  z=np.zeros(qcqp.dim_z, dtype=hynet_float_))
    except RuntimeError as exception:
        _log.warning("Copper plate initialization failed: " + str(exception))
    _log.debug("Copper plate initial point calculation ({:.3f} sec.)"
               .format(timer.total()))
    return initial_point


def select_solver(model, solver_type=None):
    """
    Return the most appropriate solver of those available for the given conditions.

    Parameters
    ----------
    model : SystemModel
        Steady state model for which the OPF shall be calculated.
    solver_type : SolverType, optional
        Specification of the solver type. By default, the most appropriate
        among all available solver types is selected.

    Returns
    -------
    solver : SolverInterface
        Selected solver interface *class*.

    Raises
    ------
    RuntimeError
        In case no appropriate solver was found.
    """
    if not AVAILABLE_SOLVERS:
        raise RuntimeError("No supported solvers were found.")

    qcqp_solvers = [x for x in AVAILABLE_SOLVERS if x().type == SolverType.QCQP]
    sdr_solvers = [x for x in AVAILABLE_SOLVERS if x().type == SolverType.SDR]
    socr_solvers = [x for x in AVAILABLE_SOLVERS if x().type == SolverType.SOCR]

    if solver_type is not None:
        if solver_type == SolverType.QCQP:
            if qcqp_solvers:
                solver = qcqp_solvers[0]
            else:
                raise RuntimeError("No supported QCQP solvers were found.")
        elif solver_type == SolverType.SDR:
            if sdr_solvers:
                solver = sdr_solvers[0]
            else:
                raise RuntimeError("No supported SDR solvers were found.")
        elif solver_type == SolverType.SOCR:
            if socr_solvers:
                solver = socr_solvers[0]
            else:
                raise RuntimeError("No supported SOCR solvers were found.")
        else:
            raise ValueError("The solver type must be a SolverType member.")
    else:
        if model.has_hybrid_architecture:
            # For the hybrid architecture, choose the most efficient solver
            if socr_solvers:
                solver = socr_solvers[0]
            elif sdr_solvers:
                solver = sdr_solvers[0]
            else:
                solver = qcqp_solvers[0]
        else:
            if qcqp_solvers:
                solver = qcqp_solvers[0]
            else:
                raise RuntimeError("Please install a QCQP solver to reliably "
                                   "solve the OPF for systems without the "
                                   "hybrid architecture.")
    return solver
