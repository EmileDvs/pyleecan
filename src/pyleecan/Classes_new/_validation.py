"""Type, min and max validation of the dataclass fields (hand-written).

The rules follow the pydantic models of ``Classes_pydantic`` (strict mode), so
that both implementations accept the same values:

- ``float``: int or float (not bool), numpy numbers included
- ``int``: int (not bool, not float); ``bool``: bool; ``str``: str
- ``complex``: int, float, complex or its string form ("1+2j", converted)
- ``np.ndarray``: array, or list/tuple (converted)
- ``list[X]``, ``dict[str, X]``: the container, each item checked against X
- Pyleecan class: an instance, or a dict (built with ``model_validate``)
- other classes: an instance; ``Callable``: a callable; ``Any``: anything
- ``X | None``: None or X
- ``min``/``max`` field metadata: bounds of numbers and of array elements

The lenient mode adds the legacy rules (``LegacyClass``): None is accepted by
every field and in containers, an int field accepts a float with an integer
value (converted to int), a function field accepts its source (a lambda or
the path to a python file, converted to a ``SourceFunction``) and an object
field accepts the path of a file to load, or an array for an ImportMatrix
(``classes_common.legacy_values``).

A checker is compiled once per class and field, from the resolved annotations.
"""

import sys
import typing
from collections.abc import Callable
from dataclasses import fields
from functools import cache
from types import NoneType, UnionType
from typing import Any, ForwardRef, Union, get_args, get_origin

import numpy as np

from ..classes_common.base import PyleecanBase
from ..classes_common.errors import CheckMaxError, CheckMinError, CheckTypeError
from ..classes_common.functions import SourceFunction
from ..classes_common.legacy_values import annotation_classes, legacy_object_value


def field_checkers(cls, lenient=False):
    """Checker of each field of a dataclass: {name: check(value) -> value}.

    Parameters
    ----------
    cls : type
        Pyleecan dataclass
    lenient : bool
        True for the legacy rules (None everywhere, integral float for int)

    Returns
    -------
    checkers : dict
        {field name: function returning the (converted) valid value, raising
        CheckTypeError, CheckMinError or CheckMaxError}
    """
    return _field_checkers(cls, lenient)


@cache
def _field_checkers(cls, lenient):
    hints = _resolved_hints(cls)
    checkers = {}
    for field_info in fields(cls):
        annotation = hints.get(field_info.name, Any)
        type_check = _type_checker(annotation, lenient)
        bounds = (field_info.metadata.get("min"), field_info.metadata.get("max"))
        checkers[field_info.name] = _field_checker(
            field_info.name, annotation, type_check, *bounds, lenient
        )
    return checkers


@cache
def _import_class():
    from ._import import import_class

    return import_class


def _field_checker(name, annotation, type_check, vmin, vmax, lenient):
    expected = _expected(annotation)
    # Conversions of the legacy setters: only for the object fields
    converts = lenient and bool(annotation_classes(annotation))

    def check(value):
        if value is None and lenient:
            return None
        if converts and isinstance(value, (str, list, np.ndarray)):
            value = legacy_object_value(value, annotation, _import_class())
        try:
            value = type_check(value)
        except _Invalid:
            raise CheckTypeError(
                f"For {name} : {expected} expected, {type(value).__name__} given"
            ) from None
        if value is not None:
            _check_bounds(name, value, vmin, vmax)
        return value

    return check


def _check_bounds(name, value, vmin, vmax):
    if vmin is None and vmax is None:
        return
    if isinstance(value, np.ndarray):
        if value.size == 0 or not np.issubdtype(value.dtype, np.number):
            return
        low, high = value.min(), value.max()
    elif isinstance(value, (int, float, np.number)) and not isinstance(value, bool):
        low = high = value
    else:
        return
    if vmin is not None and low < vmin:
        raise CheckMinError(f"{name} must be >= {vmin}, {value} given")
    if vmax is not None and high > vmax:
        raise CheckMaxError(f"{name} must be <= {vmax}, {value} given")


class _Invalid(Exception):
    """Value rejected by a type checker (turned into CheckTypeError)."""


def _resolved_hints(cls):
    """Annotations of the fields, evaluated; unresolvable ones are Any."""
    try:
        return typing.get_type_hints(cls)
    except Exception:  # e.g. an optional dependency not installed
        pass
    import annotationlib

    hints = {}
    for klass in reversed(cls.__mro__):
        namespace = vars(sys.modules.get(klass.__module__, typing))
        annotations = annotationlib.get_annotations(
            klass, format=annotationlib.Format.FORWARDREF
        )
        for name, annotation in annotations.items():
            try:
                hints[name] = (
                    typing.evaluate_forward_ref(annotation, globals=namespace)
                    if isinstance(annotation, ForwardRef)
                    else annotation
                )
            except Exception:
                hints[name] = Any
    return hints


def _expected(annotation):
    """Name of the expected type, for the error messages."""
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation).replace("typing.", "")


def _is_int(value):
    return isinstance(value, (int, np.integer)) and not isinstance(
        value, (bool, np.bool_)
    )


def _type_checker(annotation, lenient):
    """Function returning the (converted) value of annotation, raising _Invalid."""
    if annotation is Any or isinstance(annotation, (str, ForwardRef)):
        return lambda value: value
    if annotation is None or annotation is NoneType:

        def check_none(value):
            if value is not None:
                raise _Invalid
            return value

        return check_none

    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        options = get_args(annotation)
        accepts_none = NoneType in options
        checkers = [
            _type_checker(option, lenient)
            for option in options
            if option is not NoneType
        ]

        def check_union(value):
            if value is None and accepts_none:
                return None
            for checker in checkers:
                try:
                    return checker(value)
                except _Invalid:
                    continue
            raise _Invalid

        return check_union

    if origin is list:
        item_check = _item_checker(get_args(annotation), 0, lenient)

        def check_list(value):
            if not isinstance(value, list):
                raise _Invalid
            for index, item in enumerate(value):
                checked = item_check(item)
                if checked is not item:  # Converted item: new list (no copy else)
                    return value[:index] + [checked] + [
                        item_check(other) for other in value[index + 1 :]
                    ]
            return value

        return check_list

    if origin is dict:
        item_check = _item_checker(get_args(annotation), 1, lenient)

        def check_dict(value):
            if not isinstance(value, dict):
                raise _Invalid
            checked = {key: item_check(item) for key, item in value.items()}
            if all(checked[key] is item for key, item in value.items()):
                return value  # No converted item: keep the given dict
            return checked

        return check_dict

    if origin is not None and isinstance(origin, type) and issubclass(origin, Callable):
        annotation = Callable
    if annotation is Callable:

        def check_callable(value):
            if lenient and isinstance(value, str):
                try:
                    return SourceFunction(value)  # Legacy: function source
                except ValueError:
                    raise _Invalid from None
            if not callable(value):
                raise _Invalid
            return value

        return check_callable

    if annotation is float:

        def check_float(value):
            if not (_is_int(value) or isinstance(value, (float, np.floating))):
                raise _Invalid
            return value

        return check_float

    if annotation is int:

        def check_int(value):
            if _is_int(value):
                return value
            if lenient and isinstance(value, (float, np.floating)) and value % 1 == 0:
                return int(value)  # Legacy: integer value given as a float
            raise _Invalid

        return check_int

    if annotation is complex:

        def check_complex(value):
            if isinstance(value, str):
                try:
                    return complex(value.replace(" ", ""))
                except ValueError:
                    raise _Invalid from None
            if isinstance(value, (bool, np.bool_)) or not isinstance(
                value, (int, float, complex, np.number)
            ):
                raise _Invalid
            return value

        return check_complex

    if annotation is np.ndarray:

        def check_array(value):
            if isinstance(value, np.ndarray):
                return value
            if isinstance(value, (list, tuple)):
                return np.asarray(value)
            raise _Invalid

        return check_array

    if annotation in (bool, str):
        accepted = (bool, np.bool_) if annotation is bool else str

        def check_exact(value):
            if not isinstance(value, accepted):
                raise _Invalid
            return value

        return check_exact

    if isinstance(annotation, type):
        is_pyleecan = issubclass(annotation, PyleecanBase)

        def check_instance(value):
            if isinstance(value, annotation):
                return value
            if is_pyleecan and isinstance(value, dict):
                return annotation.model_validate(value)
            raise _Invalid

        return check_instance

    return lambda value: value  # Other typing constructs: not checked


def _item_checker(arguments, index, lenient):
    """Checker of the items of a container (None accepted in lenient mode)."""
    if len(arguments) <= index:
        return lambda value: value
    check = _type_checker(arguments[index], lenient)
    if not lenient:
        return check
    return lambda value: None if value is None else check(value)
