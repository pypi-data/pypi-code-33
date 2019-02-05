"""
MOSEK-based solver for the *hynet*-specific QCQP problem (SD and SOC relaxation).
"""

import logging
import sys
import abc

import numpy as np
import mosek

from hynet.types_ import hynet_float_, SolverType, SolverStatus
from hynet.utilities.base import Timer
from hynet.qcqp.solver import SolverInterface
from hynet.qcqp.problem import QCQPPoint
from hynet.qcqp.result import QCQPResult

_log = logging.getLogger(__name__)


def parse_status(status):
    """Parse the MOSEK status into a ``SolverStatus``."""
    if status == mosek.solsta.optimal:
        return SolverStatus.SOLVED
    if status == mosek.solsta.near_optimal:
        return SolverStatus.INACCURATE
    if status in [mosek.solsta.prim_infeas_cer,
                  mosek.solsta.dual_infeas_cer,
                  mosek.solsta.near_prim_infeas_cer,
                  mosek.solsta.near_dual_infeas_cer]:
        return SolverStatus.INFEASIBLE
    return SolverStatus.FAILED


class SolverBase(SolverInterface):
    """Base class for MOSEK-based solvers for a relaxation of the QCQP."""

    # REMARK concerning the logger callback:
    #   Originally, the class accepted an argument ``log_stream`` of type
    #   ``io.TextIOBase`` for the object initialization, which was set to
    #   ``sys.stdout`` by default and used as the output stream for the logging
    #   information in verbose mode. However, as a consequence of the solver
    #   object containing an open stream as an attribute, it was rendered
    #   non-serializable with pickle. As a customization of the logging output
    #   stream is typically not needed, this implementation hard-wires the
    #   logging to ``sys.stdout`` to render the solver objects 'pickleable'.
    def _logger(self, message):
        """Logger callback for MOSEK"""
        sys.stdout.write(message)
        sys.stdout.flush()

    @staticmethod
    @abc.abstractmethod
    def _add_voltage_matrix_constraints(task, qcqp, dim_x, ofs, x_lb, x_ub, x_bnd):
        """Add the SOC or PSD constraint(s) on the ``v_tld``-part of ``x``."""

    def solve(self, qcqp):
        """
        Solve the given QCQP via a relaxation using MOSEK.

        The relaxation-specific constraints on the bus voltage matrix are
        added via the (abstract) method ``_add_voltage_matrix_constraints``,
        which must be implemented in a derived class.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the relaxed problem associated with the QCQP.
        """
        # We solve the following problem:
        #
        #  min   c^T x   s.t.   Ax == b,  Bx <= d,  x_lb <= x <= x_ub
        #   x                ...and SOC or PSD constraint(s) on v_tld-part of x
        timer = Timer()
        (c, A, b, B, d, x_lb, x_ub) = qcqp.get_vectorization()
        dim_x = c.shape[0]

        # Convert from the COO to the CSR sparse matrix format: In the COO
        # format, there can be duplicate entries (i.e., more than one value for
        # the same element in the matrix, which are to be added), but this is
        # not supported by MOSEK's ``putaijlist``. To this end, the matrices
        # are converted to the CSR format, which sums up the duplicate entries.
        c = c.tocsr()
        A = A.tocsr()
        B = B.tocsr()

        x_lb_is_nan = np.isnan(x_lb)
        x_ub_is_nan = np.isnan(x_ub)
        x_bnd = np.array([mosek.boundkey.ra] * dim_x)
        x_bnd[np.logical_and(x_lb_is_nan, x_ub_is_nan)] = mosek.boundkey.fr
        x_bnd[np.logical_and(~x_lb_is_nan, x_ub_is_nan)] = mosek.boundkey.lo
        x_bnd[np.logical_and(x_lb_is_nan, ~x_ub_is_nan)] = mosek.boundkey.up
        x_bnd[x_lb == x_ub] = mosek.boundkey.fx

        # For the following code, I used the MOSEK documentation provided at
        #  1) http://docs.mosek.com/8.1/pythonapi.pdf
        #  2) https://docs.mosek.com/8.1/pythonapi/optimizer-task.html
        with mosek.Env() as env:
            if self.verbose:
                env.set_Stream(mosek.streamtype.log, self._logger)

            with env.Task() as task:
                if self.verbose:
                    task.set_Stream(mosek.streamtype.log, self._logger)

                # Variable definition and bounds
                task.appendvars(dim_x)
                task.putvarboundlist(range(dim_x), x_bnd, x_lb, x_ub)

                # Objective
                task.putobjsense(mosek.objsense.minimize)
                idx_nz = c.nonzero()[0]
                task.putclist(idx_nz, c[idx_nz].toarray()[:, 0])

                # Equality constraints
                ofs = 0
                N = b.shape[0]
                task.appendcons(N)
                idx_nz = A.nonzero()
                task.putaijlist(ofs + idx_nz[0], idx_nz[1],
                                np.asarray(A[idx_nz[0], idx_nz[1]])[0])
                task.putconboundlist(range(ofs, ofs + N),
                                     [mosek.boundkey.fx] * N, b, b)
                ofs += N

                # Inequality constraints
                M = d.shape[0]
                task.appendcons(M)
                idx_nz = B.nonzero()
                task.putaijlist(ofs + idx_nz[0], idx_nz[1],
                                np.asarray(B[idx_nz[0], idx_nz[1]])[0])
                task.putconboundlist(range(ofs, ofs + M),
                                     [mosek.boundkey.up] * M, np.zeros(M), d)
                ofs += M

                # Add relaxation-specific constraints on the voltage matrix
                # (This method is overridden appropriately in derived classes)
                self._add_voltage_matrix_constraints(task, qcqp, dim_x, ofs,
                                                     x_lb, x_ub, x_bnd)

                # Set solver parameters
                for key, value in self.param.items():
                    task.putparam(key, str(value))

                # Optimization and solution recovery
                _log.debug(self.type.name + " ~ Modeling ({:.3f} sec.)"
                           .format(timer.interval()))
                task.optimize()
                solver_time = timer.interval()
                _log.debug(self.type.name + " ~ Solver ({:.3f} sec.)"
                           .format(solver_time))

                if self.verbose:
                    task.solutionsummary(mosek.streamtype.log)

                status = parse_status(task.getsolsta(mosek.soltype.itr))

                if status in [SolverStatus.SOLVED, SolverStatus.INACCURATE]:
                    x = np.ndarray(dim_x, hynet_float_)
                    task.getxxslice(mosek.soltype.itr, 0, dim_x, x)
                    (V, f, s, z) = qcqp.split_vectorization_optimizer(x)
                    v = self.rank1approx(V, qcqp.edges, qcqp.roots)
                    optimizer = QCQPPoint(v, f, s, z)

                    dv_lb = np.ndarray(dim_x, dtype=hynet_float_)
                    task.getslxslice(mosek.soltype.itr, 0, dim_x, dv_lb)
                    dv_lb[np.isnan(x_lb)] = np.nan
                    dv_lb = qcqp.split_vectorization_bound_dual(dv_lb)

                    dv_ub = np.ndarray(dim_x, dtype=hynet_float_)
                    task.getsuxslice(mosek.soltype.itr, 0, dim_x, dv_ub)
                    dv_ub[np.isnan(x_ub)] = np.nan
                    dv_ub = qcqp.split_vectorization_bound_dual(dv_ub)

                    dv_eq_lb = np.ndarray(N, dtype=hynet_float_)
                    task.getslcslice(mosek.soltype.itr, 0, N, dv_eq_lb)
                    dv_eq_ub = np.ndarray(N, dtype=hynet_float_)
                    task.getsucslice(mosek.soltype.itr, 0, N, dv_eq_ub)
                    dv_eq = dv_eq_ub - dv_eq_lb

                    dv_ineq = np.ndarray(M, dtype=hynet_float_)
                    task.getsucslice(mosek.soltype.itr, N, N + M, dv_ineq)

                    optimal_value = task.getprimalobj(mosek.soltype.itr)

                    result = QCQPResult(qcqp, self, status, solver_time,
                                        optimizer=optimizer,
                                        V=V,
                                        optimal_value=optimal_value,
                                        dv_lb=dv_lb,
                                        dv_ub=dv_ub,
                                        dv_eq=dv_eq,
                                        dv_ineq=dv_ineq)
                else:
                    result = QCQPResult(qcqp, self, status, solver_time)

        _log.debug(self.type.name + " ~ Result creation ({:.3f} sec.)"
                   .format(timer.interval()))
        _log.debug(self.type.name + " ~ Total time for solver ({:.3f} sec.)"
                   .format(timer.total()))
        return result


class SOCRSolver(SolverBase):
    """
    MOSEK-based solver for a second-order cone relaxation of the QCQP.

    For information on solver-specific parameters, see e.g. [1]_, [2]_.

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.

    References
    ----------
    .. [1] https://docs.mosek.com/8.1/opt-server/param-groups.html
    .. [2] https://docs.mosek.com/8.1/pythonapi/solving-conic.html
    """

    @property
    def name(self):
        return "MOSEK"

    @property
    def type(self):
        return SolverType.SOCR

    def solve(self, qcqp):  # pylint: disable=useless-super-delegation
        """
        Solve the given QCQP via its second-order cone relaxation using MOSEK.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the SOCR associated with the QCQP.
        """
        # We solve the following problem:
        #
        #  min   c^T x   s.t.   Ax == b,  Bx <= d,  x_lb <= x <= x_ub
        #   x                   ...and SOC constraints on v_tld-part of x
        return super().solve(qcqp)

    @staticmethod
    def _add_voltage_matrix_constraints(task, qcqp, dim_x, ofs, x_lb, x_ub, x_bnd):
        """Add the SOC constraints on the ``v_tld``-part of ``x``."""
        # Second-order cone constraints on V (cf. QCQP.get_vectorization)
        #
        # PSD constraint on 2x2 principal submatrix =>
        #  (a) diagonal is nonnegative -> ensured by LB on voltage mag.
        #  (b) determinant is nonnegative -> rotated SOC:
        #
        #               V_ij * conj(V_ij) <= V_ii * V_jj
        #                             <=>
        #          real(V_ij)^2 + imag(V_ij)^2 <= V_ii * V_jj
        #
        #      where i is the source bus and j is the destination bus
        #      of the considered edge. Note that MOSEK requires
        #      rotated second-order cones to be specified as
        #
        #              2 * x_0 * x_1 >= x_2^2 + x_3^2
        #
        #      i.e., there is an additional scaling factor of 2.
        #
        # MOSEK limits variables to being a member of only one cone. If
        # multiple edges connect to a bus, the corresponding diagonal
        # element is a member of more than one cone. Due to this, the
        # diagonal elements V_ii and V_jj are duplicated for every
        # second-order cone, i.e., for every edge k with source node i
        # and destination node j an additional variable
        # w_k = [V_ii/2, V_jj]^T is introduced. Thus, the augmented
        # optimization variable x' is
        #
        #            x' = [x^T, w_0^T, ..., w_(K-1)^T]^T
        #
        # where K is the number of edges.

        # Add the variables w_k. Note that the diagonal elements of V
        # are at the "beginning" of x and the bounds can be reused.
        (e_src, e_dst) = qcqp.edges
        K = qcqp.num_edges
        task.appendvars(2*K)
        idx_w_src = range(dim_x, dim_x + 2*K, 2)
        idx_w_dst = range(dim_x + 1, dim_x + 2*K, 2)
        task.putvarboundlist(idx_w_src, x_bnd[e_src],
                             x_lb[e_src]/2, x_ub[e_src]/2)
        task.putvarboundlist(idx_w_dst, x_bnd[e_dst],
                             x_lb[e_dst], x_ub[e_dst])

        task.appendcons(2*K)
        idx_crt_w_src = range(ofs, ofs + 2*K, 2)
        idx_crt_w_dst = range(ofs + 1, ofs + 2*K, 2)
        task.putaijlist(idx_crt_w_src, e_src, 0.5 * np.ones(K))
        task.putaijlist(idx_crt_w_src, idx_w_src, -np.ones(K))
        task.putaijlist(idx_crt_w_dst, e_dst, np.ones(K))
        task.putaijlist(idx_crt_w_dst, idx_w_dst, -np.ones(K))
        task.putconboundlist(range(ofs, ofs + 2*K),
                             [mosek.boundkey.fx] * 2*K,
                             np.zeros(2*K), np.zeros(2*K))
        ofs += 2*K

        for k in range(K):
            task.appendcone(mosek.conetype.rquad, 0,
                            [idx_w_src[k], idx_w_dst[k],
                             qcqp.dim_v + k, qcqp.dim_v + K + k])


class SDRSolver(SolverBase):
    """
    MOSEK-based solver for a semidefinite relaxation of the QCQP.

    For information on solver-specific parameters, see e.g. [1]_. With the
    default setting, the dual variables turned out to be inaccurate, due to
    which the default tolerance on dual feasibility is adapted.

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.

    References
    ----------
    .. [1] https://docs.mosek.com/8.1/opt-server/param-groups.html
    """
    def __init__(self, **kwds):
        super().__init__(**kwds)
        if not 'MSK_DPAR_INTPNT_CO_TOL_DFEAS' in self.param:
            self.param['MSK_DPAR_INTPNT_CO_TOL_DFEAS'] = 1e-9

    @property
    def name(self):
        return "MOSEK"

    @property
    def type(self):
        return SolverType.SDR

    def solve(self, qcqp):  # pylint: disable=useless-super-delegation
        """
        Solve the given QCQP via its semidefinite relaxation using MOSEK.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the SDR associated with the QCQP.
        """
        # We solve the following problem:
        #
        #  min   c^T x   s.t.   Ax == b,  Bx <= d,  x_lb <= x <= x_ub
        #   x                   ...and a PSD constraint on the v_tld-part of x
        return super().solve(qcqp)

    @staticmethod
    def _add_voltage_matrix_constraints(task, qcqp, dim_x, ofs, x_lb, x_ub, x_bnd):
        """Add the PSD constraint on the ``v_tld``-part of ``x``."""
        # PSD constraint on V
        #
        # Consider the splitting of the Hermitian matrix V into its
        # real and imaginary part, i.e., V = V_r + j*V_i. Then,
        #
        #       V is PSD    <=>    V_cr = [ V_r  -V_i ] is PSD
        #                                 [ V_i   V_r ]
        #
        # This code implements the real-valued equivalent of V >= 0,
        # i.e., V_cr >= 0. To this end, a semidefinite matrix variable
        # V_cr is added and all relevant elements are equated to v_tld.
        # Note the following particularities:
        #
        #  1) MOSEK considers *symmetric* coefficient matrices and
        #     requires the specification of the *lower* triangular part.
        #  2) When equating the off-diagonal elements of V_cr to v_tld,
        #     the respective element of V_cr is taken twice (due to the
        #     sym. coeff. matrix), which explains the factor of 2 for
        #     the corresponding element in v_tld.
        #  3) V_i is skew-symmetric and, thus, its diagonal is zero.
        #     Correspondingly, the respective elements in V_cr are
        #     fixed at zero.
        #
        dim_v = qcqp.dim_v
        dim_V_cr = 2*dim_v
        K = qcqp.num_edges

        (e_src, e_dst) = qcqp.edges
        if np.any(e_src >= e_dst):
            raise RuntimeError("For simplicity, this solver assumes "
                               "that the source node index is smaller "
                               "than the destination node index in the "
                               "sparsity specification. At the time of "
                               "implementation, this was the default.")

        # Add the symmetric matrix V_cr
        task.appendbarvars([dim_V_cr])

        # Add constraints to equate v_tld to V_cr
        num_crt_V_cr = 3*dim_v + 4*K
        task.appendcons(num_crt_V_cr)
        task.putconboundlist(range(ofs, ofs + num_crt_V_cr),
                             [mosek.boundkey.fx] * num_crt_V_cr,
                             np.zeros(num_crt_V_cr),
                             np.zeros(num_crt_V_cr))

        # Diagonal of V_r in top-left block
        for i in range(dim_v):
            mtx_id = task.appendsparsesymmat(dim_V_cr, [i], [i], [-1])
            task.putaij(ofs + i, i, 1)
            task.putbaraij(ofs + i, 0, [mtx_id], [1.0])
        ofs += dim_v

        # Diagonal of V_r in bottom-right block
        for i in range(dim_v):
            mtx_id = task.appendsparsesymmat(dim_V_cr, [i + dim_v],
                                             [i + dim_v], [-1])
            task.putaij(ofs + i, i, 1)
            task.putbaraij(ofs + i, 0, [mtx_id], [1.0])
        ofs += dim_v

        # Diagonal of V_i in bottom-right block (fixed at zero)
        for i in range(dim_v):
            mtx_id = task.appendsparsesymmat(dim_V_cr,
                                             [i + dim_v], [i], [1])
            task.putbaraij(ofs + i, 0, [mtx_id], [1.0])
        ofs += dim_v

        # Off-diagonal elements of V_r in top-left block
        for k in range(K):
            mtx_id = task.appendsparsesymmat(dim_V_cr, [e_dst[k]],
                                             [e_src[k]], [-1])
            task.putaij(ofs + k, k + dim_v, 2)
            task.putbaraij(ofs + k, 0, [mtx_id], [1.0])
        ofs += K

        # Off-diagonal elements of V_r in bottom-right block
        for k in range(K):
            mtx_id = task.appendsparsesymmat(dim_V_cr, [e_dst[k] + dim_v],
                                             [e_src[k] + dim_v], [-1])
            task.putaij(ofs + k, k + dim_v, 2)
            task.putbaraij(ofs + k, 0, [mtx_id], [1.0])
        ofs += K

        # Upper-triangular part of V_i in bottom-left block
        for k in range(K):
            mtx_id = task.appendsparsesymmat(dim_V_cr, [e_src[k] + dim_v],
                                             [e_dst[k]], [-1])
            task.putaij(ofs + k, k + dim_v + K, 2)
            task.putbaraij(ofs + k, 0, [mtx_id], [1.0])
        ofs += K

        # Lower-triangular part of V_i in bottom-left block
        for k in range(K):
            mtx_id = task.appendsparsesymmat(dim_V_cr, [e_dst[k] + dim_v],
                                             [e_src[k]], [1])
            task.putaij(ofs + k, k + dim_v + K, 2)
            task.putbaraij(ofs + k, 0, [mtx_id], [1.0])
        ofs += K
