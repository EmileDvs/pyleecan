"""Equality of Pyleecan values, shared by the class implementations."""

import numpy as np


def values_equal(left, right):
    """True if two field values are equal (numpy arrays compared by values).

    Lists, tuples and dicts are compared item by item, so that the numpy arrays
    they hold do not raise; Pyleecan objects use their own ``__eq__``; NaN
    values of arrays are equal.

    Parameters
    ----------
    left, right : object
        Values to compare

    Returns
    -------
    is_equal : bool
        True if the values are equal
    """
    if left is None or right is None:
        return left is right
    if isinstance(left, np.ndarray) or isinstance(right, np.ndarray):
        try:
            return bool(np.array_equal(left, right, equal_nan=True))
        except TypeError:  # equal_nan on non numeric arrays
            return bool(np.array_equal(left, right))
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(
            values_equal(a, b) for a, b in zip(left, right)
        )
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            values_equal(left[key], right[key]) for key in left
        )
    try:
        return bool(left == right)
    except (TypeError, ValueError):
        return False
