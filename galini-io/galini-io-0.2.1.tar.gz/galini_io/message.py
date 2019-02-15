# Copyright 2018 Francesco Ceccon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime
import galini_io.message_pb2 as proto

DEFAULT_LEVEL = 0

def text_message(solver, run_id, content, level=None, timestamp=None):
    if level is None:
        level = DEFAULT_LEVEL
    message = solver_message(solver, run_id, timestamp)
    message.text.level = level
    message.text.content = content

    return message


def tensor_message(solver, run_id, filename, group, dataset, sizes,
                   timestamp=None):
    message = solver_message(solver, run_id, timestamp)
    message.tensor.filename = filename
    message.tensor.group_ = group
    message.tensor.dataset = dataset
    message.tensor.sizes.extend(sizes)
    return message


def solve_start_message(solver, run_id, timestamp=None):
    message = solver_message(solver, run_id, timestamp)
    message.solve_start.flag = True
    return message


def solve_end_message(solver, run_id, timestamp=None):
    message = solver_message(solver, run_id, timestamp)
    message.solve_end.flag = True
    return message


def update_variable_message(solver, run_id, name, iteration, value, timestamp=None):
    message = solver_message(solver, run_id, timestamp)
    message.update_variable.name = name
    message.update_variable.iteration = iteration
    message.update_variable.value = value
    return message


def add_bab_node_message(solver, run_id, coordinate, lower_bound, upper_bound,
                         branching_variables=None, timestamp=None):
    message = solver_message(solver, run_id, timestamp)
    for value in coordinate:
        message.add_bab_node.coordinate.append(value)
    message.add_bab_node.lower_bound = lower_bound
    message.add_bab_node.upper_bound = upper_bound
    if branching_variables is None:
        branching_variables = []
    for (br_name, br_lower_bound, br_upper_bound) in branching_variables:
        variable_info = message.add_bab_node.variables_information.add()
        variable_info.variable_name = br_name
        variable_info.lower_bound = br_lower_bound
        variable_info.upper_bound = br_upper_bound
    return message


def prune_bab_node_message(solver, run_id, coordinate, timestamp=None):
    message = solver_message(solver, run_id, timestamp)
    for value in coordinate:
        message.prune_bab_node.coordinate.append(value)
    return message


def solver_message(solver, run_id, timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()

    message = proto.SolverMessage()
    if solver:
        message.solver = solver
    if run_id:
        message.run_id = run_id
    message.timestamp = timestamp_to_uint64(timestamp)
    return message


def timestamp_to_uint64(timestamp):
    """Convert timestamp to milliseconds since epoch."""
    return int(timestamp.timestamp() * 1e3)
