"""Experimental dataclass-based class generator."""

import ast
from os.path import dirname, join
from textwrap import indent

import black

from ...Generator import PYTHON_TYPE, TAB
from ...Generator.ClassGenerator.class_generator import (
    CLASS_BODY_CONSTANTS,
    CLASS_MODULE_CONSTANT_EXPRESSIONS,
    CLASS_MODULE_CONSTANTS,
    _apply_import_style,
    _apply_numpy_import_style,
    _organize_header_imports,
    _prepare_class_methods,
    _regroup_pyleecan_imports,
    get_class_import_graph,
)
from ...Generator.ClassGenerator.import_method_generator import import_method
from ...Generator.read_fct import (
    find_import_type,
    get_value_str,
    is_dict_list_pyleecan_type,
    is_dict_pyleecan_type,
    is_list_pyleecan_type,
)

_BASE_TYPES = {"bool", "complex", "float", "int", "str"}


def _is_none_default(value):
    return value is None or value == "None"


def _field_type(prop_type, default, gen_dict, soft_name):
    """Return a Python annotation and imports needed for one CSV property."""
    imports = set()

    def resolve_type(type_name):
        if type_name in _BASE_TYPES:
            return type_name
        if type_name == "ndarray":
            imports.add("import numpy as np")
            return "np.ndarray"
        if type_name == "function":
            imports.update(("from typing import Any, Callable",))
            return "Callable[..., Any]"
        if type_name in ("list", "[]"):
            imports.add("from typing import Any")
            return "list[Any]"
        if type_name == "dict":
            imports.add("from typing import Any")
            return "dict[str, Any]"
        if type_name in ("[ndarray]", "{ndarray}"):
            imports.add("import numpy as np")
            return (
                "list[np.ndarray]"
                if type_name == "[ndarray]"
                else "dict[str, np.ndarray]"
            )
        if is_list_pyleecan_type(type_name):
            return f"list[{resolve_type(type_name[1:-1])}]"
        if is_dict_list_pyleecan_type(type_name):
            return f"dict[str, list[{resolve_type(type_name[2:-2])}]]"
        if is_dict_pyleecan_type(type_name):
            return f"dict[str, {resolve_type(type_name[1:-1])}]"

        if type_name in gen_dict:
            imports.add(f"from {soft_name}.Classes.{type_name} import {type_name}")
            return type_name
        if "." in type_name:
            module_name, _, symbol = type_name.rpartition(".")
            imports.add(f"from {module_name} import {symbol}")
            return symbol
        imports.add("from typing import Any")
        return "Any"

    annotation = resolve_type(prop_type) if prop_type else "Any"
    if _is_none_default(default) and annotation not in ("Any", "None"):
        annotation = f"{annotation} | None"
    return annotation, imports


def _field_default(prop):
    """Format a dataclass default, using field() only when it is required."""
    prop_type = prop["type"]
    value = prop["value"]
    metadata = {}
    if prop.get("as_dict") not in (None, ""):
        metadata["as_dict"] = prop["as_dict"]

    requires_field = False
    if value in ("", None):
        if prop_type in ("list", "[]", "[ndarray]"):
            default = "default_factory=list"
            requires_field = True
        elif prop_type in ("dict", "{ndarray}"):
            default = "default_factory=dict"
            requires_field = True
        else:
            default = "None"
    elif prop_type == "list" and value == -1:
        default = "default_factory=list"
        requires_field = True
    elif prop_type == "dict" and value == -1:
        default = "default_factory=dict"
        requires_field = True
    elif prop_type == "ndarray" and isinstance(value, list):
        default = f"default_factory=lambda: np.array({value!r})"
        requires_field = True
    elif prop_type in ("list", "dict", "[ndarray]", "{ndarray}") and isinstance(
        value, (list, dict)
    ):
        default = f"default_factory=lambda: {value!r}"
        requires_field = True
    elif prop_type in PYTHON_TYPE:
        default = get_value_str(value, prop_type)
    elif isinstance(value, str) and value.endswith("()"):
        default = f"default_factory={value[:-2]}"
        requires_field = True
    else:
        default = repr(value)

    if metadata:
        requires_field = True
    if not requires_field:
        return default

    field_args = (
        default if default.startswith("default_factory=") else f"default={default}"
    )
    if metadata:
        field_args += f", metadata={metadata!r}"
    return f"field({field_args})"


def _attribute_docstring(description):
    """Format a CSV description as a safe triple-quoted attribute docstring."""
    escaped_description = repr(description)[1:-1]
    return f'"""{escaped_description}"""'


def _display_default(prop):
    value = prop["value"]
    prop_type = prop["type"]
    if value in ("", None, "None"):
        if prop_type == "list":
            return "[]"
        if prop_type == "dict":
            return "{}"
        return "None"
    if prop_type == "bool":
        return get_value_str(value, prop_type)
    if prop_type in PYTHON_TYPE:
        formatted = get_value_str(value, prop_type)
        if prop_type == "str":
            return formatted
        return formatted
    return repr(value)


def _class_docstring(class_dict):
    """Build a NumPy-style class docstring from class and property metadata."""
    description = class_dict.get("desc") or class_dict["name"]
    lines = [description, "", "Attributes", "----------"]
    for prop in class_dict["properties"]:
        prop_type = prop.get("type") or "Any"
        if prop.get("value") in ("", None, "None"):
            prop_type += " or None"
        lines.extend(
            [
                f"{prop['name']} : {prop_type}",
                *(
                    [f"    {line}" for line in prop["desc"].splitlines()]
                    if prop.get("desc")
                    else ["    No description provided."]
                ),
            ]
        )
        details = []
        if prop.get("unit"):
            details.append(f"Unit: {prop['unit']}")
        details.append(f"Default: {_display_default(prop)}")
        if prop.get("min") not in (None, ""):
            details.append(f"Minimum: {prop['min']}")
        if prop.get("max") not in (None, ""):
            details.append(f"Maximum: {prop['max']}")
        lines.extend(f"    {detail}" for detail in details)
    return '"""' + "\n".join(lines) + '\n"""'


def _generic_methods():
    return '''    @classmethod
    def from_dict(cls, data):
        """Create this dataclass from a Pyleecan-style dictionary."""
        values = {key: value for key, value in data.items() if key != "__class__"}
        hints = get_type_hints(cls)
        hooks = {}
        for field_info in fields(cls):
            field_type = hints.get(field_info.name)
            for candidate in _walk_types(field_type):
                if isinstance(candidate, type) and hasattr(candidate, "as_dict"):
                    hooks[candidate] = lambda value, target=candidate: (
                        value if isinstance(value, target) else target(init_dict=value)
                    )
        instance = from_dict(cls, values, config=Config(type_hooks=hooks))
        instance._set_child_parents()
        return instance

    def _set_child_parents(self):
        """Set parent links on nested Pyleecan objects."""
        for field_info in fields(self):
            if field_info.name == "parent":
                continue
            _set_parent_links(getattr(self, field_info.name), self)

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
                    values[field_info.name] = _serialize_value(
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
                except (TypeError, ValueError):
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
                values[field_info.name] = _copy_value(value)
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
'''


def _runtime_helpers():
    return """def _walk_types(type_hint):
    yield type_hint
    for argument in get_args(type_hint):
        yield from _walk_types(argument)


def _set_parent_links(value, parent):
    if isinstance(value, (list, tuple)):
        for item in value:
            _set_parent_links(item, parent)
    elif isinstance(value, dict):
        for item in value.values():
            _set_parent_links(item, parent)
    elif hasattr(value, "parent"):
        value.parent = parent


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
            key: _serialize_value(item, type_handle_ndarray, keep_function, kwargs)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [
            _serialize_value(item, type_handle_ndarray, keep_function, kwargs)
            for item in value
        ]
    if type(value) is complex:
        return str(value)
    if callable(value) and not keep_function:
        return None
    return value


def _copy_value(value):
    if value is None:
        return None
    if isinstance(value, list):
        return [_copy_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _copy_value(item) for key, item in value.items()}
    if hasattr(value, "copy"):
        return value.copy()
    return deepcopy(value)
"""


def generate_class_new(
    gen_dict,
    class_name,
    path_to_gen,
    soft_name="pyleecan",
    is_log=True,
    import_style="absolute",
    output_name=None,
):
    """Generate one experimental dataclass-based Pyleecan class.

    Methods are prepared by the existing generator, retaining its method import
    resolution, helper inlining, and circular-import handling.
    """
    if import_style not in ("relative", "absolute"):
        raise ValueError("import_style must be 'relative' or 'absolute'")

    class_dict = gen_dict[class_name]
    generated_name = output_name or class_name + "_new"
    class_pack = class_dict["package"]
    source_class_dir = join(dirname(path_to_gen), "Classes")
    class_import_graph = get_class_import_graph(source_class_dir, gen_dict, soft_name)
    reserved_names = {prop["name"] for prop in class_dict["properties"]}
    reserved_names.update(constant["name"] for constant in class_dict["constants"])
    reserved_names.update(method.split(".")[-1] for method in class_dict["methods"])
    (
        method_sources,
        method_imports,
        fallback_reasons,
        class_attributes,
        method_default_overrides,
        class_error_definitions,
    ) = _prepare_class_methods(
        path_to_gen,
        class_pack,
        class_name,
        class_dict["methods"],
        soft_name,
        reserved_names=reserved_names,
        class_import_graph=class_import_graph,
    )

    class_path = join(path_to_gen, generated_name + ".py")
    imports = {
        "from copy import deepcopy",
        "from dataclasses import dataclass, field, fields",
        "from sys import getsizeof",
        "from typing import Any, ClassVar, get_args, get_type_hints",
        "import numpy as np",
        "from dacite import Config, from_dict",
        f"from {soft_name}.Functions.get_logger import get_logger",
        f"from {soft_name}.Functions.save import save",
    }

    for prop in class_dict["properties"]:
        annotation, type_imports = _field_type(
            prop["type"], prop["value"], gen_dict, soft_name
        )
        imports.update(type_imports)

    for method in class_dict["methods"]:
        if method_sources[method] is None:
            imports.add(import_method(class_pack, class_name, method).strip())
    imports.update(ast.unparse(node) for node in method_imports)
    imports.update(
        f"from {soft_name}.Classes.{name} import {name}"
        for name in find_import_type(gen_dict, class_dict, [])
        if name in gen_dict and name != class_name
    )

    chunks = [
        "# Experimental dataclass generated from "
        + class_dict["path"][class_dict["path"].find("Generator") :]
        + "\n",
        '"""Generated experimental dataclass; do not edit by hand."""\n\n',
        "\n".join(sorted(imports)) + "\n\n",
        _runtime_helpers() + "\n\n",
        f"@dataclass(eq=False)\nclass {generated_name}:\n",
        indent(_class_docstring(class_dict), TAB) + "\n\n",
    ]

    body = []
    body.extend(
        f"{TAB}{name}: ClassVar = {value!r}\n"
        for name, value in CLASS_MODULE_CONSTANTS.get(class_name, {}).items()
    )
    body.extend(
        f"{TAB}{name}: ClassVar = {expression}\n"
        for name, expression in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(
            class_name, {}
        ).items()
    )
    body.extend(
        f"{TAB}{name}: ClassVar = {expression}\n"
        for name, expression in CLASS_BODY_CONSTANTS.get(class_name, {}).items()
    )
    body.extend(
        f"{TAB}{constant['name']}: ClassVar = {constant['value']}\n"
        for constant in class_dict["constants"]
        if constant["name"] not in CLASS_MODULE_CONSTANTS.get(class_name, {})
        and constant["name"]
        not in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(class_name, {})
    )
    body.extend(f"{TAB}{ast.unparse(assignment)}\n" for assignment in class_attributes)

    if not body:
        body.append(f"{TAB}pass\n")

    body.append(
        f'{TAB}parent: Any = field(default=None, init=False, repr=False, compare=False, metadata={{"serialize": False, "compare": False}})\n'
    )
    if not any(constant["name"] == "VERSION" for constant in class_dict["constants"]):
        body.append(f"{TAB}VERSION: ClassVar = 1\n")
    for prop in class_dict["properties"]:
        annotation, _ = _field_type(prop["type"], prop["value"], gen_dict, soft_name)
        body.append(f"{TAB}{prop['name']}: {annotation} = {_field_default(prop)}\n")
        if prop.get("desc"):
            body.append(f"{TAB}{_attribute_docstring(prop['desc'])}\n")

    body.append(f"\n{TAB}def __post_init__(self):\n")
    body.append(f"{TAB}{TAB}self._set_child_parents()\n")
    body.extend(_generic_methods().splitlines(keepends=True))

    for method in class_dict["methods"]:
        if method_sources[method] is None:
            body.append(f"\n{TAB}{method.split('.')[-1]} = {method.split('.')[-1]}\n")
            continue
        body.append(
            f"\n{TAB}# Inlined from Methods.{class_pack}.{class_name}.{method}\n"
        )
        body.append(indent(method_sources[method], TAB) + "\n")
        for override in method_default_overrides[method]:
            body.append(f"{TAB}{ast.unparse(override)}\n")
    body.extend(
        f"\n{TAB}{ast.unparse(definition).replace(chr(10), chr(10) + TAB)}\n"
        for definition in class_error_definitions
    )
    chunks.append("".join(body))
    if class_error_definitions:
        chunks.append(
            "\n"
            + "".join(
                f"{definition.name} = {generated_name}.{definition.name}\n"
                for definition in class_error_definitions
            )
        )
    if fallback_reasons:
        chunks.append(
            "\n# Methods retained as imports because they could not be inlined:\n"
            + "".join(
                f"# {method}: {reason}\n" for method, reason in fallback_reasons.items()
            )
        )

    source = "".join(chunks)
    source = _apply_numpy_import_style(source)
    source = _apply_import_style(source, soft_name, import_style)
    source = _organize_header_imports(source, generated_name, class_path)
    source = _regroup_pyleecan_imports(source, generated_name, class_path)
    source = black.format_str(source, mode=black.FileMode())
    with open(class_path, "w", encoding="utf-8") as generated_file:
        generated_file.write(source)
    return class_path
