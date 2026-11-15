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
