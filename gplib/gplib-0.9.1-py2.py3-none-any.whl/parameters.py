# -*- coding: utf-8 -*-
#
#    Copyright 2019 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np


class Parametrizable(object):
    """

    """

    def is_array(self):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def set_param_values(self, params, optimizable_only=False, trans=False):
        """

        :param params:
        :type params:
        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def set_params_at_random(self, trans=True):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_values(self, optimizable_only=False, trans=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_keys(self, recursive=True, optimizable_only=False):
        """

        :param recursive:
        :type recursive:
        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_n(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")


class WithParameters(Parametrizable):
    """

    """
    def __init__(self, hyperparameters):
        """

        :param hyperparameters:
        :type hyperparameters:
        """
        self.hyperparameters = hyperparameters

    def is_array(self):
        """

        :return:
        :rtype:
        """

        raise True

    def set_param_values(self, params, optimizable_only=False, trans=False):
        """

        :param params:
        :type params:
        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        assert (len(params) == self.get_param_n(
            optimizable_only=optimizable_only)),\
            "length of params is not correct"

        i = 0
        for hyperparameter in self.hyperparameters:
            number_of_params = \
                hyperparameter.get_param_n(optimizable_only=optimizable_only)
            param_slice = slice(i, i + number_of_params)
            hyperparameter.set_param_values(
                params[param_slice],
                optimizable_only=optimizable_only,
                trans=trans
            )
            i += number_of_params

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.set_params_to_default(
                optimizable_only=optimizable_only
            )

    def set_params_at_random(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.set_params_at_random(trans)

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.save_current_as_optimized()

    def get_param_values(self, optimizable_only=False, trans=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        params = []
        for hyperparameter in self.hyperparameters:
            params += hyperparameter.get_param_values(
                optimizable_only=optimizable_only,
                trans=trans
            )

        return params

    def get_param_keys(self, recursive=True, optimizable_only=False):
        """

        :param recursive:
        :type recursive:
        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        if not recursive:
            return self.__class__.__name__

        params = []

        for hyperparameter in self.hyperparameters:
            name = self.__class__.__name__
            params += [
                name + "_" + item for item in hyperparameter.get_param_keys(
                    optimizable_only=optimizable_only
                )
            ]

        return params

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        bounds = []

        for hyperparameter in self.hyperparameters:
            bounds += hyperparameter.get_param_bounds(trans)

        return bounds

    def get_param_n(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        n_optimizable = 0

        for hyperparameter in self.hyperparameters:
            n_optimizable += hyperparameter.get_param_n(
                optimizable_only=optimizable_only
            )

        return n_optimizable

    def get_hyperparams(self):
        """

        :return:
        :rtype:
        """

        return self.hyperparameters

    def set_hyperparams(self, hyperparams):
        """

        :param hyperparams:
        :type hyperparams:
        :return:
        :rtype:
        """

        assert type(hyperparams) is list,\
            "hyperparams must be a list"
        self.hyperparameters = hyperparams

    def get_hyperparam(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        for hyperparameter in self.hyperparameters:
            hp_name = hyperparameter.get_param_keys(
                recursive=False,
                optimizable_only=False
            )
            if name == hp_name:
                return hyperparameter

    def get_param_value(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        hyperparam = self.get_hyperparam(name)

        value = hyperparam.get_param_values(optimizable_only=False)

        if hyperparam.is_array():
            return value

        return value[0]


class Parameter(Parametrizable):
    """

    """
    def __init__(self, name, transformation, default_value):
        """

        :param name:
        :type name:
        :param transformation:
        :type transformation:
        :param default_value:
        :type default_value:
        """

        self.name = name
        self.transformation = transformation
        self.default_value = default_value
        self.array = hasattr(self.default_value, "__len__")
        self.current_value = self.default_value

        self.dims = 1
        if self.array:
            self.dims = len(self.default_value)

    def is_array(self):
        """

        :return:
        :rtype:
        """
        return self.array

    def set_param_values(self, params, optimizable_only=False, trans=False):
        """

        :param params:
        :type params:
        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        assert len(params) == self.dims, \
            "length of {} is not correct".format(self.name)

        if trans:
            if self.array:
                params = self.transformation.inv_trans(params).tolist()
            else:
                params = self.transformation.inv_trans(params)

        if self.array is False:
            self.current_value = params[0]
        else:
            self.current_value = params

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        self.current_value = self.default_value

    def set_params_at_random(self, trans=False):
        """

        :return:
        :rtype:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_values(self, optimizable_only=False, trans=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        assert self.current_value is not None, \
            "{} has not been initialized".format(self.name)

        current_value = self.current_value
        if trans:
            current_value = self.transformation.trans(current_value)
            if self.array:
                current_value = current_value.tolist()

        if self.array:
            return current_value
        return [current_value]

    def get_param_keys(self, recursive=True, optimizable_only=False):
        """

        :param recursive:
        :type recursive:
        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        if not recursive:
            return self.name

        if self.dims == 1:
            return [self.name]

        return [
            "{}_d{}".format(self.name, dim) for dim in range(self.dims)
        ]

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_n(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        return self.dims


class OptimizableParameter(Parameter):
    """

    """
    def __init__(self, name, transformation, default_value=1.0,
                 min_value=-np.inf, max_value=np.inf,
                 jitter_sd=0.1):
        """

        :param name:
        :type name:
        :param transformation:
        :type transformation:
        :param default_value:
        :type default_value:
        :param min_value:
        :type min_value:
        :param max_value:
        :type max_value:
        :param jitter_sd:
        :type jitter_sd:
        """

        super(OptimizableParameter, self).__init__(
            name, transformation, default_value
        )

        self.min_value = np.float64(min_value)
        self.max_value = np.float64(max_value)

        assert (np.all(self.min_value <= default_value) and
                np.all(default_value <= self.max_value)),\
            "{} is out of bounds".format(self.name)

        self.optimized_value = None

        self.jitter_sd = jitter_sd
        


    def set_param_values(self, params, optimizable_only=False, trans=False):
        """

        :param params:
        :type params:
        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        super(OptimizableParameter, self).set_param_values(
            params, optimizable_only=optimizable_only, trans=trans
        )

        assert (np.all(self.min_value <= self.current_value) and
                np.all(self.current_value <= self.max_value)), \
            "{} is out of bounds".format(self.name)

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        self.optimized_value = None

        super(OptimizableParameter, self).set_params_to_default(
            optimizable_only=optimizable_only
        )

    def set_params_at_random(self, trans=False):
        """

        :return:
        :rtype:
        """
        min_value = self.min_value
        max_value = self.max_value
        if trans:
            min_value = self.transformation.trans(min_value)
            max_value = self.transformation.trans(max_value)

        if self.optimized_value is not None:
            optimized_value = self.optimized_value
            if trans:
                optimized_value = self.transformation.trans(optimized_value)
            current_value = None
            while not (current_value is not None and
                       np.all(min_value < current_value) and
                       np.all(current_value < max_value)):
                current_value = optimized_value + \
                    np.array(
                        np.random.normal(
                            loc=0.0,
                            scale=self.jitter_sd,
                            size=self.dims
                        )
                    )
        else:
            current_value = np.array(np.random.uniform(
                min_value, max_value, self.dims
            ))

        self.set_param_values(current_value, trans=trans)

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """
        self.optimized_value = self.current_value

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        min_value = self.min_value
        max_value = self.max_value

        if trans:
            min_value = self.transformation.trans(min_value)
            max_value = self.transformation.trans(max_value)

        return [(min_value, max_value)] * self.dims

    def set_min_value(self, min_value):
        """

        :param min_value:
        :type min_value:
        :return:
        :rtype:
        """
        self.min_value = min_value

    def set_max_value(self, max_value):
        """

        :param max_value:
        :type max_value:
        :return:
        :rtype:
        """
        self.max_value = max_value

    def grad_trans(self, df):
        """

        :param df:
        :type df:
        :return:
        :rtype:
        """

        return self.transformation.grad_trans(self.current_value, df)


class FixedParameter(Parameter):
    """

    """

    def set_param_values(self, params, optimizable_only=False, trans=False):
        """

        :param params:
        :type params:
        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        if optimizable_only:
            return

        super(FixedParameter, self).set_param_values(
            params, optimizable_only=optimizable_only, trans=trans
        )

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        if optimizable_only:
            return

        super(FixedParameter, self).set_params_to_default(
            optimizable_only=optimizable_only
        )

    def set_params_at_random(self, trans=False):
        """

        :return:
        :rtype:
        """
        pass

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """
        pass

    def get_param_values(self, optimizable_only=False, trans=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        if optimizable_only:
            return []

        return super(FixedParameter, self).get_param_values(
            optimizable_only=optimizable_only, trans=trans
        )

    def get_param_keys(self, recursive=True, optimizable_only=False):
        """

        :param recursive:
        :type recursive:
        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        if optimizable_only:
            return []

        return super(FixedParameter, self).get_param_keys(
            recursive=recursive,
            optimizable_only=optimizable_only
        )

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        return []

    def get_param_n(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        if optimizable_only:
            return 0

        return super(FixedParameter, self).get_param_n(
            optimizable_only=optimizable_only
        )
