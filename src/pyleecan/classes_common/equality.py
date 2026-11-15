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


def compare_values(left, right, path, ignore_list=None, is_add_value=False):
    """Paths of the differences between two field values (legacy compare).

    Same format as the legacy compare methods: Pyleecan objects are compared
    with their own compare, lists and dicts of objects item by item
    ("name.list[0]", "name.dict[key]", "len(name.list)" for a length
    difference), the other values as a whole.

    Parameters
    ----------
    left, right : object
        Values to compare
    path : str
        Path of the value (e.g. "self.stator")
    ignore_list : list, optional
        Paths of the differences to ignore (applied by the caller)
    is_add_value : bool
        True to add the values to the differences

    Returns
    -------
    differences : list
        Paths of the differences
    """
    if left is None or right is None:
        return [] if left is right else [path + " None mismatch"]
    if hasattr(left, "compare") and not isinstance(left, type):
        return left.compare(
            right, name=path, ignore_list=ignore_list, is_add_value=is_add_value
        )
    if _holds_objects(left) and type(right) is type(left):
        if len(left) != len(right):
            return ["len(" + path + ")"]
        keys = left if isinstance(left, dict) else range(len(left))
        if isinstance(left, dict) and left.keys() != right.keys():
            return ["len(" + path + ")"]
        return [
            difference
            for key in keys
            for difference in compare_values(
                left[key], right[key], f"{path}[{key}]", ignore_list, is_add_value
            )
        ]
    if values_equal(left, right):
        return []
    return [path + (f" (self={left}, other={right})" if is_add_value else "")]


def _holds_objects(value):
    """True for a non empty list or dict holding objects with a compare."""
    items = value.values() if isinstance(value, dict) else value
    return isinstance(value, (list, tuple, dict)) and any(
        hasattr(item, "compare") for item in items
    )
