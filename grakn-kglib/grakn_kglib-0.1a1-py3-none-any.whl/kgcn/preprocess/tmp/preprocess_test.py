#
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
#

preprocessors = {'role_type': lambda x: tf.convert_to_tensor(x, dtype=tf.string),
                     'role_direction': lambda x: x,
                     'neighbour_type': lambda x: tf.convert_to_tensor(x, dtype=tf.string),
                     'neighbour_data_type': lambda x: x,
                     'neighbour_value_long': lambda x: x,
                     'neighbour_value_double': lambda x: x,
                     'neighbour_value_boolean': lambda x: x,
                     'neighbour_value_date': date.datetime_to_unixtime,
                     'neighbour_value_string': lambda x: x}