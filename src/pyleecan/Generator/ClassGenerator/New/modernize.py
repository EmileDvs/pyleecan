"""Modernization of the legacy sources (methods and functions).

The pipeline shared by the method generator (``generate_methods_new.py``) and
the functions generator (``generate_function_new_classes.py``): the
transformations of a legacy module that do not depend on the class it is
inlined in. This module centralizes them (PLAN.md Step 5); the class generator
imports them for its own passes and keeps only the class assembly.

- ``remove_coding_declaration``: useless UTF-8 encoding declarations
- ``apply_import_styles`` (``_apply_*_import_style``): ``import numpy as np``,
  ``import pyvista as pv``, ``import os``
- ``_replace_empty_containers``: ``list()`` -> ``[]``, ``dict()`` -> ``{}``
- ``modernize_names``: shared errors (``_redirect_shared_error_imports``),
  class imports (``_redirect_experimental_class_imports``), keyword calls
  (``_keyword_geometry_calls``), function imports
  (``_redirect_experimental_function_imports``)
- ``_function_import_style``: absolute or relative pyleecan imports

Every transformation is idempotent: applied to a modernized source, it
changes nothing.
"""

import ast
import io
import re
import tokenize
from bisect import bisect_left
from importlib.util import resolve_name
from pathlib import Path

from pyleecan.classes_common.class_lookup import (
    NORMALIZATION_CLASS_NAMES,
    class_module_name,
)

CODING_DECLARATION = re.compile(r"^[ \t\f]*#.*?coding[:=][ \t]*utf-?8\b.*$", re.I)
"""UTF-8 encoding declaration (PEP 263), useless: UTF-8 is the default"""


def remove_coding_declaration(source):
    """Remove a UTF-8 encoding declaration (``# -*- coding: utf-8 -*-``).

    Only the first two lines can hold a declaration (PEP 263); a declaration
    of another encoding is kept. The blank lines left at the top are removed.
    """
    lines = source.splitlines(keepends=True)
    for index in range(min(2, len(lines))):
        if CODING_DECLARATION.match(lines[index]):
            del lines[index]
            while lines and not lines[0].strip():
                del lines[0]
            return "".join(lines)
    return source


REFLECTIVE_CALLS = frozenset({"eval", "exec", "globals", "locals"})
"""Calls reading names dynamically: their modules keep their imports as written"""


def is_reflective(source):
    """True if the module calls eval, exec, globals or locals."""
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in REFLECTIVE_CALLS
        for node in ast.walk(ast.parse(source))
    )


def apply_import_styles(source):
    """``import numpy as np``, ``import pyvista as pv`` and ``import os``.

    ``from numpy import array`` becomes ``import numpy as np`` with ``np.array``
    references (same for pyvista and os). A reflective module (eval, exec...)
    is left unchanged: its names may be read dynamically.
    """
    if is_reflective(source):
        return source
    source = _apply_numpy_import_style(source)
    source = _apply_pyvista_import_style(source)
    return _apply_os_import_style(source)


NAME_PASSES = (
    "dynamic_imports",
    "errors",
    "classes",
    "keywords",
    "normalizations",
    "loaders",
    "static_imports",
    "functions",
)
"""Name passes of modernize_names, in the order of the class generator"""

MOVED_NAME_PASSES = frozenset({"errors", "classes", "keywords", "functions"})
"""Name passes moved from the class generator (PLAN.md Step 5, point 2).

Four passes depend on the class assembly and stay in the class generator:

- "dynamic_imports" and "normalizations": the dynamic class imports
  (``module = __import__("pyleecan.Classes.X")``) are replaced there using the
  imports of the whole class, with the legacy names. The normalization classes
  are imported with their new name and their legacy binding
  (``NormRef as Norm_ref``) meanwhile.
- "loaders" and "static_imports": the legacy ``import_class("pyleecan.Classes",
  "X")`` becomes a function-local import after the class generator has
  renamed the normalization classes and placed the imports of the class
  (header or local, to avoid import cycles). The chain dynamic imports ->
  normalizations -> loaders -> static imports moves as a whole, with the
  class-level import placement."""


def modernize_names(
    source, package, gen_dict, class_name=None, soft_name="pyleecan", passes=None
):
    """Import the classes and functions with their new names (static imports).

    The passes of the class generator, in its order, on one legacy module
    (NAME_PASSES): shared errors, class imports (Classes -> Classes_new),
    keyword calls, normalization class names, loader imports, static class
    imports instead of import_class, function imports (Functions ->
    Functions_new, renamed modules); then the class modules are relocated to
    their sub-package and the imports made relative to the module again.

    Parameters
    ----------
    source : str
        Legacy source
    package : str
        Package of the module (to resolve its relative imports)
    gen_dict : dict
        Generation dictionary (contains all the csv data)
    class_name : str, optional
        Class the method belongs to (its own class is not imported locally)
    soft_name : str
        Name of the software package
    passes : set, optional
        Passes to apply (default: MOVED_NAME_PASSES)

    Returns
    -------
    source : str
        Source with the new names
    """
    from ....classes_common.class_lookup import NORMALIZATION_CLASS_NAMES
    from .class_generator import (  # Passes kept in the class generator
        _redirect_experimental_loader_imports,
        _rename_experimental_normalizations,
        _replace_dynamic_class_imports,
        _static_local_class_imports,
        class_module_paths,
        relocate_class_imports,
    )
    from .function_module_names import (
        function_module_mapping,
        redirect_function_module_imports,
        redirect_rule_module_name,
    )

    passes = MOVED_NAME_PASSES if passes is None else passes
    source = _function_import_style(source, package, "absolute")
    if "dynamic_imports" in passes:
        # __import__("pyleecan.Classes.X") -> import_class (made static below)
        tree = ast.parse(source)
        bindings = {
            alias.asname
            or (alias.name.split(".")[0] if isinstance(node, ast.Import) else alias.name)
            for node in tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        source, replaced = _replace_dynamic_class_imports(source, soft_name, bindings)
        if replaced:
            loader = ast.ImportFrom(
                module=f"{soft_name}.Functions.Load.import_class",
                names=[ast.alias(name="import_class", asname="_pyleecan_import_class")],
                level=0,
            )
            source = ast.unparse(loader) + "\n" + source
    if "errors" in passes:
        source = _redirect_shared_error_imports(source, package, soft_name)
    if "classes" in passes:
        source = _redirect_experimental_class_imports(source, soft_name, gen_dict)
        if "normalizations" not in passes:
            source = _alias_normalization_imports(source, soft_name)
    if "keywords" in passes:
        source = _keyword_geometry_calls(source, soft_name, gen_dict)
    if "normalizations" in passes:
        source = _rename_experimental_normalizations(source, soft_name)
    if "loaders" in passes:
        source = _redirect_experimental_loader_imports(source, soft_name)
    if "static_imports" in passes and class_name is not None:
        source = _static_local_class_imports(
            source,
            soft_name,
            gen_dict,
            NORMALIZATION_CLASS_NAMES.get(class_name, class_name),
        )
    if "functions" in passes:
        source = _redirect_experimental_function_imports(source, soft_name)
        source = redirect_function_module_imports(
            source, package, function_module_mapping(), soft_name
        )
        source = redirect_rule_module_name(source, soft_name)
    source = relocate_class_imports(
        source, soft_name, "Classes_new", class_module_paths(gen_dict)
    )
    return _function_import_style(source, package, "relative")


def _alias_normalization_imports(source, soft_name="pyleecan"):
    """Import the normalization classes by their new name, legacy binding.

    ``from pyleecan.Classes_new.norm_ref import Norm_ref`` becomes
    ``from pyleecan.Classes_new.norm_ref import NormRef as Norm_ref``: the
    module can be imported, its code keeps the legacy name (renamed by the
    class generator, see MOVED_NAME_PASSES).
    """
    from ....classes_common.class_lookup import NORMALIZATION_CLASS_NAMES

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == 10:  # newline
            offsets.append(index + 1)
    replacements = []
    prefix = soft_name + ".Classes_new."
    for node in ast.walk(ast.parse(source)):
        if not (
            isinstance(node, ast.ImportFrom)
            and not node.level
            and (node.module or "").startswith(prefix)
            and any(alias.name in NORMALIZATION_CLASS_NAMES for alias in node.names)
        ):
            continue
        names = [
            ast.alias(
                name=NORMALIZATION_CLASS_NAMES[alias.name],
                asname=alias.asname or alias.name,
            )
            if alias.name in NORMALIZATION_CLASS_NAMES
            else alias
            for alias in node.names
        ]
        replacement = ast.ImportFrom(module=node.module, names=names, level=0)
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


def _get_import_scope_info(scope_body, package):
    """Collect names local to a scope and its directly imported package symbols."""
    local_names = set()
    package_names = {}
    global_names = set()
    assigned_names = set()

    class ScopeVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            local_names.add(node.name)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            local_names.add(node.name)

        def visit_Lambda(self, node):
            return

        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                local_names.add(node.id)
                assigned_names.add(node.id)

        def visit_Global(self, node):
            global_names.update(node.names)

        def visit_Import(self, node):
            for alias in node.names:
                local_names.add(alias.asname or alias.name.split(".")[0])
                if alias.name == package or alias.name.startswith(package + "."):
                    module_name = alias.name[len(package) :].lstrip(".")
                    package_names[alias.asname or alias.name.split(".")[0]] = (
                        (module_name or None) if alias.asname else None
                    )

        def visit_ImportFrom(self, node):
            for alias in node.names:
                local_names.add(alias.asname or alias.name)
                if (
                    node.module
                    and (
                        node.module == package or node.module.startswith(package + ".")
                    )
                    and alias.name != "*"
                ):
                    module_name = node.module[len(package) :].lstrip(".")
                    imported_name = ".".join(
                        part for part in (module_name, alias.name) if part
                    )
                    package_names[alias.asname or alias.name] = imported_name

    visitor = ScopeVisitor()
    for statement in scope_body:
        visitor.visit(statement)

    local_names.difference_update(global_names)
    for name in global_names:
        package_names.pop(name, None)
    shadowed_names = assigned_names.intersection(package_names)
    return local_names, package_names, shadowed_names


def _apply_package_import_style(source, package, package_alias):
    """Normalize package imports and their references to a shared module alias."""
    tree = ast.parse(source)
    if package in ("numpy", "pyvista", "os"):
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names.update(
                    alias.asname or alias.name.split(".")[0]
                    for alias in node.names
                    if alias.name == package or alias.name.startswith(package + ".")
                )
                if package == "os" and any(
                    alias.name.startswith("os.") for alias in node.names
                ):
                    return source
            elif isinstance(node, ast.ImportFrom) and node.module and (
                node.module == package or node.module.startswith(package + ".")
            ):
                if node.level:
                    return source
                if package == "os" and node.module != "os" and node.module != "os.path":
                    return source
                imported_names.update(alias.asname or alias.name for alias in node.names)
        for node in ast.walk(tree):
            if package == "os" and isinstance(node, (ast.Import, ast.ImportFrom)):
                aliases = node.names
                is_os_import = (
                    isinstance(node, ast.Import)
                    and any(
                        item.name == package or item.name.startswith(package + ".")
                        for item in aliases
                    )
                ) or (
                    isinstance(node, ast.ImportFrom)
                    and node.module is not None
                    and (node.module == package or node.module.startswith(package + "."))
                )
                if is_os_import:
                    if any(
                        isinstance(other, ast.stmt)
                        and other is not node
                        and (
                            other.lineno == node.lineno
                            and other.col_offset < node.col_offset
                            or other.lineno == node.end_lineno
                            and other.col_offset >= node.end_col_offset
                        )
                        for other in ast.walk(tree)
                    ):
                        return source
            if (
                isinstance(node, ast.Name)
                and node.id == package_alias
                and isinstance(node.ctx, (ast.Store, ast.Del))
            ) or (isinstance(node, ast.arg) and node.arg == package_alias):
                return source
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == package_alias:
                    return source
            if isinstance(node, ast.ExceptHandler) and node.name == package_alias:
                return source
            if isinstance(node, (ast.Global, ast.Nonlocal)) and (
                set(node.names) & (imported_names | {package_alias})
            ):
                return source
            if isinstance(node, ast.Lambda) and any(
                argument.arg in imported_names
                for argument in (
                    node.args.posonlyargs
                    + node.args.args
                    + node.args.kwonlyargs
                    + ([node.args.vararg] if node.args.vararg else [])
                    + ([node.args.kwarg] if node.args.kwarg else [])
                )
            ):
                return source
            if isinstance(node, ast.comprehension) and any(
                isinstance(target, ast.Name) and target.id in imported_names
                for target in ast.walk(node.target)
            ):
                return source
            if isinstance(node, ast.ClassDef) and any(
                isinstance(child, ast.Name)
                and isinstance(child.ctx, (ast.Store, ast.Del))
                and child.id in imported_names
                for statement in node.body
                if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
                for child in ast.walk(statement)
            ):
                return source
            if isinstance(node, ast.Import):
                if any(
                    (alias.asname or alias.name.split(".")[0]) == package_alias
                    and not (
                        alias.name == package or alias.name.startswith(package + ".")
                    )
                    for alias in node.names
                ):
                    return source
            if isinstance(node, ast.ImportFrom):
                if node.module == package or (
                    node.module and node.module.startswith(package + ".")
                ):
                    if any(alias.name == "*" for alias in node.names):
                        return source
                elif any(
                    (alias.asname or alias.name) == package_alias
                    for alias in node.names
                ):
                    return source
            if isinstance(
                node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                _, _, shadowed_names = _get_import_scope_info(node.body, package)
                if shadowed_names:
                    return source
    _, module_names, module_shadowed_names = _get_import_scope_info(tree.body, package)

    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    duplicate_module_imports = set()
    has_module_package_import = False
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and (node.module == package or node.module.startswith(package + "."))
        ):
            if any(alias.name == "*" for alias in node.names):
                continue
            if has_module_package_import:
                duplicate_module_imports.add(id(node))
            has_module_package_import = True
        elif isinstance(node, ast.Import):
            package_aliases = [
                alias
                for alias in node.names
                if alias.name == package or alias.name.startswith(package + ".")
            ]
            if package_aliases:
                if has_module_package_import:
                    duplicate_module_imports.add(id(node))
                has_module_package_import = True

    def add_statement_replacement(node, replacement):
        start = line_offsets[node.lineno - 1]
        statement_start = start + node.col_offset
        end = line_offsets[node.end_lineno - 1] + node.end_col_offset
        line_end = source_bytes.find(b"\n", end)
        if line_end == -1:
            line_end = len(source_bytes)
        indentation = source_bytes[start:statement_start]
        suffix = source_bytes[end:line_end]
        replacements.append((start, line_end, indentation + replacement + suffix))

    class ReferenceVisitor(ast.NodeVisitor):
        def __init__(self):
            self.scopes = []

        def visit_FunctionDef(self, node):
            self._visit_function(node)

        def visit_AsyncFunctionDef(self, node):
            self._visit_function(node)

        def _visit_function(self, node):
            for decorator in node.decorator_list:
                self.visit(decorator)
            for default in node.args.defaults + node.args.kw_defaults:
                if default is not None:
                    self.visit(default)
            for argument in (
                node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            ):
                if argument.annotation is not None:
                    self.visit(argument.annotation)
            if node.args.vararg and node.args.vararg.annotation:
                self.visit(node.args.vararg.annotation)
            if node.args.kwarg and node.args.kwarg.annotation:
                self.visit(node.args.kwarg.annotation)
            if node.returns is not None:
                self.visit(node.returns)
            body = node.body
            local_names, package_names, shadowed_names = _get_import_scope_info(
                body, package
            )
            argument_names = {
                argument.arg
                for argument in (
                    node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                )
            }
            if node.args.vararg:
                argument_names.add(node.args.vararg.arg)
            if node.args.kwarg:
                argument_names.add(node.args.kwarg.arg)
            local_names.update(argument_names)
            self.scopes.append((local_names, package_names, shadowed_names))
            for statement in body:
                self.visit(statement)
            self.scopes.pop()

        def visit_ClassDef(self, node):
            for decorator in node.decorator_list:
                self.visit(decorator)
            for base in node.bases:
                self.visit(base)
            for keyword in node.keywords:
                self.visit(keyword.value)
            for statement in node.body:
                self.visit(statement)

        def visit_Name(self, node):
            if not isinstance(node.ctx, ast.Load):
                return

            imported_name = None
            for local_names, package_names, shadowed_names in reversed(self.scopes):
                if node.id in shadowed_names:
                    return
                if node.id in package_names:
                    imported_name = package_names[node.id]
                    break
                if node.id in local_names:
                    return
            else:
                if node.id not in module_names:
                    return
                if node.id in module_shadowed_names:
                    return
                imported_name = module_names[node.id]

            if imported_name is None:
                replacement = package_alias.encode("utf-8")
            else:
                replacement = (package_alias + "." + imported_name).encode("utf-8")
            start = line_offsets[node.lineno - 1] + node.col_offset
            end = start + len(node.id.encode("utf-8"))
            replacements.append((start, end, replacement))

    ReferenceVisitor().visit(tree)

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and (node.module == package or node.module.startswith(package + "."))
        ):
            if any(alias.name == "*" for alias in node.names):
                continue
            replacement = (
                b""
                if id(node) in duplicate_module_imports
                else (
                    f"import {package}"
                    if package == package_alias
                    else f"import {package} as {package_alias}"
                ).encode("utf-8")
            )
            add_statement_replacement(node, replacement)
        elif isinstance(node, ast.Import):
            aliases = []
            changed = False
            package_seen = False
            for alias in node.names:
                if alias.name == package or alias.name.startswith(package + "."):
                    if id(node) in duplicate_module_imports or package_seen:
                        changed = True
                        continue
                    aliases.append(
                        ast.alias(
                            name=package,
                            asname=package_alias if package != package_alias else None,
                        )
                    )
                    package_seen = True
                    changed = True
                else:
                    aliases.append(alias)
            if changed:
                add_statement_replacement(
                    node,
                    (
                        ast.unparse(ast.Import(names=aliases)).encode("utf-8")
                        if aliases
                        else b""
                    ),
                )

    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _apply_numpy_import_style(source):
    """Use ``import numpy as np`` for NumPy imports and their references."""
    return _apply_package_import_style(source, "numpy", "np")


def _apply_pyvista_import_style(source):
    """Use ``import pyvista as pv`` for PyVista imports and their references."""
    return _apply_package_import_style(source, "pyvista", "pv")


def _apply_os_import_style(source):
    """Use ``import os`` for os imports and their references."""
    return _apply_package_import_style(source, "os", "os")


def _replace_empty_containers(source, blocked_names=(), include_tuple=False):
    """Replace unshadowed empty built-in container calls with literals."""
    tree = ast.parse(source)
    blocked = set(blocked_names)
    literals = {"dict": b"{}", "list": b"[]"}
    if include_tuple:
        literals["tuple"] = b"()"
    candidates = set(literals)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            blocked.add(node.id)
        elif isinstance(node, ast.arg):
            blocked.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            blocked.add(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            blocked.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            blocked.update(node.names)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name == "*":
                    blocked.update(candidates)
                else:
                    blocked.add(
                        alias.asname
                        or (
                            alias.name.split(".")[0]
                            if isinstance(node, ast.Import)
                            else alias.name
                        )
                    )
        elif isinstance(node, ast.MatchAs) and node.name:
            blocked.add(node.name)
        elif isinstance(node, ast.MatchStar) and node.name:
            blocked.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            blocked.add(node.rest)

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in candidates - blocked
            and not node.args
            and not node.keywords
        ):
            start = offsets[node.lineno - 1] + node.col_offset
            end = offsets[node.end_lineno - 1] + node.end_col_offset
            # Preserve comments inside multiline calls.
            if b"#" not in encoded[start:end]:
                replacements.append((start, end, literals[node.func.id]))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


def _redirect_experimental_class_imports(source, soft_name, gen_dict):
    """Redirect generated classes and selected support imports to Classes_new."""
    from .class_generator import CLASS_ERROR_NAMES, VENDORED_CLASS_PACKAGES, _check_error_definitions

    source_bytes = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            offsets.append(index + 1)

    replacements = []
    prefix = soft_name + ".Classes."
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom) or node.level != 0 or not node.module:
            continue
        if node.module == soft_name + ".Classes":
            error_aliases = [
                alias for alias in node.names if alias.name in CLASS_ERROR_NAMES
            ]
            # get_class_dict has no Classes_new equivalent (use ClassInfo)
            legacy_aliases = [
                alias for alias in node.names if alias not in error_aliases
            ]
            if not error_aliases:
                continue
            imports = [
                ast.ImportFrom(
                    module=f"{soft_name}.Classes_new._error",
                    names=error_aliases,
                    level=0,
                )
            ]
            if legacy_aliases:
                imports.append(
                    ast.ImportFrom(module=node.module, names=legacy_aliases, level=0)
                )
            replacement = ("\n" + " " * node.col_offset).join(
                ast.unparse(import_node) for import_node in imports
            )
        elif node.module == prefix + "_check":
            error_names = _check_error_definitions()
            error_aliases = [alias for alias in node.names if alias.name in error_names]
            check_aliases = [alias for alias in node.names if alias.name not in error_names]
            imports = []
            if error_aliases:
                imports.append(
                    ast.ImportFrom(
                        module=f"{soft_name}.Classes_new._error",
                        names=error_aliases,
                        level=0,
                    )
                )
            if check_aliases:
                imports.append(
                    ast.ImportFrom(
                        module=f"{soft_name}.Classes_new._check",
                        names=check_aliases,
                        level=0,
                    )
                )
            replacement = ("; ").join(ast.unparse(item) for item in imports)
        elif node.module.startswith(prefix) and (
            node.module[len(prefix) :].split(".")[0] in VENDORED_CLASS_PACKAGES
        ):
            replacement = ast.unparse(
                ast.ImportFrom(
                    module=f"{soft_name}.Classes_new.{node.module[len(prefix):]}",
                    names=node.names,
                    level=0,
                )
            )
        elif node.module.startswith(prefix) and (
            node.module[len(prefix) :] in gen_dict
            or node.module[len(prefix) :] in ("_check", "_FEMMHandler")
        ):
            class_name = node.module[len(prefix) :]
            module_name = {
                "_check": "_check",
                "_FEMMHandler": "_femm_handler",
            }.get(class_name, class_module_name(class_name))
            replacement = ast.unparse(
                ast.ImportFrom(
                    module=f"{soft_name}.Classes_new.{module_name}",
                    names=node.names,
                    level=0,
                )
            )
        else:
            continue
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, replacement.encode("utf-8")))

    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _legacy_init_arguments(class_name, gen_dict):
    """Positional arguments of a legacy constructor: own properties, then mother's."""
    arguments = []
    while class_name in gen_dict:
        arguments.extend(
            prop["name"]
            for prop in gen_dict[class_name]["properties"]
            if prop["name"] not in arguments
        )
        class_name = gen_dict[class_name]["mother"]
    return tuple(arguments)


def _keyword_geometry_calls(source, soft_name, gen_dict=None):
    """Preserve legacy geometry constructor arguments in generated methods.

    Positional arguments become keyword arguments (in the legacy constructor
    order) for Segment, Arc1, Arc2, Arc3 and, given gen_dict, for every
    generated class: pydantic models only accept keyword arguments, and both
    implementations share the same method code.
    """
    arguments = {
        "Segment": ("begin", "end", "prop_dict"),
        "Arc1": ("begin", "end", "radius", "is_trigo_direction", "prop_dict"),
        "Arc2": ("begin", "center", "angle", "prop_dict"),
        "Arc3": ("begin", "end", "is_trigo_direction", "prop_dict"),
    }
    if gen_dict is not None:
        for name in gen_dict:
            arguments.setdefault(
                NORMALIZATION_CLASS_NAMES.get(name, name),
                _legacy_init_arguments(name, gen_dict),
            )

    def imported_geometry(node, alias):
        module = class_module_name(alias.name) if alias.name in arguments else None
        return (
            isinstance(node, ast.ImportFrom)
            and module is not None
            and (
                node.level == 0
                and node.module == f"{soft_name}.Classes_new.{module}"
                or node.level == 1
                and node.module == module
                or node.level > 1  # e.g. from ...Classes_new.segment (functions)
                and node.module == f"Classes_new.{module}"
            )
        )

    tree = ast.parse(source)
    bindings = {
        alias.asname or alias.name: alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
        if imported_geometry(node, alias)
    }
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in bindings
        and node.args
    ]
    if not calls:
        return source
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, (ast.Store, ast.Del))
            and node.id in bindings
            or isinstance(node, ast.arg) and node.arg in bindings
            or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.name in bindings
        ):
            raise ValueError("Cannot safely rewrite a shadowed geometry class import")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                binding = alias.asname or alias.name.split(".")[0]
                if binding in bindings and (
                    not imported_geometry(node, alias)
                    or bindings[binding] != alias.name
                ):
                    raise ValueError("Cannot safely rewrite a conflicting geometry class import")

    encoded = source.encode("utf-8")
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line.encode("utf-8")))

    def token_offset(position):
        line, column = position
        if line > len(lines):
            return offsets[-1]
        return offsets[line - 1] + len(lines[line - 1][:column].encode("utf-8"))

    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    token_starts = [token_offset(token.start) for token in tokens]
    ignored = {
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.COMMENT,
        tokenize.INDENT,
        tokenize.DEDENT,
    }
    edits = []
    for call in calls:
        class_name = bindings[call.func.id]
        names = arguments[class_name]
        if len(call.args) > len(names) or any(
            isinstance(arg, ast.Starred) for arg in call.args
        ):
            raise ValueError(f"Cannot safely rewrite unpacked {class_name} arguments")
        if {keyword.arg for keyword in call.keywords}.intersection(names[:len(call.args)]):
            raise ValueError(f"{class_name} receives the same argument more than once")
        function_end = offsets[call.func.end_lineno - 1] + call.func.end_col_offset
        index = bisect_left(token_starts, function_end)
        while tokens[index].type in ignored:
            index += 1
        if tokens[index].string != "(":
            raise ValueError(f"Cannot locate {class_name} call arguments")
        depth = 1
        starts = []
        expect_start = True
        for token in tokens[index + 1:]:
            if token.type in ignored:
                continue
            position = token_offset(token.start)
            if depth == 1 and expect_start and token.string != ")":
                starts.append(position)
                expect_start = False
            if token.type == tokenize.OP:
                if token.string in "([{":
                    depth += 1
                elif token.string in ")]}":
                    depth -= 1
                    if depth == 0:
                        break
                elif token.string == "," and depth == 1:
                    expect_start = True
        previous_end = function_end
        for name, argument in zip(names, call.args):
            arg_start = offsets[argument.lineno - 1] + argument.col_offset
            candidates = [start for start in starts if previous_end < start <= arg_start]
            if not candidates:
                raise ValueError(f"Cannot locate {class_name} positional argument")
            edits.append((candidates[-1], (name + "=").encode("utf-8")))
            previous_end = offsets[argument.end_lineno - 1] + argument.end_col_offset

    for position, text in sorted(edits, reverse=True):
        encoded = encoded[:position] + text + encoded[position:]
    return encoded.decode("utf-8")


def _redirect_experimental_function_imports(source, soft_name):
    """Use copied functions while retaining the legacy loading and saving APIs."""
    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == ord("\n"):
            offsets.append(index + 1)
    prefix = soft_name + ".Functions"
    deferred = {
        prefix + ".load",
        prefix + ".save",
        prefix + ".Load",
        prefix + ".Save",
    }
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"import_module", "__import__"}
            and node.args
        ):
            argument = node.args[0]
            first = (
                argument.values[0]
                if isinstance(argument, ast.JoinedStr) and argument.values
                else argument
            )
            if (
                isinstance(first, ast.Constant)
                and isinstance(first.value, str)
                and (first.value == prefix or first.value.startswith(prefix + "."))
                and not any(
                    first.value == name or first.value.startswith(name + ".")
                    for name in deferred
                )
            ):
                start = offsets[argument.lineno - 1] + argument.col_offset
                end = offsets[argument.end_lineno - 1] + argument.end_col_offset
                segment = data[start:end]
                old = prefix.encode("utf-8")
                replacements.append(
                    (
                        start,
                        end,
                        segment.replace(old, (prefix + "_new").encode("utf-8"), 1),
                    )
                )
            continue
        if not isinstance(node, ast.ImportFrom) or node.level or not node.module:
            continue
        module = node.module
        if not (module == prefix or module.startswith(prefix + ".")):
            continue
        if any(module == name or module.startswith(name + ".") for name in deferred):
            continue
        replacement = ast.ImportFrom(
            module=soft_name + ".Functions_new" + module[len(prefix):],
            names=node.names,
            level=0,
        )
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        data = data[:start] + replacement + data[end:]
    return data.decode("utf-8")


def shared_error_names(error_path=None):
    """Names of the shared exceptions (classes_common/errors.py)."""
    from pyleecan.definitions import MAIN_DIR

    error_path = Path(error_path or Path(MAIN_DIR) / "classes_common" / "errors.py")
    if not error_path.is_file():
        return frozenset()
    tree = ast.parse(error_path.read_text(encoding="utf-8"))
    return frozenset(node.name for node in tree.body if isinstance(node, ast.ClassDef))


def _function_import_style(source, package, import_style):
    """Convert Pyleecan from-imports relative to the generated module package."""
    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == 10:
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom) or node.module == "__future__":
            continue
        module = node.module or ""
        if node.level:
            module = resolve_name("." * node.level + module, package)
        if module != "pyleecan" and not module.startswith("pyleecan."):
            continue
        if import_style == "absolute":
            new_module, level = module, 0
        else:
            current_parts = package.split(".")
            module_parts = module.split(".")
            common = 0
            for left, right in zip(current_parts, module_parts):
                if left != right:
                    break
                common += 1
            level = len(current_parts) - common + 1
            new_module = ".".join(module_parts[common:]) or None
        replacement = ast.ImportFrom(module=new_module, names=node.names, level=level)
        replacements.append((
            offsets[node.lineno - 1] + node.col_offset,
            offsets[node.end_lineno - 1] + node.end_col_offset,
            ast.unparse(replacement).encode("utf-8"),
        ))
    for start, end, replacement in sorted(replacements, reverse=True):
        data = data[:start] + replacement + data[end:]
    return data.decode("utf-8")


def _redirect_shared_error_imports(
    source, package, soft_name="pyleecan", method_error_names=None
):
    """Redirect imports of centralized errors, preserving bindings.

    The function errors (FUNCTION_ERRORS) and, given method_error_names (see
    shared_error_names), the errors imported from a legacy method module
    (``from pyleecan.Methods.Geometry.Segment import PointSegmentError``) are
    imported from the shared errors instead.
    """
    from .generate_function_new_classes import FUNCTION_ERRORS

    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == 10:
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        if node.level:
            module = resolve_name("." * node.level + module, package)
        errors = None
        for prefix in (f"{soft_name}.Functions.", f"{soft_name}.Functions_new."):
            if module.startswith(prefix):
                errors = FUNCTION_ERRORS.get(module[len(prefix) :])
                break
        if (
            errors is None
            and method_error_names
            and module.startswith(f"{soft_name}.Methods.")
            and not any(alias.name == "*" for alias in node.names)
        ):
            from .class_generator import _shared_error_name

            errors = {
                alias.name: _shared_error_name((module, alias.name))
                for alias in node.names
                if _shared_error_name((module, alias.name)) in method_error_names
            }
        if not errors:
            continue
        if any(alias.name == "*" for alias in node.names):
            raise ValueError(f"{module}:{node.lineno}: wildcard error import requires review")
        selected = [alias for alias in node.names if alias.name in errors]
        if not selected:
            continue
        remaining = [alias for alias in node.names if alias.name not in errors]
        shared = [
            ast.alias(
                name=errors[alias.name],
                asname=alias.asname or (
                    alias.name if errors[alias.name] != alias.name else None
                ),
            )
            for alias in selected
        ]
        imports = []
        if remaining:
            imports.append(ast.ImportFrom(module=node.module, names=remaining, level=node.level))
        imports.append(
            ast.ImportFrom(module=f"{soft_name}.Classes_new._error", names=shared, level=0)
        )
        replacement = ("; ".join(ast.unparse(item) for item in imports)).encode("utf-8")
        replacements.append(
            (offsets[node.lineno - 1] + node.col_offset,
             offsets[node.end_lineno - 1] + node.end_col_offset, replacement)
        )
    for start, end, replacement in sorted(replacements, reverse=True):
        data = data[:start] + replacement + data[end:]
    return data.decode("utf-8")
