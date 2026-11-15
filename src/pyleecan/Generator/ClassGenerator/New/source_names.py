"""Legacy <-> new names of the class and function imports of a source.

Shared by the generators of the new sources (method generator, functions
generator): the legacy sources import the classes and the functions with
their legacy names, the new sources with the new ones.

========================================  ===============================================
legacy                                    new
========================================  ===============================================
``pyleecan.Classes.Segment``              ``pyleecan.Classes_new.geometry.segment``
``pyleecan.Classes.Norm_ref.Norm_ref``    ``pyleecan.Classes_new.scidatatool.norm_ref.NormRef``
``pyleecan.Functions.FEMM.comp_FEMM_dict``  ``pyleecan.Functions_new.FEMM.comp_femm_dict``
========================================  ===============================================

``to_new_names`` translates a legacy source; ``to_legacy_names`` translates
back. Relative imports stay relative (same form), absolute ones absolute.
"""

import ast
from functools import lru_cache
from importlib.util import resolve_name

from pyleecan.classes_common.class_lookup import (
    NORMALIZATION_CLASS_NAMES,
    class_module_name,
)
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    VENDORED_CLASS_PACKAGES,
    class_subpackage,
)
from pyleecan.Generator.ClassGenerator.New.function_module_names import (
    function_module_mapping,
)

LEGACY_CLASSES = "pyleecan.Classes"
NEW_CLASSES = "pyleecan.Classes_new"
LEGACY_FUNCTIONS = "pyleecan.Functions"
NEW_FUNCTIONS = "pyleecan.Functions_new"


class NameMaps:
    """Legacy <-> new names of the classes and of the function modules.

    Parameters
    ----------
    gen_dict : dict
        Generation dictionary (contains all the csv data)
    function_mapping : dict, optional
        {legacy function module path: new path} of the renamed modules
        (default: function_module_mapping())
    """

    def __init__(self, gen_dict, function_mapping=None):
        self.class_modules = {}  # legacy class name -> new module path
        self.module_classes = {}  # new module path -> legacy class name
        for name in gen_dict:
            module = f"{class_subpackage(name, gen_dict)}.{class_module_name(name)}"
            self.class_modules[name] = module
            self.module_classes[module] = name
        mapping = function_mapping if function_mapping is not None else (
            function_module_mapping()
        )
        self.function_modules = dict(mapping)
        self.legacy_function_modules = {new: old for old, new in mapping.items()}


@lru_cache
def name_maps():
    """NameMaps of the repository (generation dictionary of the CSV files)."""
    from pyleecan.definitions import DOC_DIR
    from pyleecan.Generator.read_fct import read_all

    return NameMaps(read_all(DOC_DIR))


def to_new_names(source, package, maps=None):
    """Import the classes and the functions with their new names.

    Parameters
    ----------
    source : str
        Source with legacy names
    package : str
        Package of the module (to resolve its relative imports)
    maps : NameMaps, optional
        Default: name_maps()

    Returns
    -------
    source : str
        Source with the new names
    """
    maps = maps or name_maps()

    def translate(module, names):
        if module.startswith(LEGACY_CLASSES + "."):
            class_name = module[len(LEGACY_CLASSES) + 1 :]
            if class_name not in maps.class_modules:
                return None  # Support module (_check, _frozen...) or vendored
            new_names = [
                ast.alias(
                    name=NORMALIZATION_CLASS_NAMES.get(alias.name, alias.name),
                    asname=alias.asname
                    or (alias.name if alias.name in NORMALIZATION_CLASS_NAMES else None),
                )
                for alias in names
            ]
            return f"{NEW_CLASSES}.{maps.class_modules[class_name]}", new_names
        if module == LEGACY_FUNCTIONS or module.startswith(LEGACY_FUNCTIONS + "."):
            path = module[len(LEGACY_FUNCTIONS) + 1 :]
            if path.split(".")[0] in VENDORED_CLASS_PACKAGES:
                return f"{NEW_FUNCTIONS}.{path}", names
            new_path = maps.function_modules.get(path, path)
            new_names = []
            for alias in names:  # from pyleecan.Functions.FEMM import comp_FEMM_dict
                submodule = maps.function_modules.get(f"{path}.{alias.name}" if path else alias.name)
                if submodule is not None:
                    alias = ast.alias(
                        name=submodule.split(".")[-1], asname=alias.asname or alias.name
                    )
                new_names.append(alias)
            return ".".join(filter(None, [NEW_FUNCTIONS, new_path])), new_names
        return None

    return _translate_imports(source, package, translate)


def to_legacy_names(source, package, maps=None):
    """Import the classes and the functions with their legacy names.

    Inverse of to_new_names (used by the class generator, whose passes still
    use the legacy names: PLAN.md Step 5).
    """
    maps = maps or name_maps()
    legacy_class_names = {new: old for old, new in NORMALIZATION_CLASS_NAMES.items()}

    def translate(module, names):
        if module.startswith(NEW_CLASSES + "."):
            class_module = module[len(NEW_CLASSES) + 1 :]
            if class_module not in maps.module_classes:
                return None  # Support module or vendored
            legacy_names = []
            for alias in names:
                name = legacy_class_names.get(alias.name, alias.name)
                asname = None if alias.asname == name else alias.asname
                legacy_names.append(ast.alias(name=name, asname=asname))
            return f"{LEGACY_CLASSES}.{maps.module_classes[class_module]}", legacy_names
        if module == NEW_FUNCTIONS or module.startswith(NEW_FUNCTIONS + "."):
            path = module[len(NEW_FUNCTIONS) + 1 :]
            if path.split(".")[0] in VENDORED_CLASS_PACKAGES:
                return f"{LEGACY_FUNCTIONS}.{path}", names
            legacy_path = maps.legacy_function_modules.get(path, path)
            legacy_names = []
            for alias in names:
                submodule = maps.legacy_function_modules.get(
                    f"{path}.{alias.name}" if path else alias.name
                )
                if submodule is not None:
                    name = submodule.split(".")[-1]
                    alias = ast.alias(
                        name=name, asname=None if alias.asname == name else alias.asname
                    )
                legacy_names.append(alias)
            return ".".join(filter(None, [LEGACY_FUNCTIONS, legacy_path])), legacy_names
        return None

    return _translate_imports(source, package, translate)


def _translate_imports(source, package, translate):
    """Apply translate(absolute module, aliases) -> (module, aliases) | None."""
    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == 10:  # newline
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom) or (not node.module and not node.level):
            continue
        absolute = (
            resolve_name("." * node.level + (node.module or ""), package)
            if node.level
            else node.module
        )
        translated = translate(absolute, node.names)
        if translated is None:
            continue
        new_module, new_names = translated
        if node.level:
            package_parts = package.split(".")
            target_parts = new_module.split(".")
            common = 0
            while (
                common < len(package_parts)
                and common < len(target_parts)
                and package_parts[common] == target_parts[common]
            ):
                common += 1
            replacement = ast.ImportFrom(
                module=".".join(target_parts[common:]) or None,
                names=new_names,
                level=len(package_parts) - common + 1,
            )
        else:
            replacement = ast.ImportFrom(module=new_module, names=new_names, level=0)
        if ast.dump(replacement) == ast.dump(
            ast.ImportFrom(module=node.module, names=node.names, level=node.level)
        ):
            continue  # Unchanged: keep the source text
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")
