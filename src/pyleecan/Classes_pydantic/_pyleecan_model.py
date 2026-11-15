"""Target base of the Pyleecan classes built on pydantic ``BaseModel`` (hand-written).

``PyleecanModel`` is the Phase 2 design (see PLAN.md): the legacy behaviours
are in ``LegacyModel`` (``_legacy_model.py``), which the generated classes
inherit during Phase 1.

- Validation: pydantic checks the type of every field, and its bounds (``ge``/``le``
  in ``Field``), at construction AND on assignment (``validate_assignment``).
  Strict mode, like the legacy ``check_var``: no silent conversion ("3" is not
  an int, True is not an int), but an int is accepted for a float.
- Native types: ``complex`` also accepts int, float and its string form;
  ``NDArray`` (numpy has no pydantic support) accepts a list.
- API (shared with the dataclass base ``PyleecanClass``):
  ``model_dump(mode="python"|"json")``, ``model_validate(data)``,
  ``model_copy(deep=...)`` and ``==`` (numpy arrays compared by values).
- Polymorphism: the dump has a ``"__class__"`` key, and a dict with
  ``"__class__"`` builds that class, which must be a subclass of the declared
  type. Unknown keys are rejected.
- Metadata: the attribute docstrings are the field descriptions
  (``use_attribute_docstrings``), bounds are ``annotated_types.Ge``/``Le`` and
  the unit is in ``json_schema_extra``: everything is in ``model_fields``.
"""

from typing import Annotated, Any, ClassVar

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    PlainSerializer,
    PlainValidator,
    Strict,
    model_serializer,
    model_validator,
)
from pydantic_core import PydanticCustomError

from ..classes_common.base import PyleecanBase
from ..classes_common.equality import values_equal
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


def _to_ndarray(value):
    if isinstance(value, np.ndarray):
        return value
    if isinstance(value, (list, tuple)):
        return np.asarray(value)
    raise PydanticCustomError("ndarray_type", "Input should be a ndarray or a list")


NDArray = Annotated[
    np.ndarray,
    PlainValidator(_to_ndarray, json_schema_input_type=list[Any]),
    PlainSerializer(lambda value: value.tolist(), when_used="json"),
]
"""numpy array: a list is converted; kept in python dumps, a list in JSON dumps"""

Complex = Annotated[complex, Strict(False)]
"""complex number (native pydantic type): int, float and "1+2j" are accepted"""


class PyleecanModel(BaseModel, PyleecanBase):
    """Target base of the Pyleecan classes built on pydantic."""

    model_config = ConfigDict(
        strict=True,  # Like check_var: no silent conversion
        validate_assignment=True,  # Check on every assignment, not only at init
        extra="forbid",  # Like FrozenClass: no new attribute
        arbitrary_types_allowed=True,
        use_attribute_docstrings=True,  # Attribute docstring -> field description
        revalidate_instances="never",  # Keep the given (sub)class objects
        polymorphic_serialization=True,  # Dump subclass objects with their fields
        # A legacy field name starting with "_" is the alias of the field (the
        # generator removes the "_"): both names are accepted, the alias is dumped
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
    )

    _package: ClassVar[str] = ""
    """Name of the package of the legacy class module"""

    @model_validator(mode="wrap")
    @classmethod
    def _load_class(cls, data, handler):
        """A dict with "__class__" builds that class (a subclass of cls)."""
        if isinstance(data, dict) and "__class__" in data:
            target = _import_model(data["__class__"])
            data = target._loaded_values(data)
            if target is not cls:
                if not issubclass(target, cls):
                    raise PydanticCustomError(
                        "class_type",
                        "{target} is not a subclass of {expected}",
                        {"target": target.__name__, "expected": cls.__name__},
                    )
                return target.model_validate(data)
        return handler(data)

    @classmethod
    def _loaded_values(cls, data):
        """Values of serialized data, without the "__class__" key."""
        return {key: value for key, value in data.items() if key != "__class__"}

    @model_serializer(mode="wrap")
    def _dump_class(self, handler):
        data = handler(self)
        data["__class__"] = type(self).__name__
        return data

    def __eq__(self, other):
        # BaseModel.__eq__ fails on ndarray fields
        return type(other) is type(self) and all(
            values_equal(getattr(self, name), getattr(other, name))
            for name in type(self).model_fields
        )

    __hash__ = None

    def get_logger(self):
        from ..Functions_pydantic.get_logger import get_logger

        return get_logger(self)

    def save(self, *args, **kwargs):
        from ..Functions_pydantic.save import save

        return save(self, *args, **kwargs)
