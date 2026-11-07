"""Shared abstract base for experimental dataclass-based Pyleecan classes."""

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field, fields
from sys import getsizeof
from typing import Any, get_args, get_type_hints

import numpy as np
from dacite import Config, from_dict

from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.Load.retrocompatibility import (
    construct_experimental_class,
    load_experimental_normalization_values,
)
from pyleecan.Functions.save import save


@dataclass(eq=False)
class PyleecanClass(ABC):
    """Abstract base providing common behavior for generated Pyleecan dataclasses."""

    parent: Any = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
        metadata={"serialize": False, "compare": False},
    )

    @abstractmethod
    def __post_init__(self):
        self._set_child_parents()

    @classmethod
    def from_dict(cls, data):
        """Create this dataclass from a Pyleecan-style dictionary."""
        values = {
            key: load_experimental_normalization_values(value)
            for key, value in data.items()
            if key != "__class__"
        }
        hints = get_type_hints(cls)
        hooks = {np.ndarray: np.asarray}
        for field_info in fields(cls):
            field_type = hints.get(field_info.name)
            for candidate in cls._walk_types(field_type):
                if isinstance(candidate, type) and hasattr(candidate, "as_dict"):
                    hooks[candidate] = lambda value, target=candidate: (
                        value
                        if isinstance(value, target)
                        else construct_experimental_class(target, value)
                    )
        instance = from_dict(cls, values, config=Config(type_hooks=hooks))
        instance._set_child_parents()
        return instance

    def _set_child_parents(self):
        """Set parent links on nested Pyleecan objects."""
        for field_info in fields(self):
            if field_info.name != "parent":
                self._set_parent_links(getattr(self, field_info.name), self)

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """Serialize dataclass fields using Pyleecan's object dictionary format."""
        if type_handle_ndarray not in (0, 1, 2):
            raise ValueError(f"Unknown type_handle_ndarray: {type_handle_ndarray}")
        values = {}
        for field_info in fields(self):
            if field_info.metadata.get("serialize", True):
                if field_info.metadata.get("as_dict") in ("1", "2"):
                    values[field_info.name] = None
                else:
                    values[field_info.name] = self._serialize_value(
                        getattr(self, field_info.name),
                        type_handle_ndarray,
                        keep_function,
                        kwargs,
                    )
        values["__class__"] = type(self).__name__
        return values

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare dataclass fields and return paths to differing values."""
        if type(other) is not type(self):
            return [f"type({name})"]
        ignored = set(ignore_list or ())
        differences = []
        for field_info in fields(self):
            if not field_info.metadata.get("compare", True):
                continue
            left = getattr(self, field_info.name)
            right = getattr(other, field_info.name)
            field_name = f"{name}.{field_info.name}"
            if left is None or right is None:
                if left is not right:
                    differences.append(field_name + " None mismatch")
                continue
            if hasattr(left, "compare"):
                differences.extend(
                    left.compare(
                        right,
                        name=field_name,
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
                continue
            if isinstance(left, np.ndarray) or isinstance(right, np.ndarray):
                equal = np.array_equal(left, right, equal_nan=True)
            else:
                try:
                    equal = bool(left == right)
                except TypeError, ValueError:
                    equal = False
            if not equal:
                suffix = f" (self={left}, other={right})" if is_add_value else ""
                differences.append(field_name + suffix)
        return [item for item in differences if item not in ignored]

    def __eq__(self, other):
        return isinstance(other, type(self)) and not self.compare(other)

    def copy(self):
        """Copy dataclass values and their nested Pyleecan objects."""
        values = {}
        for field_info in fields(self):
            if not field_info.init:
                continue
            mode = field_info.metadata.get("as_dict")
            value = getattr(self, field_info.name)
            if mode == "1":
                values[field_info.name] = None
            elif mode == "2":
                values[field_info.name] = value
            else:
                values[field_info.name] = self._copy_value(value)
        return type(self)(**values)

    def _set_None(self):
        """Set fields to None, recursively clearing nested objects."""
        for field_info in fields(self):
            if field_info.name == "parent":
                continue
            value = getattr(self, field_info.name)
            if value is not None and hasattr(value, "_set_None"):
                value._set_None()
            else:
                setattr(self, field_info.name, None)

    def __sizeof__(self):
        return object.__sizeof__(self) + sum(
            getsizeof(getattr(self, field_info.name))
            for field_info in fields(self)
            if field_info.name != "parent"
        )

    def __str__(self):
        return self.__repr__()

    def get_logger(self):
        return get_logger(self)

    def save(self, *args, **kwargs):
        return save(self, *args, **kwargs)

    @staticmethod
    def _walk_types(type_hint):
        yield type_hint
        for argument in get_args(type_hint):
            yield from PyleecanClass._walk_types(argument)

    @staticmethod
    def _set_parent_links(value, parent):
        if isinstance(value, (list, tuple)):
            for item in value:
                PyleecanClass._set_parent_links(item, parent)
        elif isinstance(value, dict):
            for item in value.values():
                PyleecanClass._set_parent_links(item, parent)
        elif hasattr(value, "parent"):
            assert_parent_type = getattr(value, "_assert_parent_type", None)
            if assert_parent_type is not None:
                assert_parent_type(parent)
            value.parent = parent

    @staticmethod
    def _serialize_value(value, type_handle_ndarray, keep_function, kwargs):
        if value is None:
            return None
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
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        if isinstance(value, dict):
            return {
                key: PyleecanClass._serialize_value(
                    item, type_handle_ndarray, keep_function, kwargs
                )
                for key, item in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [
                PyleecanClass._serialize_value(
                    item, type_handle_ndarray, keep_function, kwargs
                )
                for item in value
            ]
        if type(value) is complex:
            return str(value)
        if callable(value) and not keep_function:
            return None
        return value

    @staticmethod
    def _copy_value(value):
        if value is None:
            return None
        if isinstance(value, list):
            return [PyleecanClass._copy_value(item) for item in value]
        if isinstance(value, dict):
            return {key: PyleecanClass._copy_value(item) for key, item in value.items()}
        if hasattr(value, "copy"):
            return value.copy()
        return deepcopy(value)
