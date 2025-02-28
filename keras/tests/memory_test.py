# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Tests for memory leaks in eager execution.

It is possible that this test suite will eventually become flaky due to taking
too long to run (since the tests iterate many times), but for now they are
helpful for finding memory leaks since not all PyObject leaks are found by
introspection (test_util decorators). Please be careful adding new tests here.
"""

import tensorflow.compat.v2 as tf

import keras
from tensorflow.python.eager.memory_tests import memory_test_util


class SingleLayerNet(keras.Model):
  """Simple keras model used to ensure that there are no leaks."""

  def __init__(self):
    super().__init__()
    self.fc1 = keras.layers.Dense(5)

  def call(self, x):
    return self.fc1(x)


class MemoryTest(tf.test.TestCase):

  def testMemoryLeakInSimpleModelForwardOnly(self):
    if not memory_test_util.memory_profiler_is_available():
      self.skipTest("memory_profiler required to run this test")

    inputs = tf.zeros([32, 100], tf.float32)
    net = SingleLayerNet()

    def f():
      with tf.GradientTape():
        net(inputs)

    memory_test_util.assert_no_leak(f)

  def testMemoryLeakInSimpleModelForwardAndBackward(self):
    if not memory_test_util.memory_profiler_is_available():
      self.skipTest("memory_profiler required to run this test")

    inputs = tf.zeros([32, 100], tf.float32)
    net = SingleLayerNet()

    def f():
      with tf.GradientTape() as tape:
        result = net(inputs)

      tape.gradient(result, net.variables)

      del tape

    memory_test_util.assert_no_leak(f)


if __name__ == "__main__":
  tf.test.main()
