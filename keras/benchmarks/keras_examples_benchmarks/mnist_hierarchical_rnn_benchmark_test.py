# Copyright 2020 The TensorFlow Authors. All Rights Reserved.
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
"""Benchmarks on Hierarchical RNN on MNIST digits."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow.compat.v2 as tf

from keras.benchmarks import benchmark_util


class HierarchicalRNNBenchmark(tf.test.Benchmark):
  """Benchmarks for Hierarchical RNN using `tf.test.Benchmark`."""

  def __init__(self):
    super().__init__()
    self.num_classes = 10
    self.row_hidden, self.col_hidden = 128, 128
    (self.x_train, self.y_train), _ = tf.keras.datasets.mnist.load_data()
    self.x_train = self.x_train.reshape(self.x_train.shape[0], 28, 28, 1)
    self.x_train = self.x_train.astype('float32') / 255
    self.y_train = tf.keras.utils.to_categorical(self.y_train, self.num_classes)

  def _build_model(self):
    """Model from https://github.com/keras-team/keras/blob/master/examples

    /mnist_hierarchical_rnn.py.
    """
    row, col, pixel = self.x_train.shape[1:]
    inputs = tf.keras.layers.Input(shape=(row, col, pixel))
    encoded_rows = tf.keras.layers.TimeDistributed(
        tf.keras.layers.LSTM(self.row_hidden))(
            inputs)
    encoded_cols = tf.keras.layers.LSTM(self.col_hidden)(encoded_rows)
    outputs = tf.keras.layers.Dense(
        self.num_classes, activation='softmax')(
            encoded_cols)
    model = tf.keras.Model(inputs, outputs)

    return model

  # In each benchmark test, the required arguments for the
  # method `measure_performance` include:
  #   x: Input data, it could be Numpy or loaded from tfds.
  #   y: Target data. If `x` is a dataset or generator instance,
  #      `y` should not be specified.
  #   loss: Loss function for model.
  #   optimizer: Optimizer for model.
  #   Check more details in `measure_performance()` method of
  #   benchmark_util.
  def benchmark_hrnn_mnist_bs_256(self):
    """Measure performance with batch_size=256."""
    batch_size = 256
    metrics, wall_time, extras = benchmark_util.measure_performance(
        self._build_model,
        x=self.x_train,
        y=self.y_train,
        batch_size=batch_size,
        optimizer='rmsprop',
        loss='categorical_crossentropy',
        metrics=['accuracy'])

    metadata = benchmark_util.get_keras_examples_metadata(
        'hierarchical_rnn', batch_size)
    extras.update(metadata)
    self.report_benchmark(wall_time=wall_time, metrics=metrics, extras=extras)

  def benchmark_hrnn_mnist_bs_512(self):
    """Measure performance with batch_size=512."""
    batch_size = 512
    metrics, wall_time, extras = benchmark_util.measure_performance(
        self._build_model,
        x=self.x_train,
        y=self.y_train,
        batch_size=batch_size,
        optimizer='rmsprop',
        loss='categorical_crossentropy',
        metrics=['accuracy'])

    metadata = benchmark_util.get_keras_examples_metadata(
        'hierarchical_rnn', batch_size)
    extras.update(metadata)
    self.report_benchmark(wall_time=wall_time, metrics=metrics, extras=extras)

  def benchmark_hrnn_mnist_bs_1024(self):
    """Measure performance with batch_size=1024."""
    batch_size = 1024
    metrics, wall_time, extras = benchmark_util.measure_performance(
        self._build_model,
        x=self.x_train,
        y=self.y_train,
        batch_size=batch_size,
        optimizer='rmsprop',
        loss='categorical_crossentropy',
        metrics=['accuracy'])

    metadata = benchmark_util.get_keras_examples_metadata(
        'hierarchical_rnn', batch_size)
    extras.update(metadata)
    self.report_benchmark(wall_time=wall_time, metrics=metrics, extras=extras)

  def benchmark_hrnn_mnist_bs_1024_gpu_2(self):
    """Measure performance with batch_size=1024, gpu=2 and

    distribution_strategy='mirrored'
    """
    batch_size = 1024
    metrics, wall_time, extras = benchmark_util.measure_performance(
        self._build_model,
        x=self.x_train,
        y=self.y_train,
        batch_size=batch_size,
        num_gpus=2,
        distribution_strategy='mirrored',
        optimizer='rmsprop',
        loss='categorical_crossentropy',
        metrics=['accuracy'])

    metadata = benchmark_util.get_keras_examples_metadata(
        'hierarchical_rnn', batch_size)
    extras.update(metadata)
    self.report_benchmark(wall_time=wall_time, metrics=metrics, extras=extras)


if __name__ == '__main__':
  tf.test.main()
