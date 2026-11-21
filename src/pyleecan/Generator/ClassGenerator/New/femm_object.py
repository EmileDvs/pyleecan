"""The FEMM interface object femm_pyleecan (PLAN.md Step 8, group 10).

The legacy FEMM functions (``Functions/FEMM``) take the FEMM handler as
``femm``. They become the methods of one plain helper class, ``femm_pyleecan``,
holding the handler (``femm_pyleecan.handler``): one object per FEMM instance,
i.e. per parallel worker (``OutMagFEMM.handler_list``).

- a function taking ``femm`` becomes a method: ``femm.mi_...`` ->
  ``self.handler.mi_...``, ``femm`` given to another function -> ``self``; the
  other functions are static methods; the calls between them go through the
  object (or the class);
- the class is written by the functions generator in
  ``Functions_new/FEMM/femm_pyleecan.py`` (a ``femm`` sub-package would be the
  same folder as ``FEMM`` on Windows); the legacy modules are deprecated
  aliases (they accept a handler or a femm_pyleecan object);
- the callers (methods, functions) pass the femm_pyleecan object: calls
  ``f(femm, ...)`` -> ``femm.f(...)``, ``_FEMMHandler()`` -> ``femm_pyleecan()``,
  ``femm.mi_...`` -> ``femm.handler.mi_...`` in the functions with a ``femm``
  variable.
"""

import ast
import re
import textwrap
from importlib.util import resolve_name
from pathlib import Path
from typing import NamedTuple

from .moved_functions import _line_offsets, _remove_statements

FEMM_PACKAGE = "FEMM"
"""Folder of the legacy FEMM functions below Functions"""
FEMM_CLASS = "femm_pyleecan"
FEMM_MODULE = "femm_pyleecan"
"""Module of the class in the FEMM folder (Functions_new/FEMM/femm_pyleecan.py)"""
HANDLER = "femm"
"""Name of the FEMM handler parameter of the legacy functions"""
HANDLER_CLASS = "_FEMMHandler"
CIRCULAR_COMMENT = "# Local import: circular import with the class module"
FEMM_HELP = "FEMM interface object (handler and FEMM functions)"


class InterfaceObject(NamedTuple):
    """Object gathering the legacy functions of a Functions folder."""

    package: str
    """Folder of the legacy functions below Functions"""
    class_name: str
    """Name of the class (and of its module in the folder)"""
    module: str
    """Module of the class in the folder"""
    handler: str | None = None
    """Name of the handler parameter of the legacy functions (None: static
    methods only)"""
    handler_class: str | None = None
    """Class of the handler, built by the callers (replaced by the object)"""
    description: str = ""
    """Docstring of the class"""
    handler_module: str = "classes_common.femm_handler"
    """Module of the handler class below pyleecan"""


FEMM = InterfaceObject(
    "FEMM",
    "femm_pyleecan",
    "femm_pyleecan",
    "femm",
    "_FEMMHandler",
    "Interface of pyleecan with FEMM: the FEMM handler and the FEMM functions\n\n"
    "One object per FEMM instance (per parallel worker of MagFEMM, see\n"
    "OutMagFEMM.handler_list). The FEMM commands are sent with self.handler.",
)
GMSH = InterfaceObject(
    "GMSH",
    "gmsh_pyleecan",
    "gmsh_pyleecan",
    description="Interface of pyleecan with gmsh: the gmsh functions of pyleecan\n\n"
    "Static methods for now (the gmsh API is a module): the object gathers the\n"
    "functions, to be improved later (PLAN.md Step 8).",
)
PYVISTA = InterfaceObject(
    "Plot.Pyvista",
    "pv_plotter_pyleecan",
    "pv_plotter_pyleecan",
    description="Plots of pyleecan with PyVista: the PyVista functions of pyleecan\n\n"
    "Static methods for now (configure_plot creates the plotter): the object\n"
    "gathers the functions, to be improved later (PLAN.md Step 8).",
)
INTERFACE_OBJECTS = (FEMM, GMSH, PYVISTA)
"""The objects gathering the functions of a Functions folder"""


def _returns(node):
    """Return annotation of a function signature (" -> X" or "")."""
    return f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""


def _is_type_checking_block(node):
    return (
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "TYPE_CHECKING"
        and not node.orelse
    )


def _add_type_hints(source, package):
    """Type hints of the functions of a legacy module (type_hints.py)."""
    from .source_names import name_maps
    from .type_hints import add_type_hints

    return add_type_hints(source, package, name_maps().gen_dict)


def _up(spec):
    """Relative import prefix from a module of the folder to pyleecan."""
    return "." * (len(spec.package.split(".")) + 2)


def femm_modules(functions_dir, spec=FEMM):
    """{module name: source} of the legacy FEMM modules (the deprecated modules
    of moved_functions.DEPRECATED_MODULES excluded: they stay at their path)."""
    from .moved_functions import DEPRECATED_MODULES

    FEMM_PACKAGE, FEMM_CLASS, FEMM_MODULE, HANDLER, HANDLER_CLASS = spec[:5]
    folder = Path(functions_dir).joinpath(*FEMM_PACKAGE.split("."))
    return {
        path.stem: path.read_text(encoding="utf-8")
        for path in sorted(folder.glob("*.py"))
        if path.name != "__init__.py"
        and path.stem != FEMM_MODULE
        and f"{FEMM_PACKAGE}.{path.stem}" not in DEPRECATED_MODULES
    }


_SIGNATURES = {}


def legacy_signatures(spec=FEMM):
    """femm_signatures of the legacy modules of an interface object (cached)."""
    if spec.class_name not in _SIGNATURES:
        from pyleecan.definitions import MAIN_DIR

        modules = femm_modules(Path(MAIN_DIR) / "Functions", spec)
        _SIGNATURES[spec.class_name] = femm_signatures(modules, spec)
    return _SIGNATURES[spec.class_name]


def legacy_femm_signatures():
    """legacy_signatures of the FEMM interface object."""
    return legacy_signatures(FEMM)


def femm_signatures(modules, spec=FEMM):
    """{function: index of the handler parameter or None} of the FEMM modules."""
    FEMM_PACKAGE, FEMM_CLASS, FEMM_MODULE, HANDLER, HANDLER_CLASS = spec[:5]
    signatures = {}
    for source in modules.values():
        for node in ast.parse(source).body:
            if isinstance(node, ast.FunctionDef):
                names = [argument.arg for argument in node.args.args]
                signatures[node.name] = names.index(HANDLER) if HANDLER in names else None
    return signatures


def _is_femm_import(node, package, spec=FEMM):
    FEMM_PACKAGE, FEMM_CLASS, FEMM_MODULE, HANDLER, HANDLER_CLASS = spec[:5]
    if not isinstance(node, ast.ImportFrom):
        return False
    module = resolve_name("." * node.level + (node.module or ""), package) if node.level else node.module
    return bool(module) and module.startswith(f"pyleecan.Functions.{FEMM_PACKAGE}.")


def _call_without_handler(source, offsets, call, index, spec=FEMM):
    """Replacements removing the handler argument of a call (position or keyword)."""
    FEMM_PACKAGE, FEMM_CLASS, FEMM_MODULE, HANDLER, HANDLER_CLASS = spec[:5]
    argument = None
    if index is not None and index < len(call.args):
        argument = call.args[index]
    else:
        argument = next((k for k in call.keywords if k.arg == HANDLER), None)
    if argument is None:
        return None, []
    items = call.args + call.keywords
    position = items.index(argument)
    start = offsets[argument.lineno - 1] + argument.col_offset
    if isinstance(argument, ast.keyword):
        value = argument.value
    else:
        value = argument
    value_text = source[
        offsets[value.lineno - 1] + value.col_offset : offsets[value.end_lineno - 1] + value.end_col_offset
    ]
    if position + 1 < len(items):  # Remove up to the next argument
        following = items[position + 1]
        end = offsets[following.lineno - 1] + following.col_offset
    else:
        end = offsets[argument.end_lineno - 1] + argument.end_col_offset
        if position > 0:  # Remove the separator before
            previous = items[position - 1]
            start = offsets[previous.end_lineno - 1] + previous.end_col_offset
    return value_text, [(start, end, "")]


def _method_source(source, node, signatures, spec=FEMM):
    """Method (unindented) of a legacy FEMM function."""
    FEMM_PACKAGE, FEMM_CLASS, FEMM_MODULE, HANDLER, HANDLER_CLASS = spec[:5]
    offsets = _line_offsets(source)
    names = [argument.arg for argument in node.args.args]
    regular = HANDLER in names
    replacements = []
    handled = set()  # id of the handler Name nodes handled by a call
    for call in ast.walk(node):
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in signatures):
            continue
        index = signatures[call.func.id]
        func = call.func
        func_start = offsets[func.lineno - 1] + func.col_offset
        func_end = offsets[func.end_lineno - 1] + func.end_col_offset
        if index is not None or any(k.arg == HANDLER for k in call.keywords):
            if not regular:
                raise ValueError(f"{node.name}: call of {func.id} without FEMM handler")
            _, removal = _call_without_handler(source, offsets, call, index, spec)
            replacements.extend(removal)
            argument = call.args[index] if index is not None and index < len(call.args) else None
            if argument is not None:
                handled.add(id(argument))
            for keyword in call.keywords:
                if keyword.arg == HANDLER:
                    handled.add(id(keyword.value))
            replacements.append((func_start, func_end, "self." + func.id))
        else:
            replacements.append((func_start, func_end, ("self." if regular else FEMM_CLASS + ".") + func.id))
    if regular:
        for item in ast.walk(node):
            if isinstance(item, ast.Attribute) and isinstance(item.value, ast.Name) and item.value.id == HANDLER:
                start = offsets[item.value.lineno - 1] + item.value.col_offset
                replacements.append((start, start + len(HANDLER), "self.handler"))
                handled.add(id(item.value))
        for item in ast.walk(node):
            if (
                isinstance(item, ast.Name)
                and item.id == HANDLER
                and isinstance(item.ctx, ast.Load)
                and id(item) not in handled
            ):
                start = offsets[item.lineno - 1] + item.col_offset
                replacements.append((start, start + len(HANDLER), "self"))
    # Body (docstring included), with the replacements
    body_start = offsets[node.body[0].lineno - 1]
    body_end = offsets[node.end_lineno]
    body = source[body_start:body_end]
    for start, end, text in sorted(replacements, reverse=True):
        if start < body_start:
            continue  # In the signature (handled below)
        body = body[: start - body_start] + text + body[end - body_start :]
    if regular:
        # The handler documented as the object
        body = re.sub(
            rf"^(\s*){HANDLER}\s*:.*$", rf"\1self : {FEMM_CLASS}", body, count=1, flags=re.M
        )
        arguments = node.args
        index = names.index(HANDLER)
        defaults = arguments.defaults
        first_default = len(names) - len(defaults)
        new_args = ast.arguments(
            posonlyargs=[],
            args=[ast.arg("self")] + [a for i, a in enumerate(arguments.args) if i != index],
            vararg=arguments.vararg,
            kwonlyargs=arguments.kwonlyargs,
            kw_defaults=arguments.kw_defaults,
            kwarg=arguments.kwarg,
            defaults=[d for i, d in enumerate(defaults) if first_default + i != index],
        )
        signature = f"def {node.name}({ast.unparse(new_args)}){_returns(node)}:\n"
        return signature + _indent_body(body)
    signature = f"@staticmethod\ndef {node.name}({ast.unparse(node.args)}){_returns(node)}:\n"
    return signature + _indent_body(body)


def _indent_body(body):
    """Body lines as written in the module (already indented by 4)."""
    return body if body.endswith("\n") else body + "\n"


def femm_object_source(modules, shared_errors=None, spec=FEMM):
    """Legacy-style source of Functions/FEMM/femm_pyleecan.py.

    Parameters
    ----------
    modules : dict
        {legacy FEMM module name: source}
    shared_errors : dict, optional
        {legacy FEMM module name: names of its exceptions shared in
        classes_common.errors} (imported instead of defined)

    Returns
    -------
    source : str
        Module with the imports of the FEMM modules, their module-level
        definitions and the class femm_pyleecan
    """
    FEMM_PACKAGE, FEMM_CLASS, FEMM_MODULE, HANDLER, HANDLER_CLASS = spec[:5]
    shared_errors = shared_errors or {}
    package = f"pyleecan.Functions.{FEMM_PACKAGE}"
    signatures = femm_signatures(modules, spec)
    imports, definitions, methods, type_checking = [], [], [], []
    for name, source in modules.items():
        # Imports of the other FEMM modules (module level or local): removed
        source = _remove_statements(source, lambda stmt: _is_femm_import(stmt, package, spec))
        tree = ast.parse(source)
        lines = source.splitlines(keepends=True)
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                text = ast.unparse(node)
                if text not in imports:
                    imports.append(text)
            elif isinstance(node, ast.FunctionDef):
                methods.append(_method_source(source, node, signatures, spec))
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue  # Module docstring
            elif _is_type_checking_block(node):  # One block for the module
                for item in node.body:
                    text = ast.unparse(item)
                    if text not in type_checking and not (
                        isinstance(item, ast.ImportFrom)
                        and [alias.name for alias in item.names] == [FEMM_CLASS]
                    ):
                        type_checking.append(text)
            elif isinstance(node, ast.ClassDef) and node.name in shared_errors.get(name, ()):
                text = f"from {_up(spec)}classes_common.errors import {node.name}"
                if text not in imports:
                    imports.append(text)
            else:  # Classes, constants
                first = node.lineno - 1 - len(getattr(node, "decorator_list", []))
                definitions.append("".join(lines[first : node.end_lineno]).rstrip() + "\n")
    description = spec.description.split("\n")
    class_lines = [f"class {FEMM_CLASS}:", '    """' + description[0]]
    class_lines += [("    " + line).rstrip() for line in description[1:]]
    class_lines += ['    """', ""]
    if HANDLER is not None:
        type_checking.append(f"from {_up(spec)}{spec.handler_module} import {HANDLER_CLASS}")
        class_lines += [
            f"    def __init__(self, handler: {HANDLER_CLASS} | None = None) -> None:",
            '        """Create the object, with a new handler if none is given."""',
            "        if handler is None:",
            f"            from {_up(spec)}{spec.handler_module} import {HANDLER_CLASS}",
            "",
            f"            handler = {HANDLER_CLASS}()",
            "        self.handler = handler",
            "",
        ]
    body = "\n".join(class_lines) + "\n"
    for method in methods:
        body += "\n" + textwrap.indent(method, "    ", lambda line: line.strip() != "")
    header = (
        f'"""Interface of pyleecan with FEMM ({FEMM_CLASS}), written by the functions\n'
        f"generator from the modules of Functions/{FEMM_PACKAGE} (PLAN.md Step 8).\n"
        '"""\n\n'
    )
    if type_checking:  # The class imports of the type hints
        if "from typing import TYPE_CHECKING" not in imports:
            imports.append("from typing import TYPE_CHECKING")
        imports.append(
            "\nif TYPE_CHECKING:\n" + "\n".join(f"    {text}" for text in type_checking)
        )
    return (
        header
        + "\n".join(imports)
        + "\n\n\n"
        + "\n\n".join(definitions)
        + ("\n\n" if definitions else "")
        + body
    )


def femm_alias_source(name, source, modules, shared_errors=None, spec=FEMM):
    """Deprecated aliases of a legacy FEMM module (methods of femm_pyleecan)."""
    FEMM_PACKAGE, FEMM_CLASS, FEMM_MODULE, HANDLER, HANDLER_CLASS = spec[:5]
    signatures = femm_signatures(modules, spec)
    lines = [
        f'"""Deprecated aliases of {FEMM_CLASS} methods (removed in Phase 2)."""',
        "",
        "from warnings import warn",
        "",
    ]
    exported = []
    for node in ast.parse(source).body:
        if isinstance(node, (ast.ClassDef, ast.Assign)) and not isinstance(node, ast.FunctionDef):
            names = [node.name] if isinstance(node, ast.ClassDef) else [
                t.id for t in node.targets if isinstance(t, ast.Name)
            ]
            exported.extend(names)
    shared = [item for item in exported if item in (shared_errors or {}).get(name, ())]
    exported = [item for item in exported if item not in shared]
    if shared:
        lines.append(f"from {_up(spec)}classes_common.errors import {', '.join(shared)}  # noqa: F401")
    if exported:
        lines.append(f"from .{FEMM_MODULE} import {', '.join(exported)}  # noqa: F401")
    for node in ast.parse(source).body:
        if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
            continue
        message = f"{node.name} is deprecated, use {FEMM_CLASS}.{node.name} (removed in Phase 2)"
        lines += ["", ""]
        lines += [
            f"def {node.name}(*args, **kwargs):",
            f'    """Deprecated: use {FEMM_CLASS}.{node.name}"""',
            f"    from .{FEMM_MODULE} import {FEMM_CLASS}",
            "",
            f'    warn("{message}", DeprecationWarning, stacklevel=2)',
        ]
        index = signatures[node.name]
        if index is None:
            lines.append(f"    return {FEMM_CLASS}.{node.name}(*args, **kwargs)")
        else:
            lines += [
                "    args = list(args)",
                f'    femm = kwargs.pop("{HANDLER}") if "{HANDLER}" in kwargs else args.pop({index})',
                f"    if not isinstance(femm, {FEMM_CLASS}):  # FEMM handler",
                f"        femm = {FEMM_CLASS}(femm)",
                f"    return femm.{node.name}(*args, **kwargs)",
            ]
    return "\n".join(lines) + "\n"


def redirect_femm_calls(source, package, signatures, spec=FEMM):
    """Use the femm_pyleecan object in a method or function module.

    - ``from ...Functions.FEMM.x import f``: removed (the other names are
      imported from the femm_pyleecan module);
    - ``f(femm, a)`` -> ``femm.f(a)``, static ``g(a)`` -> ``femm_pyleecan.g(a)``;
    - ``_FEMMHandler()`` -> ``femm_pyleecan()``;
    - in a function with a ``femm`` variable, ``femm.X`` -> ``femm.handler.X``
      (X not a method of femm_pyleecan).

    Parameters
    ----------
    source : str
        Source of the module
    package : str
        Package of the module (to resolve the relative imports)
    signatures : dict
        {FEMM function: index of the handler parameter or None}

    Returns
    -------
    source : str
        Source using femm_pyleecan
    """
    FEMM_PACKAGE, FEMM_CLASS, FEMM_MODULE, HANDLER, HANDLER_CLASS = spec[:5]
    if (HANDLER is None or HANDLER not in source) and (
        HANDLER_CLASS is None or HANDLER_CLASS not in source
    ) and not any(name in source for name in signatures):
        return source
    tree = ast.parse(source)
    offsets = _line_offsets(source)
    replacements = []
    imported = {}  # local name: function
    up = "." * len(package.split("."))
    femm_module = f"{up}Functions.{FEMM_PACKAGE}.{FEMM_MODULE}"
    for node in ast.walk(tree):
        if not _is_femm_import(node, package, spec) or node.module.split(".")[-1] == FEMM_MODULE:
            continue
        functions = [alias for alias in node.names if alias.name in signatures]
        others = [alias for alias in node.names if alias.name not in signatures]
        for alias in functions:
            imported[alias.asname or alias.name] = alias.name
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        text = (
            ast.unparse(ast.ImportFrom(module=femm_module.lstrip("."), names=others, level=len(up)))
            if others
            else "pass"
        )
        replacements.append((start, end, text))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    class_imports = {}  # function: needs femm_pyleecan
    method_names = set(signatures) | {"handler"}
    for function in functions:
        has_handler = any(argument.arg == HANDLER for argument in function.args.args) or any(
            isinstance(item, ast.Name) and item.id == HANDLER and isinstance(item.ctx, ast.Store)
            for item in ast.walk(function)
        )
        for item in ast.walk(function):
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Name):
                func = item.func
                func_start = offsets[func.lineno - 1] + func.col_offset
                func_end = offsets[func.end_lineno - 1] + func.end_col_offset
                if func.id == HANDLER_CLASS:  # New FEMM interface object
                    replacements.append((func_start, func_end, FEMM_CLASS))
                    class_imports[function.name] = function
                elif func.id in imported:
                    name = imported[func.id]
                    index = signatures[name]
                    value, removal = _call_without_handler(source, offsets, item, index, spec)
                    if value is not None:
                        replacements.extend(removal)
                        if not value.isidentifier():
                            value = f"({value})"
                        replacements.append((func_start, func_end, f"{value}.{name}"))
                    else:  # Static method
                        replacements.append((func_start, func_end, f"{FEMM_CLASS}.{name}"))
                        class_imports[function.name] = function
            elif (
                has_handler
                and isinstance(item, ast.Attribute)
                and isinstance(item.value, ast.Name)
                and item.value.id == HANDLER
                and item.attr not in method_names
            ):
                start = offsets[item.value.lineno - 1] + item.value.col_offset
                replacements.append((start, start + len(HANDLER), HANDLER + ".handler"))
    for function in class_imports.values():
        first = (
            function.body[1]
            if ast.get_docstring(function) is not None and len(function.body) > 1
            else function.body[0]
        )
        indent = " " * first.col_offset
        start = offsets[first.lineno - 1]
        replacements.append(
            (
                start,
                start,
                f"{indent}{CIRCULAR_COMMENT}\n{indent}from {femm_module} import {FEMM_CLASS}\n\n",
            )
        )
    if not replacements:
        return source
    for start, end, text in sorted(replacements, key=lambda r: (r[0], r[1]), reverse=True):
        source = source[:start] + text + source[end:]
    # Imports left empty
    return _remove_statements(
        source, lambda stmt: isinstance(stmt, ast.Pass) and stmt.col_offset == 0
    )
