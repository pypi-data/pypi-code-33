import numpy as np

from astropy import units as u
from abc import ABCMeta, abstractmethod
from scipy.optimize import fsolve
from stasma import logger, const, units


class System(metaclass=ABCMeta):
    """
    Abstract class defining System
    see https://docs.python.org/3.5/library/abc.html for more informations
    """

    ID = 1
    KWARGS = []
    OPTIONAL_KWARGS = []
    ALL_KWARGS = KWARGS + OPTIONAL_KWARGS

    def __init__(self, name=None, suppress_logger=False, **kwargs):
        self._logger = logger.getLogger(System.__name__, suppress=suppress_logger)
        self.initial_kwargs = kwargs.copy()
        self._inclination = None

        if name is None:
            self._name = str(System.ID)
            self._logger.debug("name of class instance {} set to {}".format(System.__name__, self._name))
            System.ID += 1
        else:
            self._name = str(name)

    @property
    def name(self):
        """
        name of object initialized on base of this abstract class

        :return: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        setter for name of system

        :param name: str
        :return:
        """
        self._name = str(name)

    @property
    def inclination(self):
        """
        inclination of system, angle between z axis and line of sight

        :return: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        """
        return self._inclination

    @inclination.setter
    def inclination(self, inclination):
        """
        set orbit inclination of system, if unit is not specified, default unit is assumed

        :param inclination: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """

        if isinstance(inclination, u.quantity.Quantity):
            self._inclination = np.float64(inclination.to(units.ARC_UNIT))
        elif isinstance(inclination, (int, np.int, float, np.float)):
            self._inclination = np.float64((inclination*u.rad).to(units.ARC_UNIT))
        else:
            raise TypeError('input of variable `inclination` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance')

        if not 0 <= self.inclination <= const.PI:
            raise ValueError('inclination value of {} is out of bounds (0, pi).'
                             ''.format(self.inclination))

        self._logger.debug("setting property inclination of class instance {} to {}"
                           "".format(System.__name__, self._inclination))

    @abstractmethod
    def build_mesh(self, *args, **kwargs):
        """
        abstract method for creating surface points

        :param args:
        :param kwargs:
        :return:
        """
        pass

    @abstractmethod
    def build_surface(self, *args, **kwargs):
        """
        abstract method which builds surface from ground up including points and faces of surface and spots

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def solver(self, fn, condition, *args, **kwargs):
        """
        will solve fn implicit function taking args by using scipy.optimize.fsolve method and return
        solution if satisfy conditional function


        :param self:
        :param fn: function
        :param condition: function
        :param args: tuple
        :return: float (np.nan), bool
        """
        # precalculation of auxiliary values
        solution, use = np.nan, False
        scipy_solver_init_value = np.array([1. / 10000.])
        try:
            solution, _, ier, msg = fsolve(fn, scipy_solver_init_value, full_output=True, args=args, xtol=1e-10)
            if ier == 1 and not np.isnan(solution[0]):
                solution = solution[0]
                use = True if 1e15 > solution > 0 else False
            else:
                self._logger.warning('solution in implicit solver was not found, cause: {}'.format(msg))
        except Exception as e:
            self._logger.debug("attempt to solve function {} finished w/ exception: {}".format(fn.__name__, str(e)))
            use = False

        args_to_use = kwargs.get('solver_condition_args', args)
        return (solution, use) if condition(solution, *args_to_use) else (np.nan, False)

    @abstractmethod
    def evaluate_spots_mesh(self, *args, **kwargs):
        pass
