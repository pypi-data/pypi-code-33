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

import unittest

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub


class TestShit(unittest.TestCase):
    def test_stuff(self):
        # embed = hub.Module("https://tfhub.dev/google/Wiki-words-250/1")
        # embeddings = embed(["cat is on the mat", "dog is in the fog"])
        # print(embeddings)

        # In case of issues https://github.com/tensorflow/hub/issues/61
        with tf.Graph().as_default():
            module_url = "https://tfhub.dev/google/nnlm-en-dim128-with-normalization/1"
            embed = hub.Module(module_url)
            embeddings = embed(["A long sentence.",
                                "single-word",
                                "http://example.com",
                                "Accipitridae",
                                "Haliaeetus",
                                "North America",
                                "GB",
                                "SG",
                                "BY",
                                "specimens",
                                "S",
                                "W",
                                "Oryx dammah",
                                "trophies",
                                "seeds",
                                "Sclerocactus papyracanthus",
                                "kg",
                                "ml",
                                ""])

            with tf.Session() as sess:
                sess.run(tf.global_variables_initializer())
                sess.run(tf.tables_initializer())

                output_embeddings = sess.run(embeddings)
                print(output_embeddings)
                np.savetxt('embeddings.txt', output_embeddings)  # , fmt='%d')
