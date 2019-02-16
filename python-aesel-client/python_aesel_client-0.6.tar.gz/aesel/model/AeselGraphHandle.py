#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Typical animation is done by manipulating keyframes, and then adjust the
movement graphs generated in order to get exactly the animation desired.

A Graph Handle allows replication of not just the keyframes, but also the
interpolated graphs in-between them.

:left_type: The type of the left graph handle.
:left_x: The x-value of the left graph handle.
:left_y: The y-value of the left graph handle.
:right_type: The type of the right graph handle.
:right_x: The x-value of the right graph handle.
:right_y: The y-value of the right graph handle.
"""

"""
Apache2 License Notice
Copyright 2018 Alex Barry
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

class AeselGraphHandle(object):
    def __init__(self):
        self.left_type = None
        self.left_x = None
        self.left_y = None
        self.right_type = None
        self.right_x = None
        self.right_y = []
