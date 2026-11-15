"""Legacy ``as_dict`` serialization, shared by the legacy layers.

Both ``LegacyClass`` (dataclass) and ``LegacyModel`` (pydantic) build their
``as_dict`` with these functions, so that both implementations write the same
legacy dictionaries:

- complex properties are written as str (``str(value)``: the legacy setters
  kept an int or a float given to a complex property, e.g. ``"0"``),
- numpy arrays follow ``type_handle_ndarray`` (0: list, 1: copy, 2: array),
- nested objects are written with their own ``as_dict``,
- functions are written by their source (``SourceFunction``), kept with
  ``keep_function`` or written as None,
- the properties with an ``as_dict`` mode "1" or "2" are written as None.
"""

from types import NoneType, UnionType
from typing import Annotated, Union, get_args, get_origin

import numpy as np

from .functions import SourceFunction


def is_complex_annotation(annotation):
    """True for complex, complex | None or an Annotated complex."""
    if annotation is complex:
        return True
    origin = get_origin(annotation)
    if origin is Annotated:
        return is_complex_annotation(get_args(annotation)[0])
    if origin in (Union, UnionType):
        options = [option for option in get_args(annotation) if option is not NoneType]
        return len(options) == 1 and is_complex_annotation(options[0])
    return False


def legacy_field(value, is_complex, as_dict_mode, type_handle_ndarray, keep_function, kwargs):
    """Legacy serialization of a property value.

    Parameters
    ----------
    value : object
        Value of the property
    is_complex : bool
        True for a complex property (written as str)
    as_dict_mode : str or None
        "1" or "2" for a property written as None
    type_handle_ndarray : int
        0: ndarray as list, 1: copy of the ndarray, 2: ndarray
    keep_function : bool
        True to keep the functions (not given by their source)
    kwargs : dict
        Other arguments of as_dict, passed to the nested objects

    Returns
    -------
    value : object
        Serialized value
    """
    if as_dict_mode in ("1", "2"):
        return None
    if is_complex:
        return None if value is None else str(value)
    return legacy_value(value, type_handle_ndarray, keep_function, kwargs)


def legacy_value(value, type_handle_ndarray, keep_function, kwargs):
    """Legacy serialization of a value (recursing into lists and dicts)."""
    if value is None:
        return None
    if isinstance(value, SourceFunction):
        return value.source  # Functions are saved by their source
    if isinstance(value, np.ndarray):
        if type_handle_ndarray == 0:
            return value.tolist()
        if type_handle_ndarray == 1:
            return value.copy()
        if type_handle_ndarray == 2:
            return value
        raise ValueError(f"Unknown type_handle_ndarray: {type_handle_ndarray}")
    if hasattr(value, "as_dict"):
        return value.as_dict(
            type_handle_ndarray=type_handle_ndarray, keep_function=keep_function, **kwargs
        )
    if isinstance(value, dict):
        return {
            key: legacy_value(item, type_handle_ndarray, keep_function, kwargs)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [
            legacy_value(item, type_handle_ndarray, keep_function, kwargs)
            for item in value
        ]
    if type(value) is complex:
        return str(value)
    if callable(value) and not keep_function:
        return None
    return value
