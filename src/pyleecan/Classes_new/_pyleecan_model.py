"""Base of the Pyleecan classes built on pydantic ``BaseModel`` (hand-written).

The classes of the legacy packages listed in the class generator
(``PYDANTIC_PACKAGES``) derive from ``PyleecanModel``; the other classes are
stdlib dataclasses deriving from ``PyleecanClass`` (``_pyleecan_class.py``).

Compared to ``Classes_new/_pyleecan_class.py`` (stdlib dataclass + dacite):

- Validation: pydantic checks the type of every field, and its bounds (``ge``/``le``
  in ``Field``), at construction AND on assignment (``validate_assignment``).
  Strict mode is used, like the legacy ``check_var``: no silent conversion
  ("3" is not an int, True is not an int), but an int is accepted for a float.
- Loading: ``model_validate`` builds the nested objects (no dacite); a dict with a
  ``"__class__"`` key (legacy serialization) builds that class, which must be a
  subclass of the declared type.
- Serialization: ``model_dump`` (``as_dict`` keeps the legacy format, with
  ``"__class__"`` and the actual class of nested objects).
- Metadata: the attribute docstrings are the field descriptions
  (``use_attribute_docstrings``), bounds are ``annotated_types.Ge``/``Le`` and
  the unit is in ``json_schema_extra``: everything is in ``model_fields``.

Legacy behaviours kept, on top of pydantic:

- every field accepts None (legacy setters skipped the checks for None),
- ``-1`` sets the default value (e.g. a default object) of a field,
- nested objects get a ``parent`` link to the object holding them.
"""

from copy import deepcopy
from inspect import getattr_static
from types import FunctionType
from typing import Annotated, Any, ClassVar

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    PlainSerializer,
    PlainValidator,
    PrivateAttr,
    SerializationInfo,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic_core import PydanticCustomError

from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..classes_common.base import PyleecanBase
from ._import import import_class


def _import_model(class_name):
    """Class of serialized data ("__class__" key), only known at runtime."""
    from ..classes_common.errors import InitUnKnowClassError

    try:
        return import_class(class_name)
    except InitUnKnowClassError as error:
        raise PydanticCustomError(
            "unknown_class", "Unknown class {class_name}", {"class_name": class_name}
        ) from error


# Field types needing a conversion or a legacy serialization
def _to_ndarray(value):
    if isinstance(value, np.ndarray):
        return value
    if isinstance(value, (list, tuple)):
        return np.asarray(value)
    raise PydanticCustomError("ndarray_type", "Input should be a ndarray or a list")


def _ndarray_as_dict(value, info: SerializationInfo):
    mode = (info.context or {}).get("type_handle_ndarray", 0)
    if info.mode_is_json() or mode == 0:
        return value.tolist()
    return value.copy() if mode == 1 else value


NDArray = Annotated[
    np.ndarray,
    PlainValidator(_to_ndarray, json_schema_input_type=list[Any]),
    PlainSerializer(_ndarray_as_dict),
]
"""numpy array; a list is converted (legacy set_array), serialized as a list"""


def _to_complex(value):
    if isinstance(value, (int, float, complex, np.number)) and not isinstance(
        value, (bool, np.bool_)
    ):
        return complex(value)
    if isinstance(value, str):  # Legacy serialization of complex values
        try:
            return complex(value.replace(" ", ""))
        except ValueError:
            pass
    raise PydanticCustomError("complex_type", "Input should be a complex number")


Complex = Annotated[
    complex,
    PlainValidator(_to_complex, json_schema_input_type=complex | str),
    PlainSerializer(str),
]
"""complex number; int and float are accepted, serialized as str (legacy)"""


class PyleecanModel(BaseModel, PyleecanBase):
    """Base of the Pyleecan classes built on pydantic."""

    model_config = ConfigDict(
        strict=True,  # Like check_var: no silent conversion
        validate_assignment=True,  # Check on every assignment, not only at init
        extra="forbid",  # Like FrozenClass: no new attribute
        arbitrary_types_allowed=True,
        use_attribute_docstrings=True,  # Attribute docstring -> field description
        revalidate_instances="never",  # Keep the given (sub)class objects
        polymorphic_serialization=True,  # Dump subclass objects with their fields
    )

    _parent: Any = PrivateAttr(default=None)

    _package: ClassVar[str] = ""
    """Name of the package of the legacy class module"""

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
        if isinstance(value, PyleecanModel):
            value._assert_parent_type(self)
            value._parent = self
        elif isinstance(value, (list, tuple)):
            for item in value:
                self._set_parent_links(item)
        elif isinstance(value, dict):
            for item in value.values():
                self._set_parent_links(item)

    # Legacy behaviours on top of the pydantic validation
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

    @model_validator(mode="wrap")
    @classmethod
    def _load_class(cls, data, handler):
        """A dict with "__class__" (legacy serialization) builds that class.

        Like the legacy init_dict, the keys that are not fields of the class are
        ignored: serialization keys ("__save_date__", "__version__") and the
        properties removed since the file was saved. The constructor and the
        assignments still reject unknown fields.
        """
        if isinstance(data, dict) and "__class__" in data:
            target = _import_model(data["__class__"])
            data = {
                key: value for key, value in data.items() if key in target.model_fields
            }
            if target is not cls:
                if not issubclass(target, cls):
                    raise PydanticCustomError(
                        "class_type",
                        "{target} is not a subclass of {expected}",
                        {"target": target.__name__, "expected": cls.__name__},
                    )
                return target.model_validate(data)
        return handler(data)

    @model_serializer(mode="wrap")
    def _dump_class(self, handler):
        data = handler(self)
        data["__class__"] = type(self).__name__
        return data

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
        keep_function is not handled by the prototype (no function field).
        """
        if type_handle_ndarray not in (0, 1, 2):
            raise ValueError(f"Unknown type_handle_ndarray: {type_handle_ndarray}")
        return self.model_dump(context={"type_handle_ndarray": type_handle_ndarray})

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

    def __eq__(self, other):
        # BaseModel.__eq__ fails on ndarray fields and compares the parents
        return isinstance(other, type(self)) and not self.compare(other)

    __hash__ = None

    def _assert_parent_type(self, parent):
        """Check the parent against the generated rules (_parent_types.py)."""
        from ._pyleecan_class import PyleecanClass

        PyleecanClass._assert_parent_type(self, parent)

    def get_logger(self):
        return get_logger(self)

    def save(self, *args, **kwargs):
        return save(self, *args, **kwargs)

    def _set_None(self):
        """Set the fields to None, recursively clearing the nested objects."""
        for name in type(self).model_fields:
            value = getattr(self, name)
            if isinstance(value, PyleecanModel):
                value._set_None()
            else:
                setattr(self, name, None)


def _compare(left, right, path, ignore_list, is_add_value):
    """Differences between two field values (recursing into lists and dicts)."""
    if left is None or right is None:
        return [] if left is right else [path + " None mismatch"]
    if isinstance(left, PyleecanModel):
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
