import logging
import typing
import uuid
import yaml

from d3m import container, exceptions, utils
from d3m.metadata import base as metadata_base, pipeline as pipeline_module
from d3m.primitive_interfaces.base import MultiCallResult, CallResult
from d3m.metadata import hyperparams as hyperparams_module

from .pipeline_run_primitive_step import PipelineRunPrimitiveStep
from .pipeline_run_step import PipelineRunStep
from .pipeline_run_subpipeline_step import PipelineRunSubpipelineStep
from .run import Run
from .runtime_environment import RuntimeEnvironment
from .status import Status
from .user import User

__all__ = ('PipelineRun',)

logger = logging.getLogger(__name__)

PIPELINE_RUN_SCHEMA_VERSION = 'https://metadata.datadrivendiscovery.org/schemas/v0/pipeline_run.json'
PIPELINE_RUN_JSON = metadata_base.SCHEMAS[PIPELINE_RUN_SCHEMA_VERSION]
PIPELINE_RUN_SCHEMA_VALIDATOR, = utils.load_schema_validators(metadata_base.SCHEMAS, ('pipeline_run.json',))


class PipelineRun:
    STEPS = 'steps'
    METHOD_CALLS = 'method_calls'

    def __init__(
        self, pipeline: pipeline_module.Pipeline, problem_description: typing.Dict = None, *,
        phase: metadata_base.PipelineRunPhase, context: metadata_base.Context,
        previous_pipeline_run_id: str = None, environment: RuntimeEnvironment = None,
        users: typing.Sequence[User] = None,
    ) -> None:
        self.schema = PIPELINE_RUN_SCHEMA_VERSION

        self.pipeline = {
            'id': pipeline.id,
            'digest': pipeline.get_digest(),
        }

        self.datasets: typing.List[typing.Dict[str, typing.Any]] = []

        self.problem: typing.Dict[str, typing.Any] = None
        if problem_description is not None:
            self.set_problem(problem_description)

        self.steps: typing.List[PipelineRunStep] = []
        self.status = Status()
        self.run: Run = Run(phase)
        self.context = context
        self.previous_pipeline_run_id = previous_pipeline_run_id
        if users is None:
            self.users: typing.List[User] = []
        else:
            self.users = list(users)
        self.environment = environment

        self._components: typing.Dict[str, typing.Any] = {}

    def _to_json_structure(self) -> typing.Dict:
        json_structure = {
            'schema': self.schema,
            'pipeline': self.pipeline,
            'datasets': self.datasets,
            'steps': [step.to_json_structure() for step in self.steps],
            'status': self.status.to_json_structure(),
            'run': self.run.to_json_structure(),
            'environment': self.environment.to_json_structure()
        }

        if self.previous_pipeline_run_id is not None:
            json_structure['previous_pipeline_run'] = {
                'id': self.previous_pipeline_run_id
            }

        if self.context is not None:
            json_structure['context'] = self._context_to_json_structure()

        if self.problem is not None:
            json_structure['problem'] = self.problem

        if len(self.users) > 0:
            json_structure['users'] = [user.to_json_structure() for user in self.users]

        json_structure['id'] = utils.compute_hash_id(json_structure)

        return json_structure

    def to_json_structure(self) -> typing.Dict:
        json_structure = self._to_json_structure()

        PIPELINE_RUN_SCHEMA_VALIDATOR.validate(json_structure)

        return json_structure

    def _context_to_json_structure(self) -> str:
        return self.context.name

    def to_yaml(self, file: typing.TextIO, *, appending: bool = False, **kwargs: typing.Any) -> typing.Optional[str]:
        obj = self.to_json_structure()

        if 'default_flow_style' not in kwargs:
            kwargs['default_flow_style'] = False
        if appending and 'explicit_start' not in kwargs:
            kwargs['explicit_start'] = True

        return yaml.safe_dump(obj, stream=file, **kwargs)

    def add_input_dataset(self, dataset: container.Dataset) -> None:
        metadata = dataset.metadata.query(())
        if 'id' in metadata and 'digest' in metadata:
            self.datasets.append({
                'id': metadata['id'],
                'digest': metadata['digest']
            })
        else:
            # does not validate against schema: dataset.metadata.to_json_structure()[0]['metadata']
            self.datasets.append({
                'id': '0000000000000000000000000000000000000000000000000000000000000000',
                'digest': '0000000000000000000000000000000000000000000000000000000000000000'
            })

    def add_primitive_step(self, step: pipeline_module.PrimitiveStep) -> int:
        if not isinstance(step, pipeline_module.PrimitiveStep):
            raise exceptions.InvalidArgumentTypeError('step must be of type PrimitiveStep, not {}'.format(type(step)))
        self.steps.append(
            PipelineRunPrimitiveStep(step)
        )
        return len(self.steps) - 1

    def _get_primitive_step(self, primitive_step_id: int) -> PipelineRunPrimitiveStep:
        if primitive_step_id >= len(self.steps):
            raise exceptions.InvalidArgumentValueError('There does not exist a step with id {}'.format(primitive_step_id))

        primitive_step = self.steps[primitive_step_id]
        if not isinstance(primitive_step, PipelineRunPrimitiveStep):
            raise exceptions.InvalidArgumentValueError('Step id {} does not refer to a PipelineRunPrimitiveStep'.format(primitive_step_id))

        return primitive_step

    def set_primitive_step_hyperparams(
        self, primitive_step_id: int,
        hyperparams: hyperparams_module.Hyperparams,
        pipeline_hyperparams: typing.Dict[str, typing.Dict],
    ) -> None:
        primitive_step = self._get_primitive_step(primitive_step_id)
        primitive_step.set_hyperparams(hyperparams, pipeline_hyperparams)

    def set_primitive_step_random_seed(self, primitive_step_id: int, random_seed: int) -> None:
        primitive_step = self._get_primitive_step(primitive_step_id)
        primitive_step.set_random_seed(random_seed)

    def add_subpipeline_step(self, subpipeline_run: 'PipelineRun') -> int:
        pipeline_run_subpipeline_step = PipelineRunSubpipelineStep()
        for step_id, step in enumerate(subpipeline_run.steps):
            step_json = step.to_json_structure()
            pipeline_run_subpipeline_step.add_step(step_json)
            state = step_json['status']['state']
            message = step_json['status'].get('message', None)
            if state == metadata_base.PipelineRunStatusState.SUCCESS.name:
                pipeline_run_subpipeline_step.set_successful(message)
            elif state == metadata_base.PipelineRunStatusState.FAILURE.name:
                message = 'Failed on subpipeline step {}:\n{}'.format(step_id, message)
                pipeline_run_subpipeline_step.set_failed(message)
                message = 'Failed on step {}:\n{}'.format(len(self.steps) - 1, message)
                self.status.set_failed(message)
            else:
                raise exceptions.UnexpectedValueError('unknown subpipeline status state: {}'.format(state))

        self.steps.append(pipeline_run_subpipeline_step)

        return len(self.steps) - 1

    def add_method_call_to_primitive_step(
        self, primitive_step_id: int, method_name: str, *,
        runtime_arguments: typing.Dict = None, environment: RuntimeEnvironment = None
    ) -> typing.Tuple[int, int]:
        if runtime_arguments is None:
            runtime_arguments = {}

        # todo allow runtime arguments not specified in pipeline?
        primitive_step = self._get_primitive_step(primitive_step_id)
        method_call_id = primitive_step.add_method_call(
            method_name, runtime_arguments=runtime_arguments, environment=environment
        )
        return (primitive_step_id, method_call_id)

    def get_method_call_logging_callback(
        self, step_and_method_call_id: typing.Tuple[int, int]
    ) -> typing.Callable:
        step_id, method_call_id = step_and_method_call_id
        primitive_step = self._get_primitive_step(step_id)
        return primitive_step.get_method_call_logging_callback(method_call_id)

    def set_method_call_start_timestamp(self, step_and_method_call_id: typing.Tuple[int, int]) -> None:
        step_id, method_call_id = step_and_method_call_id
        primitive_step = self._get_primitive_step(step_id)
        primitive_step.set_method_call_start_timestamp(method_call_id)

    def set_method_call_end_timestamp(self, step_and_method_call_id: typing.Tuple[int, int]) -> None:
        step_id, method_call_id = step_and_method_call_id
        primitive_step = self._get_primitive_step(step_id)
        primitive_step.set_method_call_end_timestamp(method_call_id)

    def set_method_call_result_metadata(
        self, step_and_method_call_id: typing.Tuple[int, int],
        result: typing.Union[CallResult, MultiCallResult]
    ) -> None:
        step_id, method_call_id = step_and_method_call_id
        primitive_step = self._get_primitive_step(step_id)
        primitive_step.set_method_call_result_metadata(method_call_id, result)

    def run_successful(self, message: str = None) -> None:
        self.status.set_successful(message)

    def step_successful(self, step_id: int, message: str = None) -> None:
        if step_id >= len(self.steps):
            raise exceptions.InvalidArgumentValueError('There does not exist a step with id {}'.format(step_id))
        self.steps[step_id].set_successful(message)

    def method_call_successful(self, step_and_method_call_id: typing.Tuple[int, int], message: str = None) -> None:
        step_id, method_call_id = step_and_method_call_id
        primitive_step = self._get_primitive_step(step_id)
        primitive_step.set_method_call_successful(method_call_id, message)

    def run_failed(self, message: str = None) -> None:
        self.status.set_failed(message)

    def step_failed(self, step_id: int, message: str = None) -> None:
        if step_id >= len(self.steps):
            raise exceptions.InvalidArgumentValueError('There does not exist a step with id {}'.format(step_id))
        self.steps[step_id].set_failed(message)

        message = 'Failed on step {}:\n{}'.format(step_id, message)
        self.run_failed(message)

    def method_call_failed(self, step_and_method_call_id: typing.Tuple[int, int], message: str = None) -> None:
        step_id, method_call_id = step_and_method_call_id
        primitive_step = self._get_primitive_step(step_id)
        primitive_step.set_method_call_failed(method_call_id, message)

        message = 'Failed on method call {}:\n{}'.format(method_call_id, message)
        self.step_failed(step_id, message)

    def is_failed(self) -> bool:
        return self.status.is_failed()

    def set_problem(self, problem_description: typing.Dict) -> None:
        self.problem = {
            'id': problem_description['id'],
            'digest': problem_description['digest'],
        }

    def set_fold_group(self, fold_group_id: uuid.UUID, fold: int) -> None:
        self.run.set_fold_group(fold_group_id, fold)

    def set_data_preparation_pipeline_run(
        self, data_preparation_pipeline_run: 'PipelineRun'
    ) -> None:
        self.run.set_data_preparation_pipeline(
            data_preparation_pipeline_run.pipeline,
            data_preparation_pipeline_run.steps,
            data_preparation_pipeline_run.status,
        )
        if data_preparation_pipeline_run.is_failed():
            message = 'Data preparation pipeline failed:\n{}'.format(
                data_preparation_pipeline_run.status.message
            )
            self.status.set_failed(message)

    def set_scoring_pipeline_run(self, scoring_pipeline_run: 'PipelineRun') -> None:
        self.run.set_scoring_pipeline(
            scoring_pipeline_run.pipeline,
            scoring_pipeline_run.steps,
            scoring_pipeline_run.status,
        )
        if scoring_pipeline_run.is_failed():
            message = 'Scoring pipeline failed:\n{}'.format(
                scoring_pipeline_run.status.message
            )
            self.status.set_failed(message)

    def set_scores(
        self, scores: container.DataFrame, metrics: typing.Sequence[typing.Dict], problem_description: typing.Dict,
    ) -> None:
        self.run.set_scores(scores, metrics, problem_description)

    def set_predictions(self, predictions: container.DataFrame) -> None:
        self.run.set_predictions(predictions)

    def add_user(self, user: User) -> None:
        self.users.append(user)

    def get_id(self) -> str:
        return self._to_json_structure()['id']
