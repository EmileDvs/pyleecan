"""Runtime information on the generated Pyleecan classes.

Shared by the class implementations: each implementation package binds
``ClassInfo`` to its own classes (e.g. ``Classes_new/_class_info.py``).

The class information (name, description, inheritance, properties, methods...)
is rebuilt from the classes themselves (stdlib dataclasses or pydantic models):
field annotations, defaults, ``field(metadata=...)`` or pydantic ``Field``
(unit, min, max...) written by the class generator and
the attribute docstrings written below each field (read from the module source,
as linters do, or from the class docstring when the source is not available).
Neither the legacy CSV files nor ``_class_dict.json`` are required.
"""

import ast
import re
import sys
from collections.abc import Callable
from dataclasses import MISSING, fields
from functools import cache
from importlib import import_module
from inspect import cleandoc, getsourcefile
from types import FunctionType, NoneType, UnionType
from typing import Annotated, Any, ForwardRef, NamedTuple, Union, get_args, get_origin

import numpy as np
from annotated_types import Ge, Le
from pydantic_core import PydanticUndefined

from .base import PyleecanBase, is_generated_class
from .class_lookup import ClassLookup, class_module_name

BASE_TYPES = (bool, complex, float, int, str)
"""Python types reported by their plain name"""

DATACLASS_METHODS = frozenset(
    (
        "__init__",
        "__repr__",
        "__eq__",
        "__hash__",
        "__lt__",
        "__le__",
        "__gt__",
        "__ge__",
        "__setattr__",
        "__delattr__",
        "__getstate__",
        "__setstate__",
        "__replace__",
    )
)
"""Methods that @dataclass may add to a class"""

ATTRIBUTES_SECTION = re.compile(r"\n\s*Attributes\s*\n\s*-+\s*(?:\n|$)")
"""Header of the NumPy Attributes section of the generated class docstrings"""

COMPILER_METHODS = frozenset(("__annotate__", "__annotate_func__"))
"""Functions created by the compiler for lazy annotations (Python 3.14)"""


class ClassInfo:
    """Information on all the generated Pyleecan classes of a package.

    ``class_dict`` maps each class name to a dict with the keys:

    - ``name``, ``desc``, ``package``, ``module``, ``class`` (the type object)
    - ``mother`` (``""`` for a base class), ``inherit`` (ordered mothers) and
      ``daughters`` (all the classes inheriting from it)
    - ``methods`` and ``constants`` defined by the class itself
    - ``properties`` (own properties then inherited ones) and ``prop_dict``

    Each property is a dict with the keys ``name``, ``type`` (Pyleecan type
    string such as ``"float"``, ``"[Segment]"`` or ``"{Data}"``),
    ``annotation``, ``desc``, ``unit``, ``min``, ``max`` (None when not set),
    ``as_dict``, ``value`` (static default or None), ``default_factory``
    (callable or None) and ``field`` (the dataclass Field or pydantic FieldInfo).

    The dict is built once per process and package, and shared: do not
    modify it.

    Parameters
    ----------
    package : str
        Name of the class package (e.g. "pyleecan.Classes_new")
    """

    def __init__(self, package):
        self.package = package
        self.class_dict = self.__init_dict__()

    def __init_dict__(self):
        """Get a dict on the pyleecan classes, i.e. class name, description,
        properties, methods, etc.

        Returns
        -------
        class_dict : dict
            dict of class information
        """
        return _build_class_dict(self.package)

    def get_dict(self):
        return self.class_dict

    def get_prop_types(self):
        """Get a set of all defined property types of all classes."""
        type_set = set()

        for cls in self.class_dict.values():
            for prop in cls["prop_dict"].values():
                type_set.add(prop["type"])

        return type_set

    def get_base_classes(self):
        """Get the base classes, i.e. classes that have no mother class."""
        return sorted(
            key for key, item in self.class_dict.items() if not item["mother"]
        )

    def get_mothers(self, cls_name, stop=""):
        """Get a ordered list of the mothers of a class."""
        mothers = []
        if stop not in self.class_dict:
            stop = ""
        if cls_name in self.class_dict:
            mother = self.class_dict[cls_name]["mother"]
            while mother and cls_name != stop:
                mothers.append(mother)
                cls_name = mother
                mother = self.class_dict[mother]["mother"]

        return mothers


@cache
def _build_class_dict(package):
    """Import every generated class of the package and gather its information."""
    classes = _all_classes(package)
    class_dict = {name: _class_info(cls) for name, cls in classes.items()}

    for cls_name, cls_dict in class_dict.items():
        # Inheritance information
        inherit = []
        mother_name = cls_dict["mother"]
        while mother_name:
            inherit.append(mother_name)
            mother_name = class_dict[mother_name]["mother"]
        cls_dict["inherit"] = inherit
        for mother in inherit:
            class_dict[mother]["daughters"].append(cls_name)

    for cls_dict in class_dict.values():
        cls_dict["daughters"].sort()
        # Complete properties with the ones of the mothers
        prop_names = {prop["name"] for prop in cls_dict["properties"]}
        for mother in cls_dict["inherit"]:
            for mother_prop in class_dict[mother]["properties"]:
                if mother_prop["name"] not in prop_names:
                    cls_dict["properties"].append(mother_prop)
                    prop_names.add(mother_prop["name"])
        cls_dict["prop_dict"] = {prop["name"]: prop for prop in cls_dict["properties"]}

    return class_dict


def _all_classes(package):
    """Pyleecan classes defined in the class modules of a package.

    Each class is defined in the module named after it (see class_module_name),
    in one of the sub-packages (see class_lookup.find_module_paths).
    """
    classes = {}
    for module_name, path in ClassLookup(package).module_paths().items():
        module = import_module(f"{package}.{path}")
        for name, value in vars(module).items():
            if (
                is_generated_class(value)
                and value.__module__ == module.__name__
                and class_module_name(name) == module_name
            ):
                classes[name] = value
    return dict(sorted(classes.items()))


def _class_info(cls):
    """Information defined by one class (inherited items are added later)."""
    mother_cls = next(
        (
            base
            for base in cls.__bases__
            if is_generated_class(base)
        ),
        None,
    )
    mother = "" if mother_cls is None else mother_cls.__name__
    mother_fields = (
        set() if mother_cls is None else {f.name for f in _class_fields(mother_cls)}
    )
    own_names = set(_own_annotations(cls))
    descriptions = _attribute_docstrings(cls) or _docstring_attributes(cls)
    properties = [
        _prop_info(cls, field, descriptions.get(field.name, ""))
        for field in _class_fields(cls)
        if field.name in own_names or field.name not in mother_fields
    ]
    return {
        "name": cls.__name__,
        "desc": _class_desc(cls),
        "package": vars(cls).get("_package", ""),
        "module": cls.__module__,
        "class": cls,
        "mother": mother,
        "daughters": [],
        "methods": _own_methods(cls),
        "constants": _own_constants(cls),
        "properties": properties,
    }


def _own_annotations(cls):
    """Names annotated in the class body itself (Python 3.14 lazy annotations)."""
    try:
        from annotationlib import Format, get_annotations
    except ImportError:  # Python < 3.14
        return vars(cls).get("__annotations__", {})
    return get_annotations(cls, format=Format.FORWARDREF)


def _class_desc(cls):
    """First section of the class docstring, before its Attributes section."""
    doc = cls.__doc__
    if not doc or doc.startswith(cls.__name__ + "("):  # dataclass default doc
        return ""
    desc = ATTRIBUTES_SECTION.split(cleandoc(doc), maxsplit=1)[0]
    desc = desc.strip()
    # The generator falls back on the class name when no description is set
    return "" if desc == cls.__name__ else desc


def _own_methods(cls):
    """Methods defined in the class body, without the dataclass generated ones."""
    module_file = getattr(sys.modules[cls.__module__], "__file__", None)
    methods = []
    for name, value in vars(cls).items():
        if isinstance(value, (staticmethod, classmethod)):
            value = value.__func__
        if not isinstance(value, FunctionType) or name in COMPILER_METHODS:
            continue
        # Dunders added by @dataclass come from outside the class module
        if name in DATACLASS_METHODS and value.__code__.co_filename != module_file:
            continue
        methods.append(name)
    return sorted(methods)


def _own_constants(cls):
    """Upper case class attributes defined in the class body."""
    return [
        {"name": name, "value": value}
        for name, value in vars(cls).items()
        if name.isupper() and not isinstance(value, type) and not callable(value)
    ]


def _attribute_docstrings(cls):
    """Map each field of the class body to the docstring written below it."""
    try:
        path = getsourcefile(cls)
        with open(path, encoding="utf-8") as source_file:
            module = ast.parse(source_file.read())
    except OSError, TypeError, SyntaxError:  # no source (e.g. frozen app)
        return {}
    class_node = next(
        (
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == cls.__name__
        ),
        None,
    )
    if class_node is None:
        return {}
    descriptions = {}
    for node, next_node in zip(class_node.body, class_node.body[1:]):
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and isinstance(next_node, ast.Expr)
            and isinstance(next_node.value, ast.Constant)
            and isinstance(next_node.value.value, str)
        ):
            descriptions[node.target.id] = next_node.value.value
    return descriptions


def _docstring_attributes(cls):
    """Map the fields to their description in the class docstring.

    Fallback when the module source is not available. The generator writes a
    NumPy "Attributes" section where each description is followed by a
    "Unit: ...; Default: ..." line.
    """
    doc = cls.__doc__
    if not doc:
        return {}
    parts = ATTRIBUTES_SECTION.split(cleandoc(doc), maxsplit=1)
    if len(parts) < 2:
        return {}
    descriptions = {}
    lines = None
    for line in parts[1].splitlines():
        # A raw newline in a description can prevent cleandoc from dedenting
        header = re.match(r"^\s*(\w+) : \S", line)
        if header:
            lines = descriptions.setdefault(header.group(1), [])
        elif lines is not None and not re.match(r"^\s*(Unit|Default): ", line):
            lines.append(line.strip())
    return {
        name: "" if desc == "No description provided." else desc
        for name, desc in (
            (name, "\n".join(lines)) for name, lines in descriptions.items()
        )
    }


class _FieldRecord(NamedTuple):
    """Field of a dataclass or of a pydantic model, in a common form."""

    name: str
    annotation: Any
    metadata: dict
    default: Any
    default_factory: Any
    field: Any


def _class_fields(cls):
    """Fields of a generated class (without the parent link).

    Pydantic models are recognized by their ``model_fields``, dataclasses
    otherwise (no implementation is imported here).
    """
    if isinstance(getattr(cls, "model_fields", None), dict):
        records = []
        for name, info in cls.model_fields.items():
            extra = info.json_schema_extra
            metadata = dict(extra) if isinstance(extra, dict) else {}
            for item in info.metadata:  # Field(ge=..., le=...)
                if isinstance(item, Ge):
                    metadata["min"] = item.ge
                elif isinstance(item, Le):
                    metadata["max"] = item.le
            records.append(
                _FieldRecord(
                    name,
                    info.annotation,
                    metadata,
                    MISSING if info.default is PydanticUndefined else info.default,
                    MISSING if info.default_factory is None else info.default_factory,
                    info,
                )
            )
        return records
    return [
        _FieldRecord(
            field.name,
            field.type,
            field.metadata,
            field.default,
            field.default_factory,
            field,
        )
        for field in fields(cls)
        if field.name != "parent"
    ]


def _prop_info(cls, field: _FieldRecord, desc=""):
    annotation = _resolve_annotation(cls, field.annotation)
    metadata = field.metadata
    # A pydantic field renamed by the generator keeps its legacy name as alias
    legacy_name = getattr(field.field, "alias", None)
    return {
        "name": legacy_name or field.name,
        "type": _type_name(annotation),
        "annotation": annotation,
        "desc": desc,
        "unit": metadata.get("unit", ""),
        "min": metadata.get("min"),
        "max": metadata.get("max"),
        "as_dict": metadata.get("as_dict", ""),
        "value": None if field.default is MISSING else field.default,
        "default_factory": (
            None if field.default_factory is MISSING else field.default_factory
        ),
        "field": field.field,
    }


def _resolve_annotation(cls, annotation):
    """Evaluate a postponed annotation in the namespace of its module."""
    if isinstance(annotation, ForwardRef):
        annotation = annotation.__forward_arg__
    if not isinstance(annotation, str):
        return annotation
    namespace = dict(vars(sys.modules[cls.__module__]))
    namespace.setdefault(cls.__name__, cls)
    try:
        return eval(annotation, namespace)
    except NameError, AttributeError, SyntaxError, TypeError:
        return annotation


def _type_name(annotation):
    """Convert an annotation to a Pyleecan type string.

    ``float | None`` -> ``"float"``, ``list[Segment]`` -> ``"[Segment]"``,
    ``dict[str, Data]`` -> ``"{Data}"``, ``dict[str, list[Data]]`` ->
    ``"{[Data]}"``, ``np.ndarray`` -> ``"ndarray"``, ``Callable`` ->
    ``"function"``, other classes -> ``"module.Class"``, Any -> ``""``.
    """
    if isinstance(annotation, str):
        return annotation
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (Union, UnionType):
        not_none = [arg for arg in args if arg is not NoneType]
        if len(not_none) == 1:
            return _type_name(not_none[0])
        return " | ".join(_type_name(arg) for arg in not_none)
    if origin is Annotated:  # pydantic field types (Complex, NDArray)
        return _type_name(args[0])
    if annotation is Any or annotation is None:
        return ""
    if annotation is np.ndarray:
        return "ndarray"
    if annotation in BASE_TYPES:
        return annotation.__name__
    if annotation is Callable or origin is Callable:
        return "function"
    if origin is list or annotation is list:
        if not args or args[0] is Any:
            return "list"
        return "[" + _type_name(args[0]) + "]"
    if origin is dict or annotation is dict:
        if len(args) != 2 or args[1] is Any:
            return "dict"
        return "{" + _type_name(args[1]) + "}"
    if isinstance(annotation, type):
        if issubclass(annotation, PyleecanBase):
            return annotation.__name__
        return annotation.__module__ + "." + annotation.__qualname__
    return str(annotation)
