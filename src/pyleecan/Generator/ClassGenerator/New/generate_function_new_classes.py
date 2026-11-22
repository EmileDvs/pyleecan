"""Generate Functions_new from Functions without modifying the legacy package.

Run ``python -m pyleecan.Generator.ClassGenerator.New.generate_function_new_classes``
after generating Classes_new. Existing generated copies are overwritten. Legacy
load/save compatibility and unsupported dynamic imports are reported for review.
Use ``--import-style absolute`` for absolute Pyleecan imports; relative is the default.
Selected function exceptions are imported directly from classes_common.errors;
regenerate the classes first when those shared definitions change.

Experimental adaptations are implemented as targeted source transformations
here. Changes made only in Functions_new are overwritten on regeneration.
"""

import argparse
import ast
import re
import shutil
import subprocess
import tokenize
from functools import cache
from importlib.util import resolve_name
from pathlib import Path

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.classes_common.class_lookup import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator.ClassGenerator.New.class_generator import VENDORED_CLASS_PACKAGES, _format_source_with_ruff, _static_local_class_imports, class_module_name, common_dir, generated_module_paths, relocate_class_imports
from pyleecan.Generator.ClassGenerator.New.modernize import _keyword_geometry_calls, _replace_empty_containers
from pyleecan.Generator.ClassGenerator.New.legacy_fixes import (
    FUNCTION_LEGACY_FIXES,
    apply_fixes,
)
from pyleecan.Generator.ClassGenerator.New.function_module_names import (
    RULE_FUNCTIONS_FOLDER,
    function_module_mapping,
    function_module_name,
    redirect_function_module_imports,
    rename_rule_self,
)
from pyleecan.Generator.ClassGenerator.New.femm_object import (
    INTERFACE_OBJECTS,
    femm_alias_source,
    femm_modules,
    femm_object_source,
    femm_signatures,
    redirect_femm_calls,
)
from pyleecan.Generator.ClassGenerator.New.moved_functions import (
    DEPRECATED_MODULES,
    MERGED_MODULES,
    MOVED_FUNCTIONS,
    MOVED_MODULES,
    REMOVED_FUNCTION_ALIASES,
    alias_source,
    deprecate_source,
    merged_alias_source,
    merged_location,
    merged_module_source,
    moved_module_alias_source,
    redirect_moved_calls,
    redirect_moved_modules,
)
from pyleecan.Generator.read_fct import read_all
from pyleecan.Generator.ClassGenerator.New.modernize import (
    _function_import_style,
    _redirect_shared_error_imports,
    shared_error_names,
)

HAND_WRITTEN_FUNCTION_MODULES = frozenset(
    {
        # Step 12 freeze (decided 2026-11-22): the modules reading the parent
        # links, refactored by hand in Steps 13-17
        "check_parent.py",
        "get_logger.py",
        "FEMM/femm_pyleecan.py",
    }
)
"""Modules of Functions_new written by hand (paths in Functions_new): the
generator neither writes nor removes them; it writes the other modules and
the deprecated aliases"""

SKIPPED_FUNCTION_MODULES = {
    Path("load_switch.py"): (
        "registry of the legacy classes (from Classes.import_all import *), imported "
        "by no new module: the class lookup of each backend replaces it"
    ),
    Path("copy.py"): (
        "unused legacy function (copy objects through init_dict): the new classes "
        "use model_copy (or the legacy copy)"
    ),
}
"""Legacy Functions modules that are not copied in Functions_new (with the reason)"""

FUNCTION_ERRORS = {
    "Converter.Utils.ConvertionError": {"ConvertionError": "ConvertionError"},
    "Converter.Utils.EquivalentError": {"EquivalentError": "EquivalentError"},
    "FEMM.draw_FEMM": {"FEMMError": "FEMMError"},
    "Geometry.create_surface": {"SurfaceError": "SurfaceError"},
    "Geometry.merge_notch_list": {"NotchError": "NotchError"},
    "GMSH": {"InputError": "GMSHInputError"},
    "Load.load_json": {"LoadMissingFileError": "LoadMissingFileError"},
    "Load.retrocompatibility": {"RetroCompatibilityError": "RetroCompatibilityError"},
    "load": {
        "LoadMissingFolderError": "LoadMissingFolderError",
        "LoadWrongDictClassError": "LoadWrongDictClassError",
        "LoadWrongTypeError": "LoadWrongTypeError",
        "LoadSwitchError": "LoadSwitchError",
    },
    "path_tools": {"FileError": "FileError", "ImportError": "PathImportError"},
    "save": {"FormatError": "FormatError"},
    "SciDataTool": {
        "FTError": "FTError",
        "AxisError": "AxisError",
        "UnitError": "UnitError",
        "NormError": "NormError",
    },
    "Structural.conversions": {"DimError": "DimError"},
}


def _redirect_function_errors(source, path, relative_path, class_dir):
    """Replace selected definitions with shared imports only where used."""
    parts = list(relative_path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    errors = FUNCTION_ERRORS.get(".".join(parts))
    if not errors:
        return source
    tree = ast.parse(source, filename=str(path))
    definitions = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }
    missing = set(errors) - definitions.keys()
    if missing:
        raise ValueError(
            f"{path}: missing function exceptions: {', '.join(sorted(missing))}"
        )
    error_path = Path(common_dir(str(class_dir))) / "errors.py"
    if not error_path.is_file():
        raise FileNotFoundError(
            f"Shared exceptions not generated: {error_path}; generate classes first"
        )
    with tokenize.open(error_path) as error_file:
        shared = {
            node.name: node
            for node in ast.parse(error_file.read(), filename=str(error_path)).body
            if isinstance(node, ast.ClassDef)
        }
    for name, shared_name in errors.items():
        node = definitions[name]
        shared_node = shared.get(shared_name)
        if shared_node is None:
            raise ValueError(f"{error_path}: missing {shared_name}; regenerate classes")
        expected_bases = [
            errors.get(base.id, base.id) if isinstance(base, ast.Name) else None
            for base in node.bases
        ]
        if expected_bases != [
            base.id if isinstance(base, ast.Name) else None for base in shared_node.bases
        ]:
            raise ValueError(
                f"{error_path}: incompatible {shared_name}; regenerate classes"
            )
        if node.decorator_list:
            raise ValueError(f"{path}:{node.lineno}: decorated exception {name}")
    used = {
        node.id
        for item in tree.body
        if item not in (definitions[name] for name in errors)
        for node in ast.walk(item)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    lines = source.splitlines(keepends=True)
    imports = []
    for name, shared_name in sorted(
        errors.items(), key=lambda item: definitions[item[0]].lineno, reverse=True
    ):
        node = definitions[name]
        alias = f" as {name}" if name != shared_name else ""
        if name in used:
            imports.append(f"from pyleecan.Classes_new._error import {shared_name}{alias}\n")
        lines[node.lineno - 1 : node.end_lineno] = []
    if imports:
        header = tree.body[0].lineno - 1
        has_docstring = False
        for node in tree.body:
            if (
                isinstance(node, ast.Expr)
                and not has_docstring
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ) or (isinstance(node, ast.ImportFrom) and node.module == "__future__"):
                header = node.end_lineno
                has_docstring = True
            else:
                break
        lines[header:header] = ["".join(reversed(imports)) + "\n"]
    return "".join(lines)


def _format_function_source(source, path):
    """Apply the same import styles and Ruff formatting as generated classes."""
    from .modernize import remove_coding_declaration, remove_python2_branches  # Shared with the methods

    source = remove_coding_declaration(source)
    source = remove_python2_branches(source)
    source = _replace_empty_containers(source, include_tuple=True)
    from .modernize import apply_import_styles  # Shared with the methods

    source = apply_import_styles(source)
    result = subprocess.run(
        ["ruff", "check", "--select", "I001", "--fix", "--quiet",
         "--stdin-filename", str(path), "-"],
        input=source, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Ruff could not organize imports in {path}: {result.stderr.strip()}")
    return _format_source_with_ruff(result.stdout, str(path))


def _adapt_retrocompatibility(source, path):
    """Apply the versioned normalization migration to the legacy source."""
    tree = ast.parse(source, filename=str(path))
    lines = source.splitlines(keepends=True)

    def unique_node(predicate, description):
        matches = [node for node in tree.body if predicate(node)]
        if len(matches) != 1:
            raise ValueError(f"{path}: expected exactly one {description}")
        return matches[0]

    def function(name):
        return unique_node(
            lambda node: isinstance(node, ast.FunctionDef) and node.name == name,
            f"function {name}",
        )

    existing_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    }
    if "NORMALIZATION_CLASS_NAMES" in existing_names:
        raise ValueError(f"{path}: normalization name mapping already exists")
    search = function("_search_and_update")
    if (
        len(search.body) < 2
        or not isinstance(search.body[0], ast.Expr)
        or not isinstance(search.body[0].value, ast.Constant)
        or not isinstance(search.body[0].value.value, str)
        or not isinstance(search.body[1], ast.If)
    ):
        raise ValueError(f"{path}: unexpected _search_and_update structure")
    versions = unique_node(
        lambda node: isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "OBJECT_VERSION_DICT"
        and isinstance(node.value, ast.Dict),
        "OBJECT_VERSION_DICT",
    )
    if any(
        isinstance(key, ast.Constant) and key.value == "Normalization"
        for key in versions.value.keys
    ):
        raise ValueError(f"{path}: Normalization version already exists")
    if lines[versions.end_lineno - 1].strip() != "}":
        raise ValueError(f"{path}: unexpected OBJECT_VERSION_DICT layout")
    mapping_source = repr(NORMALIZATION_CLASS_NAMES)
    conversion = (
        f"NORMALIZATION_CLASS_NAMES = {mapping_source}\n\n\n"
        'Normalization_VERSION = "1.5.2"\n\n\n'
        "def convert_normalization(init_dict):\n"
        '    """Update an old normalization class name in place."""\n'
        '    class_name = init_dict.get("__class__")\n'
        "    if class_name in NORMALIZATION_CLASS_NAMES:\n"
        '        init_dict["__class__"] = NORMALIZATION_CLASS_NAMES[class_name]\n'
    )
    convert_init = function("convert_init_dict")
    edits = [
        (convert_init.lineno - 1, convert_init.lineno - 1, conversion + "\n\n"),
        (
            search.body[1].lineno - 1,
            search.body[1].lineno - 1,
            '    if update_dict["Normalization"]:\n        convert_normalization(obj_dict)\n',
        ),
        (
            versions.end_lineno - 1,
            versions.end_lineno - 1,
            '    "Normalization": Normalization_VERSION,\n',
        ),
    ]
    for start, end, replacement in sorted(edits, reverse=True):
        lines[start:end] = [replacement]
    return "".join(lines)


def _adapt_json_load(source, path):
    """Adapt legacy load entry points to experimental dataclass construction."""
    replacements = {
        "from .Load.import_class import import_class":
            "from pyleecan.Classes_new._import import import_class",
        'class_obj = import_class("pyleecan.Classes", obj.get("__class__"), "")':
            'class_obj = import_class(obj.get("__class__"))',
        '''if folder_path != "":
                wd = getcwd()
                chdir(folder_path)
                new_obj = class_obj(init_dict=obj)
                chdir(wd)
                return new_obj
            else:
                return class_obj(init_dict=obj)''':
            "return class_obj.from_dict(obj, base_path=folder_path)",
        "_, obj = load_json(file_path)": "file_path, obj = load_json(file_path)",
        "    return init_data(obj, file_path)\n\n\ndef load_list":
            "    if isinstance(obj, dict):\n"
            "        convert_init_dict(obj)\n"
            "    elif isinstance(obj, list):\n"
            "        for item in obj:\n"
            "            _convert_collections(item)\n"
            "    return init_data(obj, file_path)\n\n\ndef load_list",
        "def load_list(file_path):":
            "def _convert_collections(obj):\n"
            "    if isinstance(obj, dict):\n"
            "        convert_init_dict(obj)\n"
            "    elif isinstance(obj, list):\n"
            "        for item in obj:\n"
            "            _convert_collections(item)\n\n\n"
            "def load_list(file_path):",
        'Material = import_class("pyleecan.Classes", "Material")':
            'Material = import_class("Material")',
    }
    for old, new in replacements.items():
        if source.count(old) != 1:
            raise ValueError(f"{path}: unexpected JSON loader source: {old[:60]}")
        source = source.replace(old, new, 1)
    return source


def _adapt_json_retrocompatibility(source, path):
    """Redirect compatibility constructors and make root conversions possible."""
    tree = ast.parse(source, filename=str(path))
    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == 10:
            offsets.append(index + 1)
    edits = []

    def replace(node, text):
        edits.append((
            offsets[node.lineno - 1] + node.col_offset,
            offsets[node.end_lineno - 1] + node.end_col_offset,
            text.encode("utf-8"),
        ))

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and (node.level, node.module)
            in {(1, "import_class"), (3, "Functions.Load.import_class")}
        ):
            replace(node, "from pyleecan.Classes_new._import import import_class")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "import_class"
            and len(node.args) == 2
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "pyleecan.Classes"
        ):
            replace(node, f"import_class({ast.unparse(node.args[1])})")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and not node.args
            and len(node.keywords) == 1
            and node.keywords[0].arg == "init_dict"
        ):
            replace(node, f"{node.func.id}.from_dict({ast.unparse(node.keywords[0].value)})")
        elif (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Subscript)
            and ast.unparse(node.targets[0]) == "parent[parent_index]"
            and isinstance(node.value, ast.Call)
        ):
            value = ast.unparse(node.value)
            replace(
                node,
                f"_converted = {value}\n"
                + " " * node.col_offset
                + "if not isinstance(_converted, dict):\n"
                + " " * (node.col_offset + 4)
                + "_converted = _converted.as_dict()\n"
                + " " * node.col_offset
                + "if _converted is not obj_dict:\n"
                + " " * (node.col_offset + 4)
                + "obj_dict.clear()\n"
                + " " * (node.col_offset + 4)
                + "obj_dict.update(_converted)",
            )
    for start, end, text in sorted(edits, reverse=True):
        data = data[:start] + text + data[end:]
    source = data.decode("utf-8")
    replacements = {
        "            parent is not None\n            and \"slot\" in parent.keys()":
            "            isinstance(parent, dict)\n            and \"slot\" in parent.keys()",
        "        rename_varparam(obj_dict)": '        obj_dict["__class__"] = "VarParamSweep"',
        "    else:\n        # walk through the dict\n": "    # walk through the dict\n",
        'return len(obj_dict["surf_list"][0]["label"].split("_")) > 3':
            'return bool(obj_dict.get("surf_list")) and len(obj_dict["surf_list"][0]["label"].split("_")) > 3',
        'if isinstance(meshsolution_dict_new["mesh"], list):':
            'if isinstance(meshsolution_dict_new.get("mesh"), list):',
        "    class_obj = Class_obj.from_dict(obj_dict_new)":
            "    class_obj = obj_dict_new",
        "    class_obj.OP = OP\n    return class_obj":
            '    class_obj["OP"] = OP.as_dict()\n    return class_obj',
    }
    for old, new in replacements.items():
        if source.count(old) != 1:
            raise ValueError(f"{path}: unexpected retrocompatibility source: {old[:60]}")
        source = source.replace(old, new, 1)
    class_returns = {
        "HoleUD": ("hole_dict_new", "HoleUD"),
        "Winding": ("wind_dict_new", "Winding"),
        "Winding_class": ("wind_dict_new", None),
        "VarParamSweep": ("varparam_dict_new", "VarParamSweep"),
        "OptiConstraint": ("opticonstraint_dict_new", "OptiConstraint"),
        "OptiDesignVarSet": ("optidesignvar_dict_new", "OptiDesignVarSet"),
        "OptiDesignVarInterval": ("optidesignvar_dict_new", "OptiDesignVarInterval"),
        "MeshSolution": ("meshsolution_dict_new", "MeshSolution"),
    }
    for class_name, (variable, serialized_name) in class_returns.items():
        old = f"return {class_name}.from_dict({variable})"
        if old not in source:
            raise ValueError(f"{path}: missing compatibility return: {old}")
        if serialized_name is None:
            replacement = f"return {variable}"
        else:
            replacement = f'return {{**{variable}, "__class__": "{serialized_name}"}}'
        source = source.replace(old, replacement)
    for name in ("Class_obj", *class_returns):
        source = re.sub(
            rf"(?m)^[ \t]*{name} = import_class\([^\n]*\)\n", "", source
        )
    start = source.index("    # walk through the dict\n")
    end = source.index("\n\n############################################", start)
    source = (
        source[:start]
        + "    def visit(value, parent, index):\n"
        + "        if isinstance(value, dict):\n"
        + "            _search_and_update(value, parent, index, update_dict)\n"
        + "        elif isinstance(value, list):\n"
        + "            for index, item in enumerate(value):\n"
        + "                visit(item, value, index)\n\n"
        + "    for key, value in obj_dict.items():\n"
        + "        visit(value, obj_dict, key)\n"
        + source[end:]
    )
    return source


LEGACY_CLASS_REPLACEMENTS = {
    ("pyleecan.Classes._frozen", "FrozenClass"): (
        "pyleecan.classes_common.base",
        "PyleecanBase",
    ),
    # The loader error (Load/import_class.py): the shared one
    ("pyleecan.Classes._check", "InitUnKnowClassError"): (
        "pyleecan.classes_common.errors",
        "InitUnKnowClassError",
    ),
}
"""Legacy class support imports replaced by their equivalent, independent of the
class implementation (marker base of the dataclass and pydantic bases)"""


def _legacy_class_replacements(tree, package):
    """Map the local names of replaced legacy classes to their new names.

    Only the names imported without alias are renamed in the module body.
    """
    renamed = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        if node.level:
            module = resolve_name("." * node.level + module, package)
        for alias in node.names:
            target = LEGACY_CLASS_REPLACEMENTS.get((module, alias.name))
            if target is not None and alias.asname is None:
                renamed[alias.name] = target[1]
    return renamed


@cache
def _class_gen_dict():
    """Class information of the legacy CSVs (constructor arguments)."""
    return read_all(DOC_DIR)


def _static_function_class_imports(source, class_dir):
    """Replace the local loads of known classes by static local imports.

    ``X = import_class("Name")`` in a function becomes
    ``from pyleecan.Classes_new.name import Name as X`` when the module of the
    class exists in class_dir; import_class is kept for the runtime names.
    """
    names = {
        node.args[0].value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
        and node.args[0].value.isidentifier()
    }
    modules = {
        name: class_module_name(name)
        for name in names
        if class_module_name(name) in generated_module_paths(class_dir)
    }
    if not modules:
        return source
    return _static_local_class_imports(source, "pyleecan", {}, None, modules=modules)


def _class_dict_getters(tree, package):
    """Names bound to the legacy ``pyleecan.Classes.get_class_dict`` function.

    Their calls are replaced by ``ClassInfo().get_dict()`` which builds the
    class information from the generated dataclasses (no _class_dict.json).
    """
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = resolve_name("." * node.level + module, package)
            if module == "pyleecan.Classes":
                names.update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name == "get_class_dict"
                )
    return names


def _rewrite_source(source, path, relative_path, class_dir):
    """Redirect supported imports and report legacy references needing review."""
    tree = ast.parse(source, filename=str(path))
    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == 10:
            offsets.append(index + 1)

    def offset(line, column):
        return offsets[line - 1] + column

    package_parts = ["pyleecan", "Functions"] + list(relative_path.parts[:-1])
    package = ".".join(package_parts)
    replacements = []
    issues = []
    deferred = relative_path.parts[0] in {"Load", "Save"} or relative_path.name in {
        "load.py",
        "save.py",
        "load_switch.py",
    }
    dynamic_assignments = {}
    if not deferred:
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "import_class"
                and len(node.value.args) == 2
                and all(isinstance(arg, ast.Constant) for arg in node.value.args)
                and node.value.args[0].value == "pyleecan.Classes"
                and isinstance(node.value.args[1].value, str)
            ):
                continue
            name = node.value.args[1].value
            if class_module_name(name) in generated_module_paths(class_dir):
                dynamic_assignments[node] = name
    class_dict_getters = _class_dict_getters(tree, package)
    renamed_classes = _legacy_class_replacements(tree, package)
    converted_calls = {id(node.value.func) for node in dynamic_assignments}
    remaining_loader_uses = any(
        isinstance(node, ast.Name)
        and node.id == "import_class"
        and isinstance(node.ctx, ast.Load)
        and id(node) not in converted_calls
        for node in ast.walk(tree)
    )
    for node in ast.walk(tree):
        if node in dynamic_assignments:
            name = dynamic_assignments[node]
            target = node.targets[0].id
            imported_name = NORMALIZATION_CLASS_NAMES.get(name, name)
            replacement = ast.ImportFrom(
                module="pyleecan.Classes_new." + class_module_name(name),
                names=[
                    ast.alias(
                        name=imported_name,
                        asname=target if target != imported_name else None,
                    )
                ],
                level=0,
            )
            start = offset(node.lineno, node.col_offset)
            end = offset(node.end_lineno, node.end_col_offset)
            replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = resolve_name("." * node.level + module, package)
            if (
                dynamic_assignments
                and not remaining_loader_uses
                and module == "pyleecan.Functions.Load.import_class"
                and len(node.names) == 1
                and node.names[0].name == "import_class"
                and node.names[0].asname is None
            ):
                start = offset(node.lineno, node.col_offset)
                end = offset(node.end_lineno, node.end_col_offset)
                replacements.append((start, end, b""))
                continue
            replaced_aliases = [
                alias
                for alias in node.names
                if (module, alias.name) in LEGACY_CLASS_REPLACEMENTS
            ]
            if replaced_aliases:
                imports = [
                    ast.ImportFrom(
                        module=LEGACY_CLASS_REPLACEMENTS[(module, alias.name)][0],
                        names=[
                            ast.alias(
                                name=LEGACY_CLASS_REPLACEMENTS[(module, alias.name)][1],
                                asname=alias.asname,
                            )
                        ],
                        level=0,
                    )
                    for alias in replaced_aliases
                ]
                others = [alias for alias in node.names if alias not in replaced_aliases]
                if others:
                    issues.append((node.lineno, f"legacy import: {module}"))
                    imports.append(
                        ast.ImportFrom(module=node.module, names=others, level=node.level)
                    )
                start = offset(node.lineno, node.col_offset)
                end = offset(node.end_lineno, node.end_col_offset)
                replacement = ("\n" + " " * node.col_offset).join(
                    ast.unparse(import_node) for import_node in imports
                )
                replacements.append((start, end, replacement.encode("utf-8")))
                continue
            if module == "pyleecan.Classes" and any(
                alias.name == "get_class_dict" for alias in node.names
            ):
                # The class dict is built from the dataclasses by ClassInfo
                imports = [
                    ast.ImportFrom(
                        module="pyleecan.Classes_new._class_info",
                        names=[ast.alias(name="ClassInfo")],
                        level=0,
                    )
                ]
                others = [alias for alias in node.names if alias.name != "get_class_dict"]
                if others:
                    issues.append((node.lineno, f"legacy import: {module}"))
                    imports.append(
                        ast.ImportFrom(module=node.module, names=others, level=node.level)
                    )
                start = offset(node.lineno, node.col_offset)
                end = offset(node.end_lineno, node.end_col_offset)
                replacement = ("\n" + " " * node.col_offset).join(
                    ast.unparse(import_node) for import_node in imports
                )
                replacements.append((start, end, replacement.encode("utf-8")))
                continue
            if module == "pyleecan.Classes" or module.startswith("pyleecan.Classes."):
                name = module.removeprefix("pyleecan.Classes.")
                if name.split(".")[0] in VENDORED_CLASS_PACKAGES:
                    module_path = class_dir.joinpath(*name.split("."))
                    if not module_path.with_suffix(".py").is_file() and not (
                        module_path / "__init__.py"
                    ).is_file():
                        issues.append((node.lineno, f"legacy import: {module}"))
                        continue
                    replacement = ast.ImportFrom(
                        module="pyleecan.Classes_new." + name,
                        names=node.names,
                        level=0,
                    )
                elif (
                    module == "pyleecan.Classes"
                    or "." in name
                    or name.startswith("_")
                    or class_module_name(name) not in generated_module_paths(class_dir)
                    or any(alias.name == "*" for alias in node.names)
                ):
                    issues.append((node.lineno, f"legacy import: {module}"))
                    continue
                else:
                    aliases = []
                    for alias in node.names:
                        renamed = NORMALIZATION_CLASS_NAMES.get(alias.name, alias.name)
                        binding = alias.asname or (
                            alias.name if renamed != alias.name else None
                        )
                        aliases.append(ast.alias(name=renamed, asname=binding))
                    replacement = ast.ImportFrom(
                        module="pyleecan.Classes_new." + class_module_name(name),
                        names=aliases,
                        level=0,
                    )
            elif not node.level and (
                module == "pyleecan.Functions"
                or module.startswith("pyleecan.Functions.")
            ):
                replacement = ast.ImportFrom(
                    module=module.replace(
                        "pyleecan.Functions", "pyleecan.Functions_new", 1
                    ),
                    names=node.names,
                    level=0,
                )
            elif (
                node.level
                and (
                    module == "pyleecan.Functions"
                    or module.startswith("pyleecan.Functions.")
                )
                and (node.module or "").startswith("Functions")
            ):
                replacement = ast.ImportFrom(
                    module=node.module.replace("Functions", "Functions_new", 1),
                    names=node.names,
                    level=node.level,
                )
            else:
                continue
            start = offset(node.lineno, node.col_offset)
            end = offset(node.end_lineno, node.end_col_offset)
            replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(("pyleecan.Classes", "pyleecan.Functions")):
                    issues.append(
                        (node.lineno, f"import requires review: {alias.name}")
                    )
        elif isinstance(node, ast.Call):
            if any(node is assignment.value for assignment in dynamic_assignments):
                continue
            if (
                isinstance(node.func, ast.Name)
                and node.func.id in class_dict_getters
                and not node.args
                and not node.keywords
            ):
                start = offset(node.lineno, node.col_offset)
                end = offset(node.end_lineno, node.end_col_offset)
                replacements.append((start, end, b"ClassInfo().get_dict()"))
                continue
            if isinstance(node.func, ast.Name) and node.func.id == "import_class":
                issues.append((node.lineno, "dynamic class loader requires review"))
            elif any(
                isinstance(arg, ast.Constant)
                and isinstance(arg.value, str)
                and re.search(r"\bpyleecan\.(Classes|Functions)\b", arg.value)
                for arg in node.args
            ):
                issues.append((node.lineno, "dynamic legacy package reference"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in renamed_classes:
            start = offset(node.lineno, node.col_offset)
            end = offset(node.end_lineno, node.end_col_offset)
            replacements.append(
                (start, end, renamed_classes[node.id].encode("utf-8"))
            )
    for start, end, replacement in sorted(replacements, reverse=True):
        data = data[:start] + replacement + data[end:]
    rewritten = data.decode("utf-8")
    ast.parse(rewritten, filename=str(path))
    return rewritten, sorted(issues)


def generate_functions(
    source_dir=None,
    output_dir=None,
    class_dir=None,
    import_style="relative",
    hand_written=None,
):
    """Copy the complete function tree and return unresolved legacy references.

    hand_written: modules of output_dir edited by hand, kept (default:
    HAND_WRITTEN_FUNCTION_MODULES for the Functions_new of the repository,
    none for another output_dir).
    """
    if import_style not in ("relative", "absolute"):
        raise ValueError("import_style must be 'relative' or 'absolute'")
    root = Path(MAIN_DIR)
    source_dir = Path(source_dir) if source_dir is not None else root / "Functions"
    if hand_written is None:
        hand_written = HAND_WRITTEN_FUNCTION_MODULES if output_dir is None else ()
    output_dir = Path(output_dir) if output_dir is not None else root / "Functions_new"
    hand_written = frozenset(hand_written)
    missing = [name for name in sorted(hand_written) if not (output_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Hand-written function modules not found: {missing}")
    class_dir = Path(class_dir) if class_dir is not None else root / "Classes_new"
    for directory in (source_dir, class_dir):
        if not directory.is_dir():
            raise FileNotFoundError(f"Required directory does not exist: {directory}")
    if (
        source_dir.resolve() == output_dir.resolve()
        or source_dir.resolve() in output_dir.resolve().parents
        or output_dir.resolve() in source_dir.resolve().parents
    ):
        raise ValueError("Source and output function trees must be separate")

    issues = []
    generated = set()
    module_mapping = function_module_mapping(source_dir)
    generated_module_paths.cache_clear()
    class_module_paths = generated_module_paths(class_dir)
    # Legacy modules, then the aliases of the modules deleted from legacy
    # (a merge target that is also one of its legacy modules: written by the
    # merge, the legacy module is not copied)
    merge_targets = {
        source_dir.joinpath(*module.split(".")).with_suffix(".py") for module in MERGED_MODULES
    }
    entries = [
        (path, None)
        for path in sorted(source_dir.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path not in merge_targets
    ]
    entries += [
        (source_dir.joinpath(*module.split(".")).with_suffix(".py"), alias)
        for module, alias in sorted(REMOVED_FUNCTION_ALIASES.items())
        if not source_dir.joinpath(*module.split(".")).with_suffix(".py").exists()
        and source_dir.joinpath(*module.split(".")[:-1]).is_dir()
    ]

    # The FEMM interface object, from the legacy FEMM modules (femm_object.py)
    interface_modules = {
        spec: femm_modules(source_dir, spec)
        if source_dir.joinpath(*spec.package.split(".")).is_dir()
        else {}
        for spec in INTERFACE_OBJECTS
    }
    interface_signatures = {
        spec: femm_signatures(modules, spec) for spec, modules in interface_modules.items()
    }
    interface_errors = {
        spec: {
            module[len(spec.package) + 1 :]: set(errors)
            for module, errors in FUNCTION_ERRORS.items()
            if module.startswith(spec.package + ".")
        }
        for spec in INTERFACE_OBJECTS
    }
    for spec, modules in interface_modules.items():
        if modules:
            entries.append(
                (
                    source_dir.joinpath(*spec.package.split("."), spec.module + ".py"),
                    femm_object_source(modules, interface_errors[spec], spec),
                )
            )

    # Merged modules (MERGED_MODULES): written from their legacy modules
    def read_legacy(module):
        with tokenize.open(source_dir.joinpath(*module.split(".")).with_suffix(".py")) as file:
            return file.read()

    entries += [
        (
            source_dir.joinpath(*module.split(".")).with_suffix(".py"),
            merged_module_source(module, read_legacy),
        )
        for module, spec in sorted(MERGED_MODULES.items())
        if all(
            source_dir.joinpath(*legacy.split(".")).with_suffix(".py").exists()
            for legacy, _ in spec["sources"]
        )
    ]
    # Moved modules (MOVED_MODULES): the module at its new path, a deprecated
    # module re-exporting its names at the legacy path
    moved_module_paths = {
        source_dir.joinpath(*module.split(".")).with_suffix(".py"): new
        for module, new in MOVED_MODULES.items()
    }
    entries += [
        (
            path,
            moved_module_alias_source(
                module, path.read_text(encoding="utf-8"), FUNCTION_ERRORS.get(module)
            ),
        )
        for module in sorted(MOVED_MODULES)
        if (path := source_dir.joinpath(*module.split(".")).with_suffix(".py")).exists()
    ]
    for path, removed_alias in entries:
        relative = path.relative_to(source_dir)
        output_relative = relative.with_name(function_module_name(relative.stem) + ".py") if path.suffix == ".py" else relative
        if path in moved_module_paths and removed_alias is None:
            if moved_module_paths[path].startswith("GUI_new."):
                continue  # Written by the GUI generator
            output_relative = Path(*moved_module_paths[path].split(".")).with_suffix(".py")
        destination = output_dir / output_relative
        if destination.relative_to(output_dir).as_posix() in hand_written:
            generated.add(destination)  # Edited by hand since the freeze: kept
            continue
        if relative in SKIPPED_FUNCTION_MODULES:
            # Not generated: remove a copy left by a previous generation
            destination.unlink(missing_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if removed_alias is not None:
            source, encoding = removed_alias, "utf-8"
        elif path.suffix == ".py":
            with tokenize.open(path) as source_file:
                source = source_file.read()
                encoding = source_file.encoding
        if path.suffix == ".py":
            legacy_module = ".".join(relative.with_suffix("").parts)
            if removed_alias is None and relative.as_posix() in FUNCTION_LEGACY_FIXES:
                # Fixes of the legacy bugs (legacy_fixes.py, Step 15)
                source = apply_fixes(
                    source.replace("\r\n", "\n"),
                    FUNCTION_LEGACY_FIXES[relative.as_posix()],
                    relative.as_posix(),
                )
            if removed_alias is None and legacy_module.startswith(RULE_FUNCTIONS_FOLDER + "."):
                # Complex rule functions: `self` is the RuleComplex (Step 15)
                source = rename_rule_self(source)
            moved = MOVED_FUNCTIONS.get(legacy_module)
            shared_errors_imported = (
                path in moved_module_paths and removed_alias is not None
            )  # The deprecated module of a moved module imports them
            if merged_location(legacy_module) is not None and removed_alias is None:
                # Deprecated aliases of the merged module (and of its methods)
                source = merged_alias_source(legacy_module, source)
                moved = "femm"  # Aliases: the shared errors are imported
            elif moved is not None:  # Deprecated alias of the method
                source = alias_source(legacy_module, moved, source)
                errors = FUNCTION_ERRORS.get(legacy_module)
                if errors:  # The errors of the module, from the shared ones
                    up = "." * (len(relative.parts) + 1)
                    source += (
                        f"\nfrom {up}classes_common.errors import "
                        f"{', '.join(sorted(set(errors.values())))}  # noqa: F401, E402\n"
                    )
                    shared_errors_imported = True
            elif removed_alias is None and any(
                ".".join(relative.parts[:-1]) == spec.package and relative.stem in modules
                for spec, modules in interface_modules.items()
            ):  # Deprecated aliases of the methods of an interface object
                spec = next(
                    spec
                    for spec, modules in interface_modules.items()
                    if ".".join(relative.parts[:-1]) == spec.package and relative.stem in modules
                )
                source = femm_alias_source(
                    relative.stem,
                    source,
                    interface_modules[spec],
                    interface_errors[spec],
                    spec,
                )
                moved = "femm"
            replacement = DEPRECATED_MODULES.get(".".join(relative.with_suffix("").parts))
            if replacement is not None:  # Deprecated module: its functions warn
                source = deprecate_source(source, replacement)
            if relative == Path("Load") / "retrocompatibility.py":
                source = _adapt_retrocompatibility(source, path)
                source = _adapt_json_retrocompatibility(source, path)
            elif relative == Path("load.py"):
                source = _adapt_json_load(source, path)
            if moved != "femm" and not shared_errors_imported:
                # The FEMM aliases (and the aliases with errors) import the
                # shared errors
                source = _redirect_function_errors(source, path, relative, class_dir)
            package = ".".join(["pyleecan", "Functions", *relative.parts[:-1]])
            if moved is None:  # Callers of the moved functions call the methods
                for spec in INTERFACE_OBJECTS:
                    if (".".join(relative.parts[:-1]), relative.stem) != (spec.package, spec.module):
                        source = redirect_femm_calls(
                            source, package, interface_signatures[spec], spec
                        )
                source = redirect_moved_calls(source, package)
                from .modernize import redirect_get_logger

                source = redirect_get_logger(source, package)
            # The errors of the methods too (NotImplementedYetError of the
            # Methods package): the shared ones
            source = _redirect_shared_error_imports(
                source, package, method_error_names=shared_error_names()
            )
            rewritten, found = _rewrite_source(source, path, relative, class_dir)
            if relative in (
                Path("Converter") / "Utils" / "ConvertionError.py",
                Path("Converter") / "Utils" / "EquivalentError.py",
            ):
                body = ast.parse(rewritten).body
                if body:
                    raise ValueError(f"{path}: error-only module contains other code")
                if destination.exists():
                    with tokenize.open(destination) as existing:
                        existing_tree = ast.parse(existing.read(), filename=str(destination))
                    if any(
                        not isinstance(node, ast.ImportFrom)
                        or node.module
                        not in ("pyleecan.Classes_new._error", "pyleecan.classes_common.errors")
                        for node in existing_tree.body
                    ):
                        raise ValueError(f"{destination}: refusing to remove modified module")
                    destination.unlink()
                continue
            generated_package = ".".join(
                ["pyleecan", "Functions_new", *relative.parts[:-1]]
            )
            rewritten = redirect_function_module_imports(
                rewritten, generated_package, module_mapping
            )
            rewritten = _static_function_class_imports(rewritten, class_dir)
            # Pydantic models only accept keyword arguments
            rewritten = _keyword_geometry_calls(rewritten, "pyleecan", _class_gen_dict())
            # Class modules are in sub-packages of Classes_new
            rewritten = _function_import_style(rewritten, generated_package, "absolute")
            rewritten = relocate_class_imports(
                rewritten, "pyleecan", "Classes_new", class_module_paths
            )
            # The GUI of the backend (GUI resources: set_plot_gui_icon)
            from .generate_gui_new import GUI_PACKAGES, package_redirect, redirect_imports

            rewritten = redirect_imports(
                rewritten, generated_package, package_redirect("GUI", GUI_PACKAGES["dataclass"])
            )
            if not (path in moved_module_paths and removed_alias is not None):
                rewritten = redirect_moved_modules(rewritten, generated_package)
            if path in moved_module_paths and removed_alias is None:
                # The imports are absolute here: relative from the new location
                generated_package = ".".join(
                    ["pyleecan", "Functions_new", *output_relative.parts[:-1]]
                )
            rewritten = _function_import_style(rewritten, generated_package, import_style)
            legacy_name = relative.with_suffix("").as_posix().replace("/", ".")
            if legacy_name in HINTED_FUNCTION_MODULES or (
                # The modules that stay utilities (Step 8): not the deprecated
                # aliases, not the vendored code
                removed_alias is None
                and moved is None
                and relative.parts[0] not in VENDORED_CLASS_PACKAGES
                # Split into classes_common below by text (legacy signatures)
                and relative != RETROCOMPATIBILITY_MODULE
            ):
                # Type hints drafted from the docstrings, as the methods
                from .source_names import name_maps
                from .type_hints import add_type_hints

                rewritten = add_type_hints(rewritten, generated_package, name_maps().gen_dict)
            rewritten = _format_function_source(rewritten, destination)
            if relative == RETROCOMPATIBILITY_MODULE:
                # Shared by the backends in classes_common (Step 8), this
                # module binds it to the classes of Functions_new
                common = output_dir.parent / "classes_common" / "retrocompatibility.py"
                if common.parent.is_dir():
                    common.write_text(
                        _format_function_source(
                            common_retrocompatibility_source(rewritten), common
                        ),
                        encoding="utf-8",
                        newline="",
                    )
                    rewritten = _format_function_source(
                        backend_retrocompatibility_source(rewritten), destination
                    )
            destination.write_text(rewritten, encoding=encoding, newline="")
            issues.extend((relative, line, message) for line, message in found)
        else:
            shutil.copy2(path, destination)
        generated.add(destination)
    # Static registry of the complex rule functions (Step 8)
    from .function_module_names import RULE_FUNCTIONS_MODULE, rule_functions_source

    if source_dir.joinpath("Converter", "MotorCAD").is_dir():
        registry = output_dir.joinpath(*RULE_FUNCTIONS_MODULE.split(".")).with_suffix(".py")
        registry.write_text(
            _format_function_source(
                rule_functions_source(source_dir, DEPRECATED_MODULES), registry
            ),
            encoding="utf-8",
        )
        generated.add(registry)
    remove_stale_modules(output_dir, generated)
    return issues


HINTED_FUNCTION_MODULES = {
    f"{spec.package}.{spec.module}" for spec in INTERFACE_OBJECTS
} | set(MERGED_MODULES)
"""Function modules with type hints drafted from their docstrings (the
interface objects and the merged modules of Step 8; the other utilities: Step 8
task)"""

RETROCOMPATIBILITY_MODULE = Path("Load") / "retrocompatibility.py"
"""Legacy module of the file retrocompatibility, shared in classes_common"""


def common_retrocompatibility_source(source):
    """classes_common version of the Functions_new retrocompatibility module.

    The conversions do not depend on the backend, except two of them building
    objects (OPMatrix, OPdq): ``convert_init_dict(init_dict, import_class)``
    takes the class lookup of the backend, kept for the conversion in a
    context variable (the converters keep their signatures).
    """
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    replacements = []  # (first line, last line, text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        text = None
        if node.level and module.startswith("Classes_new"):  # Backend class
            indent = " " * node.col_offset
            text = "".join(
                f'{indent}{alias.asname or alias.name} = _import_class("{alias.name}")\n'
                for alias in node.names
            )
        elif node.level == 3 and module.startswith("classes_common."):
            text = ast.unparse(
                ast.ImportFrom(module=module[len("classes_common.") :], names=node.names, level=1)
            ) + "\n"
        elif node.level == 3:  # pyleecan.<module>
            text = ast.unparse(ast.ImportFrom(module=module, names=node.names, level=2)) + "\n"
        elif node.level == 2:  # pyleecan.Functions_new.<module>
            text = ast.unparse(
                ast.ImportFrom(module="Functions_new." + module, names=node.names, level=2)
            ) + "\n"
        if text is not None:
            replacements.append((node.lineno - 1, node.end_lineno, text))
    for first, last, text in sorted(replacements, reverse=True):
        lines[first:last] = [text]
    source = "".join(lines)
    # The class lookup of the backend, for the conversion in progress
    function = next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "convert_init_dict"
    )
    lines = source.splitlines(keepends=True)
    body_start = function.body[1].lineno - 1  # After the docstring
    lines[body_start:function.end_lineno] = [
        "    token = _IMPORT_CLASS.set(import_class)\n",
        "    try:\n",
        *("    " + line if line.strip() else line for line in lines[body_start:function.end_lineno]),
        "    finally:\n",
        "        _IMPORT_CLASS.reset(token)\n",
    ]
    def_line = function.lineno - 1
    lines[def_line] = lines[def_line].replace(
        "def convert_init_dict(init_dict):", "def convert_init_dict(init_dict, import_class=None):"
    )
    source = "".join(lines)
    source = source.replace(
        "    init_dict : dict\n        The dictionnary to update\n",
        "    init_dict : dict\n        The dictionnary to update\n"
        "    import_class : function\n"
        "        Class lookup of the backend (name -> class), for the conversions\n"
        "        building objects\n",
        1,
    )
    header = (
        '"""Retrocompatibility of the pyleecan files, shared by the class backends.\n\n'
        "Written by the functions generator from Functions/Load/retrocompatibility.py\n"
        "(PLAN.md Step 8). Functions_new and Functions_pydantic bind\n"
        "convert_init_dict to their classes.\n"
        '"""\n\n'
        "from contextvars import ContextVar\n\n"
    )
    helpers = (
        '\n\n_IMPORT_CLASS = ContextVar("import_class", default=None)\n'
        '"""Class lookup of the backend during convert_init_dict"""\n\n\n'
        "def _import_class(name):\n"
        '    """Class of the backend of the conversion in progress."""\n'
        "    import_class = _IMPORT_CLASS.get()\n"
        "    if import_class is None:\n"
        "        raise RetroCompatibilityError(\n"
        '            "convert_init_dict needs the class lookup of the backend (import_class) "\n'
        '            "to convert " + name\n'
        "        )\n"
        "    return import_class(name)\n"
    )
    tree = ast.parse(source)
    last_import = max(
        node.end_lineno for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    lines = source.splitlines(keepends=True)
    lines.insert(last_import, helpers)
    return header + "".join(lines)


def backend_retrocompatibility_source(source):
    """Functions_new module: the shared retrocompatibility with the backend classes."""
    names = [
        node.name
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name != "convert_init_dict"
    ]
    names += [
        target.id
        for node in ast.parse(source).body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id.isupper()
    ]
    return (
        '"""Retrocompatibility of the pyleecan files with the classes of this backend\n'
        '(shared implementation: classes_common.retrocompatibility)."""\n\n'
        "from ...Classes_new._import import import_class\n"
        "from ...classes_common import retrocompatibility as _common\n"
        "from ...classes_common.retrocompatibility import (  # noqa: F401\n"
        + "".join(f"    {name},\n" for name in names)
        + ")\n\n\n"
        "def convert_init_dict(init_dict):\n"
        '    """Convert an init_dict from an old version of pyleecan to the current one\n'
        "    (modification in place)\n\n"
        "    Parameters\n"
        "    ----------\n"
        "    init_dict : dict\n"
        "        The dictionnary to update\n"
        '    """\n'
        "    _common.convert_init_dict(init_dict, import_class=import_class)\n"
    )


def remove_stale_modules(output_dir, generated):
    """Remove the modules of output_dir left by a previous generation.

    A legacy function module deleted or renamed upstream leaves its copy in
    Functions_new, the tree is not cleared (only the generated files are
    overwritten).

    Parameters
    ----------
    output_dir : Path
        Root of the generated function tree
    generated : set
        Paths written by this generation

    Returns
    -------
    removed : list
        Removed module paths
    """
    removed = []
    for path in sorted(Path(output_dir).rglob("*.py")):
        if "__pycache__" not in path.parts and path not in generated:
            path.unlink()
            removed.append(path)
    return removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-style", choices=("relative", "absolute"), default="relative")
    args = parser.parse_args()
    issues = generate_functions(import_style=args.import_style)
    print("Copied Functions to Functions_new; existing copies were overwritten.")
    if issues:
        print("Legacy references requiring manual review:")
        for path, line, message in issues:
            print(f"  {path}:{line}: {message}")


if __name__ == "__main__":
    main()
