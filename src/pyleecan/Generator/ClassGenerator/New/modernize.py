"""Modernization of the legacy sources (methods and functions).

The pipeline shared by the method generator (``generate_methods_new.py``) and
the functions generator (``generate_function_new_classes.py``): the
transformations of a legacy module that do not depend on the class it is
inlined in. They are the passes of the class generator moved here
(PLAN.md Step 5), which keeps only the class assembly.

Every transformation is idempotent: applied to a modernized source, it
changes nothing.
"""

import ast
import re

from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _apply_numpy_import_style,
    _apply_os_import_style,
    _apply_pyvista_import_style,
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
    from .class_generator import (
        _keyword_geometry_calls,
        _replace_dynamic_class_imports,
        _redirect_experimental_class_imports,
        _redirect_experimental_function_imports,
        _redirect_experimental_loader_imports,
        _rename_experimental_normalizations,
        _static_local_class_imports,
        class_module_paths,
        relocate_class_imports,
    )
    from .function_module_names import (
        function_module_mapping,
        redirect_function_module_imports,
        redirect_rule_module_name,
    )
    from .generate_function_new_classes import (
        _function_import_style,
        _redirect_shared_error_imports,
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
