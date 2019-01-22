import json
from typing import Optional, Any, Dict, List

import grpc
from google.protobuf.empty_pb2 import Empty
from google.protobuf.wrappers_pb2 import Int64Value, StringValue, BoolValue
from optuna import structs, distributions, logging
from optuna.storages import base
from optuna.storages.rdb.models import NOT_FOUND_MSG

from optuna_firestore_proto.study_pb2 import CreateNewStudyIdRequest, SetStudyUserAttrRequest, \
    StudyMsg, SetStudyDirectionRequest, SetStudySystemAttrRequest, GetAllStudySummariesResponse, StudySummaryMsg
from optuna_firestore_proto.study_pb2_grpc import StudyServiceStub
from optuna_firestore_proto.trial_pb2 import CreateNewTrialIdRequest, CreateNewTrialIdResponse, TrialMsg, \
    SetTrialStateRequest, SetTrialValueRequest, SetTrialParamRequest, TrialParamMsg, SetTrialIntermediateValueRequest, \
    SetTrialUserAttrRequest, GetAllTrialsRequest, GetAllTrialsResponse, SetTrialSystemAttrRequest
from optuna_firestore_proto.trial_pb2_grpc import TrialServiceStub


def create_rpc_storage(target: str):
    study_service_stub = StudyServiceStub(grpc.insecure_channel(target))
    trial_service_stub = TrialServiceStub(grpc.insecure_channel(target))
    return RPCStorage(study_service_stub, trial_service_stub)


class RPCStorage(base.BaseStorage):
    def __init__(self, study_service_stub: StudyServiceStub, trial_service_stub: TrialServiceStub):
        self.study_service = study_service_stub
        self.trial_service = trial_service_stub
        self.logger = logging.get_logger(__name__)

    def create_new_study_id(self, study_name: Optional[str] = None) -> int:
        req = CreateNewStudyIdRequest(study_name=study_name)

        try:
            study_msg: StudyMsg = self.study_service.CreateNewStudyId(req)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise structs.DuplicatedStudyError(
                    "Another study with name '{}' already exists. "
                    "Please specify a different name, or reuse the existing one "
                    "by setting `load_if_exists` (for Python API) or "
                    "`--skip-if-exists` flag (for CLI).".format(study_name))
            raise e

        self.logger.info('A new study created with name: {}'.format(study_name))

        return study_msg.study_id

    def set_study_user_attr(self, study_id: int, key: str, value: Any) -> None:
        req = SetStudyUserAttrRequest(
            study_id=study_id,
            key=key,
            value_json=json.dumps(value, separators=(',', ':'))
        )
        self.study_service.SetStudyUserAttr(req)

    def set_study_direction(self, study_id: int, direction: structs.StudyDirection) -> None:
        req = SetStudyDirectionRequest(study_id=study_id, direction=direction.value)

        try:
            self.study_service.SetStudyDirection(req)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.FAILED_PRECONDITION:
                raise ValueError(e.details())
            raise e

    def set_study_system_attr(self, study_id: int, key: str, value: Any) -> None:
        req = SetStudySystemAttrRequest(
            study_id=study_id,
            key=key,
            value_json=json.dumps(value, separators=(',', ':'))
        )
        self.study_service.SetStudySystemAttr(req)

    def get_study_id_from_name(self, study_name: str) -> int:
        req = StringValue(value=study_name)
        study_msg: StudyMsg = self.study_service.GetStudyFromName(req)
        return study_msg.study_id

    def get_study_name_from_id(self, study_id: int) -> str:
        req = Int64Value(value=study_id)
        study_msg: StudyMsg = self.study_service.GetStudyFromId(req)
        return study_msg.study_name

    def get_study_direction(self, study_id: int) -> structs.StudyDirection:
        req = Int64Value(value=study_id)
        study_msg: StudyMsg = self.study_service.GetStudyFromId(req)
        return structs.StudyDirection(study_msg.direction)

    def get_study_user_attrs(self, study_id: int) -> Dict[str, Any]:
        req = Int64Value(value=study_id)
        study_msg: StudyMsg = self.study_service.GetStudyFromId(req)
        return {
            k: json.loads(v)
            for k, v
            in zip(study_msg.user_attributes.keys(), study_msg.user_attributes.values())
        }

    def get_study_system_attrs(self, study_id: int) -> Dict[str, Any]:
        req = Int64Value(value=study_id)
        study_msg: StudyMsg = self.study_service.GetStudyFromId(req)
        return {
            k: json.loads(v)
            for k, v
            in zip(study_msg.system_attributes.keys(), study_msg.system_attributes.values())
        }

    def get_all_study_summaries(self) -> List[structs.StudySummary]:
        res: GetAllStudySummariesResponse = self.study_service.GetAllStudySummaries(Empty())

        return [_summary_msg_to_summary(s) for s in res.study_summaries]

    def create_new_trial_id(self, study_id: int) -> int:
        req = CreateNewTrialIdRequest(study_id=study_id)
        res: CreateNewTrialIdResponse = self.trial_service.CreateNewTrialId(req)
        return res.trial_id

    def set_trial_state(self, trial_id: int, state: structs.TrialState) -> None:
        req = SetTrialStateRequest(trial_id=trial_id, state=state.value)
        self.trial_service.SetTrialState(req)

    def set_trial_param(self,
                        trial_id: int,
                        param_name: str,
                        param_value_internal: float,
                        distribution: distributions.BaseDistribution) -> bool:
        req = SetTrialParamRequest(
            trial_id=trial_id,
            param_name=param_name,
            param_value=param_value_internal,
            distribution_json=distributions.distribution_to_json(distribution)
        )
        res: BoolValue = self.trial_service.SetTrialParam(req)

        return res.value

    def get_trial_param(self, trial_id: int, param_name: str) -> float:
        trial_req = Int64Value(value=trial_id)
        trial_msg: TrialMsg = self.trial_service.GetTrialFromId(trial_req)
        trial_param_msg: TrialParamMsg = trial_msg.trial_params[param_name]

        if not trial_param_msg.is_exist:
            raise ValueError(NOT_FOUND_MSG)

        return trial_param_msg.param_value

    def set_trial_value(self, trial_id: int, value: float) -> None:
        req = SetTrialValueRequest(trial_id=trial_id, value=value)
        self.trial_service.SetTrialValue(req)

    def set_trial_intermediate_value(self, trial_id: int, step: int, intermediate_value: float) -> bool:
        req = SetTrialIntermediateValueRequest(trial_id=trial_id, step=step, intermediate_value=intermediate_value)
        res: BoolValue = self.trial_service.SetTrialIntermediateValue(req)

        return res.value

    def set_trial_user_attr(self, trial_id: int, key: str, value: Any) -> None:
        req = SetTrialUserAttrRequest(
            trial_id=trial_id,
            key=key,
            value_json=json.dumps(value, separators=(',', ':'))
        )
        self.trial_service.SetTrialUserAttr(req)

    def set_trial_system_attr(self, trial_id: int, key: str, value: Any) -> None:
        req = SetTrialSystemAttrRequest(
            trial_id=trial_id,
            key=key,
            value_json=json.dumps(value, separators=(',', ':'))
        )
        self.trial_service.SetTrialSystemAttr(req)

    def get_trial(self, trial_id: int) -> structs.FrozenTrial:
        req = Int64Value(value=trial_id)
        trial_msg: TrialMsg = self.trial_service.GetTrialFromId(req)

        return _msg_to_trial(trial_msg)

    def get_all_trials(self, study_id: int) -> List[structs.FrozenTrial]:
        req = GetAllTrialsRequest(study_id=study_id)
        res: GetAllTrialsResponse = self.trial_service.GetAllTrials(req)

        return [_msg_to_trial(trial_msg) for trial_msg in res.trials]

    def get_n_trials(self, study_id: int, state: Optional[structs.TrialState] = None) -> int:
        trials = self.get_all_trials(study_id)
        if state is None:
            return len(trials)
        return len([t for t in trials if t.state == state])


def _msg_to_trial(msg: TrialMsg) -> structs.FrozenTrial:
    if msg.HasField('datetime_start'):
        datetime_start = msg.datetime_start.ToDatetime()
    else:
        datetime_start = None

    if msg.HasField('datetime_complete'):
        datetime_complete = msg.datetime_complete.ToDatetime()
    else:
        datetime_complete = None

    value = msg.value if msg.HasField('value') else None

    user_attrs = {
        k: json.loads(v)
        for k, v
        in zip(msg.user_attributes.keys(), msg.user_attributes.values())
    }

    intermediate_values = {
        k: v
        for k, v
        in zip(msg.trial_values.keys(), msg.trial_values.values())
    }

    params = {}
    params_in_internal_repr = {}
    for k, v in zip(msg.trial_params.keys(), msg.trial_params.values()):
        distribution = distributions.json_to_distribution(v.distribution_json)
        params[k] = distribution.to_external_repr(v.param_value)
        params_in_internal_repr[k] = v.param_value

    return structs.FrozenTrial(
        trial_id=msg.trial_id,
        state=structs.TrialState(msg.state),
        params=params,
        user_attrs=user_attrs,
        system_attrs={},
        value=value,
        intermediate_values=intermediate_values,
        params_in_internal_repr=params_in_internal_repr,
        datetime_start=datetime_start,
        datetime_complete=datetime_complete,
    )


def _summary_msg_to_summary(msg: StudySummaryMsg) -> structs.StudySummary:
    if msg.HasField('best_trial'):
        trial = _msg_to_trial(msg.best_trial)
    else:
        trial = None

    if msg.HasField('datetime_start'):
        datetime_start = msg.datetime_start.ToDatetime()
    else:
        datetime_start = None

    return structs.StudySummary(
        study_id=msg.study_id,
        study_name=msg.study_name,
        direction=structs.StudyDirection(msg.direction),
        user_attrs={
            k: json.loads(v)
            for k, v
            in zip(msg.user_attributes.keys(), msg.user_attributes.values())
        },
        system_attrs={
            k: json.loads(v)
            for k, v
            in zip(msg.system_attributes.keys(), msg.system_attributes.values())
        },
        n_trials=msg.n_trials,
        best_trial=trial,
        datetime_start=datetime_start
    )
