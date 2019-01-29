from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from tensorflow.python.framework import load_library, ops
from tensorflow.python.platform import resource_loader

ops_module = load_library.load_op_library(resource_loader.get_path_to_datafile('_tfunicode_ops.so'))

ops.NotDifferentiable('CobineSparseSuccessor')
ops.NotDifferentiable('ExpandCharNgrams')
ops.NotDifferentiable('ExpandSplitChars')
ops.NotDifferentiable('ExpandSplitWords')
ops.NotDifferentiable('TransformLowerCase')
ops.NotDifferentiable('TransformNormalizeUnicode')
ops.NotDifferentiable('TransformRegexReplace')
ops.NotDifferentiable('TransformStringReplace')
ops.NotDifferentiable('TransformTitleCase')
ops.NotDifferentiable('TransformUpperCase')
ops.NotDifferentiable('TransformWrapWith')
ops.NotDifferentiable('TransformZeroDigits')


def transform_normalize_unicode(source, form):
    """Normalize unicode strings tensor.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to normalize.
        form: Scalar value, name of normalization algorithm.
            One of `"NFD"`, `"NFC"`, `"NFKD"`, `"NFKC"`.
    Returns:
        `Tensor` or `SparseTensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        result = tf.SparseTensor(
            indices=source.indices,
            values=ops_module.transform_normalize_unicode(source.values, form),
            dense_shape=source.dense_shape
        )
    else:
        result = ops_module.transform_normalize_unicode(source, form)

    return result


def transform_lower_case(source):
    """Lowercase strings tensor.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to make lower.
    Returns:
        `Tensor` or `SparseTensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        result = tf.SparseTensor(
            indices=source.indices,
            values=ops_module.transform_lower_case(source.values),
            dense_shape=source.dense_shape
        )
    else:
        result = ops_module.transform_lower_case(source)

    return result


def transform_regex_replace(source, pattern, rewrite):
    """Replace all substrings from `needle` to corresponding strings in `haystack` with source.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, source strings for replacing.
        pattern: List of RE2 patterns to search in source
        rewrite: List of strings to replace with. Should have same length as `needle`.
    Returns:
        `Tensor` or `SparseTensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        result = tf.SparseTensor(
            indices=source.indices,
            values=ops_module.transform_regex_replace(source.values, pattern, rewrite),
            dense_shape=source.dense_shape
        )
    else:
        result = ops_module.transform_regex_replace(source, pattern, rewrite)

    return result


def transform_string_replace(source, needle, haystack):
    """Replace all substrings from `needle` to corresponding strings in `haystack` with source.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, source strings for replacing.
        needle: List of strings to search in source
        haystack: List of strings to replace with. Should have same length as `needle`.
    Returns:
        `Tensor` or `SparseTensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        result = tf.SparseTensor(
            indices=source.indices,
            values=ops_module.transform_string_replace(source.values, needle, haystack),
            dense_shape=source.dense_shape
        )
    else:
        result = ops_module.transform_string_replace(source, needle, haystack)

    return result


def transform_title_case(source):
    """Titlecase strings tensor.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to make title.
    Returns:
        `Tensor` or `SparseTensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        result = tf.SparseTensor(
            indices=source.indices,
            values=ops_module.transform_title_case(source.values),
            dense_shape=source.dense_shape
        )
    else:
        result = ops_module.transform_title_case(source)

    return result


def transform_upper_case(source):
    """Uppercase strings tensor.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to make upper.
    Returns:
        `Tensor` or `SparseTensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        result = tf.SparseTensor(
            indices=source.indices,
            values=ops_module.transform_upper_case(source.values),
            dense_shape=source.dense_shape
        )
    else:
        result = ops_module.transform_upper_case(source)

    return result


def transform_zero_digits(source):
    """Replace each digit with 0.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to replace digits.
    Returns:
        `Tensor` or `SparseTensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        result = tf.SparseTensor(
            indices=source.indices,
            values=ops_module.transform_zero_digits(source.values),
            dense_shape=source.dense_shape
        )
    else:
        result = ops_module.transform_zero_digits(source)

    return result


def transform_wrap_with(source, left, right):
    """Wrap source strings with "left" and "right" strings

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to replace digits.
        left: Scalar string to add in the beginning
        right: Scalar string to add in the ending
    Returns:
        `SparseTensor` of same shape and size as input.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        result = tf.SparseTensor(
            indices=source.indices,
            values=ops_module.transform_wrap_with(source.values, left, right),
            dense_shape=source.dense_shape
        )
    else:
        result = ops_module.transform_wrap_with(source, left, right)

    return result


def expand_split_words(source, extended=False):
    """Split unicode strings into words.
    Result tokens could be simply joined with empty separator to obtain original strings.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to split
        source: Boolean flag, should rules WB6 and WB7 break on "stop" marks
    Returns:
        `SparseTensor` with an additional dimension of size 1 added.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        child_indices, child_values, child_shape = ops_module.expand_split_words(source.values, extended)
        result = _combine_sparse_successor(source.indices, source.dense_shape, child_indices, child_values, child_shape)
    else:
        indices, values, shape = ops_module.expand_split_words(source, extended)
        result = tf.SparseTensor(indices=indices, values=values, dense_shape=shape)

    return result


def expand_split_chars(source):
    """Split unicode strings into characters.
    Result tokens could be simply joined with empty separator to obtain original strings.

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to split
    Returns:
        `SparseTensor` with an additional dimension of size 1 added.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        child_indices, child_values, child_shape = ops_module.expand_split_chars(source.values)
        result = _combine_sparse_successor(source.indices, source.dense_shape, child_indices, child_values, child_shape)
    else:
        indices, values, shape = ops_module.expand_split_chars(source)
        result = tf.SparseTensor(indices=indices, values=values, dense_shape=shape)

    return result


def expand_char_ngrams(source, minn, maxn, itself='ASIS'):
    """Split unicode strings into char ngrams.
    Ngrams size configures with minn and max

    Args:
        source: `Tensor` or `SparseTensor` of any shape, strings to split
        minn: Minimum length of char ngram
        minn: Maximum length of char ngram
        itself: Scalar value, strategy for source word preserving.
            One of `"ASIS"`, `"NEVER"`, `"ALWAYS"`, `"ALONE"`.
    Returns:
        `SparseTensor` with an additional dimension of size 1 added.
    """

    source = tf.convert_to_tensor_or_sparse_tensor(source, dtype=tf.string)
    if isinstance(source, tf.SparseTensor):
        child_indices, child_values, child_shape = ops_module.expand_char_ngrams(source.values, minn, maxn, itself)
        result = _combine_sparse_successor(source.indices, source.dense_shape, child_indices, child_values, child_shape)
    else:
        indices, values, shape = ops_module.expand_char_ngrams(source, minn, maxn, itself)
        result = tf.SparseTensor(indices=indices, values=values, dense_shape=shape)

    return result


def _combine_sparse_successor(parent_indices, parent_shape, child_indices, child_values, child_shape):
    """Combines two string `SparseTensor`s, where second `SparseTensor` is the result of expanding
    first `SparseTensor`'s values.

    Args:
        parent_indices: 2D int64 `Tensor` with parent `SparseTensor` indices
        parent_shape: 1D int64 `Tensor` with parent `SparseTensor` dense_shape
        child_indices: 2D int64 `Tensor` with child `SparseTensor` indices
        child_values: 1D int64 `Tensor` with child `SparseTensor` values
        child_shape: 1D int64 `Tensor` with child `SparseTensor` dense_shape
    Returns:
        `SparseTensor` with an additional dimension of size 1 added.
    """

    indices, values, shape = ops_module.cobine_sparse_successor(
        parent_indices,
        parent_shape,
        child_indices,
        child_values,
        child_shape
    )

    return tf.SparseTensor(indices=indices, values=values, dense_shape=shape)
