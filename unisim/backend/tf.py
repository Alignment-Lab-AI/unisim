"""
 Copyright 2023 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """

from pathlib import Path
import tensorflow as tf

# typing
from ..types import TensorEmbedding, BatchEmbeddings
from ..types import GlobalEmbedding, BatchGlobalEmbeddings  # noqa
from ..types import PartialEmbedding, PartialEmbeddings, BatchPartialEmbeddings  # noqa
from ..types import BatchDistances, BatchDistances2D, BatchIndexes
from typing import Tuple


@tf.function(jit_compile=True)
def avg_vects(embeddings: BatchEmbeddings) -> BatchGlobalEmbeddings:
    num_embs = tf.cast(tf.shape(embeddings)[0], dtype=embeddings.dtype)
    return tf.reduce_sum(embeddings) / num_embs

# FIXME doesn't wokr on irregular shape
# @tf.function(jit_compile=True)
# def gather_and_avg(embeddings: BatchEmbeddings,
#                    indices: BatchIndexes) -> BatchGlobalEmbeddings:
#     vects = tf.gather(embeddings, indices=indices)
#     num_vects = tf.cast(tf.shape(vects)[0], dtype=vects.dtype)
#     return tf.reduce_sum(vects, axis=0) / num_vects

# @tf.function(jit_compile=True)
# def average_embeddings(embeddings: BatchPartialEmbeddings,
#                        axis: int = 0) -> BatchGlobalEmbeddings:
#     """Compute embeddings average"""
#     return tf.reduce_sum(embeddings, axis=axis) / tf.shape(embeddings)[axis]


@tf.function(jit_compile=True)
def cosine_similarity(query_embeddings: BatchEmbeddings,
                      index_embeddings: BatchEmbeddings) -> BatchDistances2D:
    """Compute cosine similarity between embeddings

    Args:
        query_embeddings: embeddings of the content to be searched
        index_embeddings: embeddings of the indexed content
    Returns:
        distances: matrix of distances
    """

    return tf.matmul(query_embeddings, index_embeddings, transpose_b=True)


@tf.function(jit_compile=True)
def knn(query: TensorEmbedding,
        targets: BatchEmbeddings,
        k: int = 5) -> Tuple[BatchIndexes, BatchDistances]:
    "perform a KNN search"
    distances = tf.matmul(query, targets, transpose_b=True)
    # top k
    top_dists = tf.math.top_k(distances, k=k)
    indices = tf.cast(top_dists.indices, dtype=tf.int64)
    values = top_dists.values
    return indices, values


def load_model(path: Path, verbose: int = 0):
    # specialize path
    mpath = str(path)
    if verbose:
        print(f"|-model path: {mpath}")

    model: tf.keras.Model = tf.keras.models.load_model(mpath)
    if verbose:
        model.summary()
    return model


@tf.function()  # jit_compile=True)
def predict(model, batch) -> BatchEmbeddings:
    # add strategy here
    return model(batch, training=False)
