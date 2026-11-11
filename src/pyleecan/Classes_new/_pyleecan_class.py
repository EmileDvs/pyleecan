"""Shared base for experimental dataclass-based Pyleecan classes."""

from copy import deepcopy
from dataclasses import dataclass, field, fields
from importlib import import_module
from pathlib import Path
from sys import getsizeof
from typing import Any, get_args, get_origin, get_type_hints

import numpy as np
from dacite import Config, from_dict

from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.Load.import_class import import_class as import_legacy_class
from pyleecan.Functions.save import save
from pyleecan.Functions_new.Load.retrocompatibility import NORMALIZATION_CLASS_NAMES

from ._parent_types import PARENT_TYPES


def import_experimental_class(mod_name, class_name, prop_name=""):
    """Load experimental normalizations under either name, or a legacy class."""
    package = __package__.rsplit(".", 1)[0]
    if mod_name == package + ".Classes":
        for old_name, new_name in NORMALIZATION_CLASS_NAMES.items():
            if class_name in (old_name, new_name):
                module = import_module(f"{package}.Classes_new.{old_name.lower()}")
                return getattr(module, new_name)
    return import_legacy_class(mod_name, class_name, prop_name)


def construct_experimental_class(class_obj, data):
    """Construct an experimental dataclass or a legacy init_dict class."""
    if issubclass(class_obj, PyleecanClass):
        return class_obj.from_dict(data)
    return class_obj(init_dict=data)


def load_experimental_normalization_values(value):
    """Convert serialized experimental normalizations recursively."""
    if isinstance(value, dict):
        class_name = value.get("__class__")
        if class_name in NORMALIZATION_CLASS_NAMES or class_name in (
            NORMALIZATION_CLASS_NAMES.values()
        ):
            package = __package__.rsplit(".", 1)[0]
            target = import_experimental_class(package + ".Classes", class_name)
            return target.from_dict(value)
        return {
            key: load_experimental_normalization_values(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [load_experimental_normalization_values(item) for item in value]
    return value


@dataclass(eq=False)
class PyleecanClass:
    """Base providing common behavior for generated Pyleecan dataclasses."""

    parent: Any = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
        metadata={"serialize": False, "compare": False},
    )

    def __new__(cls, *args, **kwargs):
        if cls is PyleecanClass:
            raise TypeError("PyleecanClass cannot be instantiated directly")
        return super().__new__(cls)

    def __post_init__(self):
        self._set_child_parents()

    def __setattr__(self, name, value):
        if name != "parent" and name in self.__dataclass_fields__:
            field_info = self.__dataclass_fields__[name]
            if type(value) is int and value == -1:
                class_name = field_info.metadata.get("default_class")
                if class_name is not None:
                    value = self._construct_default_class(class_name)
            self._set_parent_links(value, self)
        super().__setattr__(name, value)

    @staticmethod
    def _construct_default_class(class_name):
        from ._import import import_class

        return import_class(class_name)()

    @classmethod
    def from_dict(cls, data, *, base_path=None):
        """Create this dataclass, resolving split JSON references from base_path.

        Legacy serialized None values are retained even for non-optional fields.
        """
        hints = get_type_hints(cls)
        values = dict(data)
        for field_info in fields(cls):
            if field_info.name in values:
                values[field_info.name] = cls._deserialize_field(
                    values[field_info.name], hints.get(field_info.name, Any), base_path
                )
        values.pop("__class__", None)
        for field_info in fields(cls):
            value = values.get(field_info.name)
            class_name = field_info.metadata.get("default_class")
            if class_name is not None and type(value) is int and value == -1:
                values[field_info.name] = cls._construct_default_class(class_name)
        # Legacy setters accept None even for properties declared as non-optional.
        null_fields = [
            field_info.name
            for field_info in fields(cls)
            if field_info.init
            and field_info.name in values
            and values[field_info.name] is None
            and hints.get(field_info.name) is not Any
            and type(None) not in get_args(hints.get(field_info.name))
        ]
        for name in null_fields:
            values.pop(name)
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
        for name in null_fields:
            setattr(instance, name, None)
        instance._set_child_parents()
        return instance

    @classmethod
    def _deserialize_field(cls, value, annotation, base_path):
        from ._import import import_class

        candidates = tuple(
            candidate
            for candidate in cls._walk_types(annotation)
            if isinstance(candidate, type) and issubclass(candidate, PyleecanClass)
        )
        if isinstance(value, str) and candidates and base_path is not None:
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
            return target.from_dict(value, base_path=base_path)
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

    def _set_child_parents(self):
        """Set parent links on nested Pyleecan objects."""
        for field_info in fields(self):
            if field_info.name != "parent":
                self._set_parent_links(getattr(self, field_info.name), self)

    def _assert_parent_type(self, parent):
        """Validate a parent against the generated rules inherited by this class."""
        if parent is None:
            return
        for cls in type(self).__mro__:
            module_prefix = __package__ + "."
            if not cls.__module__.startswith(module_prefix):
                continue
            key = (cls.__module__[len(module_prefix) :], cls.__name__)
            if key in PARENT_TYPES:
                parent_names = PARENT_TYPES[key]
                parent_types = tuple(
                    getattr(import_module("." + module, __package__), name)
                    for module, name in parent_names
                )
                if not isinstance(parent, parent_types):
                    expected = " or ".join(name for _, name in parent_names)
                    raise TypeError(
                        f"{cls.__name__} parent must be an instance of {expected}, "
                        f"or None; got {type(parent).__name__}"
                    )
                return

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
