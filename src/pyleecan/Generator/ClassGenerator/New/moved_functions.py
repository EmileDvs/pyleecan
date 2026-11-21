"""Legacy functions moved to a class as methods (PLAN.md Step 5).

A legacy function that depends on the meaning or the data of one class
becomes a method of that class:

- the method generator writes the function module in the method folder of
  the class (``Methods_new/<sub-package>/<Class>/<method>.py``): the first
  parameter becomes ``self`` (regular method), or the function gets
  ``@staticmethod`` (function not using the object);
- the class generator adds the method to the class (the CSV files are not
  changed: ``add_moved_methods`` extends the generation dictionary);
- the callers in Methods_new call the method (``obj.method(...)``);
- the function generator keeps the old function path in Functions_new as a
  deprecated alias, until Phase 2.
"""

import ast
from importlib.util import resolve_name
from typing import NamedTuple


class MovedFunction(NamedTuple):
    """Legacy function moved to a class."""

    class_name: str
    """Class receiving the method"""
    method: str
    """Name of the method (and of the legacy function)"""
    static: bool = False
    """True: @staticmethod (the function does not use the object)"""


MOVED_FUNCTIONS = {
    "MeshSolution.get_area": MovedFunction("MeshSolution", "get_area"),
    "MeshSolution.get_indices_limited": MovedFunction(
        "MeshSolution", "get_indices_limited"
    ),
    "Simulation.VarSimu.run_multisim_step": MovedFunction(
        "VarSimu", "run_multisim_step", static=True
    ),
    # Step 8, group 4: datakeepers of the multi-simulations
    "Simulation.VarSimu.get_elec_datakeeper_dict": MovedFunction(
        "VarSimu", "get_elec_datakeeper_dict", static=True
    ),
    "Simulation.VarSimu.log_datakeeper_step_result": MovedFunction(
        "VarSimu", "log_datakeeper_step_result", static=True
    ),
    # Step 8, group 3: NSGA-II with DEAP (the functions work on the DEAP
    # individuals of OptiGenAlgNsga2Deap.create_toolbox; OptiBayesAlgSmoot
    # imported them without using them and has its own evaluate)
    "Optimization.evaluate": MovedFunction("OptiGenAlgNsga2Deap", "evaluate"),
    "Optimization.check_cstr": MovedFunction("OptiGenAlgNsga2Deap", "check_cstr"),
    "Optimization.tournamentDCD": MovedFunction(
        "OptiGenAlgNsga2Deap", "tournamentDCD", static=True
    ),
    "Optimization.update": MovedFunction("OptiGenAlgNsga2Deap", "update", static=True),
}
"""{legacy function module below Functions: MovedFunction}"""

DEPRECATION_MESSAGE = "{function} is deprecated, use {target} (removed in Phase 2)"


def add_moved_methods(gen_dict, moved=None):
    """Add the moved functions to the method lists of the generation dictionary.

    Parameters
    ----------
    gen_dict : dict
        Generation dictionary (changed in place)
    moved : dict, optional
        {legacy module: MovedFunction} (default: MOVED_FUNCTIONS)

    Returns
    -------
    gen_dict : dict
        The same dictionary
    """
    moved = MOVED_FUNCTIONS if moved is None else moved
    for target in moved.values():
        methods = gen_dict[target.class_name]["methods"]
        if target.method not in methods:
            methods.append(target.method)
    return gen_dict


def _line_offsets(source):
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _function_node(tree, name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ValueError(f"Function {name} not found")


def _relocate_relative_imports(source, old_package, new_package):
    """Rewrite the relative imports of a module moved to another package."""
    offsets = _line_offsets(source)
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom) or not node.level:
            continue
        absolute = resolve_name("." * node.level + (node.module or ""), old_package)
        package_parts = new_package.split(".")
        target_parts = absolute.split(".")
        common = 0
        while (
            common < min(len(package_parts), len(target_parts))
            and package_parts[common] == target_parts[common]
        ):
            common += 1
        replacement = ast.ImportFrom(
            module=".".join(target_parts[common:]) or None,
            names=node.names,
            level=len(package_parts) - common + 1,
        )
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, ast.unparse(replacement)))
    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source


def method_source(source, target, old_package, new_package):
    """Source of the method module of a moved function.

    Parameters
    ----------
    source : str
        Source of the legacy function module
    target : MovedFunction
        Where the function goes
    old_package : str
        Package of the legacy module ("pyleecan.Functions.MeshSolution")
    new_package : str
        Package of the method module ("pyleecan.Methods.MeshSolution")

    Returns
    -------
    source : str
        Source of the method module
    """
    source = _relocate_relative_imports(source, old_package, new_package)
    node = _function_node(ast.parse(source), target.method)
    offsets = _line_offsets(source)
    if target.static:
        start = offsets[node.lineno - 1]
        return source[:start] + "@staticmethod\n" + source[start:]
    if not node.args.args:
        raise ValueError(f"{target.method} has no parameter to become self")
    first = node.args.args[0].arg
    positions = [node.args.args[0]]
    positions.extend(
        name
        for name in ast.walk(node)
        if isinstance(name, ast.Name) and name.id == first
    )
    replacements = []
    for item in positions:
        start = offsets[item.lineno - 1] + item.col_offset
        replacements.append((start, start + len(first), "self"))
    docstring = node.body[0] if ast.get_docstring(node) is not None else None
    if docstring is not None:
        doc_start = offsets[docstring.lineno - 1] + docstring.col_offset
        doc_end = offsets[docstring.end_lineno - 1] + docstring.end_col_offset
        text = source[doc_start:doc_end]
        lines = text.split("\n")
        for index, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.split(":")[0].strip() == first and ":" in stripped:
                indent = line[: len(line) - len(stripped)]
                lines[index] = indent + "self" + stripped[len(first) :]
                break
        replacements.append((doc_start, doc_end, "\n".join(lines)))
    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source


def alias_source(legacy_module, target):
    """Legacy source of the deprecated alias kept at the old function path.

    The alias goes through the function generator like the other legacy
    function modules (class imports relocated, pydantic rewriting).
    """
    depth = len(legacy_module.split("."))  # Functions/<...>/<module>.py
    up = "." * (depth + 1)
    message = DEPRECATION_MESSAGE.format(
        function=target.method, target=f"{target.class_name}.{target.method}"
    )
    lines = [
        f'"""Deprecated alias of {target.class_name}.{target.method} '
        '(moved to the class, removed in Phase 2)."""',
        "",
        "from warnings import warn",
        "",
        "",
    ]
    if target.static:
        lines += [
            f"def {target.method}(*args, **kwargs):",
            f'    """Deprecated: use {target.class_name}.{target.method}"""',
            f"    from {up}Classes.{target.class_name} import {target.class_name}",
            "",
            f'    warn("{message}", DeprecationWarning, stacklevel=2)',
            f"    return {target.class_name}.{target.method}(*args, **kwargs)",
        ]
    else:
        lines += [
            f"def {target.method}(obj, *args, **kwargs):",
            f'    """Deprecated: use {target.class_name}.{target.method}"""',
            f'    warn("{message}", DeprecationWarning, stacklevel=2)',
            f"    return obj.{target.method}(*args, **kwargs)",
        ]
    return "\n".join(lines) + "\n"


def _class_lineage(class_name, gen_dict):
    """The class and its mother classes (from the generation dictionary)."""
    lineage = []
    while class_name and class_name not in lineage:
        lineage.append(class_name)
        class_name = (gen_dict or {}).get(class_name, {}).get("mother") or None
    return lineage


def _is_static_function(node):
    """True for a function without self: @staticmethod or no parameter."""
    if any(
        isinstance(decorator, ast.Name) and decorator.id == "staticmethod"
        for decorator in node.decorator_list
    ):
        return True
    args = node.args.posonlyargs + node.args.args
    return not args or args[0].arg != "self"


def redirect_moved_calls(source, package, class_name=None, moved=None, gen_dict=None):
    """Call the moved methods instead of the legacy functions.

    ``from ....Functions.MeshSolution.get_area import get_area`` is removed and
    ``get_area(ms, ...)`` becomes ``ms.get_area(...)``. A static method is
    called in a method of its class or of a daughter class: on ``self`` in a
    regular method, on the class in a static method (class imported in the
    function, as the other class imports of the methods).

    Parameters
    ----------
    source : str
        Source of a legacy method module
    package : str
        Package of the module (to resolve its relative imports)
    class_name : str, optional
        Class of the method module
    moved : dict, optional
        {legacy module: MovedFunction} (default: MOVED_FUNCTIONS)
    gen_dict : dict, optional
        Generation dictionary, for the mother classes of class_name

    Returns
    -------
    source : str
        Source calling the methods
    """
    moved = MOVED_FUNCTIONS if moved is None else moved
    if not any(target.method in source for target in moved.values()):
        return source
    tree = ast.parse(source)
    offsets = _line_offsets(source)
    replacements = []
    names = {}  # Local name: MovedFunction
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        module = (
            resolve_name("." * node.level + (node.module or ""), package)
            if node.level
            else node.module
        )
        if not module.startswith("pyleecan.Functions."):
            continue
        target = moved.get(module[len("pyleecan.Functions.") :])
        if target is None:
            continue
        kept = [alias for alias in node.names if alias.name != target.method]
        for alias in node.names:
            if alias.name == target.method:
                names[alias.asname or alias.name] = target
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        if kept:
            text = ast.unparse(
                ast.ImportFrom(module=node.module, names=kept, level=node.level)
            )
        else:  # Remove the line
            text = ""
            end = offsets[node.end_lineno]
            start = offsets[node.lineno - 1]
        replacements.append((start, end, text))
    if not names:
        return source
    lineage = _class_lineage(class_name, gen_dict)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    class_imports = {}  # Static function: classes to import in its body
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in names
        ):
            continue
        target = names[node.func.id]
        func_start = offsets[node.func.lineno - 1] + node.func.col_offset
        func_end = offsets[node.func.end_lineno - 1] + node.func.end_col_offset
        if target.static:
            if target.class_name not in lineage:
                raise ValueError(
                    f"{package}: call of the static method {target.method} "
                    "outside of its class (or a daughter class) is not supported"
                )
            caller = next(
                (f for f in functions if f.lineno <= node.lineno <= f.end_lineno),
                None,
            )
            if caller is None or _is_static_function(caller):
                if caller is None:
                    raise ValueError(
                        f"{package}: call of {target.method} outside of a function"
                    )
                class_imports.setdefault(caller.name, (caller, set()))[1].add(
                    target.class_name
                )
                owner = target.class_name
            else:
                owner = "self"
            replacements.append((func_start, func_end, f"{owner}.{target.method}"))
            continue
        if not node.args or isinstance(node.args[0], ast.Starred):
            raise ValueError(f"{package}: call of {target.method} without object")
        first = node.args[0]
        first_start = offsets[first.lineno - 1] + first.col_offset
        first_end = offsets[first.end_lineno - 1] + first.end_col_offset
        obj = source[first_start:first_end]
        if not isinstance(first, (ast.Name, ast.Attribute, ast.Subscript, ast.Call)):
            obj = f"({obj})"
        # Remove the object argument and its separator
        rest = node.args[1:] + node.keywords
        if rest:
            following = min(rest, key=lambda item: (item.lineno, item.col_offset))
            next_start = offsets[following.lineno - 1] + following.col_offset
            replacements.append((first_start, next_start, ""))
        else:
            replacements.append((first_start, first_end, ""))
        replacements.append((func_start, func_end, f"{obj}.{target.method}"))
    # Class import at the start of the body of the static functions
    up = "." * len(package.split("."))  # pyleecan.<...>: one dot per package
    for caller, classes in class_imports.values():
        body = caller.body
        first = body[1] if ast.get_docstring(caller) is not None and len(body) > 1 else body[0]
        indent = " " * first.col_offset
        start = offsets[first.lineno - 1]
        text = "".join(
            f"{indent}from {up}Classes.{name} import {name}\n" for name in sorted(classes)
        )
        replacements.append((start, start, text))
    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source
