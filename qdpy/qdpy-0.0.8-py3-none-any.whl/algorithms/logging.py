#    This file is part of qdpy.
#
#    qdpy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    qdpy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with qdpy. If not, see <http://www.gnu.org/licenses/>.

"""TODO""" # TODO


from typing import Optional, Tuple, List, Iterable, Iterator, Any, TypeVar, Generic, Union, Sequence, MutableSet, MutableSequence, Type, Callable, Generator, Mapping, MutableMapping, overload
import warnings
import numpy as np
import pandas as pd
import threading


from .base import *
from qdpy.utils import *
from qdpy.base import *
from qdpy.collections import *
from qdpy import tools



class AlgorithmLogger(Saveable):
    """TODO""" # TODO
    algorithms: Sequence[QDAlgorithmLike]
    iteration_filenames: Union[str, Callable]  # XXX complete type
    final_filename: str
    final_hdf_filename: Optional[str]
    save_period: int
    verbose: bool

    _cols_names: Sequence[str] = ["alg_name", "iteration", "cont_size", "evals", "nb_updated", "avg", "std", "min", "max", "elapsed"]
    _cols_size: Sequence[int]
    _min_cols_size: int = 15
    _first_iteration: bool
    _current_iteration: int
    _current_evaluation: int

    _cols_names_evals: Sequence[str] = ["alg_name", "iteration", "cont_size", "max", "elapsed"]
    _evals_data: MutableMapping[str, Sequence[Any]]
    _iterations_data: MutableMapping[str, Sequence[Any]]
    _lock_evals_data: threading.Lock
    _lock_iterations_data: threading.Lock

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['_lock_evals_data']
        del odict['_lock_iterations_data']
        return odict


    def __init__(self, algorithms: Union[QDAlgorithmLike, Sequence[QDAlgorithmLike]] = [],
            iteration_filenames: Union[str, Callable] = "iteration-%i.p", final_filename: str = "final.p",
            final_hdf_filename: Optional[str] = None,
            save_period: int = 0, verbose: bool = True):
        self.iteration_filenames = iteration_filenames
        self.final_filename = final_filename
        self.final_hdf_filename = final_hdf_filename
        self.save_period = save_period
        self.verbose = verbose
        self.algorithms = []
        self._cols_size = [len(x) for x in self._cols_names]
        self._first_iteration = False
        self._current_iteration = 0
        self._current_evaluation = 0
        # Initialise dataframes
        #self.evals = pd.DataFrame(index=np.arange(0, tot_budget), columns=self._cols_names_evals, dtype=object)
        #self.evals = pd.DataFrame(index=np.arange(0, tot_budget), columns=self._cols_names_evals)
        #self.evals = pd.DataFrame(columns=self._cols_names_evals)
        #self.iterations = pd.DataFrame(columns=self._cols_names)
        self._iterations_data = {k:[] for k in self._cols_names}
        self._lock_iterations_data = threading.Lock()
        self._evals_data = {k:[] for k in self._cols_names_evals}
        self._lock_evals_data = threading.Lock()
        # Set algorithms to be monitored
        self.monitor(algorithms)


    @property
    def evals(self) -> pd.DataFrame:
        self._lock_evals_data.acquire()
        res = pd.DataFrame(self._evals_data)
        self._lock_evals_data.release()
        return res

    @property
    def iterations(self) -> pd.DataFrame:
        self._lock_iterations_data.acquire()
        res = pd.DataFrame(self._iterations_data)
        self._lock_iterations_data.release()
        return res


    def __get_saved_state__(self) -> Mapping[str, Any]:
        """Return a dictionary containing the relevant information to save.
        Only include information from `self.algorithms`, and evaluations and iterations DataFrames."""
        if len(self.algorithms) == 1:
            algos = self.algorithms[0].__get_saved_state__()
        else:
            algos = {a.name: a for a in self.algorithms}
        return {**algos, "evals": self.evals, "iterations": self.iterations}


    def _output(self, *args):
        print(*args)

    def _gen_iteration_filename(self, iteration: Optional[int] = None) -> str:
        """Generate the filename of an iteration log file."""
        if isinstance(self.iteration_filenames, str):
            if iteration is None:
                raise ValueError("`iteration` must be provided.")
            return self.iteration_filenames % iteration
        else:
            return self.iteration_filenames()

    def _stats(self, algo: QDAlgorithmLike, batch_elapsed: float) -> Sequence[Any]:
        alg_name = algo.name
        #iteration = algo.current_iter - 1
        iteration = self._current_iteration
        cont_size = algo.container.size_str()
        evals = algo.nb_evaluations_in_iteration
        nb_updated = algo.nb_updated_in_iteration
        fitness_values = np.array([ind.fitness.values for ind in algo.container])
        avg_values = np.mean(fitness_values, axis=0) if len(fitness_values) else np.nan
        std_values = np.std(fitness_values, axis=0) if len(fitness_values) else np.nan
        min_values = np.min(fitness_values, axis=0) if len(fitness_values) else np.nan
        max_values = np.max(fitness_values, axis=0) if len(fitness_values) else np.nan
        res = [alg_name, iteration, cont_size, evals, nb_updated, avg_values, std_values, min_values, max_values, batch_elapsed]
        return res

    def _init_cols(self, content: Sequence[Any]) -> None:
        assert len(content) == len(self._cols_size)
        c_size: Sequence[int] = [len(f"{c}") for c in content]
        self._cols_size = [max(a, b, self._min_cols_size) for a, b in zip(self._cols_size, c_size)]


    def _vals_to_cols(self, content: Sequence[Any]) -> str:
        assert len(content) == len(self._cols_size)
        str_c: Sequence[str] = []
        for i, c in enumerate(content):
            str_c.append(("{0:<" + str(self._cols_size[i]) + "}").format(f"{c}"))
        return "\t".join(str_c)

    def _vals_to_cols_title(self, content: Sequence[Any]) -> str:
        return self._vals_to_cols(content)

    def _str_to_col(self, s: str, length: int) -> str:
        return ("{0:<" + str(length) + "}").format(s)


    def _tell(self, algo: QDAlgorithmLike, ind: IndividualLike) -> None:
        self._lock_evals_data.acquire()
        self._evals_data['alg_name'].append(algo.name)
        self._evals_data['iteration'].append(self._current_iteration)
        self._evals_data['cont_size'].append(algo.container.size)
        best_fitness = algo.container.best_fitness
        best_fitness = list(best_fitness) if best_fitness is not None else [np.nan]
        self._evals_data['max'].append(best_fitness)
        self._evals_data['elapsed'].append(ind.elapsed)
        self._lock_evals_data.release()
        self._current_evaluation += 1

    def _iteration(self, algo: QDAlgorithmLike, batch_elapsed: float) -> None:
        if self.verbose:
            stats: Sequence[Any] = self._stats(algo, batch_elapsed)
            if self._first_iteration:
                self._first_iteration = False
                self._init_cols(stats)
                self._output(self._vals_to_cols_title(self._cols_names))
            self._output(self._vals_to_cols(stats))
        #finished_iter_nb: int = algo.current_iter - 1
        finished_iter_nb: int = self._current_iteration
        if self.save_period != 0 and finished_iter_nb % self.save_period == 0:
            if not (isinstance(self.iteration_filenames, str) and len(self.iteration_filenames) == 0):
                self.save(_gen_iteration_filename(finished_iter_nb))
        # Update iteration infos
        self._lock_iterations_data.acquire()
        for i in range(len(self._cols_names)):
            self._iterations_data[self._cols_names[i]].append(stats[i])
        self._lock_iterations_data.release()
        # Update current iteration nb
        self._current_iteration += 1

    def _started_optimisation(self, algo: QDAlgorithmLike) -> None:
        self._first_iteration = True

    def _finished_optimisation(self, algo: QDAlgorithmLike, optimisation_elapsed: float) -> None:
        if self.verbose:
            self._output(f"Finished optimisation using algorithm '{algo.name}'. Total elapsed: {optimisation_elapsed}.")
        if self.final_filename:
            self.save(self.final_filename)
        if self.final_hdf_filename:
            self.iterations.to_hdf(self.final_hdf_filename, key="iterations", mode="w")
            self.evals.to_hdf(self.final_hdf_filename, key="evals")

    def monitor(self, algorithms: Union[QDAlgorithmLike, Sequence[QDAlgorithmLike]]) -> None:
        """Monitor an algorithm or a Sequence of algorithms.
        It will the events of the optimisation process, namely when an iteration is finished,
        or when the `ask` or `tell` methods are called.
        
        Parameters
        ----------
        :param algorithms: Union[QDAlgorithmLike, Sequence[QDAlgorithmLike]]
            Either the algorithm to monitor, or a Sequence of algorithms to monitor.
        """
        if isinstance(algorithms, QDAlgorithmLike):
            algorithms = [algorithms]
        for a in algorithms:
            a.add_callback("tell", self._tell)
            a.add_callback("iteration", self._iteration)
            a.add_callback("started_optimisation", self._started_optimisation)
            a.add_callback("finished_optimisation", self._finished_optimisation)
            self.algorithms.append(a)

_default_algorithm_logger = AlgorithmLogger(iteration_filenames = "", final_filename = "", verbose = True)


# Colorama is a python package to easily produce colored terminal outputs
try:
    import colorama
    _IMPORTED_COLORAMA = True
    colorama.init()
except Exception:
    _IMPORTED_COLORAMA = False


try:
    import tqdm
    _IMPORTED_TQDM = True
    class TQDMAlgorithmLogger(AlgorithmLogger):
        """TODO"""
        _tqdm_pbar: Optional[Any]

        def __getstate__(self):
            entries = {k:v for k,v in inspect.getmembers(self) if not k.startswith('_') and not inspect.ismethod(v)}
            return entries

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._tqdm_pbar = None

        def _output(self, *args):
            if self._tqdm_pbar is not None:
                self._tqdm_pbar.write("".join(args))

        def _started_optimisation(self, algo: QDAlgorithmLike) -> None:
            super()._started_optimisation(algo)
            if self._tqdm_pbar is not None:
                self._tqdm_pbar.close()
            self._tqdm_pbar = tqdm.tqdm(total=algo.budget, unit="eval", leave=False)

        def _finished_optimisation(self, algo: QDAlgorithmLike, optimisation_elapsed: float) -> None:
            super()._finished_optimisation(algo, optimisation_elapsed)
            self._tqdm_pbar.close()
            self._tqdm_pbar = None

        def _tell(self, algo: QDAlgorithmLike, ind: IndividualLike) -> None:
            super()._tell(algo, ind)
            self._tqdm_pbar.set_postfix(iteration=self._current_iteration)
            self._tqdm_pbar.update(1)

        def _vals_to_cols_title(self, content: Sequence[Any]) -> str:
            if _IMPORTED_COLORAMA:
                assert len(content) == len(self._cols_size)
                prefix = "" + colorama.Style.BRIGHT + colorama.Back.RED
                suffix = "" + colorama.Style.RESET_ALL
                str_c: Sequence[str] = []
                for i, c in enumerate(content):
                    str_c.append(("{0:<" + str(self._cols_size[i]) + "}").format(f"{c}"))
                return prefix + "\t".join(str_c) + suffix
            else:
                return super()._vals_to_cols_title(content)

except ImportError:
    class TQDMAlgorithmLogger(AlgorithmLogger):
        def __init__(self, *args, **kwargs):
            warnings.warn(f"`TQDMAlgorithmLogger` class needs the 'tqdm' package to be installed and importable. Using the base `AlgorithmLogger` instead.")
            super().__init__(*args, **kwargs)
            #raise NotImplementedError("`TQDMAlgorithmLogger` needs the 'tqdm' package to be installed and importable.")


# MODELINE	"{{{1
# vim:expandtab:softtabstop=4:shiftwidth=4:fileencoding=utf-8
# vim:foldmethod=marker
