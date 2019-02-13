from typing import List

import json

from uttut.elements import Datum

from .ops.base import LabelAligner
from .step import Step
from .intermediate import Intermediate
from .ops import op_factory as default_factory
from .utils import unpack_datum


class Pipe:

    def __init__(self, operator_factory=None):
        self._steps = []
        self._step_info = []
        self._checkpoints = {}

        self.operator_factory = operator_factory
        if self.operator_factory is None:
            self.operator_factory = default_factory

    def add(self, op_name: str, op_kwargs=None, checkpoint=None):
        """Add steps based on the operation name.

        This method creates a step, which has an op. The op
        is created.

        Args:
            op_name (str): the name of operator
            op_kwargs (dict): the corresponding of keyword arguments
            checkpoint (str): the name of checkpoint

        Raises:
            KeyError if the input checkpoint has existed in self._checkpoints

        """
        if op_kwargs is None:
            op_kwargs = {}

        op = self.operator_factory[op_name](**op_kwargs)
        step = Step(op)

        self._validate_steps(step)

        self._push_step(step)
        self._push_step_info(op_name, op_kwargs)
        self._push_checkpoint(checkpoint)

    def _validate_steps(self, step: Step):
        if len(self._steps) > 0:
            target_type = self._steps[-1].output_type
            in_type = step.input_type
            if in_type != target_type:
                raise TypeError(
                    "InputType of the step op is not valid."
                    f"Got {in_type}, but requires {target_type}")

    def _push_checkpoint(self, name: str):
        if name is not None:
            if name in self._checkpoints:
                raise KeyError(f"duplicated checkpoints {name}")
            self._checkpoints[name] = len(self._steps)

    def _push_step(self, step: Step):
        self._steps.append(step)

    def _push_step_info(self, name: str, kwargs: dict):
        self._step_info.append(
            {  # for serialization
                'op_name': name,
                'op_kwargs': kwargs,
            },
        )

    def __eq__(self, other):
        same_op_factory = self.operator_factory == other.operator_factory
        same_steps = self._steps == other._steps
        same_step_info = self._step_info == other._step_info
        same_checkpoints = self._checkpoints == other._checkpoints
        return same_op_factory and same_steps and same_step_info and same_checkpoints

    def transform(self, datum: Datum):
        """Process data based on Steps(Ops).

        This method processes datum according to the Pipe's steps.

        Arg:
            datum (Datum)

        Returns:
            output_sequence: transfromed sequence
            intent_labels (ints)
            entity_labels (ints)W
            label_alingers: an instance of LabelAlignerSequence
            intermediate: an instance of Intermediate

        """
        input_sequence, intent_labels, entity_labels = unpack_datum(datum)
        output_sequence, label_aligners, intermediate = self.transform_sequence(input_sequence)
        updated_entity_labels = label_aligners.transform(entity_labels)

        return output_sequence, intent_labels, updated_entity_labels, label_aligners, intermediate

    def transform_sequence(self, input_sequence):
        """Process input_sequence based on Steps(Ops).

        This method processes input_sequence according to the Pipe's steps.

        Arg:
            input_sequence

        Returns:
            output_sequence: transfromed sequence
            label_alingers: an instance of LabelAlignerSequence
            intermediate: an instance of Intermediate

        """
        intermediate = Intermediate(self._checkpoints)

        intermediate.add(input_sequence)
        label_aligners = LabelAlignerSequence()

        for step in self._steps:
            input_sequence, label_aligner = step.transform(input_sequence)
            intermediate.add(input_sequence)
            label_aligners.add(label_aligner)

        return input_sequence, label_aligners, intermediate

    def serialize(self) -> str:
        to_serialize = {
            'steps': self._step_info,
            'checkpoints': self._checkpoints,
        }
        return json.dumps(to_serialize)

    @classmethod
    def deserialize(cls, serialized_str: str, operator_factory=None) -> 'Pipe':
        pipe = cls(operator_factory)
        pipe_bundle = json.loads(serialized_str)
        # restore steps
        step_infos = pipe_bundle['steps']
        for step_info in step_infos:
            pipe.add(
                op_name=step_info['op_name'],
                op_kwargs=step_info['op_kwargs'],
            )
        # restore checkpoints
        pipe._checkpoints = pipe_bundle['checkpoints']
        return pipe


class LabelAlignerSequence:

    def __init__(self):
        self.collections = []

    def add(self, label_aligner: LabelAligner):
        """Append label_aligner into collections

        Arg:
            label_aligner: an instance of LabelAligner

        """
        self.collections.append(label_aligner)

    def transform(self, labels: List[int]) -> List[int]:
        """Update labels based on given label_aligners

        Arg:
            labels (ints): raw labels (entity)

        Return:
            ints: updated labels which has the same length as
                  transformed sequence

        """
        for label_aligner in self.collections:
            labels = label_aligner.transform(labels)
        return labels

    def inverse_transform(self, labels: List[int]) -> List[int]:
        """Realign model prediction to its original input

        Arg:
            labels (ints): model prediction (entity)

        Return:
            ints: updated labels which has the same length as
                  original input (utterance)

        """
        for label_aligner in self.collections[::-1]:
            labels = label_aligner.inverse_transform(labels)
        return labels
