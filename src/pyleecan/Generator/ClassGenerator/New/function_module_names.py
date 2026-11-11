"""Rename experimental function modules without changing function names."""

import ast
import re
from importlib.util import resolve_name
from pathlib import Path

from pyleecan.definitions import MAIN_DIR


def function_module_name(name):
    """Convert a legacy function module name to a lowercase Python identifier."""
    if name == "curve_B(H)":
        return "curve_bh"
    original = name
    name = re.sub(r"[^a-z0-9_]+", "_", name.lower())
    if not original.endswith("_"):
        name = name.rstrip("_")
    if not name.isidentifier():
        name = name.strip("_")
    if not name or not name.isidentifier():
        raise ValueError(f"Invalid function module name: {name!r}")
    return name


def function_module_mapping(source_dir=None):
    """Map old package-qualified module paths to their generated paths."""
    root = Path(source_dir) if source_dir is not None else Path(MAIN_DIR) / "Functions"
    mapping = {}
    destinations = {}
    for path in root.rglob("*.py"):
        relative = path.relative_to(root)
        name = function_module_name(path.stem)
        old = ".".join(relative.with_suffix("").parts)
        new = ".".join((*relative.parts[:-1], name))
        key = new.lower()
        if key in destinations and destinations[key] != old:
            raise ValueError(f"Function module collision: {destinations[key]} and {old}")
        destinations[key] = old
        if old != new:
            mapping[old] = new
    return mapping


def redirect_function_module_imports(source, package, mapping, soft_name="pyleecan"):
    """Rewrite static imports of renamed Functions_new modules."""
    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == 10:
            offsets.append(index + 1)
    prefix = soft_name + ".Functions_new."
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(prefix):
                    renamed = mapping.get(alias.name[len(prefix):])
                    if renamed:
                        start = offsets[alias.lineno - 1] + alias.col_offset
                        replacements.append((
                            start, start + len(alias.name.encode("utf-8")),
                            (prefix + renamed).encode("utf-8"),
                        ))
            continue
        if isinstance(node, ast.Attribute):
            expression = ast.unparse(node)
            if expression.startswith(prefix):
                renamed = mapping.get(expression[len(prefix):])
                if renamed:
                    replacements.append((
                        offsets[node.lineno - 1] + node.col_offset,
                        offsets[node.end_lineno - 1] + node.end_col_offset,
                        (prefix + renamed).encode("utf-8"),
                    ))
            continue
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in ("import_module", "__import__")
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
            and node.args[0].value.startswith(prefix)
        ):
            argument = node.args[0]
            renamed = mapping.get(argument.value[len(prefix):])
            if renamed:
                replacements.append((
                    offsets[argument.lineno - 1] + argument.col_offset,
                    offsets[argument.end_lineno - 1] + argument.end_col_offset,
                    repr(prefix + renamed).encode("utf-8"),
                ))
            continue
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        absolute = resolve_name("." * node.level + module, package) if node.level else module
        if not absolute.startswith(prefix):
            continue
        suffix = absolute[len(prefix):]
        changed_module = mapping.get(suffix)
        aliases = []
        changed_alias = False
        for alias in node.names:
            renamed = mapping.get(suffix + "." + alias.name)
            if renamed and renamed.rsplit(".", 1)[0] == suffix:
                new_name = renamed.rsplit(".", 1)[1]
                aliases.append(ast.alias(name=new_name, asname=alias.asname or alias.name))
                changed_alias = True
            else:
                aliases.append(alias)
        if not changed_module and not changed_alias:
            continue
        if changed_module:
            module_parts = module.split(".") if module else []
            module_parts[-1] = changed_module.rsplit(".", 1)[1]
            module = ".".join(module_parts)
        replacement = ast.ImportFrom(module=module or None, names=aliases, level=node.level)
        replacements.append((
            offsets[node.lineno - 1] + node.col_offset,
            offsets[node.end_lineno - 1] + node.end_col_offset,
            ast.unparse(replacement).encode("utf-8"),
        ))
    for start, end, replacement in sorted(replacements, reverse=True):
        data = data[:start] + replacement + data[end:]
    return data.decode("utf-8")


def redirect_rule_module_name(source, soft_name="pyleecan"):
    """Keep legacy rule names while resolving their renamed MotorCAD modules."""
    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == 10:
            offsets.append(index + 1)
    replacements = []
    prefix = f"{soft_name}.Functions_new.Converter.MotorCAD."
    for node in ast.walk(ast.parse(source)):
        if not (
            isinstance(node, ast.JoinedStr)
            and len(node.values) == 2
            and isinstance(node.values[0], ast.Constant)
            and node.values[0].value == prefix
            and isinstance(node.values[1], ast.FormattedValue)
            and ast.unparse(node.values[1].value) == "self.fct_name"
        ):
            continue
        node.values[1].value = ast.parse(
            "('curve_bh' if self.fct_name == 'curve_B(H)' else "
            "self.fct_name.lower().replace('(', '_').replace(')', ''))",
            mode="eval",
        ).body
        replacements.append((
            offsets[node.lineno - 1] + node.col_offset,
            offsets[node.end_lineno - 1] + node.end_col_offset,
            ast.unparse(node).encode("utf-8"),
        ))
    for start, end, replacement in sorted(replacements, reverse=True):
        data = data[:start] + replacement + data[end:]
    return data.decode("utf-8")
