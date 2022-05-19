# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
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
"""Reuters topic classification dataset."""

import json

import numpy as np

from keras.preprocessing.sequence import _remove_long_seq
from keras.utils.data_utils import get_file
from tensorflow.python.platform import tf_logging as logging
from tensorflow.python.util.tf_export import keras_export


@keras_export('keras.datasets.reuters.load_data')
def load_data(path='reuters.npz',
              num_words=None,
              skip_top=0,
              maxlen=None,
              test_split=0.2,
              seed=113,
              start_char=1,
              oov_char=2,
              index_from=3,
              **kwargs):
  """Loads the Reuters newswire classification dataset.

  This is a dataset of 11,228 newswires from Reuters, labeled over 46 topics.

  This was originally generated by parsing and preprocessing the classic
  Reuters-21578 dataset, but the preprocessing code is no longer packaged
  with Keras. See this
  [github discussion](https://github.com/keras-team/keras/issues/12072)
  for more info.

  Each newswire is encoded as a list of word indexes (integers).
  For convenience, words are indexed by overall frequency in the dataset,
  so that for instance the integer "3" encodes the 3rd most frequent word in
  the data. This allows for quick filtering operations such as:
  "only consider the top 10,000 most
  common words, but eliminate the top 20 most common words".

  As a convention, "0" does not stand for a specific word, but instead is used
  to encode any unknown word.

  Args:
    path: where to cache the data (relative to `~/.keras/dataset`).
    num_words: integer or None. Words are
        ranked by how often they occur (in the training set) and only
        the `num_words` most frequent words are kept. Any less frequent word
        will appear as `oov_char` value in the sequence data. If None,
        all words are kept. Defaults to None, so all words are kept.
    skip_top: skip the top N most frequently occurring words
        (which may not be informative). These words will appear as
        `oov_char` value in the dataset. Defaults to 0, so no words are
        skipped.
    maxlen: int or None. Maximum sequence length.
        Any longer sequence will be truncated. Defaults to None, which
        means no truncation.
    test_split: Float between 0 and 1. Fraction of the dataset to be used
      as test data. Defaults to 0.2, meaning 20% of the dataset is used as
      test data.
    seed: int. Seed for reproducible data shuffling.
    start_char: int. The start of a sequence will be marked with this
        character. Defaults to 1 because 0 is usually the padding character.
    oov_char: int. The out-of-vocabulary character.
        Words that were cut out because of the `num_words` or
        `skip_top` limits will be replaced with this character.
    index_from: int. Index actual words with this index and higher.
    **kwargs: Used for backwards compatibility.

  Returns:
    Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`.

  **x_train, x_test**: lists of sequences, which are lists of indexes
    (integers). If the num_words argument was specific, the maximum
    possible index value is `num_words - 1`. If the `maxlen` argument was
    specified, the largest possible sequence length is `maxlen`.

  **y_train, y_test**: lists of integer labels (1 or 0).

  Note: The 'out of vocabulary' character is only used for
  words that were present in the training set but are not included
  because they're not making the `num_words` cut here.
  Words that were not seen in the training set but are in the test set
  have simply been skipped.
  """
  # Legacy support
  if 'nb_words' in kwargs:
    logging.warning('The `nb_words` argument in `load_data` '
                    'has been renamed `num_words`.')
    num_words = kwargs.pop('nb_words')
  if kwargs:
    raise TypeError(f'Unrecognized keyword arguments: {str(kwargs)}')

  origin_folder = 'https://storage.googleapis.com/tensorflow/tf-keras-datasets/'
  path = get_file(
      path,
      origin=f'{origin_folder}reuters.npz',
      file_hash=
      'd6586e694ee56d7a4e65172e12b3e987c03096cb01eab99753921ef915959916',
  )
  with np.load(path, allow_pickle=True) as f:  # pylint: disable=unexpected-keyword-arg
    xs, labels = f['x'], f['y']

  rng = np.random.RandomState(seed)
  indices = np.arange(len(xs))
  rng.shuffle(indices)
  xs = xs[indices]
  labels = labels[indices]

  if start_char is not None:
    xs = [[start_char] + [w + index_from for w in x] for x in xs]
  elif index_from:
    xs = [[w + index_from for w in x] for x in xs]

  if maxlen:
    xs, labels = _remove_long_seq(maxlen, xs, labels)

  if not num_words:
    num_words = max(max(x) for x in xs)

  # by convention, use 2 as OOV word
  # reserve 'index_from' (=3 by default) characters:
  # 0 (padding), 1 (start), 2 (OOV)
  if oov_char is not None:
    xs = [[w if skip_top <= w < num_words else oov_char for w in x] for x in xs]
  else:
    xs = [[w for w in x if skip_top <= w < num_words] for x in xs]

  idx = int(len(xs) * (1 - test_split))
  x_train, y_train = np.array(xs[:idx], dtype='object'), np.array(labels[:idx])
  x_test, y_test = np.array(xs[idx:], dtype='object'), np.array(labels[idx:])

  return (x_train, y_train), (x_test, y_test)


@keras_export('keras.datasets.reuters.get_word_index')
def get_word_index(path='reuters_word_index.json'):
  """Retrieves a dict mapping words to their index in the Reuters dataset.

  Args:
      path: where to cache the data (relative to `~/.keras/dataset`).

  Returns:
      The word index dictionary. Keys are word strings, values are their index.
  """
  origin_folder = 'https://storage.googleapis.com/tensorflow/tf-keras-datasets/'
  path = get_file(
      path,
      origin=f'{origin_folder}reuters_word_index.json',
      file_hash='4d44cc38712099c9e383dc6e5f11a921',
  )
  with open(path) as f:
    return json.load(f)
