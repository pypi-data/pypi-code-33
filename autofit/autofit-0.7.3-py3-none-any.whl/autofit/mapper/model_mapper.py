import inspect
import itertools
import os
import re

from autofit import conf
from autofit import exc
from autofit.mapper.prior import TuplePrior, GaussianPrior, LogUniformPrior, UniformPrior, Prior, Constant, \
    cast_collection, PriorNameValue, ConstantNameValue, AttributeNameValue


class PriorModelNameValue(AttributeNameValue):
    @property
    def prior_model(self):
        return self.value


path = os.path.dirname(os.path.realpath(__file__))


class AbstractModel(object):
    def __add__(self, other):
        instance = self.__class__()

        def add_items(item_dict):
            for key, value in item_dict.items():
                if isinstance(value, list) and hasattr(instance, key):
                    setattr(instance, key, getattr(instance, key) + value)
                else:
                    setattr(instance, key, value)

        add_items(self.__dict__)
        add_items(other.__dict__)
        return instance


class ModelMapper(AbstractModel):
    """A mapper of priors formed by passing in classes to be reconstructed
        @DynamicAttrs
    """

    def __init__(self, **classes):
        """
        Examples
        --------
        # The ModelMapper converts a set of classes whose input attributes may be modeled using a non-linear search,
        # to parameters with priors attached.

        # A config is passed into the model mapper to provide default setup values for the priors:

        mapper = ModelMapper(config)

        # All class instances that are to be generated by the model mapper are specified by adding classes to it:
        
        mapper = ModelMapper()

        mapper.sersic = light_profiles.AbstractEllipticalSersic
        mapper.gaussian = light_profiles.EllipticalGaussian)
        mapper.any_class = SomeClass

        # A PriorModel instance is created each time we add a class to the mapper. We can access those models using
        # the mapper attributes:

        sersic_model = mapper.sersic

        # This allows us to replace the default priors:

        mapper.sersic.intensity = GaussianPrior(mean=2., sigma=5.)

        # Or maybe we want to tie two priors together:

        mapper.sersic.phi = mapper.other_sersic.phi

        # This statement reduces the number of priors by one and means that the two sersic instances will always share
        # the same rotation angle phi.

        # We can then create instances of every class for a unit hypercube vector with length equal to
        # len(mapper.priors):

        model_instance = mapper.model_instance_for_vector([.4, .2, .3, .1])

        # The attributes of the model_instance are named the same as those of the mapper:

        sersic_1 = mapper.sersic_1

        # But this attribute is an instance of the actual AbstractEllipticalSersic:P class

        # A ModelMapper can be concisely constructed using keyword arguments:

        mapper = prior.ModelMapper(source_light_profile=light_profile.AbstractEllipticalSersic,
                                    lens_mass_profile=mass_profile.EllipticalCoredIsothermal,
                                    lens_light_profile=light_profile.EllipticalCoreSersic)
        """
        super(ModelMapper, self).__init__()

        for name, cls in classes.items():
            self.__setattr__(name, cls)

    def __setattr__(self, key, value):
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], AbstractPriorModel):
            value = ListPriorModel(value)
        elif inspect.isclass(value):
            value = PriorModel(value)
        super(ModelMapper, self).__setattr__(key, value)

    @property
    def prior_count(self):
        return len(self.prior_tuples_ordered_by_id)

    @property
    def constant_count(self):
        return len(self.constant_tuples_ordered_by_id)

    @property
    @cast_collection(PriorModelNameValue)
    def prior_model_tuples(self):
        """
        Returns
        -------
        prior_model_tuples: [(String, PriorModel)]
        """
        return list(filter(lambda t: isinstance(t[1], AbstractPriorModel), self.__dict__.items()))

    @property
    @cast_collection(PriorModelNameValue)
    def list_prior_model_tuples(self):
        """
        Returns
        -------
        list_prior_model_tuples: [(String, ListPriorModel)]
        """
        return list(filter(lambda t: isinstance(t[1], ListPriorModel), self.__dict__.items()))

    @property
    @cast_collection(PriorModelNameValue)
    def flat_prior_model_tuples(self):
        """
        Returns
        -------
        prior_model_tuples: [(String, PriorModel)]
            A list of tuples with the names of prior models and associated prior models. Names are fully qualified by
            all objects in which they are embedded.
        """
        all_flat_prior_model_tuples = [("{}".format(prior_model_name), flat_prior_model) for
                                       prior_model_name, prior_model in
                                       self.prior_model_tuples for
                                       flat_prior_model_name, flat_prior_model in
                                       prior_model.flat_prior_model_tuples]
        filtered_flat_prior_model_tuples = []

        # Prior models can be members of lists and attributes of the prior model simultaneously. This line prevents
        #  duplication.
        for flat_prior_model_tuple in all_flat_prior_model_tuples:
            if flat_prior_model_tuple[1] not in [item[1] for item in filtered_flat_prior_model_tuples]:
                filtered_flat_prior_model_tuples.append(flat_prior_model_tuple)
        return filtered_flat_prior_model_tuples

    @property
    @cast_collection(PriorNameValue)
    def prior_tuple_dict(self):
        """
        Returns
        -------
        prior_tuple_dict: [(Prior, PriorTuple)]
            The set of all priors associated with this mapper
        """
        return {prior_tuple.prior: prior_tuple
                for name, prior_model in self.prior_model_tuples
                for prior_tuple in prior_model.prior_tuples}.values()

    @property
    def priors(self):
        return [prior_tuple.prior for prior_tuple in self.prior_tuple_dict]

    @property
    @cast_collection(ConstantNameValue)
    def constant_tuple_dict(self):
        """
        Returns
        -------
        constant_tuple_dict: {Constant: ConstantTuple}
            The set of all constants associated with this mapper
        """
        return {constant_tuple.constant: constant_tuple
                for name, prior_model in self.prior_model_tuples
                for constant_tuple in prior_model.constant_tuples}.values()

    @property
    @cast_collection(PriorNameValue)
    def prior_tuples_ordered_by_id(self):
        """
        Returns
        -------
        priors: [Prior]
            An ordered list of unique priors associated with this mapper
        """
        return sorted(list(self.prior_tuple_dict), key=lambda prior_tuple: prior_tuple.prior.id)

    @property
    @cast_collection(ConstantNameValue)
    def constant_tuples_ordered_by_id(self):
        """
        Returns
        -------
        constants: [(str, Constant)]
            A list of tuples mapping strings to constants constants ordered by id
        """
        return sorted(list(self.constant_tuple_dict), key=lambda constant_tuple: constant_tuple.constant.id)

    @property
    def prior_class_dict(self):
        """
        Returns
        -------
        prior_class_dict: {Prior: class}
            A dictionary mapping Priors to associated classes. Each prior will only have one class; if a prior is
            shared by two classes then only one of those classes will be in this dictionary.
        """
        return {prior: cls
                for prior_model_tuple in self.prior_model_tuples
                for prior, cls in
                prior_model_tuple.prior_model.prior_class_dict.items()}

    @property
    def prior_prior_model_dict(self):
        """
        Returns
        -------
        prior_prior_model_dict: {Prior: PriorModel}
            A dictionary mapping priors to associated prior models. Each prior will only have one prior model; if a
            prior is shared by two prior models then one of those prior models will be in this dictionary.
        """
        return {prior: prior_model[1] for prior_model in self.prior_model_tuples for _, prior in
                prior_model[1].prior_tuples}

    @property
    def prior_prior_model_name_dict(self):
        """
        Returns
        -------
        prior_prior_model_name_dict: {Prior: str}
            A dictionary mapping priors to the names of associated prior models. Each prior will only have one prior
            model name; if a prior is shared by two prior models then one of those prior model's names will be in this
            dictionary.
        """
        prior_prior_model_name_dict = {prior_tuple.prior: prior_model_tuple.name
                                       for prior_model_tuple in self.flat_prior_model_tuples
                                       for prior_tuple in prior_model_tuple.prior_model.prior_tuples}
        prior_list_prior_model_name_dict = {
            prior_tuple.value: "{}_{}".format(list_prior_model_tuple.name, label_prior_model_tuple.name) for
            list_prior_model_tuple in self.list_prior_model_tuples for label_prior_model_tuple in
            list_prior_model_tuple.value.label_prior_model_tuples for prior_tuple in
            label_prior_model_tuple.value.prior_tuples}
        prior_prior_model_name_dict.update(prior_list_prior_model_name_dict)
        return prior_prior_model_name_dict

    @property
    @cast_collection(PriorModelNameValue)
    def list_prior_model_tuples(self):
        return [tup for tup in self.prior_model_tuples if isinstance(tup.value, ListPriorModel)]

    @property
    def constant_prior_model_name_dict(self):
        """
        Returns
        -------
        prior_prior_model_name_dict: {Prior: str}
            A dictionary mapping priors to the names of associated prior models. Each prior will only have one prior
            model name; if a prior is shared by two prior models then one of those prior model's names will be in this
            dictionary.
        """
        return {constant_tuple.constant: prior_model_tuple.name
                for prior_model_tuple in self.prior_model_tuples
                for constant_tuple in prior_model_tuple.prior_model.constant_tuples}

    @property
    def prior_model_name_prior_tuples_dict(self):
        """
        Returns
        -------
        class_priors_dict: {String: [Prior]}
            A dictionary mapping_matrix the names of priors to lists of associated priors
        """
        return {name: list(prior_model.prior_tuples) for name, prior_model in self.prior_model_tuples}

    @property
    def prior_model_name_constant_tuples_dict(self):
        """
        Returns
        -------
        class_constants_dict: {String: [Constant]}
            A dictionary mapping_matrix the names of priors to lists of associated constants
        """
        return {name: list(prior_model.constant_tuples) for name, prior_model in self.prior_model_tuples}

    def physical_vector_from_hypercube_vector(self, hypercube_vector):
        """
        Parameters
        ----------
        hypercube_vector: [float]
            A unit hypercube vector

        Returns
        -------
        values: [float]
            A vector with values output by priors
        """
        return list(
            map(lambda prior_tuple, unit: prior_tuple.prior.value_for(unit), self.prior_tuples_ordered_by_id,
                hypercube_vector))

    def physical_values_ordered_by_class(self, hypercube_vector):
        """
        Parameters
        ----------
        hypercube_vector: [float]
            A unit vector

        Returns
        -------
        physical_values: [float]
            A list of physical values constructed by passing the values in the hypercube vector through associated
            priors.
        """
        model_instance = self.instance_from_unit_vector(hypercube_vector)
        result = []
        for instance_key in sorted(model_instance.__dict__.keys()):
            instance = model_instance.__dict__[instance_key]
            for attribute_key in sorted(instance.__dict__.keys()):

                value = instance.__dict__[attribute_key]

                if isinstance(value, tuple):
                    result.extend(list(value))
                else:
                    result.append(value)
        return result

    @property
    def physical_values_from_prior_medians(self):
        """
        Returns
        -------
        physical_values: [float]
            A list of physical values constructed by taking the mean possible value from each prior.
        """
        return self.physical_vector_from_hypercube_vector([0.5] * len(self.prior_tuple_dict))

    def instance_from_prior_medians(self):
        """
        Creates a list of physical values from the median values of the priors.

        Returns
        -------
        physical_values : [float]
            A list of physical values

        """
        return self.instance_from_unit_vector(unit_vector=[0.5] * len(self.prior_tuple_dict))

    def instance_from_unit_vector(self, unit_vector):
        """
        Creates a ModelInstance, which has an attribute and class instance corresponding to every PriorModel \
        attributed to this instance.

        This method takes as input a unit vector of parameter values, converting each to physical values via their \
        priors.

        Parameters
        ----------
        unit_vector: [float]
            A vector of physical parameter values.

        Returns
        -------
        model_instance : ModelInstance
            An object containing reconstructed model_mapper instances

        """
        arguments = dict(
            map(lambda prior_tuple, unit: (prior_tuple.prior, prior_tuple.prior.value_for(unit)),
                self.prior_tuples_ordered_by_id, unit_vector))

        return self.instance_for_arguments(arguments)

    def instance_from_physical_vector(self, physical_vector):
        """
        Creates a ModelInstance, which has an attribute and class instance corresponding to every PriorModel \
        attributed to this instance.

        This method takes as input a physical vector of parameter values, thus omitting the use of priors.

        Parameters
        ----------
        physical_vector: [float]
            A unit hypercube vector

        Returns
        -------
        model_instance : ModelInstance
            An object containing reconstructed model_mapper instances

        """
        arguments = dict(
            map(lambda prior_tuple, physical_unit: (prior_tuple.prior, physical_unit), self.prior_tuples_ordered_by_id,
                physical_vector))

        return self.instance_for_arguments(arguments)

    def instance_for_arguments(self, arguments):
        """
        Creates a ModelInstance, which has an attribute and class instance corresponding to every PriorModel
        attributed to this instance.

        Parameters
        ----------
        arguments : dict
            The dictionary representation of prior and parameter values. This is created in the model_instance_from_*
            routines.

        Returns
        -------
        model_instance : ModelInstance
            An object containing reconstructed model_mapper instances

        """

        model_instance = ModelInstance()

        for prior_model_tuple in self.prior_model_tuples:
            setattr(model_instance, prior_model_tuple.name,
                    prior_model_tuple.prior_model.instance_for_arguments(arguments))

        return model_instance

    def mapper_from_partial_prior_arguments(self, arguments):
        """
        Creates a new model mapper from a dictionary mapping_matrix existing priors to new priors, keeping existing
        priors where no mapping is provided.

        Parameters
        ----------
        arguments: {Prior: Prior}
            A dictionary mapping_matrix priors to priors

        Returns
        -------
        model_mapper: ModelMapper
            A new model mapper with updated priors.
        """
        original_prior_dict = {prior: prior for prior in self.priors}
        return self.mapper_from_prior_arguments({**original_prior_dict, **arguments})

    def mapper_from_prior_arguments(self, arguments):
        """
        Creates a new model mapper from a dictionary mapping_matrix existing priors to new priors.

        Parameters
        ----------
        arguments: {Prior: Prior}
            A dictionary mapping_matrix priors to priors

        Returns
        -------
        model_mapper: ModelMapper
            A new model mapper with updated priors.
        """
        mapper = ModelMapper()

        for prior_model_tuple in self.prior_model_tuples:
            setattr(mapper, prior_model_tuple.name,
                    prior_model_tuple.prior_model.gaussian_prior_model_for_arguments(arguments))

        return mapper

    def mapper_from_gaussian_tuples(self, tuples):
        """
        Creates a new model mapper from a list of floats describing the mean values of gaussian priors. The widths \
        of the new priors are taken from the width_config. The new gaussian priors must be provided in the same \
        order as the priors associated with model.

        Parameters
        ----------
        tuples

        Returns
        -------
        mapper: ModelMapper
            A new model mapper with all priors replaced by gaussian priors.
        """

        prior_tuples = self.prior_tuples_ordered_by_id
        prior_class_dict = self.prior_class_dict
        arguments = {}

        for i, prior_tuple in enumerate(prior_tuples):
            prior = prior_tuple.prior
            cls = prior_class_dict[prior]
            mean = tuples[i][0]
            width_type, value = conf.instance.prior_width.get_for_nearest_ancestor(cls, prior_tuple.name)
            if width_type == "r":
                width = value * mean
            elif width_type == "a":
                width = value
            else:
                raise exc.PriorException("Prior widths must be relative 'r' or absolute 'a' e.g. a, 1.0")
            if isinstance(prior, GaussianPrior):
                limits = (prior.lower_limit, prior.upper_limit)
            else:
                limits = conf.instance.prior_limit.get_for_nearest_ancestor(cls, prior_tuple.name)
            arguments[prior] = GaussianPrior(mean, max(tuples[i][1], width), *limits)

        return self.mapper_from_prior_arguments(arguments)

    def mapper_from_gaussian_means(self, means):
        """
        Creates a new model mapper from a list of floats describing the mean values of gaussian priors. The widths of \
        the new priors are taken from the width_config. The new gaussian priors must be provided in the same order as \
        the priors associated with model.

        Parameters
        ----------
        means: [float]
            A list containing the means of the gaussian priors.

        Returns
        -------
        mapper: ModelMapper
            A new model mapper with all priors replaced by gaussian priors.
        """
        return self.mapper_from_gaussian_tuples([(mean, 0) for mean in means])

    @property
    def info(self):
        """
        Use the priors that make up the model_mapper to generate information on each parameter of the overall model.

        This information is extracted from each priors *model_info* property.
        """
        info = []

        for prior_model_name, prior_model in self.flat_prior_model_tuples:

            # TODO : clean this up

            if 'lens_galaxies' not in prior_model_name and 'source_galaxies' not in prior_model_name:

                info.append(prior_model.cls.__name__ + '\n')

                prior_model_iterator = prior_model.prior_tuples + prior_model.constant_tuples

                for i, attribute_tuple in enumerate(prior_model_iterator):
                    attribute = attribute_tuple[1]

                    line = prior_model_name + '_' + attribute_tuple.name
                    info.append(line + ' ' * (60 - len(line)) + attribute.info)

                info.append('')

        return '\n'.join(info)


class ModelInstance(AbstractModel):
    """
    An object to hold model instances produced by providing arguments to a model mapper.

    @DynamicAttrs
    """

    def instances_of(self, cls):
        return [instance for source in
                [list(self.__dict__.values())] + [ls for ls in self.__dict__.values() if isinstance(ls, list)] for
                instance in
                source if isinstance(instance, cls)]

    def name_instance_tuples_for_class(self, cls):
        return [item for item in self.__dict__.items() if isinstance(item[1], cls)]


class AbstractPriorModel:
    """
    Abstract model that maps a set of priors to a particular class. Must be overridden by any prior model so that the \
    model mapper recognises its prior model attributes.
    """
    _ids = itertools.count()

    @property
    def flat_prior_model_tuples(self):
        """
        Returns
        -------
        prior_models: [(str, AbstractPriorModel)]
            A list of prior models associated with this instance
        """
        raise NotImplementedError("PriorModels must implement the flat_prior_models property")

    @property
    def prior_tuples(self):
        raise NotImplementedError()

    @property
    def constant_tuples(self):
        raise NotImplementedError()

    @property
    def prior_class_dict(self):
        raise NotImplementedError()

    def instance_for_arguments(self, arguments):
        raise NotImplementedError()


class PriorModel(AbstractPriorModel):
    """Object comprising class and associated priors
        @DynamicAttrs
    """

    @property
    def flat_prior_model_tuples(self):
        return [("", self)]

    def __init__(self, cls):
        """
        Parameters
        ----------
        cls: class
            The class associated with this instance
        """

        self.cls = cls
        self.component_number = next(self._ids)

        arg_spec = inspect.getfullargspec(cls.__init__)

        try:
            defaults = dict(zip(arg_spec.args[-len(arg_spec.defaults):], arg_spec.defaults))
        except TypeError:
            defaults = {}

        args = arg_spec.args[1:]

        if 'settings' in defaults:
            del defaults['settings']
        if 'settings' in args:
            args.remove('settings')

        for arg in args:
            if arg in defaults and isinstance(defaults[arg], tuple):
                tuple_prior = TuplePrior()
                for i in range(len(defaults[arg])):
                    attribute_name = "{}_{}".format(arg, i)
                    setattr(tuple_prior, attribute_name, self.make_prior(attribute_name, cls))
                setattr(self, arg, tuple_prior)
            else:
                setattr(self, arg, self.make_prior(arg, cls))

    @staticmethod
    def make_prior(attribute_name, cls):
        """
        Create a prior for an attribute of a class with a given name. The prior is created by searching the default
        prior config for the attribute.

        Entries in configuration with a u become uniform priors; with a g become gaussian priors; with a c become
        constants.

        If prior configuration for a given attribute is not specified in the configuration for a class then the
        configuration corresponding to the parents of that class is searched. If no configuration can be found then a
        prior exception is raised.

        Parameters
        ----------
        attribute_name: str
            The name of the attribute for which a prior is created
        cls: class
            The class to which the attribute belongs

        Returns
        -------
        prior: p.Prior
            A prior

        Raises
        ------
        exc.PriorException
            If no configuration can be found
        """
        config_arr = conf.instance.prior_default.get_for_nearest_ancestor(cls, attribute_name)
        if config_arr[0] == "u":
            return UniformPrior(config_arr[1], config_arr[2])
        elif config_arr[0] == "l":
            return LogUniformPrior(config_arr[1], config_arr[2])
        elif config_arr[0] == "g":
            limits = conf.instance.prior_limit.get_for_nearest_ancestor(cls, attribute_name)
            return GaussianPrior(config_arr[1], config_arr[2], *limits)
        elif config_arr[0] == "c":
            return Constant(config_arr[1])
        raise exc.PriorException(
            "Default prior for {} has no type indicator (u - Uniform, g - Gaussian, c - Constant".format(
                attribute_name))

    def linked_model_for_class(self, cls, make_constants_variable=False, **kwargs):
        """
        Create a PriorModel wrapping the specified class with attributes from this instance. Priors can be overridden
        using keyword arguments. Any constructor arguments of the new class for which there is no attribute associated
        with this class and no keyword argument are created from config.

        If make_constants_variable is True then constants associated with this instance will be used to set the mean
        of priors in the new instance rather than overriding them.

        Parameters
        ----------
        cls: class
            The class that the new PriorModel will wrap
        make_constants_variable: bool
            If True constants from this instance will be used to determine the mean values for priors in the new
            instance rather than overriding them
        kwargs
            Keyword arguments passed in here are used to override attributes from this instance or add new attributes

        Returns
        -------
        new_model: PriorModel
            A new prior model with priors derived from this instance
        """
        constructor_args = inspect.getfullargspec(cls).args
        attribute_tuples = self.attribute_tuples
        new_model = PriorModel(cls)
        for attribute_tuple in attribute_tuples:
            name = attribute_tuple.name
            if name in constructor_args or (
                    is_tuple_like_attribute_name(name) and tuple_name(name) in constructor_args):
                attribute = kwargs[name] if name in kwargs else attribute_tuple.value
                if make_constants_variable and isinstance(attribute, Constant):
                    new_attribute = getattr(new_model, name)
                    if isinstance(new_attribute, Prior):
                        new_attribute.mean = attribute.value
                        continue
                setattr(new_model, name, attribute)
        return new_model

    def __setattr__(self, key, value):
        if key not in ("component_number", "phase_property_position", "mapping_name"):
            try:
                if "_" in key:
                    name = key.split("_")[0]
                    tuple_prior = [v for k, v in self.tuple_prior_tuples if name == k][0]
                    setattr(tuple_prior, key, value)
                    return
            except IndexError:
                pass
            if isinstance(value, float) or isinstance(value, int):
                super().__setattr__(key, Constant(value))
                return
        super(PriorModel, self).__setattr__(key, value)

    def __getattr__(self, item):
        try:
            if "_" in item:
                return getattr([v for k, v in self.tuple_prior_tuples if item.split("_")[0] == k][0], item)

        except IndexError:
            pass
        self.__getattribute__(item)

    @property
    @cast_collection(PriorNameValue)
    def tuple_prior_tuples(self):
        """
        Returns
        -------
        tuple_prior_tuples: [(String, TuplePrior)]
        """
        return list(filter(lambda t: type(t[1]) is TuplePrior, self.__dict__.items()))

    @property
    @cast_collection(PriorNameValue)
    def direct_prior_tuples(self):
        """
        Returns
        -------
        direct_priors: [(String, Prior)]
        """
        return list(filter(lambda t: isinstance(t[1], Prior), self.__dict__.items()))

    @property
    @cast_collection(PriorNameValue)
    def prior_tuples(self):
        """
        Returns
        -------
        priors: [(String, Prior))]
        """
        return [prior for tuple_prior in self.tuple_prior_tuples for prior in
                tuple_prior[1].prior_tuples] + self.direct_prior_tuples

    @property
    @cast_collection(ConstantNameValue)
    def direct_constant_tuples(self):
        """
        Returns
        -------
        constants: [(String, Constant)]
            A list of constants
        """
        return list(filter(lambda t: isinstance(t[1], Constant), self.__dict__.items()))

    @property
    @cast_collection(ConstantNameValue)
    def constant_tuples(self):
        """
        Returns
        -------
        constants: [(String, Constant)]
        """
        return [constant_tuple for tuple_prior in self.tuple_prior_tuples for constant_tuple in
                tuple_prior[1].constant_tuples] + self.direct_constant_tuples

    @property
    @cast_collection(AttributeNameValue)
    def attribute_tuples(self):
        return self.prior_tuples + self.constant_tuples

    @property
    def prior_class_dict(self):
        return {prior[1]: self.cls for prior in self.prior_tuples}

    def instance_for_arguments(self, arguments: {Prior: float}):
        """
        Create an instance of the associated class for a set of arguments

        Parameters
        ----------
        arguments: {Prior: float}
            Dictionary mapping_matrix priors to attribute analysis_path and value pairs

        Returns
        -------
            An instance of the class
        """
        for prior, value in arguments.items():
            prior.assert_within_limits(value)
        model_arguments = {t.name: arguments[t.prior] for t in self.direct_prior_tuples}
        constant_arguments = {t.name: t.constant.value for t in self.direct_constant_tuples}
        for tuple_prior in self.tuple_prior_tuples:
            model_arguments[tuple_prior.name] = tuple_prior.prior.value_for_arguments(arguments)

        return self.cls(**{**model_arguments, **constant_arguments})

    def gaussian_prior_model_for_arguments(self, arguments):
        """
        Create a new instance of model mapper with a set of Gaussian priors based on tuples provided by a previous \
        nonlinear search.

        Parameters
        ----------
        arguments: [(float, float)]
            Tuples providing the mean and sigma of gaussians

        Returns
        -------
        new_model: ModelMapper
            A new model mapper populated with Gaussian priors
        """
        new_model = PriorModel(self.cls)

        model_arguments = {t.name: arguments[t.prior] for t in self.direct_prior_tuples}

        for tuple_prior_tuple in self.tuple_prior_tuples:
            setattr(new_model, tuple_prior_tuple.name,
                    tuple_prior_tuple.prior.gaussian_tuple_prior_for_arguments(arguments))
        for prior_tuple in self.direct_prior_tuples:
            setattr(new_model, prior_tuple.name, model_arguments[prior_tuple.name])
        for constant_tuple in self.constant_tuples:
            setattr(new_model, constant_tuple.name, constant_tuple.constant)

        return new_model


class ListPriorModel(list, AbstractPriorModel):
    @property
    def flat_prior_model_tuples(self):
        return [flat_prior_model for prior_model in self for flat_prior_model in prior_model.flat_prior_model_tuples]

    def __init__(self, prior_models):
        """
        A prior model used to represent a list of prior models for convenience.

        Parameters
        ----------
        prior_models: [PriorModel]
            A list of prior models
        """
        self.component_number = next(self._ids)
        super().__init__(prior_models)

    @property
    @cast_collection(PriorModelNameValue)
    def label_prior_model_tuples(self):
        return [(prior_model.mapping_name if hasattr(prior_model, "mapping_name") else str(i), prior_model) for
                i, prior_model in enumerate(self)]

    def instance_for_arguments(self, arguments):
        """
        Parameters
        ----------
        arguments: {Prior: float}
            A dictionary of arguments

        Returns
        -------
        model_instances: [object]
            A list of instances constructed from the list of prior models.
        """
        return [prior_model.instance_for_arguments(arguments) for prior_model in self]

    def gaussian_prior_model_for_arguments(self, arguments):
        """
        Parameters
        ----------
        arguments: {Prior: float}
            A dictionary of arguments

        Returns
        -------
        prior_models: [PriorModel]
            A new list of prior models with gaussian priors
        """
        return ListPriorModel(
            [prior_model.gaussian_prior_model_for_arguments(arguments) for prior_model in self])

    @property
    @cast_collection(PriorNameValue)
    def prior_tuples(self):
        """
        Returns
        -------
        priors: [(String, Union(Prior, TuplePrior))]
        """
        return set([prior for prior_model in self for prior in prior_model.prior_tuples])

    @property
    @cast_collection(ConstantNameValue)
    def constant_tuples(self):
        """
        Returns
        -------
        priors: [(String, Union(Prior, TuplePrior))]
        """
        return set([constant for prior_model in self for constant in prior_model.constant_tuples])

    @property
    def prior_class_dict(self):
        return {prior: cls for prior_model in self for prior, cls in prior_model.prior_class_dict.items()}


def is_tuple_like_attribute_name(attribute_name):
    """
    Determine if a string matches the pattern "{attribute_name}_#", that is if it seems to be a tuple.

    Parameters
    ----------
    attribute_name: str
        The name of some attribute that may refer to a tuple.

    Returns
    -------
    is_tuple_like: bool
        True iff the attribute name looks like that which refers to a tuple.
    """
    pattern = re.compile("^[a-zA-Z_0-9]*_[0-9]$")
    return pattern.match(attribute_name)


def tuple_name(attribute_name):
    """
    Extract the name of a tuple attribute from the name of one of its components, e.g. centre_0 -> origin

    Parameters
    ----------
    attribute_name: str
        The name of an attribute which is a component of a tuple

    Returns
    -------
    tuple_name: str
        The name of the tuple of which the attribute is a member
    """
    return "_".join(attribute_name.split("_")[:-1])
