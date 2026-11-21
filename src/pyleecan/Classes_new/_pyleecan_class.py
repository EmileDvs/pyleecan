"""Target base of the Pyleecan classes built on stdlib dataclasses (hand-written).

``PyleecanClass`` is the Phase 2 design (see PLAN.md): the legacy behaviours
are in ``LegacyClass`` (``_legacy_class.py``), which the generated classes
inherit during Phase 1.

API (shared with the pydantic base ``PyleecanModel``):

- ``model_dump(mode="python"|"json")``: dict of the field values, with a
  ``"__class__"`` key; nested objects are dumped too. In JSON mode, numpy
  arrays are lists and complex values are strings ("1+2j").
- ``model_validate(data)``: build an object from a dump (dacite); a dict with
  ``"__class__"`` builds that class, which must be a subclass of cls. Unknown
  keys are rejected.
- ``model_copy(update=None, deep=False)``
- ``==``: field by field, numpy arrays compared by values.

Validation: the type of every field, and its bounds (``min``/``max`` field
metadata), are checked at construction AND on assignment, with the rules of
the pydantic models (``_validation.py``).
"""

from copy import copy as shallow_copy
from copy import deepcopy
from dataclasses import dataclass, fields
from pathlib import Path
from sys import getsizeof
from typing import Any, ClassVar, get_args, get_origin, get_type_hints

import numpy as np
from dacite import Config, from_dict

from ..classes_common.base import PyleecanBase
from ..classes_common.equality import values_equal
from ._validation import field_checkers


def _to_complex(value):
    """complex from its string form (JSON dumps, legacy files)."""
    return complex(value.replace(" ", "")) if isinstance(value, str) else value


def _dump_value(value, mode):
    """Dump of a field value (see PyleecanClass.model_dump)."""
    if isinstance(value, PyleecanBase):
        return value.model_dump(mode=mode)
    if isinstance(value, dict):
        return {key: _dump_value(item, mode) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_dump_value(item, mode) for item in value]
    if mode == "json":
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, complex):
            return str(value).strip("()")  # Like pydantic: "1+2j"
    return value


@dataclass(eq=False)
class PyleecanClass(PyleecanBase):
    """Target base of the Pyleecan classes built on stdlib dataclasses."""

    _lenient_validation: ClassVar[bool] = False
    """True for the legacy validation rules (see _validation.field_checkers)"""

    def __new__(cls, *args, **kwargs):
        if cls is PyleecanClass:
            raise TypeError("PyleecanClass cannot be instantiated directly")
        return super().__new__(cls)

    def __setattr__(self, name, value):
        checker = field_checkers(type(self), self._lenient_validation).get(name)  # cached
        if checker is not None:
            value = checker(value)  # Validated (and converted) value
        super().__setattr__(name, value)

    # Serialization
    def model_dump(self, mode="python"):
        """Dict of the field values, with the "__class__" key.

        Parameters
        ----------
        mode : str
            "python" (values kept) or "json" (JSON-ready values)

        Returns
        -------
        data : dict
            Values of the fields (nested objects dumped too)
        """
        if mode not in ("python", "json"):
            raise ValueError(f"mode must be 'python' or 'json': {mode!r}")
        data = {
            field_info.name: _dump_value(getattr(self, field_info.name), mode)
            for field_info in fields(self)
            if field_info.metadata.get("serialize", True)
        }
        data["__class__"] = type(self).__name__
        return data

    @classmethod
    def model_validate(cls, data):
        """Build an object from a dump (see model_dump).

        Parameters
        ----------
        data : dict or PyleecanClass
            Dump of the object; a "__class__" key builds that class, which must
            be a subclass of cls. An instance of cls is returned as is.

        Returns
        -------
        obj : PyleecanClass
            The object
        """
        if isinstance(data, cls):
            return data
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__} cannot be built from {type(data).__name__}")
        target = cls._target_class(data)
        if target is not cls:
            return target.model_validate(data)
        values = cls._loaded_values(data)
        return cls._build(values, base_path=None, strict=True)

    @classmethod
    def _target_class(cls, data):
        """Class to build from serialized data (its "__class__" key)."""
        if "__class__" not in data:
            return cls
        from ._import import import_class

        target = import_class(data["__class__"])
        if not issubclass(target, cls):
            raise TypeError(f"{target.__name__} is not a subclass of {cls.__name__}")
        return target

    @classmethod
    def _loaded_values(cls, data):
        """Values of serialized data, without the "__class__" key."""
        return {key: value for key, value in data.items() if key != "__class__"}

    @classmethod
    def _build(cls, values, base_path, strict):
        """Build cls from values (dacite), building the nested objects."""
        hints = get_type_hints(cls)
        values = dict(values)
        for field_info in fields(cls):
            if field_info.name in values:
                values[field_info.name] = cls._deserialize_field(
                    values[field_info.name], hints.get(field_info.name, Any), base_path
                )
        hooks = {np.ndarray: np.asarray, complex: _to_complex}
        for field_info in fields(cls):
            for candidate in cls._walk_types(hints.get(field_info.name)):
                if isinstance(candidate, type) and (
                    issubclass(candidate, PyleecanBase) or hasattr(candidate, "as_dict")
                ):
                    hooks[candidate] = lambda value, target=candidate: (
                        value
                        if isinstance(value, target)
                        else cls._construct_from_dict(target, value, base_path)
                    )
        # The types are checked by the validation of the fields (_validation.py)
        config = Config(type_hooks=hooks, strict=strict, check_types=False)
        return from_dict(cls, values, config=config)

    @classmethod
    def _load_nested(cls, target, data, base_path):
        """Build a nested Pyleecan object of class target."""
        return target.model_validate(data)

    @classmethod
    def _construct_from_dict(cls, target, data, base_path=None):
        """Build a generated class, or another class (SciDataTool) by init_dict."""
        if issubclass(target, PyleecanBase):
            return cls._load_nested(target, data, base_path)
        return target(init_dict=data)

    @classmethod
    def _deserialize_field(cls, value, annotation, base_path):
        from ._import import import_class

        candidates = tuple(
            candidate
            for candidate in cls._walk_types(annotation)
            if isinstance(candidate, type) and issubclass(candidate, PyleecanBase)
        )
        if isinstance(value, str) and candidates and base_path is not None:
            # Legacy: object saved in a separate file (split JSON)
            path = Path(base_path) / value
            if value.endswith((".json", ".json.gz")):
                from ..Functions_new.load import load

                loaded = load(str(path))
                if not isinstance(loaded, candidates):
                    raise TypeError(
                        f"{path}: incompatible serialized class {type(loaded).__name__}"
                    )
                return loaded
        if isinstance(value, dict) and "__class__" in value:
            target = import_class(value["__class__"])
            if candidates and not issubclass(target, candidates):
                raise TypeError(
                    f"Serialized {target.__name__} is incompatible with {annotation}"
                )
            return cls._load_nested(target, value, base_path)
        origin = get_origin(annotation)
        arguments = get_args(annotation)
        if origin not in (list, tuple, dict):
            container = next(
                (
                    candidate
                    for candidate in arguments
                    if get_origin(candidate) in (list, tuple, dict)
                    and isinstance(value, get_origin(candidate))
                ),
                None,
            )
            if container is not None:
                origin = get_origin(container)
                arguments = get_args(container)
        if isinstance(value, list):
            item_type = arguments[0] if origin in (list, tuple) and arguments else Any
            return [
                cls._deserialize_field(item, item_type, base_path) for item in value
            ]
        if isinstance(value, dict):
            item_type = arguments[1] if origin is dict and len(arguments) == 2 else Any
            return {
                key: cls._deserialize_field(item, item_type, base_path)
                for key, item in value.items()
            }
        return value

    @staticmethod
    def _walk_types(type_hint):
        yield type_hint
        for argument in get_args(type_hint):
            yield from PyleecanClass._walk_types(argument)

    # Copy and comparison
    def model_copy(self, update=None, deep=False):
        """Copy of the object.

        Parameters
        ----------
        update : dict, optional
            Field values to change in the copy
        deep : bool
            True to copy the nested values too

        Returns
        -------
        obj : PyleecanClass
            The copy
        """
        new = deepcopy(self) if deep else shallow_copy(self)
        for name, value in (update or {}).items():
            setattr(new, name, value)
        return new

    def __eq__(self, other):
        return type(other) is type(self) and all(
            values_equal(getattr(self, field_info.name), getattr(other, field_info.name))
            for field_info in fields(self)
            if field_info.compare
        )

    __hash__ = None

    def __sizeof__(self):
        return object.__sizeof__(self) + sum(
            getsizeof(getattr(self, field_info.name))
            for field_info in fields(self)
            if field_info.metadata.get("serialize", True)
        )

    def __str__(self):
        return self.__repr__()

    def get_logger(self):
        from ..classes_common.logger_context import get_logger

        return get_logger(self)

    def save(self, *args, **kwargs):
        from ..Functions_new.save import save

        return save(self, *args, **kwargs)
