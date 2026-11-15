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
    if not edits:
        return source
    lines = source.splitlines(keepends=True)
    for line, column, text in sorted(edits, reverse=True):
        lines[line - 1] = lines[line - 1][:column] + text + lines[line - 1][column:]
    return _add_type_checking_imports("".join(lines), package, imports, gen_dict)


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
