"""Rename experimental function modules without changing function names."""

import ast
import re
from functools import lru_cache
from importlib.util import resolve_name
from pathlib import Path
from types import MappingProxyType

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
    """Map old package-qualified module paths to their generated paths.

    The legacy Functions tree is not modified by the generators: the mapping is
    computed once per folder (read-only view, ``_function_module_mapping``
    ``.cache_clear()`` to rescan).
    """
    root = Path(source_dir) if source_dir is not None else Path(MAIN_DIR) / "Functions"
    return _function_module_mapping(str(root.resolve()))


@lru_cache
def _function_module_mapping(root):
    root = Path(root)
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
    return MappingProxyType(mapping)


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


RULE_FUNCTIONS_FOLDER = "Converter.MotorCAD"
"""Folder (below Functions) of the functions of the complex conversion rules
(``RuleComplex.fct_name``: other_to_P / P_to_other of a module)"""

RULE_FUNCTIONS_MODULE = "Converter.rule_functions"
"""Generated registry of these functions (below Functions_new), Step 8"""


def redirect_rule_module_name(source, soft_name="pyleecan"):
    """Resolve the complex rule modules with the static registry (Step 8).

    ``__import__(f"pyleecan.Functions[_new].Converter.MotorCAD.{self.fct_name}",
    fromlist=...)`` (``RuleComplex._set_fct_name``) becomes
    ``rule_function_module(self.fct_name)``, imported from the generated
    registry (``Functions_new/Converter/rule_functions.py``) just before the
    statement (local import: the registry imports the rule modules, which import
    classes). The rule names stay the legacy ones (``curve_B(H)``, ``slotW11_H1``).
    """
    if "__import__" not in source or "Converter.MotorCAD." not in source:
        return source
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    prefixes = {
        f"{soft_name}.Functions.{RULE_FUNCTIONS_FOLDER}.",
        f"{soft_name}.Functions_new.{RULE_FUNCTIONS_FOLDER}.",
    }
    replacements = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "__import__"
            and node.args
            and isinstance(node.args[0], ast.JoinedStr)
            and len(node.args[0].values) == 2
            and isinstance(node.args[0].values[0], ast.Constant)
            and node.args[0].values[0].value in prefixes
            and isinstance(node.args[0].values[1], ast.FormattedValue)
        ):
            continue
        name = ast.unparse(node.args[0].values[1].value)
        statement = node
        while not isinstance(statement, ast.stmt):
            statement = parents[id(statement)]
        indent = " " * statement.col_offset
        line_start = offsets[statement.lineno - 1]
        module = f"{soft_name}.Functions_new.{RULE_FUNCTIONS_MODULE}"
        replacements.append((
            offsets[node.lineno - 1] + node.col_offset,
            offsets[node.end_lineno - 1] + node.end_col_offset,
            f"rule_function_module({name})",
        ))
        replacements.append((
            line_start,
            line_start,
            (
                f"{indent}# Local import (circular: the registry imports the rule modules)\n"
                f"{indent}from {module} import rule_function_module\n\n"
            ),
        ))
    for start, end, text in sorted(replacements, reverse=True):
        source = source[:start] + text + source[end:]
    return source


def rule_functions_source(source_dir, deprecated=()):
    """Source of the registry of the complex rule functions (Functions_new).

    Parameters
    ----------
    source_dir : Path
        Legacy Functions folder
    deprecated : iterable
        Legacy module names (below Functions) of the deprecated rule modules:
        loaded on request only (they warn), not imported by the registry

    Returns
    -------
    source : str
        Source of Functions_new/Converter/rule_functions.py
    """
    folder = Path(source_dir).joinpath(*RULE_FUNCTIONS_FOLDER.split("."))
    names = sorted(path.stem for path in folder.glob("*.py") if path.stem != "__init__")
    deprecated = {
        name.rpartition(".")[2]
        for name in deprecated
        if name.rpartition(".")[0] == RULE_FUNCTIONS_FOLDER
    }
    used = [name for name in names if name not in deprecated]
    package = RULE_FUNCTIONS_FOLDER.rpartition(".")[2]
    imports = "".join(f"    {function_module_name(name)},\n" for name in used)
    entries = "".join(f"    {name!r}: {function_module_name(name)},\n" for name in used)
    old = "".join(
        f"    {name!r}: {function_module_name(name)!r},\n"
        for name in names
        if name in deprecated
    )
    return (
        '"""Registry of the functions of the complex conversion rules (generated).\n\n'
        "``RuleComplex.fct_name`` names a module of this registry, whose\n"
        "``other_to_P`` / ``P_to_other`` functions convert the parameters (the\n"
        "first argument is the rule). Generated by the functions generator\n"
        "(``function_module_names.rule_functions_source``): do not edit by hand.\n"
        '"""\n\n'
        "from importlib import import_module\n\n"
        f"from .{package} import (\n{imports})\n\n"
        f"RULE_FUNCTIONS = {{\n{entries}}}\n"
        '"""{rule name (RuleComplex.fct_name): module of its functions}"""\n\n'
        f"DEPRECATED_RULE_FUNCTIONS = {{\n{old}}}\n"
        '"""{rule name: module name} of the deprecated rule modules (loaded on\n'
        'request, they warn)"""\n\n\n'
        "def rule_function_module(fct_name):\n"
        '    """Module of the functions of a complex rule\n\n'
        "    Parameters\n"
        "    ----------\n"
        "    fct_name : str\n"
        "        Name of the rule functions (RuleComplex.fct_name)\n\n"
        "    Returns\n"
        "    -------\n"
        "    module : module\n"
        "        Module with the other_to_P and P_to_other functions\n"
        '    """\n'
        "    if fct_name in RULE_FUNCTIONS:\n"
        "        return RULE_FUNCTIONS[fct_name]\n"
        "    if fct_name in DEPRECATED_RULE_FUNCTIONS:\n"
        f'        return import_module(f".{package}.{{DEPRECATED_RULE_FUNCTIONS[fct_name]}}", __package__)\n'
        '    raise KeyError(f"Unknown complex rule functions: {fct_name!r}")\n'
    )
