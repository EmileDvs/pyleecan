"""Value conversions of the legacy setters, shared by the legacy layers.

The legacy setters converted some values before checking them:

- a str given for an object property is the path of a file to load,
- an array or a list given for an ImportMatrix property is the matrix value
  (``ImportMatrixVal``).

The functions given by their source are in ``functions.py``. The conversion
of a dict into an object is done by the validation of both implementations.
"""

from types import NoneType, UnionType
from typing import Union, get_args, get_origin

import numpy as np

from .base import PyleecanBase


def annotation_classes(annotation):
    """Pyleecan classes accepted by an annotation (X, X | None)."""
    if get_origin(annotation) in (Union, UnionType):
        return tuple(
            cls
            for option in get_args(annotation)
            if option is not NoneType
            for cls in annotation_classes(option)
        )
    if isinstance(annotation, type) and issubclass(annotation, PyleecanBase):
        return (annotation,)
    return ()


def holds_pyleecan_objects(annotation):
    """True if a field of this annotation holds Pyleecan objects.

    A Pyleecan class, or a list, tuple, dict or union containing one. The
    legacy setters set the parent of the objects of these fields only: a
    field typed ``list`` (``list[Any]``, e.g. ``ParamExplorerSet.value``)
    holds objects that keep their own parent.
    """
    from typing import ForwardRef

    if isinstance(annotation, (str, ForwardRef)):
        return True  # Not resolved: may hold objects (parent links kept)
    if isinstance(annotation, type):
        return issubclass(annotation, PyleecanBase)
    return any(holds_pyleecan_objects(argument) for argument in get_args(annotation))


def load_serialized_items(value, import_class):
    """Objects of the dumps held by a list, tuple or dict of plain values.

    A field typed ``list`` (``list[Any]``) may hold dumps of objects (dicts
    with "__class__", e.g. ``ParamExplorerSet.value`` or
    ``OutMagFEMM.handler_list`` after ``init_dict=as_dict()``): they are
    loaded, as the dataclass legacy layer does, so that a copy and a reload
    hold the same objects. Other items are kept.
    """
    if isinstance(value, dict) and "__class__" in value:
        cls = import_class(value["__class__"])
        if hasattr(cls, "from_dict"):
            return cls.from_dict(value)
        return cls(init_dict=value)
    if isinstance(value, list):
        return [load_serialized_items(item, import_class) for item in value]
    if isinstance(value, tuple):
        return tuple(load_serialized_items(item, import_class) for item in value)
    if isinstance(value, dict):
        return {key: load_serialized_items(item, import_class) for key, item in value.items()}
    return value


def legacy_object_value(value, annotation, import_class):
    """Convert a value given to an object property, like the legacy setters.

    Parameters
    ----------
    value : object
        Value given to the property
    annotation : object
        Annotation of the property
    import_class : callable
        Class lookup of the class package (e.g. Classes_new._import.import_class)

    Returns
    -------
    value : object
        Converted value: the init_dict of the file for a str, an
        ImportMatrixVal for an array or a list given to an ImportMatrix
        property, the value itself otherwise
    """
    classes = annotation_classes(annotation)
    if not classes:
        return value
    if isinstance(value, str):  # Path of a file to load
        from ..Functions_new.load import load_init_dict

        return load_init_dict(value)[1]
    if isinstance(value, (np.ndarray, list)) and any(
        cls.__name__ == "ImportMatrix" for cls in classes
    ):
        return import_class("ImportMatrixVal")(value=np.asarray(value))
    return value
