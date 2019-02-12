import typing

from d3m import exceptions
from d3m.metadata import base as metadata_base, hyperparams as hyperparams_module, pipeline as pipeline_module
from d3m.primitive_interfaces.base import CallResult, MultiCallResult

from .method_call import MethodCall
from .pipeline_run_step import PipelineRunStep
from .runtime_environment import RuntimeEnvironment


class PipelineRunPrimitiveStep(PipelineRunStep):
    def __init__(
        self, step: pipeline_module.PrimitiveStep, environment: RuntimeEnvironment = None
    ) -> None:
        super().__init__(
            step_type=metadata_base.PipelineStepType.PRIMITIVE,
            environment=environment
        )
        self.hyperparams: hyperparams_module.Hyperparams = None
        self.pipeline_hyperparams: typing.Set[str] = None
        self.random_seed: typing.Optional[int] = None
        self.method_calls: typing.List[MethodCall] = []
        self.arguments = step.arguments

    def to_json_structure(self) -> typing.Dict:
        json_structure = super().to_json_structure()
        json_structure['method_calls'] = self._method_calls_to_json_structure()

        if self.random_seed is not None:
            json_structure['random_seed'] = self.random_seed

        hyperparams_json_structure = self._hyperparams_to_json_structure()
        if hyperparams_json_structure is not None:
            json_structure['hyperparams'] = hyperparams_json_structure

        return json_structure

    def _hyperparams_to_json_structure(self) -> typing.Optional[typing.Dict]:
        if self.hyperparams is None:
            return None

        hyperparams_json = {}

        for hyperparameter_name, value in self.hyperparams.items():
            if hyperparameter_name in self.pipeline_hyperparams:
                continue

            hyperparams_json[hyperparameter_name] = {
                'type': metadata_base.ArgumentType.VALUE.name,
                'data': self.hyperparams.configuration[hyperparameter_name].value_to_json(value),
            }

        if hyperparams_json:
            return hyperparams_json
        else:
            return None

    def _method_calls_to_json_structure(self) -> typing.List:
        json_structure = []
        for method_call in self.method_calls:
            json_structure.append(method_call.to_json_structure())
        return json_structure

    def set_hyperparams(
        self, hyperparams: hyperparams_module.Hyperparams,
        pipeline_hyperparams: typing.Dict[str, typing.Dict],
    ) -> None:
        self.hyperparams = hyperparams
        self.pipeline_hyperparams = set(pipeline_hyperparams.keys())

    def set_random_seed(self, random_seed: int) -> None:
        self.random_seed = random_seed

    def add_method_call(
        self, method_name: str, *, runtime_arguments: typing.Dict = None,
        environment: RuntimeEnvironment = None
    ) -> int:
        """
        Returns
        -------
        int
            The id of the method call.
        """

        if runtime_arguments is None:
            runtime_arguments = {}

        method_call = MethodCall(
            method_name, runtime_arguments=runtime_arguments, environment=environment
        )
        self.method_calls.append(method_call)
        return len(self.method_calls) - 1

    def _get_method_call(self, method_call_id: int) -> MethodCall:
        if method_call_id >= len(self.method_calls):
            raise exceptions.InvalidArgumentValueError('There does not exist a method call with id {}'.format(method_call_id))

        return self.method_calls[method_call_id]

    def set_method_call_start_timestamp(self, method_call_id: int) -> None:
        method_call = self._get_method_call(method_call_id)
        method_call.set_start_timestamp()

    def set_method_call_end_timestamp(self, method_call_id: int) -> None:
        method_call = self._get_method_call(method_call_id)
        method_call.set_end_timestamp()

    def set_method_call_result_metadata(self, method_call_id: int, result: typing.Union[CallResult, MultiCallResult]) -> None:
        method_call = self._get_method_call(method_call_id)
        method_call.set_result_metadata(result)

    def set_method_call_successful(self, method_call_id: int, message: str = None) -> None:
        method_call = self._get_method_call(method_call_id)
        method_call.set_successful(message)

    def set_method_call_failed(self, method_call_id: int, message: str = None) -> None:
        method_call = self._get_method_call(method_call_id)
        method_call.set_failed(message)

    def get_method_call_logging_callback(self, method_call_id: int) -> typing.Callable:
        method_call = self._get_method_call(method_call_id)
        return method_call.add_log_record
