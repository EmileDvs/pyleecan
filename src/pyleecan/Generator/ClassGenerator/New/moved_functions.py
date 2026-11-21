"""Legacy functions moved to a class as methods (PLAN.md Step 5).

A legacy function that depends on the meaning or the data of one class
becomes a method of that class:

- the method generator writes the function module in the method folder of
  the class (``Methods_new/<sub-package>/<Class>/<method>.py``): the first
  parameter becomes ``self`` (regular method), or the function gets
  ``@staticmethod`` (function not using the object);
- the class generator adds the method to the class (the CSV files are not
  changed: ``add_moved_methods`` extends the generation dictionary);
- the callers in Methods_new and Functions_new call the method
  (``obj.method(...)``; a static method on ``self`` in its class, else on the
  class, imported in the calling function);
- the function generator keeps the old function path in Functions_new as a
  deprecated alias, until Phase 2.

A legacy module can hold several moved functions (a tuple of MovedFunction):
each one gets its own method module, and calls between them go through the
class.
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
    bound: tuple = ()
    """(parameter, getter): the first parameter of the legacy function is data
    of the object. The legacy body becomes the static method "_<method>", and
    "<method>" a regular method taking that parameter as an optional keyword
    argument, given by ``self.<getter>()`` by default. A caller holding
    ``x = obj.<getter>(...)`` calls ``obj.<method>(..., parameter=x)``; the
    other callers call the static method"""

    @property
    def implementation(self):
        """Name of the method holding the legacy body"""
        return "_" + self.method if self.bound else self.method

    @property
    def methods(self):
        """Names of the methods added to the class"""
        return (self.implementation, self.method) if self.bound else (self.method,)


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
    # Step 8, group 2: winding matrix operations (Winding), single conductor
    # winding function (Conductor); gen_phase_list stays a utility
    "Winding.comp_cond_function": MovedFunction(
        "Conductor", "comp_cond_function", static=True
    ),
    "Winding.reverse_wind_mat": (
        MovedFunction("Winding", "reverse_wind_mat", static=True),
        MovedFunction("Winding", "reverse_layer", static=True),
        MovedFunction("Winding", "change_layer", static=True),
        MovedFunction("Winding", "permute_B_C", static=True),
    ),
    "Winding.shift_wind_mat": MovedFunction("Winding", "shift_wind_mat", static=True),
    # get_phase_id reads the connection matrix of the winding (regular method,
    # wind_mat optional); find_wind_phase_color stays static: the plots call
    # it without matrix on purpose (no winding, WindingSC: first phase color)
    "Winding.find_wind_phase_color": (
        MovedFunction("Winding", "find_wind_phase_color", static=True),
        MovedFunction(
            "Winding", "get_phase_id", bound=("wind_mat", "get_connection_mat")
        ),
    ),
}
"""{legacy function module below Functions: MovedFunction or tuple of them}"""

DEPRECATION_MESSAGE = "{function} is deprecated, use {target} (removed in Phase 2)"


def moved_targets(value):
    """The MovedFunction of a MOVED_FUNCTIONS value, as a tuple."""
    return (value,) if isinstance(value, MovedFunction) else tuple(value)


def all_moved_targets(moved=None):
    """[(legacy module, MovedFunction)] of all the moved functions."""
    moved = MOVED_FUNCTIONS if moved is None else moved
    return [
        (module, target) for module, value in moved.items() for target in moved_targets(value)
    ]


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
    for _, target in all_moved_targets(moved):
        methods = gen_dict[target.class_name]["methods"]
        for name in target.methods:
            if name not in methods:
                methods.append(name)
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


def _split_moved_siblings(source, module_name, siblings):
    """Remove the other moved functions of the module, imported instead.

    The import from the legacy module (``from .module import sibling``) is
    then rewritten by ``redirect_moved_calls`` into calls on the class.
    """
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    removed = []
    for node in reversed(tree.body):
        if isinstance(node, ast.FunctionDef) and node.name in siblings:
            first = node.lineno - 1 - len(node.decorator_list)
            del lines[first : node.end_lineno]
            removed.append(node.name)
    if not removed:
        return source
    source = "".join(lines)
    used = {
        node.id for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Name)
    }
    imported = sorted(name for name in removed if name in used)
    if not imported:
        return source
    # After the module docstring and the __future__ imports
    tree = ast.parse(source)
    position = 0
    for node in tree.body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ) or (isinstance(node, ast.ImportFrom) and node.module == "__future__"):
            position = node.end_lineno
        else:
            break
    lines = source.splitlines(keepends=True)
    lines.insert(position, f"from .{module_name} import {', '.join(imported)}\n")
    return "".join(lines)


def method_source(source, target, old_package, new_package, siblings=()):
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
    siblings : tuple, optional
        (legacy module name, names of the other moved functions of the module):
        removed from the method module, imported from the legacy module (calls
        redirected to the class by redirect_moved_calls)

    Returns
    -------
    source : str
        Source of the method module
    """
    if siblings:
        module_name, names = siblings
        source = _split_moved_siblings(source, module_name, set(names))
    source = _relocate_relative_imports(source, old_package, new_package)
    node = _function_node(ast.parse(source), target.method)
    offsets = _line_offsets(source)
    if target.static or target.bound:
        start = offsets[node.lineno - 1]
        if target.bound:  # Legacy body in the static "_<method>"
            name_start = start + source[start:].index("def " + target.method) + 4
            source = (
                source[:name_start]
                + target.implementation
                + source[name_start + len(target.method) :]
            )
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


def bound_method_source(source, target):
    """Source of the regular method of a bound moved function.

    ``get_phase_id(wind_mat, Nrad, Ntan, Zs)`` with bound=("wind_mat",
    "get_connection_mat") becomes::

        def get_phase_id(self, Nrad, Ntan, Zs, wind_mat=None):
            if wind_mat is None:
                wind_mat = self.get_connection_mat()
            return self._get_phase_id(wind_mat, Nrad, Ntan, Zs)

    The docstring of the legacy function is kept (with ``self`` and the
    default of the bound parameter documented).
    """
    parameter, getter = target.bound
    node = _function_node(ast.parse(source), target.method)
    arguments = node.args
    if arguments.posonlyargs or arguments.vararg or arguments.kwarg or arguments.kwonlyargs:
        raise ValueError(f"{target.method}: only positional parameters are supported")
    names = [argument.arg for argument in arguments.args]
    if not names or names[0] != parameter:
        raise ValueError(f"{target.method}: the first parameter must be {parameter}")
    defaults = dict(zip(names[len(names) - len(arguments.defaults) :], arguments.defaults))
    if parameter in defaults:
        raise ValueError(f"{target.method}: {parameter} must not have a default")
    signature = ["self"] + [
        name + ("=" + ast.unparse(defaults[name]) if name in defaults else "")
        for name in names[1:]
    ] + [parameter + "=None"]
    lines = [f"def {target.method}({', '.join(signature)}):"]
    docstring = ast.get_docstring(node, clean=True)
    if docstring is not None:
        doc_lines = docstring.split("\n")
        for index, line in enumerate(doc_lines):
            if line.strip() == "----------" and index and doc_lines[index - 1].strip() == "Parameters":
                doc_lines[index + 1 : index + 1] = [
                    f"self : {target.class_name}",
                    f"    A {target.class_name} object",
                ]
                break
        for index, line in enumerate(doc_lines):
            if line.split(":")[0].strip() == parameter and ":" in line:
                end = index + 1
                while end < len(doc_lines) and doc_lines[end].startswith("    "):
                    end += 1
                doc_lines.insert(end, f"    (default: self.{getter}())")
                break
        body = "\n".join(("    " + line).rstrip() for line in doc_lines)
        lines.append('    """' + body.lstrip() + "\n    " + '"""')
    lines += [
        f"    if {parameter} is None:",
        f"        {parameter} = self.{getter}()",
        f"    return self.{target.implementation}({', '.join(names)})",
    ]
    return "\n".join(lines) + "\n"


def alias_source(legacy_module, target):
    """Legacy source of the deprecated aliases kept at the old function path.

    The alias goes through the function generator like the other legacy
    function modules (class imports relocated, pydantic rewriting). ``target``
    is a MovedFunction or a tuple of them (one alias per moved function of the
    module).
    """
    targets = moved_targets(target)
    depth = len(legacy_module.split("."))  # Functions/<...>/<module>.py
    up = "." * (depth + 1)
    moved_names = ", ".join(f"{t.class_name}.{t.method}" for t in targets)
    lines = [
        f'"""Deprecated alias of {moved_names} (moved to the class, removed in Phase 2)."""',
        "",
        "from warnings import warn",
    ]
    for item in targets:
        message = DEPRECATION_MESSAGE.format(
            function=item.method, target=f"{item.class_name}.{item.method}"
        )
        lines += ["", ""]
        if item.static or item.bound:  # Legacy signature: the static method
            lines += [
                f"def {item.method}(*args, **kwargs):",
                f'    """Deprecated: use {item.class_name}.{item.method}"""',
                f"    from {up}Classes.{item.class_name} import {item.class_name}",
                "",
                f'    warn("{message}", DeprecationWarning, stacklevel=2)',
                f"    return {item.class_name}.{item.implementation}(*args, **kwargs)",
            ]
        else:
            lines += [
                f"def {item.method}(obj, *args, **kwargs):",
                f'    """Deprecated: use {item.class_name}.{item.method}"""',
                f'    warn("{message}", DeprecationWarning, stacklevel=2)',
                f"    return obj.{item.method}(*args, **kwargs)",
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


def _bound_receiver(call, caller, target, source, offsets):
    """Object of a bound call: ``x = obj.<getter>(...)`` before ``f(x, ...)``.

    Returns the source of ``obj`` when the first argument is a name whose
    nearest assignment before the call, in the calling function, is a call of
    the getter of the target; else None.
    """
    if caller is None or not call.args or not isinstance(call.args[0], ast.Name):
        return None
    name = call.args[0].id
    getter = target.bound[1]
    assignments = [
        node
        for node in ast.walk(caller)
        if isinstance(node, ast.Assign)
        and node.lineno < call.lineno
        and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
    ]
    if not assignments:
        return None
    value = max(assignments, key=lambda node: node.lineno).value
    if not (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and value.func.attr == getter
    ):
        return None
    obj = value.func.value
    start = offsets[obj.lineno - 1] + obj.col_offset
    end = offsets[obj.end_lineno - 1] + obj.end_col_offset
    return source[start:end]


def redirect_moved_calls(source, package, class_name=None, moved=None, gen_dict=None):
    """Call the moved methods instead of the legacy functions.

    ``from ....Functions.MeshSolution.get_area import get_area`` is removed and
    ``get_area(ms, ...)`` becomes ``ms.get_area(...)``. A static method is
    called on ``self`` in a regular method of its class or of a daughter
    class, else on the class (static method, other class, function), the class
    being imported in the calling function (as the other class imports of the
    methods).

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
    if not any(target.method in source for _, target in all_moved_targets(moved)):
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
        if not module or not module.startswith("pyleecan.Functions."):
            continue
        value = moved.get(module[len("pyleecan.Functions.") :])
        if value is None:
            continue
        targets = {target.method: target for target in moved_targets(value)}
        kept = [alias for alias in node.names if alias.name not in targets]
        if len(kept) == len(node.names):
            continue
        for alias in node.names:
            if alias.name in targets:
                names[alias.asname or alias.name] = targets[alias.name]
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
        caller = next(
            (f for f in functions if f.lineno <= node.lineno <= f.end_lineno), None
        )
        if target.bound:
            receiver = _bound_receiver(node, caller, target, source, offsets)
            if receiver is not None:  # obj.method(..., parameter=x)
                first = node.args[0]
                first_start = offsets[first.lineno - 1] + first.col_offset
                first_end = offsets[first.end_lineno - 1] + first.end_col_offset
                value = source[first_start:first_end]
                rest = node.args[1:] + node.keywords
                if rest:
                    following = min(rest, key=lambda item: (item.lineno, item.col_offset))
                    replacements.append(
                        (first_start, offsets[following.lineno - 1] + following.col_offset, "")
                    )
                    closing = offsets[node.end_lineno - 1] + node.end_col_offset - 1
                    replacements.append((closing, closing, f", {target.bound[0]}={value}"))
                else:
                    replacements.append(
                        (first_start, first_end, f"{target.bound[0]}={value}")
                    )
                replacements.append((func_start, func_end, f"{receiver}.{target.method}"))
                continue
        if target.static or target.bound:
            if caller is None:
                raise ValueError(
                    f"{package}: call of {target.method} outside of a function"
                )
            if target.class_name in lineage and not _is_static_function(caller):
                owner = "self"  # Method of the class or of a daughter class
            else:  # Static method, other class or function: on the class
                class_imports.setdefault(caller.name, (caller, set()))[1].add(
                    target.class_name
                )
                owner = target.class_name
            replacements.append(
                (func_start, func_end, f"{owner}.{target.implementation}")
            )
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
