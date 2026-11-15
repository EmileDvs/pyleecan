"""Legacy layer of the pydantic Pyleecan classes (Phase 1 only, hand-written).

``LegacyModel`` adds to the target base ``PyleecanModel`` the behaviours of the
legacy classes, so that the generated classes can be validated against them.
Phase 2 removes this layer: the generated classes then derive from
``PyleecanModel`` directly.

Legacy behaviours:

- every field accepts None (legacy setters skipped the checks for None),
- ``-1`` sets the default value (e.g. a default object) of a field,
- an int field accepts a float with an integer value (converted to int),
- a function field accepts its source (lambda or path to a python file,
  converted to a ``SourceFunction`` and saved by its source),
- an object field accepts the path of a file to load, or an array for an
  ImportMatrix (``classes_common.legacy_values``),
- nested objects get a ``parent`` link to the object holding them, also
  when they are added to a list or a dict field (``ParentList``,
  ``ParentDict``: the legacy getters set it on each read),
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

from ..classes_common.equality import compare_values
from ..classes_common.functions import SourceFunction, is_function_annotation
from ..classes_common.legacy_dump import is_complex_annotation, legacy_field
from ..classes_common.legacy_values import annotation_classes, legacy_object_value
from ..classes_common.parent_containers import with_parent
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
            self._store_with_parent(name)

    def _store_with_parent(self, name):
        """Lists and dicts of a field set the parent of the objects added later."""
        stored = with_parent(self.__dict__.get(name), self)
        if stored is not self.__dict__.get(name):
            self.__dict__[name] = stored  # Validated value, wrapped (ParentList...)
        self._set_parent_links(stored)

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
            self._store_with_parent(name)

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
        """Legacy values: None, -1, integral float for int, function source."""
        if value is None:
            return None
        field_info = cls.model_fields[info.field_name]
        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and is_complex_annotation(field_info.annotation)
        ):
            return value  # Legacy: an int or a float given to a complex is kept
        if type(value) is int and value == -1:
            if field_info.default_factory is not None:
                return field_info.default_factory()
            classes = annotation_classes(field_info.annotation)
            if classes:  # Like the legacy setters: the declared class
                return classes[0]()
        if (
            isinstance(value, (float, np.floating))
            and value % 1 == 0
            and field_info.annotation in (int, int | None)
        ):
            value = int(value)
        elif isinstance(value, str) and is_function_annotation(field_info.annotation):
            try:
                value = SourceFunction(value)
            except ValueError:
                pass  # Rejected by the pydantic validation
        else:
            from ._import import import_class

            value = legacy_object_value(value, field_info.annotation, import_class)
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
        values = {}
        for name, info in type(self).model_fields.items():
            extra = info.json_schema_extra if isinstance(info.json_schema_extra, dict) else {}
            values[info.alias or name] = legacy_field(  # Legacy name of a renamed field
                getattr(self, name),
                is_complex_annotation(info.annotation),
                extra.get("as_dict"),
                type_handle_ndarray,
                keep_function,
                kwargs,
            )
        values["__class__"] = type(self).__name__
        return values

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
            differences.extend(
                compare_values(left, right, path, ignore_list, is_add_value)
            )
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
