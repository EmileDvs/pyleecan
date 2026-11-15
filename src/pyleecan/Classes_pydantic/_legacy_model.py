"""Legacy layer of the pydantic Pyleecan classes (Phase 1 only, hand-written).

``LegacyModel`` adds to the target base ``PyleecanModel`` the behaviours of the
legacy classes, so that the generated classes can be validated against them.
Phase 2 removes this layer: the generated classes then derive from
``PyleecanModel`` directly.

Legacy behaviours:

- every field accepts None (legacy setters skipped the checks for None),
- ``-1`` sets the default value (e.g. a default object) of a field,
- nested objects get a ``parent`` link to the object holding them,
- an existing method can be replaced on an object (e.g. a mock in tests),
- loading ignores the unknown keys (old files, serialization keys),
- legacy API: ``as_dict`` (complex as str, ``type_handle_ndarray``),
  ``from_dict``, ``copy``, ``compare`` and ``_set_None``.
"""

from copy import deepcopy
from inspect import getattr_static
from types import FunctionType
from typing import Any

import numpy as np
from pydantic import PrivateAttr, field_validator

from ._pyleecan_model import PyleecanModel


class LegacyModel(PyleecanModel):
    """Legacy layer of the Pyleecan classes built on pydantic."""

    _parent: Any = PrivateAttr(default=None)

    # Parent link (not a field: not validated, serialized, copied or compared)
    @property
    def parent(self):
        """Object holding this object"""
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    def model_post_init(self, context):
        for name in type(self).model_fields:
            self._set_parent_links(getattr(self, name))

    def __setattr__(self, name, value):
        attribute = getattr_static(type(self), name, None)
        if (
            name not in type(self).model_fields
            and not name.startswith("_")
            and isinstance(attribute, (FunctionType, staticmethod, classmethod))
        ):
            # Like FrozenClass, an existing method can be replaced on an object
            # (e.g. by a mock in tests); it is not a field: not dumped or copied
            object.__setattr__(self, name, value)
            return
        super().__setattr__(name, value)  # Validated by pydantic
        if name in type(self).model_fields:
            self._set_parent_links(getattr(self, name))

    def _set_parent_links(self, value):
        if isinstance(value, LegacyModel):
            value._assert_parent_type(self)
            value._parent = self
        elif isinstance(value, (list, tuple)):
            for item in value:
                self._set_parent_links(item)
        elif isinstance(value, dict):
            for item in value.values():
                self._set_parent_links(item)

    def _assert_parent_type(self, parent):
        """Check the parent against the generated rules (classes_common)."""
        from ..classes_common.parents import assert_parent_type
        from ._import import LOOKUP

        assert_parent_type(self, parent, LOOKUP)

    @field_validator("*", mode="wrap")
    @classmethod
    def _legacy_values(cls, value, handler, info):
        """None is accepted by every field, -1 sets the default value."""
        if value is None:
            return None
        if type(value) is int and value == -1:
            factory = cls.model_fields[info.field_name].default_factory
            if factory is not None:
                return factory()
        return handler(value)

    @classmethod
    def _loaded_values(cls, data):
        """Like the legacy init_dict, the keys that are not fields are ignored.

        These are the serialization keys ("__class__", "__save_date__",
        "__version__") and the properties removed since the file was saved. The
        constructor and the assignments still reject unknown fields.
        """
        keys = set(cls.model_fields)
        keys.update(  # Legacy names of the renamed fields (e.g. "_statements")
            info.alias for info in cls.model_fields.values() if info.alias
        )
        return {key: value for key, value in data.items() if key in keys}

    # Legacy API
    @classmethod
    def from_dict(cls, data, *, base_path=None):
        """Build an object from its as_dict serialization.

        base_path (split JSON files) is not handled: a pydantic class does not
        hold an object saved in a separate file.
        """
        return cls.model_validate(data)

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """Serialize the object in the legacy dictionary format.

        type_handle_ndarray: 0 ndarray as list, 1 copy of the ndarray, 2 ndarray.
        Complex values are str, as the legacy setters stored them.
        """
        if type_handle_ndarray not in (0, 1, 2):
            raise ValueError(f"Unknown type_handle_ndarray: {type_handle_ndarray}")
        return _legacy_dump(self.model_dump(), type_handle_ndarray, keep_function)

    def copy(self):
        """Deep copy of the object (without its parent)."""
        return deepcopy(self)

    def __deepcopy__(self, memo=None):
        values = {
            name: deepcopy(getattr(self, name), memo)
            for name in type(self).model_fields
        }
        return type(self).model_construct(**values)  # Already valid values

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Return the paths of the differing values."""
        if type(other) is not type(self):
            return [f"type({name})"]
        differences = []
        for field_name in type(self).model_fields:
            left = getattr(self, field_name)
            right = getattr(other, field_name)
            path = f"{name}.{field_name}"
            differences.extend(_compare(left, right, path, ignore_list, is_add_value))
        ignored = set(ignore_list or ())
        return [item for item in differences if item not in ignored]

    def _set_None(self):
        """Set the fields to None, recursively clearing the nested objects."""
        for name in type(self).model_fields:
            value = getattr(self, name)
            if isinstance(value, LegacyModel):
                value._set_None()
            else:
                setattr(self, name, None)


def _legacy_dump(value, type_handle_ndarray, keep_function):
    """Convert a python dump to the legacy as_dict format."""
    if isinstance(value, dict):
        return {
            key: _legacy_dump(item, type_handle_ndarray, keep_function)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_legacy_dump(item, type_handle_ndarray, keep_function) for item in value]
    if isinstance(value, np.ndarray):
        if type_handle_ndarray == 0:
            return value.tolist()
        return value.copy() if type_handle_ndarray == 1 else value
    if type(value) is complex:
        return str(value)
    if callable(value) and not keep_function:
        return None
    return value


def _compare(left, right, path, ignore_list, is_add_value):
    """Differences between two field values (recursing into lists and dicts)."""
    if left is None or right is None:
        return [] if left is right else [path + " None mismatch"]
    if isinstance(left, LegacyModel):
        return left.compare(right, path, ignore_list, is_add_value)
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        if len(left) != len(right):
            return [path + " length mismatch"]
        return [
            item
            for index, (a, b) in enumerate(zip(left, right))
            for item in _compare(a, b, f"{path}[{index}]", ignore_list, is_add_value)
        ]
    if isinstance(left, dict) and isinstance(right, dict):
        if left.keys() != right.keys():
            return [path + " keys mismatch"]
        return [
            item
            for key in left
            for item in _compare(
                left[key], right[key], f"{path}[{key!r}]", ignore_list, is_add_value
            )
        ]
    if isinstance(left, np.ndarray) or isinstance(right, np.ndarray):
        equal = np.array_equal(left, right, equal_nan=True)
    else:
        try:
            equal = bool(left == right)
        except (TypeError, ValueError):
            equal = False
    if equal:
        return []
    return [path + (f" (self={left}, other={right})" if is_add_value else "")]
