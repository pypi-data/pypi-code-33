"""
Copyright 2019 Conductor, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import datetime
import math

EPOCH = datetime.datetime.strptime("2009-07-26", "%Y-%m-%d")


def week_number(date):
    """Convert date of format YYYY-MM-DD to Searchlight Time Period Number"""
    try:
        return math.ceil((datetime.datetime.strptime(date, "%Y-%m-%d") - EPOCH).days / 7)
    except ValueError:
        raise ValueError("Date must match format YYYY-MM-DD")
