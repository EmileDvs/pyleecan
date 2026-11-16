"""Type hints drafted from the numpydoc docstrings (PLAN.md Step 5).

A modernization pass of the method generator: the parameters and the return
of a function get the annotation of their documented type, when this type is
recognized (TYPE_NAMES, Pyleecan classes); the other documented types are
reported for review (``unrecognized``). The classes named in the hints are
imported under ``if TYPE_CHECKING:`` (no runtime import, so no import cycle;
Python 3.14 evaluates the annotations lazily).

The pass is idempotent: annotated parameters and returns are kept.
"""

import ast
import re
from importlib.util import resolve_name

from pyleecan.classes_common.class_lookup import (
    NORMALIZATION_CLASS_NAMES,
    class_module_name,
)

BUILTIN_TYPES = {
    "bool": "bool",
    "int": "int",
    "float": "float",
    "complex": "complex",
    "str": "str",
    "string": "str",
    "dict": "dict",
    "list": "list",
    "tuple": "tuple",
}
"""Documented builtin types (lowercase) -> annotation"""

IMPORTED_TYPES = {
    "ndarray": ("np.ndarray", ("numpy", "np")),
    "array": ("np.ndarray", ("numpy", "np")),
    "numpy.ndarray": ("np.ndarray", ("numpy", "np")),
    "np.ndarray": ("np.ndarray", ("numpy", "np")),
    "numpy array": ("np.ndarray", ("numpy", "np")),
    "matplotlib.figure.figure": ("Figure", ("matplotlib.figure", "Figure")),
    "matplotlib.axes.axes": ("Axes", ("matplotlib.axes", "Axes")),
    "femmhandler": (
        "_FEMMHandler",
        ("pyleecan.classes_common.femm_handler", "_FEMMHandler"),
    ),
    "matplotlib.patches.polygon": ("Polygon", ("matplotlib.patches", "Polygon")),
    "matplotlib.patches.circle": ("Circle", ("matplotlib.patches", "Circle")),
}
"""Documented types needing an import -> (annotation, (module, name)); a
("numpy", "np") import is ``import numpy as np``"""

NONE_SUFFIXES = (" or none", ", optional", " (optional)", " or None")

_SCHEMATICS_RETURNS = (
    ("matplotlib.figure.Figure", "matplotlib.axes.Axes"),
    ("Lamination",),
)
RETURN_OVERRIDES = {
    # is_return_default=True returns the default lamination of the schematics
    ("slot", name): _SCHEMATICS_RETURNS
    for name in (
        "plot_schematics",
        "plot_schematics_constant_tooth",
        "plot_schematics_radial",
        "plot_schematics_top_flat",
    )
}
"""(sub-package, function) -> returns whose docstring is incomplete: the
alternatives of the union, each a tuple of documented types (a tuple hint
when there are several)"""


def add_type_hints(source, package, gen_dict, class_name=None, unrecognized=None):
    """Annotate the functions of a module from their numpydoc docstrings.

    Parameters
    ----------
    source : str
        Source of the module
    package : str
        Package of the module (to write the relative class imports)
    gen_dict : dict
        Generation dictionary (contains all the csv data)
    class_name : str, optional
        Class of the methods (its name documents the self parameter only)
    unrecognized : collections.Counter, optional
        Updated with the documented types that are not recognized

    Returns
    -------
    source : str
        Annotated source
    """
    tree = ast.parse(source)
    subpackage = package.split(".")[2] if package.count(".") >= 2 else None
    class_names = {NORMALIZATION_CLASS_NAMES.get(name, name): name for name in gen_dict}
    edits = []  # (start, end, text) in characters of a line, by line
    imports = {}  # name -> (module, name)
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        docstring = ast.get_docstring(node) or ""
        documented = _section_types(docstring, "Parameters")
        arguments = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
        defaults = dict(
            zip(
                [arg.arg for arg in node.args.posonlyargs + node.args.args][
                    len(node.args.posonlyargs + node.args.args)
                    - len(node.args.defaults) :
                ],
                node.args.defaults,
            )
        )
        defaults.update(
            {
                arg.arg: default
                for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults)
                if default is not None
            }
        )
        for arg in arguments:
            if arg.annotation is not None or arg.arg in ("self", "cls"):
                continue
            if arg.arg not in documented:
                continue
            default = defaults.get(arg.arg)
            is_none = isinstance(default, ast.Constant) and default.value is None
            hint = _annotation(documented[arg.arg], class_names, imports, unrecognized)
            if hint is None:
                continue
            if not _default_matches(hint, default):
                if unrecognized is not None:  # The docstring contradicts the code
                    unrecognized[
                        f"{documented[arg.arg]} (default {ast.unparse(default)})"
                    ] += 1
                continue
            if is_none and not hint.endswith("| None"):
                hint += " | None"
            line_text = source.splitlines()[arg.end_lineno - 1]
            if line_text[arg.end_col_offset : arg.end_col_offset + 1] == "=":
                # PEP 8: spaces around the "=" of an annotated parameter
                edits.append((arg.end_lineno, arg.end_col_offset + 1, " "))
                edits.append((arg.end_lineno, arg.end_col_offset, f": {hint} "))
            else:
                edits.append((arg.end_lineno, arg.end_col_offset, ": " + hint))
        if node.returns is None:
            override = RETURN_OVERRIDES.get((subpackage, node.name))
            if override is None:
                returned = [tuple(_section_types(docstring, "Returns").values())]
            else:
                returned = list(override)
            alternatives = [
                _return_hint(texts, class_names, imports, unrecognized)
                for texts in returned
            ]
            if all(hint is not None for hint in alternatives):
                line, column = _signature_end(source, node)
                edits.append((line, column, " -> " + " | ".join(alternatives)))
        edits.extend(_container_local_edits(node, class_names, gen_dict, imports))
    if not edits:
        return source
    lines = source.splitlines(keepends=True)
    for line, column, text in sorted(edits, reverse=True):
        lines[line - 1] = lines[line - 1][:column] + text + lines[line - 1][column:]
    return _add_type_checking_imports("".join(lines), package, imports, gen_dict)


CONTAINER_BUILDERS = {"list": ast.List, "dict": ast.Dict}
"""Constructor names of the containers -> their display node"""

KWARGS_TYPE = "**"
"""Marker of a local dict unpacked as keyword arguments (dict[str, Any])"""


def _container_local_edits(function, class_names, gen_dict, imports):
    """Annotations of the local containers passed to a container field.

    ``list`` is invariant: ``curve_list = list()`` filled with segments is
    inferred as ``list[Segment]``, which is rejected by a ``list[Line]`` field
    (``SurfLine(line_list=curve_list)``). The first assignment of such a local
    is annotated with the field type (``curve_list: list[Line] = list()``),
    when it builds the container (empty or literal). A local passed to fields
    of different types is left unchanged. A local dict unpacked as keyword
    arguments (``line.plot(**kwargs)``) is annotated ``dict[str, Any]``.

    Parameters
    ----------
    function : ast.FunctionDef
        Function whose locals are annotated
    class_names : dict
        {class name: name in gen_dict}
    gen_dict : dict
        Generation dictionary (contains all the csv data)
    imports : dict
        Updated with the names of the hints to import (name -> (module, name))

    Returns
    -------
    edits : list
        (line, column, text) insertions
    """
    nodes = list(_walk_scope(function))
    hints = {}  # local name -> set of field types
    unpacked = set()  # local names unpacked as keyword arguments (**name)
    for node in nodes:
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg is None and isinstance(keyword.value, ast.Name):
                unpacked.add(keyword.value.id)
        if not isinstance(node.func, ast.Name) or node.func.id not in class_names:
            continue
        for keyword in node.keywords:
            if keyword.arg is None or not isinstance(keyword.value, ast.Name):
                continue
            field_type = _field_type(class_names[node.func.id], keyword.arg, gen_dict)
            if field_type and field_type[0] in "[{" and field_type not in ("[]", "{}"):
                hints.setdefault(keyword.value.id, set()).add(field_type)
    # Keyword arguments gathered in a dict: its value type is the union of the
    # values (e.g. str | int), rejected by every typed parameter
    for name in unpacked:
        hints.setdefault(name, set()).add(KWARGS_TYPE)
    if not hints:
        return []
    annotated = {
        node.target.id
        for node in nodes
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    positions = _statement_positions(function)
    assigns = {}  # name -> assignments, in source order
    for node in sorted(
        (n for n in nodes if isinstance(n, ast.Assign) and id(n) in positions),
        key=lambda n: (n.lineno, n.col_offset),
    ):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            assigns.setdefault(node.targets[0].id, []).append(node)
    edits = []
    for name, field_types in sorted(hints.items()):
        if len(field_types) != 1 or name in annotated or name not in assigns:
            continue
        field_type = next(iter(field_types))
        is_dict = field_type[0] == "{" or field_type == KWARGS_TYPE
        builder = CONTAINER_BUILDERS["dict" if is_dict else "list"]
        if not _builds_container(assigns[name][0].value, builder):
            continue  # Declared by another value (e.g. a method call)
        if field_type == KWARGS_TYPE:
            hint = "dict[str, Any]"
            imports["Any"] = ("typing", "Any")
        else:
            hint = _annotation(field_type, class_names, imports, None)
        if hint is None:
            continue
        # A declaration reaches the statements after it in its block (and in
        # the nested blocks): the assignments in another branch are annotated
        declared = []
        for node in assigns[name]:
            if not _builds_container(node.value, builder):
                continue
            if any(_dominates(positions[d], positions[id(node)]) for d in declared):
                continue
            declared.append(id(node))
            target = node.targets[0]
            edits.append((target.end_lineno, target.end_col_offset, ": " + hint))
    return edits


def _statement_positions(function):
    """{id(statement): ((id(block), index), ...)} from the function body down.

    Nested functions and classes are not entered.
    """
    positions = {}
    scopes = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

    def visit(block, path):
        for index, statement in enumerate(block):
            if isinstance(statement, scopes):
                continue
            here = path + ((id(block), index),)
            positions[id(statement)] = here
            for field in ("body", "orelse", "finalbody"):
                visit(getattr(statement, field, []), here)
            for handler in getattr(statement, "handlers", []):
                visit(handler.body, here)
            for case in getattr(statement, "cases", []):
                visit(case.body, here)

    visit(function.body, ())
    return positions


def _dominates(first, second):
    """True if the statement at position first always runs before second:
    first comes before an enclosing statement of second in the same block."""
    if len(first) > len(second):
        return False
    if first[:-1] != second[: len(first) - 1]:
        return False
    block, index = first[-1]
    other_block, other_index = second[len(first) - 1]
    return block == other_block and index < other_index


def _walk_scope(function):
    """Nodes of a function body, without the nested functions and classes."""
    scopes = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
    stack = list(function.body)
    while stack:
        node = stack.pop()
        if isinstance(node, scopes):
            continue
        yield node
        stack.extend(ast.iter_child_nodes(node))


def _builds_container(value, builder):
    """True for a container display, an empty constructor call (list()) or a
    dict built from keyword arguments (dict(a=1))."""
    if isinstance(value, builder):
        return True
    return (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and CONTAINER_BUILDERS.get(value.func.id) is builder
        and not value.args
        and (builder is ast.Dict or not value.keywords)
    )


def _field_type(class_name, field, gen_dict):
    """Documented type of a field (inherited fields included), or None."""
    while class_name in gen_dict:
        for prop in gen_dict[class_name]["properties"]:
            if prop["name"] == field:
                return prop["type"]
        class_name = gen_dict[class_name].get("mother")
    return None


LITERAL_TYPES = {
    "bool": (bool,),
    "int": (int,),
    "float": (int, float),
    "complex": (int, float, complex),
    "str": (str,),
}
"""Types of the literal defaults compatible with a builtin hint"""


def _default_matches(hint, default):
    """False if a literal default contradicts the hint (e.g. 0 for a bool)."""
    if not isinstance(default, ast.Constant) or default.value is None:
        return True
    accepted = LITERAL_TYPES.get(hint.removesuffix(" | None"))
    if accepted is None:
        return True
    value = default.value
    if isinstance(value, bool) and bool not in accepted:
        return False
    return isinstance(value, accepted)


def _section_types(docstring, section):
    """{name: documented type} of a numpydoc section ("Parameters", "Returns")."""
    match = re.search(
        rf"^\s*{section}\s*\n\s*-+\s*\n(.*?)(?=^\s*[A-Z][A-Za-z ]+\s*\n\s*-+\s*$|\Z)",
        docstring,
        re.DOTALL | re.MULTILINE,
    )
    if match is None:
        return {}
    types = {}
    for line in match.group(1).splitlines():
        found = re.match(r"^(\w+)\s*:\s*(\S.*)$", line.strip())
        # A documented entry is not indented more than the section
        if found and not line.startswith(" " * 8):
            types[found.group(1)] = found.group(2).strip()
    return types


def _annotation(text, class_names, imports, unrecognized):
    """Annotation of a documented type, or None (unrecognized)."""
    text = text.strip().rstrip(".")
    lowered = text.lower()
    optional = False
    for suffix in NONE_SUFFIXES:
        if lowered.endswith(suffix.lower()):
            text = text[: -len(suffix)].strip()
            lowered = text.lower()
            optional = True
    lowered = re.sub(r"\s+object$", "", lowered)
    text = re.sub(r"\s+object$", "", text)
    hint = None
    # Containers: pyleecan notation "[X]" / "{X}" (as in the CSV files) or
    # "list of X"; the item type must be recognized
    container = (
        re.fullmatch(r"\[(.+)\]", text)
        or re.fullmatch(r"\{(.+)\}", text)
        or re.fullmatch(r"list of (.+)", text, re.IGNORECASE)
    )
    if container is not None:
        item = _annotation(container.group(1), class_names, imports, None)
        if item is not None and not item.endswith("| None"):
            hint = f"dict[str, {item}]" if text.startswith("{") else f"list[{item}]"
    elif lowered in BUILTIN_TYPES:
        hint = BUILTIN_TYPES[lowered]
    elif lowered in IMPORTED_TYPES:
        hint, (module, name) = IMPORTED_TYPES[lowered]
        imports[hint.split(".")[0]] = (module, name)
    elif text in class_names or text in NORMALIZATION_CLASS_NAMES:
        hint = NORMALIZATION_CLASS_NAMES.get(text, text)
        imports[hint] = ("class", class_names.get(hint, text))
    if hint is None:
        if unrecognized is not None:
            unrecognized[text] += 1
        return None
    return hint + " | None" if optional else hint


def _return_hint(texts, class_names, imports, unrecognized):
    """Hint of documented returns (a tuple when several), or None."""
    hints = [_annotation(text, class_names, imports, unrecognized) for text in texts]
    if not hints or any(hint is None for hint in hints):
        return None
    return hints[0] if len(hints) == 1 else f"tuple[{', '.join(hints)}]"


def _signature_end(source, node):
    """(line, column) just before the colon ending the def statement."""
    body_start = node.body[0]
    lines = source.splitlines(keepends=True)
    # Search backwards from the first statement for the ":" closing the def
    line = body_start.lineno - 1
    while line >= node.lineno - 1:
        text = lines[line]
        end = len(text) if line != body_start.lineno - 1 else body_start.col_offset
        segment = text[:end].rstrip()
        if segment.endswith(":") and line < body_start.lineno - 1:
            return line + 1, len(segment) - 1
        line -= 1
    raise ValueError(f"Cannot find the end of the signature of {node.name}")


def _add_type_checking_imports(source, package, imports, gen_dict):
    """Add the imports of the hint names under ``if TYPE_CHECKING:``."""
    from pyleecan.Generator.ClassGenerator.New.class_generator import class_subpackage

    tree = ast.parse(source)
    bound = {
        alias.asname or alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    statements = []
    for hint_name, (module, name) in sorted(imports.items()):
        if hint_name in bound:
            continue  # Already imported (at runtime or for type checking)
        if module == "class":
            target = (
                f"pyleecan.Classes_new.{class_subpackage(name, gen_dict)}."
                f"{class_module_name(name)}"
            )
            statements.append(_relative_import(target, hint_name, package))
        elif module == "numpy":
            statements.append("import numpy as np")
        elif module.startswith("pyleecan."):
            statements.append(_relative_import(module, name, package))
        else:
            statements.append(f"from {module} import {name}")
    if not statements:
        return source
    lines = source.splitlines(keepends=True)
    block = [n for n in tree.body if _is_type_checking_block(n)]
    if block:  # Existing block: add the imports to it
        end = block[0].end_lineno
        lines.insert(end, "".join(f"    {statement}\n" for statement in statements))
        return "".join(lines)
    header = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    position = header[-1].end_lineno if header else _after_docstring(tree)
    typing_import = (
        "" if "TYPE_CHECKING" in bound else "from typing import TYPE_CHECKING\n"
    )
    text = (
        typing_import
        + "\nif TYPE_CHECKING:\n"
        + "".join(f"    {statement}\n" for statement in statements)
    )
    lines.insert(position, text)
    return "".join(lines)


def _relative_import(module, name, package):
    """``from <relative module> import name`` written from package."""
    package_parts = package.split(".")
    target_parts = module.split(".")
    common = 0
    while (
        common < len(package_parts)
        and common < len(target_parts)
        and package_parts[common] == target_parts[common]
    ):
        common += 1
    level = len(package_parts) - common + 1
    relative = "." * level + ".".join(target_parts[common:])
    assert resolve_name(relative, package) == module
    return f"from {relative} import {name}"


def _after_docstring(tree):
    """Line after the module docstring (0 if none)."""
    first = tree.body[0] if tree.body else None
    if (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        return first.end_lineno
    return 0


def _is_type_checking_block(node):
    return (
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "TYPE_CHECKING"
    )
