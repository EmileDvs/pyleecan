import ast
import builtins
import io
import re
import subprocess
import tempfile
import tokenize
import warnings
from bisect import bisect_left
from functools import lru_cache
from os import listdir, makedirs
from os.path import basename, dirname, isdir, isfile, join
from pathlib import Path
from textwrap import indent

# The naming rules of the classes are defined once (classes_common)
from ....classes_common.class_lookup import NORMALIZATION_CLASS_NAMES, class_module_name
from ....Generator import PYTHON_TYPE, TAB
from ....Generator.read_fct import (
    find_import_type,
    get_value_str,
    is_dict_list_pyleecan_type,
    is_dict_pyleecan_type,
    is_list_pyleecan_type,
)
CLASS_ERROR_NAMES = {"NotImplementedYetError", "ParentMissingError"}
VENDORED_CLASS_PACKAGES = {"_smoot", "_swat_em"}
MISSING_METHOD_REASONS = {"method source file is missing", "method function is missing"}


def validate_class_module_names(gen_dict):
    """Reject ambiguous experimental output names before writing any classes."""
    modules = {}
    for class_name in gen_dict:
        module = class_module_name(class_name)
        if module in modules:
            raise ValueError(
                f"Classes {modules[module]!r} and {class_name!r} "
                f"both map to module {module!r}"
            )
        modules[module] = class_name


# Sub-packages of the generated classes (see PLAN.md, "Class sub-packages")
SUBPACKAGE_NAMES = {
    "GUIOption": "gui_option",  # GUIOption.csv package name
    "GUI_Option": "gui_option",
    "Import": "import_data",  # import is a Python keyword
}
"""Legacy package -> sub-package, when not the lowercase legacy name"""

SIMULATION_SUBPACKAGES = {
    "Drive": "electrical",
    "EEC": "electrical",
    "Electrical": "electrical",
    "Force": "force",
    "Magnetics": "magnetics",
    "Mode": "structural",
    "Structural": "structural",
}
"""Classes of the legacy Simulation package moved to their own sub-package,
with their child classes"""


BACKENDS = {"dataclass": "Classes_new", "pydantic": "Classes_pydantic"}
"""Class implementation -> class package written by the generator

- "dataclass": stdlib dataclasses (+ dacite), base ``PyleecanClass``
  (``Classes_new/_pyleecan_class.py``)
- "pydantic": pydantic models, base ``PyleecanModel``
  (``Classes_pydantic/_pyleecan_model.py``)

The generation pipeline works on ``Classes_new`` module names; the last pass
(relocate_class_imports) moves the imports to the package of the backend.
"""

ROOT_BASES = {
    "dataclass": ("_legacy_class", "LegacyClass"),
    "pydantic": ("_legacy_model", "LegacyModel"),
}
"""(module, class) of the base of the generated root classes, by backend

Phase 1: the legacy layer (LegacyClass/LegacyModel) above the target bases
(PyleecanClass/PyleecanModel). Phase 2 switches to the target bases and
deletes the legacy layer.
"""

FUNCTION_PACKAGES = {"dataclass": "Functions_new", "pydantic": "Functions_pydantic"}
"""Function package used by the classes of each backend (Functions_pydantic is
generated from Functions_new, see generate_function_pydantic.py)"""

VENDORED_SOURCE_PACKAGE = "Classes_new"
"""Package holding the vendored code (_smoot, _swat_em) for every backend"""


def backend_package(backend):
    """Class package of a backend ("dataclass" -> "Classes_new")."""
    if backend not in BACKENDS:
        raise ValueError(f"backend must be one of {sorted(BACKENDS)}: {backend!r}")
    return BACKENDS[backend]


METHODS_NEW_PACKAGE = "Methods_new"
"""Hand-written methods (PLAN.md Step 5), read instead of the legacy Methods for
the classes bootstrapped there: Methods_new/<sub-package>/<Class>/<method>.py"""


@lru_cache
def _bootstrapped_method_dirs(root):
    """{class name: (sub-package, folder)} of the classes of Methods_new."""
    methods_dir = join(root, METHODS_NEW_PACKAGE)
    dirs = {}
    if isdir(methods_dir):
        for subpackage in sorted(listdir(methods_dir)):
            sub_dir = join(methods_dir, subpackage)
            if subpackage.startswith(("_", ".")) or not isdir(sub_dir):
                continue
            for class_name in sorted(listdir(sub_dir)):
                if not class_name.startswith(("_", ".")) and isdir(join(sub_dir, class_name)):
                    dirs[class_name] = (subpackage, join(sub_dir, class_name))
    return dirs


def method_source_location(path_to_gen, class_pack, class_name):
    """Folder and package of the method modules of a class.

    The methods of a class bootstrapped in Methods_new (hand-written, see
    PLAN.md Step 5) are read there; the other ones from the legacy Methods.
    Both folders have the same depth, so the relative imports of a method
    module resolve the same way.

    Parameters
    ----------
    path_to_gen : str
        Folder of the generated class package (e.g. .../pyleecan/Classes_new)
    class_pack : str
        Legacy package of the class (e.g. "Geometry")
    class_name : str
        Name of the class

    Returns
    -------
    method_dir : str
        Folder of the method modules of the class
    package_parts : list
        Package of these modules below the software package
        (e.g. ["Methods_new", "geometry", "Segment"])
    """
    root = dirname(path_to_gen.rstrip("/\\"))
    bootstrapped = _bootstrapped_method_dirs(root)
    if class_name in bootstrapped:
        subpackage, method_dir = bootstrapped[class_name]
        return method_dir, [METHODS_NEW_PACKAGE, subpackage, class_name]
    package_parts = [part for part in (class_pack or "").split(".") if part]
    return (
        join(root, "Methods", *package_parts, class_name),
        ["Methods", *package_parts, class_name],
    )


@lru_cache
def _methods_new_maps(root):
    """Mappings between the legacy Methods and Methods_new folders of root.

    Returns ({class: legacy package}, {sub-package: legacy package},
    {legacy package: sub-package}) for the classes of Methods_new.
    """
    legacy_classes = {}
    legacy_dir = join(root, "Methods")
    if isdir(legacy_dir):
        for package in sorted(listdir(legacy_dir)):
            if isdir(join(legacy_dir, package)) and not package.startswith(("_", ".")):
                for class_name in listdir(join(legacy_dir, package)):
                    if isdir(join(legacy_dir, package, class_name)):
                        legacy_classes.setdefault(class_name, package)
    class_packages = {}
    sub_packages = {}
    package_subs = {}
    for class_name, (subpackage, _) in _bootstrapped_method_dirs(root).items():
        package = legacy_classes.get(class_name)
        if package is None:
            continue
        class_packages[class_name] = package
        sub_packages.setdefault(subpackage, package)
        package_subs.setdefault(package, subpackage)
    return class_packages, sub_packages, package_subs


def _default_root():
    from ....definitions import MAIN_DIR

    return MAIN_DIR


def _legacy_methods_module(module, root=None):
    """Legacy name of a Methods_new module, to look up the configuration tables.

    "Methods_new.machine.Skew.comp" -> "Methods.Machine.Skew.comp"; other
    module names are returned unchanged. The tables of this module
    (METHOD_IMPORT_REDIRECTS, CLASS_METHOD_HELPERS...) use the legacy names.
    """
    parts = module.split(".")
    if not parts or parts[0] != METHODS_NEW_PACKAGE or len(parts) < 2:
        return module
    class_packages, sub_packages, _ = _methods_new_maps(root or _default_root())
    if len(parts) > 2 and parts[2] in class_packages:
        return ".".join(["Methods", class_packages[parts[2]], *parts[2:]])
    if parts[1] in sub_packages:
        return ".".join(["Methods", sub_packages[parts[1]], *parts[2:]])
    return module


def _methods_location(path_to_gen, legacy_path):
    """(folder, package parts) of a legacy method path ("Output.XOutput").

    The Methods_new copy when it exists, the legacy Methods folder otherwise.
    """
    root = dirname(path_to_gen.rstrip("/\\"))
    parts = legacy_path.split(".")
    bootstrapped = _bootstrapped_method_dirs(root)
    _, _, package_subs = _methods_new_maps(root)
    if len(parts) > 1 and parts[1] in bootstrapped:
        subpackage, _ = bootstrapped[parts[1]]
        new_parts = [METHODS_NEW_PACKAGE, subpackage, *parts[1:]]
    elif len(parts) == 1 and parts[0] in package_subs:
        new_parts = [METHODS_NEW_PACKAGE, package_subs[parts[0]]]
    else:
        new_parts = ["Methods", *parts]
    return join(root, *new_parts), new_parts


def _read_method_source(path):
    """Read a method module (or method package __init__).

    The modules of Methods_new import the classes and the functions with
    their new names; the passes of this generator still use the legacy names,
    so they are translated back (source_names.to_legacy_names). This shim is
    removed when the passes are moved to the method generator (PLAN.md Step 5).
    """
    with open(path, encoding="utf-8") as source_file:
        source = source_file.read()
    parts = path.replace("\\", "/").split("/")
    if METHODS_NEW_PACKAGE in parts:
        from .source_names import to_legacy_names

        index = len(parts) - 1 - parts[::-1].index(METHODS_NEW_PACKAGE)
        package_parts = parts[index:-1]  # The package of an __init__ is its folder
        source = to_legacy_names(source, ".".join(["pyleecan", *package_parts]))
    return source


def _is_methods_module(module_name, soft_name):
    """True for a method module, legacy (Methods) or hand-written (Methods_new)."""
    return module_name.startswith(
        (f"{soft_name}.Methods.", f"{soft_name}.{METHODS_NEW_PACKAGE}.")
    )


COMMON_PACKAGE = "classes_common"
"""Package of the support shared by the class implementations"""

SHARED_SUPPORT_MODULES = {
    "_check": "check",
    "_error": "errors",
    "_femm_handler": "femm_handler",
    "_parent_types": "parent_types",
}
"""Support modules of a class package moved to COMMON_PACKAGE (old: new name)"""


def common_dir(path_to_gen):
    """Folder of COMMON_PACKAGE, next to the class package folder path_to_gen."""
    return join(dirname(path_to_gen.rstrip("/\\")), COMMON_PACKAGE)


def class_subpackage(class_name, gen_dict):
    """Name of the sub-package of a generated class (e.g. "geometry").

    Parameters
    ----------
    class_name : str
        Name of the class (CSV name)
    gen_dict : dict
        Generation dictionary (contains all the csv data)

    Returns
    -------
    subpackage : str
        Name of the sub-package of Classes_new / Classes_pydantic
    """
    package = gen_dict[class_name]["package"]
    if package == "Simulation":
        name = class_name
        while name in gen_dict:
            if name in SIMULATION_SUBPACKAGES:
                return SIMULATION_SUBPACKAGES[name]
            name = gen_dict[name]["mother"]
    subpackage = SUBPACKAGE_NAMES.get(package, package.lower())
    if not subpackage.isidentifier() or subpackage.startswith("_"):
        raise ValueError(f"Invalid sub-package {subpackage!r} for {class_name!r}")
    return subpackage


def class_module_paths(gen_dict):
    """Module path in the class package of each class module.

    Returns
    -------
    module_paths : dict
        {module name: "subpackage.module"} (e.g. {"arc_1": "geometry.arc_1"})
    """
    return {
        class_module_name(name): f"{class_subpackage(name, gen_dict)}.{class_module_name(name)}"
        for name in gen_dict
    }


def generated_module_paths(class_dir):
    """Module path of each class module generated in class_dir.

    Same rule as the runtime lookup (Classes_new._import.module_path): the class
    modules are the public modules of the public sub-packages. Used by the
    function and test generators, which run after the class generation. The
    result is cached per folder: call ``generated_module_paths.cache_clear()``
    when the classes of a folder are generated again in the same process.

    Returns
    -------
    module_paths : dict
        {module name: "subpackage.module"} (e.g. {"arc_1": "geometry.arc_1"})
    """
    return _generated_module_paths(str(Path(class_dir).resolve()))


@lru_cache
def _generated_module_paths(class_dir):
    paths = {}
    for subpackage in sorted(Path(class_dir).iterdir()):
        if (
            subpackage.is_dir()
            and not subpackage.name.startswith(("_", "."))
            and (subpackage / "__init__.py").is_file()
        ):
            for module_file in sorted(subpackage.glob("*.py")):
                if not module_file.stem.startswith("_"):
                    paths[module_file.stem] = f"{subpackage.name}.{module_file.stem}"
    return paths


generated_module_paths.cache_clear = _generated_module_paths.cache_clear


def relocate_class_imports(
    source,
    soft_name,
    class_package,
    module_paths,
    target_package=None,
    function_packages=None,
):
    """Point the absolute imports of flat class modules to their sub-package.

    ``from pyleecan.Classes_new.arc_1 import Arc1`` becomes
    ``from pyleecan.Classes_new.geometry.arc_1 import Arc1``; string constants
    naming a class module (e.g. for import_module) are updated the same way.
    The shared support modules (SHARED_SUPPORT_MODULES, e.g. ``_error``) go to
    COMMON_PACKAGE (``pyleecan.classes_common.errors``); the other support
    modules (``_import``, ``_pyleecan_class``...) and vendored packages are kept.
    Relative imports are not modified: apply the absolute style first.
    With target_package (e.g. "Classes_pydantic"), the class modules and the
    other support modules move to that package; vendored code stays in
    class_package. With function_packages (source, target), e.g.
    ("Functions_new", "Functions_pydantic"), the function imports move too
    (vendored function code stays in the source package).
    """
    prefix = f"{soft_name}.{class_package}."
    target_prefix = f"{soft_name}.{target_package or class_package}."
    function_prefix, function_target = (
        (f"{soft_name}.{function_packages[0]}.", f"{soft_name}.{function_packages[1]}.")
        if function_packages and function_packages[0] != function_packages[1]
        else (None, None)
    )

    def relocate(module):
        if function_prefix is not None and module.startswith(function_prefix):
            first = module[len(function_prefix) :].partition(".")[0]
            if first in VENDORED_CLASS_PACKAGES:
                return None
            return function_target + module[len(function_prefix) :]
        if not module.startswith(prefix):
            return None
        first, _, rest = module[len(prefix) :].partition(".")
        rest = "." + rest if rest else ""
        if first in SHARED_SUPPORT_MODULES:
            return f"{soft_name}.{COMMON_PACKAGE}.{SHARED_SUPPORT_MODULES[first]}{rest}"
        if first in module_paths:
            return target_prefix + module_paths[first] + rest
        if first in VENDORED_CLASS_PACKAGES or target_prefix == prefix:
            return None
        return target_prefix + first + rest  # other support modules (_import...)

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and not node.level and node.module:
            new_module = relocate(node.module)
            if new_module is None:
                continue
            new_node = ast.ImportFrom(module=new_module, names=node.names, level=0)
            replacement = ast.unparse(new_node)
        elif isinstance(node, ast.Import):
            if not any(relocate(alias.name) for alias in node.names):
                continue
            if any(alias.asname is None for alias in node.names):
                raise ValueError(f"Cannot relocate unaliased import: {ast.unparse(node)}")
            new_node = ast.Import(
                names=[
                    ast.alias(relocate(alias.name) or alias.name, alias.asname)
                    for alias in node.names
                ]
            )
            replacement = ast.unparse(new_node)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            new_module = relocate(node.value)
            if new_module is None:
                continue
            replacement = repr(new_module)
        else:
            continue
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, replacement.encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


METHOD_IMPORT_REDIRECTS = {
    ("Methods.Machine", "ARC_NPOINT_D"): "Machine",
    ("Methods.Machine", "LINE_NPOINT_D"): "Machine",
    ("Methods.Machine.Skew", "TYPE_SKEW_LIST"): "Skew",
    ("Methods.Elmer.Section", "File"): "Section",
    ("Methods.Elmer.Section", "Variable"): "Section",
    ("Methods.Elmer.Section", "MATC"): "Section",
    ("Methods.Simulation.Input", "CURRENT_DIR_REF"): "Input",
    ("Methods.Simulation.Input", "ROT_DIR_REF"): "Input",
    ("Methods.Simulation.Input", "PHASE_DIR_REF"): "Input",
}
CLASS_MODULE_CONSTANTS = {
    "Machine": {"ARC_NPOINT_D": 99, "LINE_NPOINT_D": 1},
    "Skew": {
        "TYPE_SKEW_LIST": ["linear", "vshape", "zig-zag", "user-defined", "function"]
    },
    "Input": {
        "ROT_DIR_REF": -1,
        "CURRENT_DIR_REF": -1,
        "PHASE_DIR_REF": -1,
    },
}
CLASS_MODULE_CONSTANT_EXPRESSIONS = {}
CLASS_BODY_CONSTANTS = {
    "SolverInputFile": {
        "MESH_FILE": repr("Mesh"),
    }
}
# Class constants shared by a class and all its daughters: they are written in
# the body of the owner class only, and the module-level definitions of the
# same names in the method modules of the owner and its daughters are replaced
# by references to the class attribute (self.NAME, or ClassName.NAME in static
# helpers). Expressions may use the previous constants of the same owner.
CLASS_SHARED_CONSTANTS = {
    "Elmer": {
        "WHITESPACE": repr(" "),
        "INDENT": "2 * WHITESPACE",
        "COMMENT": repr("! "),
        "NEWLINE": repr("\n"),
        "END": repr("End"),
    },
    "Conductor": {
        "COND_COLOR": 'config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0].copy()',
        "INS_COLOR": 'config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][1].copy()',
    },
    "Lamination": {
        "PLUS_HATCH": repr("++"),
        "MINUS_HATCH": repr(".."),
        "ROTOR_COLOR": 'config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]',
        "STATOR_COLOR": 'config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]',
    },
    "Slot": {
        "KEY_COLOR": 'config_dict["PLOT"]["COLOR_DICT"]["KEY_COLOR"]',
        "MAGNET_COLOR": 'config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]',
    },
    "Surface": {
        "PATCH_COLOR": 'config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]',
        "PATCH_COLOR_ALPHA": 'config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]',
        "PATCH_EDGE": 'config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]',
        "PATCH_EDGE_ALPHA": 'config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]',
    },
}


def _class_constants(class_name, gen_dict=None):
    """Class body constants available in a class, inherited ones included.

    Returns a dict name -> expression with the CLASS_SHARED_CONSTANTS of the
    class and of its mothers (found in gen_dict) and its CLASS_BODY_CONSTANTS.
    """
    owners = [class_name]
    while gen_dict is not None and gen_dict.get(owners[-1], {}).get("mother"):
        mother = gen_dict[owners[-1]]["mother"]
        if mother in owners:
            break
        owners.append(mother)
    constants = {}
    for owner in reversed(owners):
        constants.update(CLASS_SHARED_CONSTANTS.get(owner, {}))
    constants.update(CLASS_BODY_CONSTANTS.get(class_name, {}))
    return constants


CLASS_CONSTANT_IMPORTS = {"config_dict": "from {soft_name}.definitions import config_dict"}
"""Imports required by the names used in the class constant expressions"""


def _class_constant_imports(constants, soft_name):
    """Imports needed to evaluate class constant expressions in the class body."""
    names = {
        node.id
        for expression in constants.values()
        for node in ast.walk(ast.parse(expression, mode="eval"))
        if isinstance(node, ast.Name)
    }
    return {
        CLASS_CONSTANT_IMPORTS[name].format(soft_name=soft_name)
        for name in names
        if name in CLASS_CONSTANT_IMPORTS
    }


def _class_constant_definitions(constants):
    """Format class body constants as typed ClassVar definitions."""
    from ....definitions import config_dict

    values = {}
    lines = []
    for name, expression in constants.items():
        try:
            values[name] = eval(
                expression,
                {"__builtins__": {}},
                {"config_dict": config_dict, **values},
            )
        except Exception:  # noqa: BLE001 - only used to infer the type
            annotation = "ClassVar"
        else:
            value_type = type(values[name])
            annotation = (
                f"ClassVar[{value_type.__name__}]"
                if value_type in (bool, complex, float, int, str)
                else "ClassVar"
            )
        lines.append((name, f"{TAB}{name}: {annotation} = {expression}\n"))
    return lines


EXPERIMENTAL_GEOMETRY_CONSTANTS = {
    "ARC_NPOINT_D": ("Arc", 99),
    "LINE_NPOINT_D": ("Line", 1),
}
CLASS_METHOD_HELPERS = {
    "XOutput": {
        "_get_symbol_data_": ("Output.XOutput", "_get_symbol_data_"),
    },
    "DataDual": {
        "is_freq": ("SciDataTool.DataDual", "is_freq"),
    },
    "MagElmer": {
        "_get_BP_dict": ("Simulation.MagElmer", "_get_BP_dict"),
    },
    "StructElmer": {
        "_get_BP_dict": ("Simulation.StructElmer", "_get_BP_dict"),
        "_execute": ("Simulation.StructElmer", "_execute"),
    },
}
CLASS_STATIC_METHOD_HELPERS = {
    "DataDual": {"is_freq"},
    "MagElmer": {"_get_BP_dict"},
    "StructElmer": {"_get_BP_dict", "_execute"},
}
EXPERIMENTAL_LOCAL_METHOD_IMPORTS = {
    ("VarSimu", "set_reused_data", "Classes.ElecLUTdq", "ElecLUTdq"),
}
CLASS_MODULE_CLASS_DEFINITIONS = {
    "Section": ("Elmer.Section", ("File", "Variable", "MATC")),
    "StructElmer": ("Simulation.StructElmer", ("ElmerProcessError",)),
}
METHOD_CALL_REDIRECTS = {
    ("OptiGenAlgNsga2Deap", "Methods.Output.XOutput", "_get_symbol_data_"): (
        "self.xoutput",
        "_get_symbol_data_",
    ),
    ("MeshMat", "Methods.Mesh.MeshMat.get_element", "_check_element_name"): (
        None,
        "_check_element_name",
    ),
}
CONFIGURED_PLOT_CONSTANT_NAMES = {
    "PATCH_COLOR_ALPHA",
    "PATCH_EDGE",
    "PATCH_EDGE_ALPHA",
    "PHASE_COLORS",
    "COLORS",
    "COLORMAP",
    "COLOR_MAP",
    "FONT_NAME",
    "FONT_SIZE_TITLE",
    "FONT_SIZE_LABEL",
    "FONT_SIZE_LEGEND",
    "FONT_FAMILY_PYVISTA",
}


def _load_method_error_module(path_to_gen, module_name):
    """Load a Methods or Functions module for error-class lookup."""
    module_parts = module_name.split(".")
    if len(module_parts) < 2 or module_parts[1] not in (
        "Methods",
        METHODS_NEW_PACKAGE,
        "Functions",
    ):
        return None, None
    methods_path = join(dirname(path_to_gen), *module_parts[1:])
    module_path = methods_path + ".py"
    package_parts = module_parts[:-1]
    if not isfile(module_path):
        module_path = join(methods_path, "__init__.py")
        package_parts = module_parts
    try:
        return (
            ast.parse(_read_method_source(module_path), filename=module_path),
            package_parts,
        )
    except FileNotFoundError:
        return None, None


def _get_exception_classes(module):
    """Return exception classes declared directly in a module."""
    classes = {
        node.name: node for node in module.body if isinstance(node, ast.ClassDef)
    }

    def is_exception_class(node, visited=()):
        if node.name in visited:
            return False
        for base in node.bases:
            base_name = (
                base.id
                if isinstance(base, ast.Name)
                else base.attr
                if isinstance(base, ast.Attribute)
                else None
            )
            if base_name in {"Exception", "BaseException"} or (
                base_name is not None and "Error" in base_name
            ):
                return True
            if base_name in classes and is_exception_class(
                classes[base_name], visited + (node.name,)
            ):
                return True
        return False

    return {name: node for name, node in classes.items() if is_exception_class(node)}


def _section_module_classes(path_to_gen):
    """Read Section's non-exception helper classes from its method package."""
    path = join(_methods_location(path_to_gen, "Elmer.Section")[0], "__init__.py")
    module = ast.parse(_read_method_source(path), filename=path)
    exceptions = _get_exception_classes(module)
    return [
        node for node in module.body
        if isinstance(node, ast.ClassDef) and node.name not in exceptions
    ]


@lru_cache(maxsize=1)
def _check_error_definitions():
    """Read the legacy validation exception hierarchy for experimental output."""
    root = dirname(dirname(dirname(dirname(__file__))))
    with open(join(root, "Classes", "_check.py"), encoding="utf-8") as check_file:
        module = ast.parse(check_file.read())
    return _get_exception_classes(module)


def _get_error_class_fingerprint(
    path_to_gen, module_name, class_name, visited=()
):
    """Return the definition of an exported exception class, if available."""
    if module_name in visited:
        return None
    module, package_parts = _load_method_error_module(path_to_gen, module_name)
    if module is None:
        return None
    class_node = _get_exception_classes(module).get(class_name)
    if class_node is not None:
        return (module_name, class_name)

    for node in module.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        for alias in node.names:
            if (alias.asname or alias.name) != class_name or alias.name == "*":
                continue
            imported_module = ".".join(_get_absolute_import_module(node, package_parts))
            return _get_error_class_fingerprint(
                path_to_gen,
                imported_module,
                alias.name,
                visited + (module_name,),
            )
    return None


def _get_error_class_definitions(
    path_to_gen, module_name, class_name, visited=()
):
    """Return exception definitions and their exception bases in dependency order."""
    if module_name in visited:
        return []
    module, package_parts = _load_method_error_module(path_to_gen, module_name)
    if module is None:
        return []

    classes = {
        node.name: node for node in module.body if isinstance(node, ast.ClassDef)
    }
    imports = {}
    for node in module.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        imported_module = ".".join(_get_absolute_import_module(node, package_parts))
        for alias in node.names:
            if alias.name != "*":
                imports[alias.asname or alias.name] = (imported_module, alias.name)

    class_node = classes.get(class_name)
    if class_node is None:
        imported = imports.get(class_name)
        if imported is None:
            return []
        return _get_error_class_definitions(
            path_to_gen,
            imported[0],
            imported[1],
            visited + (module_name,),
        )
    if class_name not in _get_exception_classes(module):
        return []

    dependencies = []
    for base in class_node.bases:
        if not isinstance(base, ast.Name):
            continue
        if base.id in classes:
            dependencies.extend(
                _get_error_class_definitions(
                    path_to_gen, module_name, base.id, visited
                )
            )
        elif base.id in imports:
            imported_module, imported_name = imports[base.id]
            dependencies.extend(
                _get_error_class_definitions(
                    path_to_gen,
                    imported_module,
                    imported_name,
                    visited + (module_name,),
                    )
            )

    definition = ast.parse(ast.unparse(class_node)).body[0]
    definition.error_origin = (module_name, class_name)
    definitions = []
    seen = set()
    for dependency in dependencies + [definition]:
        existing = next(
            (node for node in definitions if node.name == dependency.name),
            None,
        )
        if existing is not None:
            if (
                existing.error_origin != dependency.error_origin
            ):
                return []
            continue
        if dependency.name not in seen:
            definitions.append(dependency)
            seen.add(dependency.name)
    return definitions


def _sort_error_class_definitions(definitions):
    """Sort available exception classes by name, after their local base classes."""
    remaining = {definition.name: definition for definition in definitions}
    dependencies = {
        name: {
            node.id
            for base in definition.bases
            for node in ast.walk(base)
            if isinstance(node, ast.Name) and node.id in remaining
        }
        for name, definition in remaining.items()
    }
    ordered = []
    while remaining:
        ready = sorted(name for name in remaining if not dependencies[name])
        if not ready:
            raise ValueError(
                "Circular exception class dependencies: "
                + ", ".join(sorted(remaining))
            )
        name = ready[0]
        ordered.append(remaining.pop(name))
        for unresolved in remaining:
            dependencies[unresolved].discard(name)
    return ordered


def _shared_error_definitions(gen_dict, path_to_gen, soft_name, class_import_graph):
    """Find the exception definitions of the method modules (all shared).

    Every method error is written once in classes_common/errors.py, for both
    class implementations (one error class per error, see PLAN.md).
    """
    from .generate_function_new_classes import FUNCTION_ERRORS

    definitions = {}
    owners = {}
    for name, info in sorted(gen_dict.items()):
        if not info.get("methods"):
            continue
        reserved = {item["name"] for item in info["constants"]}
        reserved.update(method.split(".")[-1] for method in info["methods"])
        reserved.update(item["name"] for item in info["properties"])
        # Actual generation reports inline fallback warnings for selected classes.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=r"^Could not inline ")
            prepared = _prepare_class_methods(
                path_to_gen,
                info["package"],
                name,
                info["methods"],
                soft_name,
                reserved_names=reserved,
                class_import_graph=class_import_graph,
                class_constants=_class_constants(name, gen_dict),
            )
        for definition in prepared[-1]:
            origin = definition.error_origin
            definitions[origin] = definition
            owners.setdefault(origin, set()).add(name)
    shared = {origin: definitions[origin] for origin in owners}
    if isdir(join(dirname(path_to_gen), "Functions")):
        for module, errors in FUNCTION_ERRORS.items():
            module_name = f"{soft_name}.Functions.{module}"
            for name in errors:
                found = _get_error_class_definitions(path_to_gen, module_name, name)
                if not found or found[-1].error_origin != (module_name, name):
                    raise ValueError(f"Missing function exception {module_name}.{name}")
                for definition in found:
                    shared[definition.error_origin] = definition
    return shared


def _shared_error_name(origin):
    """Return the public name of a shared exception."""
    from .generate_function_new_classes import FUNCTION_ERRORS

    parts = origin[0].split(".", 2)
    if len(parts) == 3 and parts[1] == "Functions":
        return FUNCTION_ERRORS.get(parts[2], {}).get(origin[1], origin[1])
    return "PyleecanImportError" if origin[1] == "ImportError" else origin[1]


def _write_shared_errors(path_to_gen, definitions, source_path=None):
    """Generate shared exceptions alphabetically, after their base classes."""
    source_path = source_path or path_to_gen
    dependencies = {}
    names = {}
    check_errors = _check_error_definitions()
    duplicates = set()  # Same definition in several method modules
    for origin in sorted(definitions):
        name = _shared_error_name(origin)
        if name in names:
            if ast.dump(definitions[origin]) != ast.dump(definitions[names[name]]):
                raise ValueError(
                    f"Shared exception name {name!r} has different sources: "
                    f"{names[name]!r} and {origin!r}"
                )
            duplicates.add(origin)
            continue
        if name in CLASS_ERROR_NAMES or name in check_errors:
            raise ValueError(f"Shared exception name {name!r} is already defined")
        names[name] = origin
    for origin, definition in definitions.items():
        bases = {}
        for base in definition.bases:
            if not isinstance(base, ast.Name):
                raise TypeError(f"Unsupported exception base in {origin!r}")
            resolved = _get_error_class_fingerprint(
                source_path, origin[0], base.id
            )
            if resolved is not None:
                if resolved not in definitions:
                    raise ValueError(f"Missing shared exception base {resolved!r}")
                bases[base.id] = resolved
            else:
                builtin_base = getattr(builtins, base.id, None)
                if not isinstance(builtin_base, type) or not issubclass(
                    builtin_base, BaseException
                ):
                    raise ValueError(
                        f"Unresolved exception base {base.id!r} in {origin!r}"
                    )
        dependencies[origin] = bases

    all_definitions = ast.parse(
        'class NotImplementedYetError(Exception):\n'
        '    """NotImplementedYetError"""\n\n'
        'class ParentMissingError(Exception):\n'
        '    """ParentMissingError"""\n'
    ).body
    all_definitions.extend(check_errors.values())
    for origin, source_definition in definitions.items():
        if origin in duplicates:
            continue
        definition = ast.parse(ast.unparse(source_definition)).body[0]
        definition.name = _shared_error_name(origin)
        for index, base in enumerate(definition.bases):
            if isinstance(base, ast.Name) and base.id in dependencies[origin]:
                definition.bases[index] = ast.Name(
                    id=_shared_error_name(dependencies[origin][base.id]),
                    ctx=ast.Load(),
                )
        if (
            len(definition.body) == 2
            and isinstance(definition.body[0], ast.Expr)
            and isinstance(definition.body[0].value, ast.Constant)
            and isinstance(definition.body[0].value.value, str)
            and isinstance(definition.body[1], ast.Pass)
        ):
            definition.body.pop()
        all_definitions.append(definition)
    chunks = ['"""Generated shared exception classes; do not edit by hand."""\n\n\n']
    for definition in _sort_error_class_definitions(all_definitions):
        chunks.append(ast.unparse(definition) + "\n\n\n")
    source = "".join(chunks).rstrip() + "\n"
    error_path = join(common_dir(path_to_gen), "errors.py")
    ast.parse(source, filename=error_path)
    if definitions:
        source = _format_source_with_ruff(source, error_path)
    with open(error_path, "w", encoding="utf-8") as error_file:
        error_file.write(source)


def _same_error_class_import(path_to_gen, first_identity, second_identity):
    """Check whether two imports refer to the same exception class."""
    if (
        first_identity[0] != "ImportFrom"
        or second_identity[0] != "ImportFrom"
        or first_identity[3] != second_identity[3]
        or first_identity[4] != second_identity[4]
    ):
        return False
    first_fingerprint = _get_error_class_fingerprint(
        path_to_gen, first_identity[2], first_identity[3]
    )
    return first_fingerprint is not None and first_fingerprint == (
        _get_error_class_fingerprint(
            path_to_gen, second_identity[2], second_identity[3]
        )
    )


def _rename_method_references(source, renamed_names):
    """Rename Python name references without changing comments or string literals."""
    if not renamed_names:
        return source
    tree = ast.parse(source)
    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name) or node.id not in renamed_names:
            continue
        start = line_offsets[node.lineno - 1] + node.col_offset
        end = start + len(node.id.encode("utf-8"))
        replacements.append((start, end, renamed_names[node.id].encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _qualify_local_errors(source, error_names, class_name):
    """Qualify local errors with self in instance methods and the class otherwise."""
    if not error_names:
        return source
    tree = ast.parse(source)
    instance_references = set()
    for function in tree.body:
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = function.args.posonlyargs + function.args.args
        if not args or args[0].arg != "self" or function.decorator_list:
            continue
        body_nodes = [node for statement in function.body for node in ast.walk(statement)]
        if any(
            (
                isinstance(node, ast.Name)
                and node.id == "self"
                and isinstance(node.ctx, (ast.Store, ast.Del))
            )
            or (isinstance(node, ast.arg) and node.arg == "self")
            or (isinstance(node, ast.ExceptHandler) and node.name == "self")
            for node in body_nodes
        ):
            continue
        instance_references.update(
            id(node) for node in body_nodes if isinstance(node, ast.Name)
        )

    source_bytes = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id in error_names
        ):
            owner = "self" if id(node) in instance_references else class_name
            start = offsets[node.lineno - 1] + node.col_offset
            replacements.append(
                (
                    start,
                    start + len(node.id.encode("utf-8")),
                    f"{owner}.{node.id}".encode("utf-8"),
                )
            )
    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


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


def _replace_dynamic_class_imports(source, soft_name, blocked_names=()):
    """Replace recognized module-and-class import pairs in inlined methods."""
    if set(blocked_names).intersection(
        {"__import__", "getattr", "_pyleecan_import_class", "*"}
    ):
        return source, False
    tree = ast.parse(source)
    if any(
        (isinstance(node, ast.Name) and node.id in {"__import__", "getattr"}
         and isinstance(node.ctx, (ast.Store, ast.Del)))
        or (isinstance(node, ast.arg) and node.arg in {"__import__", "getattr"})
        for node in ast.walk(tree)
    ):
        return source, False
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    names.update(node.arg for node in ast.walk(tree) if isinstance(node, ast.arg))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            bindings = {
                alias.asname
                or (
                    alias.name.split(".")[0]
                    if isinstance(node, ast.Import)
                    else alias.name
                )
                for alias in node.names
            }
            if bindings.intersection({"__import__", "getattr", "*"}):
                return source, False
            names.update(bindings)
    if "_pyleecan_import_class" in names:
        return source, False

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)

    matches = []
    for parent in ast.walk(tree):
        for _, statements in ast.iter_fields(parent):
            if not isinstance(statements, list):
                continue
            for first, second in zip(statements, statements[1:]):
                if not (
                    isinstance(first, ast.Assign)
                    and len(first.targets) == 1
                    and isinstance(first.targets[0], ast.Name)
                    and isinstance(first.value, ast.Call)
                    and isinstance(first.value.func, ast.Name)
                    and first.value.func.id == "__import__"
                    and len(first.value.args) == 1
                    and len(first.value.keywords) == 1
                    and first.value.keywords[0].arg == "fromlist"
                    and isinstance(first.value.keywords[0].value, (ast.List, ast.Tuple))
                    and len(first.value.keywords[0].value.elts) == 1
                    and isinstance(second, ast.Assign)
                    and len(second.targets) == 1
                    and isinstance(second.targets[0], ast.Name)
                    and first.end_lineno + 1 == second.lineno
                ):
                    continue
                class_expr = first.value.keywords[0].value.elts[0]
                module_expr = first.value.args[0]
                module_name = first.targets[0].id
                value = second.value
                if isinstance(value, ast.Attribute) and (
                    isinstance(value.value, ast.Name)
                    and value.value.id == module_name
                    and isinstance(class_expr, ast.Constant)
                    and value.attr == class_expr.value
                ):
                    module_ref = value.value
                elif (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Name)
                    and value.func.id == "getattr"
                    and len(value.args) == 2
                    and not value.keywords
                    and isinstance(value.args[0], ast.Name)
                    and value.args[0].id == module_name
                    and ast.dump(value.args[1]) == ast.dump(class_expr)
                ):
                    module_ref = value.args[0]
                else:
                    continue

                package_expr = None
                if isinstance(class_expr, ast.Constant) and isinstance(
                    class_expr.value, str
                ):
                    suffix = ".Classes." + class_expr.value
                    if isinstance(module_expr, ast.Constant) and isinstance(
                        module_expr.value, str
                    ) and module_expr.value == soft_name + suffix:
                        package_expr = repr(soft_name + ".Classes")
                    elif (
                        isinstance(module_expr, ast.BinOp)
                        and isinstance(module_expr.op, ast.Add)
                        and isinstance(module_expr.left, ast.Name)
                        and module_expr.left.id == "PACKAGE_NAME"
                        and isinstance(module_expr.right, ast.Constant)
                        and module_expr.right.value == suffix
                    ):
                        package_expr = 'PACKAGE_NAME + ".Classes"'
                elif (
                    isinstance(class_expr, ast.Name)
                    and isinstance(module_expr, ast.BinOp)
                    and isinstance(module_expr.op, ast.Add)
                    and isinstance(module_expr.left, ast.Constant)
                    and module_expr.left.value == soft_name + ".Classes."
                    and ast.dump(module_expr.right) == ast.dump(class_expr)
                ):
                    package_expr = repr(soft_name + ".Classes")
                if package_expr is None:
                    continue
                first_end = offsets[first.end_lineno - 1] + first.end_col_offset
                first_start = offsets[first.lineno - 1] + first.col_offset
                line_end = encoded.find(b"\n", first_end)
                if (
                    line_end < 0
                    or encoded[first_end:line_end].strip()
                    or b"#" in encoded[first_start:first_end]
                ):
                    continue
                matches.append((first, second, module_ref, package_expr, class_expr))

    safe_refs = {id(item[2]) for item in matches}
    unsafe_modules = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in {item[0].targets[0].id for item in matches}
        and id(node) not in safe_refs
    }
    replacements = []
    for first, second, _, package_expr, class_expr in matches:
        if first.targets[0].id in unsafe_modules:
            continue
        start = offsets[first.lineno - 1] + first.col_offset
        end = offsets[second.end_lineno - 1] + second.end_col_offset
        replacement = (
            f"{second.targets[0].id} = _pyleecan_import_class("
            f"{package_expr}, {ast.unparse(class_expr)})"
        )
        replacements.append((start, end, replacement.encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8"), bool(replacements)


def _rewrite_method_call_targets(source, call_redirects):
    """Redirect imported helper calls to methods on an existing object."""
    if not call_redirects:
        return source
    tree = ast.parse(source)
    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in call_redirects
        ):
            continue
        receiver, method_name = call_redirects[node.func.id]
        function_start = line_offsets[node.func.lineno - 1] + node.func.col_offset
        function_end = function_start + len(node.func.id.encode("utf-8"))
        target = (
            "self." + method_name if receiver is None else receiver + "." + method_name
        )
        replacements.append((function_start, function_end, target.encode("utf-8")))
        if receiver is not None:
            if not node.args or ast.unparse(node.args[0]) != receiver:
                raise ValueError(
                    "Cannot redirect "
                    + node.func.id
                    + " call without its expected receiver "
                    + receiver
                )
            if len(node.args) < 2:
                raise ValueError(
                    "Cannot redirect "
                    + node.func.id
                    + " call without additional positional arguments"
                )
            first_argument_start = (
                line_offsets[node.args[0].lineno - 1] + node.args[0].col_offset
            )
            second_argument_start = (
                line_offsets[node.args[1].lineno - 1] + node.args[1].col_offset
            )
            replacements.append((first_argument_start, second_argument_start, b""))
    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _get_method_body_imports(method_node):
    """Collect static imports in a method body without entering nested scopes."""
    imports = []

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            imports.append(node)

        def visit_ImportFrom(self, node):
            imports.append(node)

        def visit_FunctionDef(self, node):
            return

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            return

    visitor = ImportVisitor()
    for statement in method_node.body:
        visitor.visit(statement)
    return imports


def _get_imported_class_modules(
    import_node, source_package, path_to_gen, soft_name, class_import_graph=None
):
    """Return generated class modules referenced by a static import."""
    imported_modules = []
    if isinstance(import_node, ast.Import):
        module_names = [alias.name.split(".") for alias in import_node.names]
    else:
        module_parts = _get_absolute_import_module(import_node, source_package)
        if module_parts[:2] != [soft_name, "Classes"]:
            return []
        if len(module_parts) > 2:
            module_names = [module_parts]
        else:
            module_names = [
                module_parts + alias.name.split(".")
                for alias in import_node.names
                if alias.name != "*"
            ]

    for module_parts in module_names:
        if module_parts[:2] != [soft_name, "Classes"] or len(module_parts) < 3:
            continue
        class_module = module_parts[2]
        if (
            class_module in class_import_graph
            if class_import_graph is not None
            else isfile(join(path_to_gen, class_module + ".py"))
        ):
            imported_modules.append(class_module)
    return imported_modules


def _class_module_imports(path_to_gen, class_module, soft_name):
    """Return top-level generated class imports for one class module."""
    class_path = join(path_to_gen, class_module + ".py")
    if not isfile(class_path):
        return []
    with open(class_path, encoding="utf-8") as class_file:
        class_tree = ast.parse(class_file.read())

    imports = []
    class_package = [soft_name, "Classes"]
    for node in class_tree.body:
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            import_nodes = [node]
        else:
            continue
        for import_node in import_nodes:
            imports.extend(
                _get_imported_class_modules(
                    import_node, class_package, path_to_gen, soft_name
                )
            )
    return imports


def get_class_import_graph(path_to_gen, gen_dict, soft_name):
    """Snapshot generated class imports before class files are rewritten."""
    return {
        class_name: tuple(_class_module_imports(path_to_gen, class_name, soft_name))
        for class_name in gen_dict
        if isfile(join(path_to_gen, class_name + ".py"))
    }


def _would_create_class_import_cycle(
    import_node,
    source_package,
    path_to_gen,
    class_name,
    soft_name,
    class_import_graph=None,
):
    """Check whether hoisting an import would create a generated-class cycle."""
    pending = _get_imported_class_modules(
        import_node,
        source_package,
        path_to_gen,
        soft_name,
        class_import_graph=class_import_graph,
    )
    visited = set()
    while pending:
        class_module = pending.pop()
        if class_module == class_name:
            return True
        if class_module in visited:
            continue
        visited.add(class_module)
        if class_import_graph is None:
            pending.extend(_class_module_imports(path_to_gen, class_module, soft_name))
        else:
            pending.extend(class_import_graph.get(class_module, ()))
    return False


def _has_method_body_import_guard(source, import_node):
    """Keep imports explicitly marked as local circular-import guards."""
    source_lines = source.splitlines()
    line_index = import_node.lineno - 2
    while line_index >= 0:
        line = source_lines[line_index].strip().lower()
        if not line:
            return False
        if line.startswith("#"):
            return "circular" in line or "importerror" in line
        if (
            line.startswith("import ")
            or line.startswith("from ")
            or line in ("(", ")")
            or line.endswith(("(", ","))
        ):
            line_index -= 1
            continue
        return False
    return False


def _remove_method_body_imports(
    source, method_body_imports, method_start_line, method_node
):
    """Remove extracted static imports while retaining the surrounding source."""
    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    extracted_imports = set(method_body_imports)
    imports_requiring_pass = set()
    for parent in ast.walk(method_node):
        for _, statements in ast.iter_fields(parent):
            if not isinstance(statements, list) or not all(
                isinstance(statement, ast.stmt) for statement in statements
            ):
                continue
            suite_imports = [
                statement for statement in statements if statement in extracted_imports
            ]
            if suite_imports and len(suite_imports) == len(statements):
                imports_requiring_pass.add(
                    min(suite_imports, key=lambda node: node.lineno)
                )

    replacements = []
    for node in method_body_imports:
        start_line = node.lineno - method_start_line
        end_line = node.end_lineno - method_start_line
        start = line_offsets[start_line] + node.col_offset
        end = line_offsets[end_line] + node.end_col_offset
        replacement = b"pass" if node in imports_requiring_pass else b""
        replacements.append((start, end, replacement))
    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _resolve_method_relative_imports(source, source_package):
    """Resolve relative imports retained inside a generated class method."""
    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom) or not node.level:
            continue
        absolute_module = ".".join(_get_absolute_import_module(node, source_package))
        replacement = ast.unparse(
            ast.ImportFrom(
                module=absolute_module,
                names=node.names,
                level=0,
            )
        ).encode("utf-8")
        start = line_offsets[node.lineno - 1] + node.col_offset
        end = line_offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, replacement))

    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _expand_error_wildcard_imports(
    module, method_node, used_names, path_to_gen, source_package
):
    """Resolve wildcard imports whose used names are package exception classes."""
    method_local_names = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
    }
    method_local_names.update(
        argument.arg
        for argument in (
            method_node.args.posonlyargs
            + method_node.args.args
            + method_node.args.kwonlyargs
        )
    )
    module_bindings = set()
    wildcard_nodes = []
    for node in module.body:
        if isinstance(node, ast.Import):
            module_bindings.update(
                alias.asname or alias.name.split(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" for alias in node.names):
                wildcard_nodes.append(node)
            else:
                module_bindings.update(
                    alias.asname or alias.name for alias in node.names
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            module_bindings.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            module_bindings.update(
                child.id
                for target in targets
                for child in ast.walk(target)
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
            )

    unresolved_names = (
        used_names - method_local_names - module_bindings - set(dir(builtins))
    )
    if not wildcard_nodes:
        return module.body, None

    providers = {}
    package_exports = {}
    for node in wildcard_nodes:
        module_parts = _get_absolute_import_module(node, source_package)
        if len(module_parts) < 3 or module_parts[1] not in ("Methods", METHODS_NEW_PACKAGE):
            return (
                None,
                "module uses a wildcard import whose names cannot be resolved safely",
            )
        init_path = join(dirname(path_to_gen), *module_parts[1:], "__init__.py")
        try:
            package_module = ast.parse(_read_method_source(init_path), filename=init_path)
        except FileNotFoundError:
            return None, "wildcard import package initializer is missing"

        exception_classes = _get_exception_classes(package_module)
        error_fingerprints = {
            name: (".".join(module_parts), name)
            for name in exception_classes
        }
        for statement in package_module.body:
            if isinstance(statement, ast.ImportFrom):
                for alias in statement.names:
                    name = alias.asname or alias.name
                    if alias.name != "*" and "Error" in name:
                        error_fingerprints[name] = _get_error_class_fingerprint(
                            path_to_gen, ".".join(module_parts), name,
                                    )
            elif isinstance(statement, ast.Import):
                for alias in statement.names:
                    name = alias.asname or alias.name.split(".")[0]
                    if "Error" in name:
                        error_fingerprints[name] = None
        package_name = ".".join(module_parts)
        package_exports[package_name] = error_fingerprints
        for name in unresolved_names.intersection(error_fingerprints):
            providers.setdefault(name, []).append(package_name)

    unresolved_names.difference_update(providers)
    if unresolved_names:
        return (
            None,
            "module uses a wildcard import whose names cannot be resolved safely",
        )

    imports_by_package = {}
    for name, package_names in providers.items():
        package_names = list(dict.fromkeys(package_names))
        canonical_package = package_names[0]
        canonical_fingerprint = package_exports[canonical_package].get(name)
        for package_name in package_names[1:]:
            candidate_fingerprint = package_exports[package_name].get(name)
            if (
                canonical_fingerprint is None
                or candidate_fingerprint is None
                or canonical_fingerprint != candidate_fingerprint
            ):
                return (
                    None,
                    "wildcard import name '"
                    + name
                    + "' refers to different class errors",
                )
        imports_by_package.setdefault(canonical_package, []).append(
            ast.alias(name=name)
        )

    replacement_nodes = []
    for package_name, aliases in imports_by_package.items():
        replacement_nodes.append(
            ast.ImportFrom(
                module=package_name,
                names=aliases,
                level=0,
            )
        )
    body = []
    inserted_imports = False
    for node in module.body:
        if node in wildcard_nodes:
            if not inserted_imports:
                body.extend(replacement_nodes)
                inserted_imports = True
        else:
            body.append(node)
    return body, None


def _get_method_source(
    path_to_gen,
    class_pack,
    class_name,
    meth,
    soft_name,
    hoist_names=(),
    class_import_graph=None,
    class_constants=None,
):
    """Return a method definition and the imports it needs.

    ``class_constants`` (name -> expression) are the class body constants
    available in the class, inherited ones included (see _class_constants).
    Module-level definitions of these names in the method module are dropped
    and their references use the class attribute instead, but only when the
    module defines the same value (a different value stays local to the method).
    """
    if class_constants is None:
        class_constants = CLASS_BODY_CONSTANTS.get(class_name, {})
    method_dir, method_package = method_source_location(path_to_gen, class_pack, class_name)
    method_path = join(method_dir, *meth.split(".")) + ".py"

    try:
        source = _read_method_source(method_path)
    except FileNotFoundError:
        return None, [], [], [], "method source file is missing"

    module = ast.parse(source, filename=method_path)
    module_values = {
        node.targets[0].id: ast.unparse(node.value)
        for node in module.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    }
    class_constants = {
        name: expression
        for name, expression in class_constants.items()
        if module_values.get(name) == ast.unparse(ast.parse(expression, mode="eval"))
    }
    method_name = meth.split(".")[-1]
    method_node = next(
        (
            node
            for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == method_name
        ),
        None,
    )
    if method_node is None:
        return None, [], [], [], "method function is missing"
    if any(
        isinstance(node, ast.ImportFrom) and node.module == "__future__"
        for node in module.body
    ):
        return None, [], [], [], "module has a __future__ import"

    source_package = [soft_name, *method_package, *meth.split(".")[:-1]]
    used_names = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    helper_function_nodes = {
        node.name: node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node is not method_node
        and not node.decorator_list
    }
    inline_helper_names = set()
    pending_helpers = list(used_names.intersection(helper_function_nodes))
    while pending_helpers:
        helper_name = pending_helpers.pop()
        if helper_name in inline_helper_names:
            continue
        inline_helper_names.add(helper_name)
        helper_used_names = {
            node.id
            for node in ast.walk(helper_function_nodes[helper_name])
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        used_names.update(helper_used_names)
        pending_helpers.extend(
            name
            for name in helper_used_names
            if name in helper_function_nodes and name not in inline_helper_names
        )
    module.body, wildcard_reason = _expand_error_wildcard_imports(
        module, method_node, used_names, path_to_gen, source_package
    )
    if wildcard_reason is not None:
        return None, [], [], [], wildcard_reason
    if any(isinstance(node, ast.Global) for node in ast.walk(method_node)):
        return None, [], [], [], "method declares module globals"

    signature_nodes = (
        method_node.decorator_list
        + method_node.args.defaults
        + [node for node in method_node.args.kw_defaults if node is not None]
        + [
            argument.annotation
            for argument in (
                method_node.args.posonlyargs
                + method_node.args.args
                + method_node.args.kwonlyargs
            )
            if argument.annotation is not None
        ]
    )
    if method_node.returns is not None:
        signature_nodes.append(method_node.returns)
    signature_names = {
        node.id
        for root_node in signature_nodes
        for node in ast.walk(root_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }

    helper_bindings = set()
    literal_defaults = {}
    has_module_helpers = False
    for node in module.body:
        if node is method_node or (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue
        if isinstance(node, ast.Import):
            continue
        elif isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" for alias in node.names):
                return (
                    None,
                    [],
                    [],
                    [],
                    "module uses a wildcard import whose names cannot be resolved safely",
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node is method_node:
                continue
            helper_bindings.add(node.name)
            has_module_helpers = True
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = {
                child.id
                for target in targets
                for child in ast.walk(target)
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
            }
            helper_bindings.update(names)
            if len(names) == 1 and len(targets) == 1:
                try:
                    ast.literal_eval(node.value)
                except ValueError, TypeError, SyntaxError:
                    pass
                else:
                    name = next(iter(names))
                    literal_defaults[name] = ast.unparse(node.value)
            has_module_helpers = True
        else:
            return (
                None,
                [],
                [],
                [],
                "module contains unsupported top-level "
                + type(node).__name__
                + " statements",
            )

    inline_literal_defaults = {
        name: value
        for name, value in literal_defaults.items()
        if name not in signature_names
        and name not in class_constants
        and name not in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(class_name, {})
    }
    method_local_names = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
    }
    method_local_names.update(
        argument.arg
        for argument in (
            method_node.args.posonlyargs
            + method_node.args.args
            + method_node.args.kwonlyargs
        )
    )
    module_assignments = {}
    for node in module.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if len(targets) != 1 or not isinstance(targets[0], ast.Name):
            continue
        name = targets[0].id
        if name in literal_defaults or name in class_constants:
            continue
        module_assignments[name] = node.value

    signature_non_defaults = method_node.decorator_list + [
        argument.annotation
        for argument in (
            method_node.args.posonlyargs
            + method_node.args.args
            + method_node.args.kwonlyargs
        )
        if argument.annotation is not None
    ]
    if method_node.returns is not None:
        signature_non_defaults.append(method_node.returns)
    signature_default_names = {
        node.id
        for default in method_node.args.defaults
        + [node for node in method_node.args.kw_defaults if node is not None]
        for node in ast.walk(default)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    direct_default_names = {
        default.id
        for default in method_node.args.defaults
        + [node for node in method_node.args.kw_defaults if node is not None]
        if isinstance(default, ast.Name)
    }
    signature_non_default_names = {
        node.id
        for root_node in signature_non_defaults
        for node in ast.walk(root_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    configured_assignment_names = {
        name
        for name in hoist_names.intersection(module_assignments)
        if any(
            isinstance(node, ast.Name) and node.id == "config_dict"
            for node in ast.walk(module_assignments[name])
        )
    }
    hoisted_names = {
        name
        for name in used_names.intersection(module_assignments, hoist_names)
        if name not in method_local_names
        and name not in signature_non_default_names
        and (name not in signature_default_names or name in direct_default_names)
    } | configured_assignment_names
    # Class constants are referenced as class attributes like hoisted names
    # (self.NAME in the body, __defaults__ restored for signature defaults)
    used_class_constants = (
        used_names.intersection(class_constants) - method_local_names
    )
    unsupported = used_class_constants & (
        signature_non_default_names | (signature_default_names - direct_default_names)
    )
    if unsupported:
        raise ValueError(
            f"{class_name}.{method_name}: class constants {sorted(unsupported)} "
            "can only be used as a whole default value in the signature"
        )
    hoisted_names |= used_class_constants
    if hoisted_names and not method_node.args.args:
        return (
            None,
            [],
            [],
            [],
            "cannot hoist module assignments for a method without an instance argument",
        )

    class_attributes = [
        ast.fix_missing_locations(
            ast.Assign(
                targets=[ast.Name(id=name, ctx=ast.Store())],
                value=value,
            )
        )
        for name, value in module_assignments.items()
        if name in hoisted_names
    ]
    extra_used_names = {
        node.id
        for assignment in class_attributes
        for node in ast.walk(assignment.value)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    } - hoisted_names
    target_package = [soft_name, "Classes"]
    method_imports = []
    local_method_imports = []
    import_used_names = used_names | extra_used_names
    renamed_method_names = {}
    method_call_redirects = {}
    method_body_imports = [
        node
        for node in _get_method_body_imports(method_node)
        if not _has_method_body_import_guard(source, node)
        and not _would_create_class_import_cycle(
            node,
            source_package,
            path_to_gen,
            class_name,
            soft_name,
            class_import_graph=class_import_graph,
        )
    ]

    if has_module_helpers:
        helper_names = sorted(
            import_used_names.intersection(
                helper_bindings
                - inline_literal_defaults.keys()
                - hoisted_names
                - class_constants.keys()
                - CLASS_MODULE_CONSTANT_EXPRESSIONS.get(class_name, {}).keys()
            )
        )
        if helper_names:
            helper_module = source_package + [method_name]
            common = 0
            while (
                common < len(target_package)
                and common < len(helper_module)
                and target_package[common] == helper_module[common]
            ):
                common += 1
            imported_helpers = [
                ast.alias(name=name)
                for name in helper_names
                if name not in inline_helper_names
                and METHOD_IMPORT_REDIRECTS.get(
                    (_legacy_methods_module(".".join(helper_module[1:])), name)
                )
                is None
            ]
            if imported_helpers:
                method_imports.append(
                    ast.ImportFrom(
                        module=".".join(helper_module[common:]),
                        names=imported_helpers,
                        level=len(target_package) - common + 1,
                    )
                )
            for name in helper_names:
                target_class = METHOD_IMPORT_REDIRECTS.get(
                    (_legacy_methods_module(".".join(helper_module[1:])), name)
                )
                if target_class is None:
                    continue
                if target_class != class_name:
                    method_imports.append(
                        ast.ImportFrom(
                            module=soft_name + ".Classes." + target_class,
                            names=[ast.alias(name=name)],
                            level=0,
                        )
                    )

    for node in module.body + method_body_imports:
        is_method_body_import = node in method_body_imports
        if isinstance(node, ast.Import):
            aliases = [
                alias
                for alias in node.names
                if is_method_body_import
                or (alias.asname or alias.name.split(".")[0]) in import_used_names
            ]
            if aliases:
                method_imports.append(ast.Import(names=aliases))
        elif isinstance(node, ast.ImportFrom):
            aliases = [
                alias
                for alias in node.names
                if is_method_body_import
                or alias.name == "*"
                or (alias.asname or alias.name) in import_used_names
            ]
            if not aliases:
                continue

            absolute_module_parts = _get_absolute_import_module(node, source_package)
            redirect_module = _legacy_methods_module(  # Keys of the tables
                ".".join(
                    absolute_module_parts[1:]
                    if absolute_module_parts[:1] == [soft_name]
                    else absolute_module_parts
                )
            )
            redirected_aliases = {}
            local_aliases = []
            for alias in aliases:
                if (
                    class_name,
                    meth,
                    redirect_module,
                    alias.name,
                ) in EXPERIMENTAL_LOCAL_METHOD_IMPORTS:
                    local_aliases.append(alias)
                    continue
                method_call_redirect = METHOD_CALL_REDIRECTS.get(
                    (class_name, redirect_module, alias.name)
                )
                if method_call_redirect is not None:
                    method_call_redirects[alias.asname or alias.name] = (
                        method_call_redirect
                    )
                    continue
                target_class = METHOD_IMPORT_REDIRECTS.get(
                    (redirect_module, alias.name)
                )
                if target_class is not None:
                    target_module = soft_name + ".Classes." + target_class
                    redirected_aliases.setdefault(target_module, []).append(alias)
            if local_aliases:
                local_method_imports.append(
                    ast.ImportFrom(
                        module=".".join(absolute_module_parts),
                        names=local_aliases,
                        level=0,
                    )
                )
                aliases = [alias for alias in aliases if alias not in local_aliases]
            for target_module, target_aliases in redirected_aliases.items():
                if (
                    target_module != soft_name + ".Classes." + class_name
                    or (
                        any(
                            alias.name in EXPERIMENTAL_GEOMETRY_CONSTANTS
                            for alias in target_aliases
                        )
                    )
                ):
                    method_imports.append(
                        ast.ImportFrom(
                            module=target_module,
                            names=target_aliases,
                            level=0,
                        )
                    )
            aliases = [
                alias
                for alias in aliases
                if (redirect_module, alias.name) not in METHOD_IMPORT_REDIRECTS
                and (
                    class_name,
                    redirect_module,
                    alias.name,
                )
                not in METHOD_CALL_REDIRECTS
            ]
            if not aliases:
                continue

            if _get_absolute_import_module(node, source_package) == [
                soft_name,
                "Functions",
                "SciDataTool",
            ]:
                updated_aliases = []
                for alias in aliases:
                    if alias.name == "axes_dict":
                        updated_aliases.append(
                            ast.alias(name="axes_dict_transformation")
                        )
                        renamed_method_names["axes_dict"] = "axes_dict_transformation"
                    else:
                        updated_aliases.append(alias)
                aliases = updated_aliases

            if node.level:
                module_parts = source_package[: len(source_package) - node.level + 1]
                if node.module:
                    module_parts.extend(node.module.split("."))

                common = 0
                while (
                    common < len(target_package)
                    and common < len(module_parts)
                    and target_package[common] == module_parts[common]
                ):
                    common += 1
                node = ast.ImportFrom(
                    module=".".join(module_parts[common:]) or None,
                    names=aliases,
                    level=len(target_package) - common + 1,
                )
            else:
                node = ast.ImportFrom(
                    module=node.module,
                    names=aliases,
                    level=0,
                )
            class_error_aliases = [
                alias for alias in aliases if alias.name in CLASS_ERROR_NAMES
            ]
            method_aliases = [
                alias for alias in aliases if alias.name not in CLASS_ERROR_NAMES
            ]
            if method_aliases:
                method_imports.append(
                    ast.ImportFrom(
                        module=node.module,
                        names=method_aliases,
                        level=node.level,
                    )
                )
            if class_error_aliases:
                method_imports.append(
                    ast.ImportFrom(
                        module=soft_name + ".Classes",
                        names=class_error_aliases,
                        level=0,
                    )
                )

    source_lines = source.splitlines()
    start_line = min(
        [method_node.lineno]
        + [decorator.lineno for decorator in method_node.decorator_list]
    )
    while start_line > 1 and source_lines[start_line - 2].lstrip().startswith("#"):
        start_line -= 1
    method_source = "\n".join(source_lines[start_line - 1 : method_node.end_lineno])
    method_source = _remove_method_body_imports(
        method_source, method_body_imports, start_line, method_node
    )
    method_source = _resolve_method_relative_imports(method_source, source_package)
    if local_method_imports:
        method_tree = ast.parse(method_source)
        function = next(
            node
            for node in method_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        docstring = ast.get_docstring(function)
        first_statement = function.body[1] if docstring is not None else function.body[0]
        lines = method_source.splitlines(keepends=True)
        indentation = " " * first_statement.col_offset
        lines.insert(
            first_statement.lineno - 1,
            "".join(
                indentation + ast.unparse(node) + "\n"
                for node in local_method_imports
            ) + "\n",
        )
        method_source = "".join(lines)
    method_source = _rename_method_references(method_source, renamed_method_names)
    method_source = _rewrite_method_call_targets(method_source, method_call_redirects)
    method_helper_names = inline_helper_names.difference(method_local_names)
    method_source = _rename_method_references(
        method_source,
        {name: "self." + name for name in method_helper_names},
    )
    method_source = _add_literal_keyword_defaults(
        method_source, inline_literal_defaults, used_names
    )
    method_source, default_overrides = _rewrite_hoisted_method_names(
        method_source,
        hoisted_names,
        method_name,
        (
            method_node.args.posonlyargs[0].arg
            if method_node.args.posonlyargs
            else method_node.args.args[0].arg
            if method_node.args.args
            else None
        ),
    )
    source_lines = source.splitlines()
    helper_sources = []
    for helper_name in sorted(inline_helper_names):
        helper_node = helper_function_nodes[helper_name]
        helper_source = "\n".join(
            source_lines[helper_node.lineno - 1 : helper_node.end_lineno]
        )
        helper_local_names = {
            node.id
            for node in ast.walk(helper_node)
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
        }
        helper_local_names.update(
            argument.arg
            for argument in (
                helper_node.args.posonlyargs
                + helper_node.args.args
                + helper_node.args.kwonlyargs
            )
        )
        helper_reference_names = {
            name: class_name + "." + name
            for name in inline_helper_names.difference(helper_local_names)
        }
        helper_reference_names.update(
            {
                name: class_name + "." + name
                for name in hoisted_names.difference(helper_local_names)
            }
        )
        helper_reference_names.update(
            {
                name: class_name + "." + name
                for name in class_constants.keys()
                if name not in helper_local_names
            }
        )
        helper_source = _rename_method_references(
            helper_source,
            helper_reference_names,
        )
        helper_sources.append("@staticmethod\n" + helper_source)
    if helper_sources:
        method_source += "\n\n" + "\n\n".join(helper_sources)
    method_import_bindings = {
        alias.asname
        or (alias.name.split(".")[0] if isinstance(node, ast.Import) else alias.name)
        for node in method_imports
        for alias in node.names
    }
    method_source, replaced_class_import = _replace_dynamic_class_imports(
        method_source, soft_name, method_import_bindings
    )
    if replaced_class_import:
        method_imports.append(
            ast.ImportFrom(
                module=soft_name + ".Functions.Load.import_class",
                names=[ast.alias(name="import_class", asname="_pyleecan_import_class")],
                level=0,
            )
        )
    method_tree = ast.parse(method_source)
    if any(
        _is_numpy_import(node) for node in method_imports + list(ast.walk(method_tree))
    ):
        method_source, method_imports = _normalize_method_numpy_imports(
            method_source, method_imports
        )
    if any(
        _is_package_import(node, "pyvista")
        for node in method_imports + list(ast.walk(ast.parse(method_source)))
    ):
        method_source, method_imports = _normalize_method_package_imports(
            method_source, method_imports, "pyvista", "pv"
        )
    class_attribute_loads = {
        node.id
        for assignment in class_attributes
        for node in ast.walk(assignment.value)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    os_import_bindings = {
        alias.asname
        or (
            alias.name.split(".")[0]
            if isinstance(node, ast.Import)
            else alias.name
        )
        for node in method_imports
        if _is_package_import(node, "os")
        for alias in node.names
        if isinstance(node, ast.ImportFrom)
        or alias.name == "os"
        or alias.name.startswith("os.")
    }
    if not class_attribute_loads.intersection(os_import_bindings) and any(
        _is_package_import(node, "os")
        for node in method_imports + list(ast.walk(ast.parse(method_source)))
    ):
        method_source, method_imports = _normalize_method_package_imports(
            method_source, method_imports, "os", "os"
        )
    return (
        method_source,
        method_imports,
        class_attributes,
        default_overrides,
        None,
    )


def _find_repeated_method_assignments(path_to_gen, class_pack, class_name, methods):
    """Find computed module assignments that are shared or used as defaults."""
    assignment_methods = {}
    method_assignments = {}
    default_assignments = {}
    configured_plot_assignments = set()

    method_dir = method_source_location(path_to_gen, class_pack, class_name)[0]
    for meth in methods:
        method_path = join(method_dir, *meth.split(".")) + ".py"
        try:
            module = ast.parse(_read_method_source(method_path), filename=method_path)
        except FileNotFoundError:
            continue

        method_name = meth.split(".")[-1]
        method_node = next(
            (
                node
                for node in module.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == method_name
            ),
            None,
        )
        if method_node is None:
            continue

        used_names = {
            node.id
            for node in ast.walk(method_node)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        local_names = {
            node.id
            for node in ast.walk(method_node)
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
        }
        local_names.update(
            argument.arg
            for argument in (
                method_node.args.posonlyargs
                + method_node.args.args
                + method_node.args.kwonlyargs
            )
        )
        direct_default_names = {
            default.id
            for default in method_node.args.defaults
            + [node for node in method_node.args.kw_defaults if node is not None]
            if isinstance(default, ast.Name)
        }
        assigned_names = set()
        for node in module.body:
            if isinstance(node, ast.Assign):
                if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                    continue
                name = node.targets[0].id
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                name = node.target.id
                value = node.value
            else:
                continue
            is_configured_plot_assignment = (
                value is not None
                and (name.endswith("_COLOR") or name in CONFIGURED_PLOT_CONSTANT_NAMES)
                and any(
                    isinstance(child, ast.Name) and child.id == "config_dict"
                    for child in ast.walk(value)
                )
            )
            if (
                value is None
                or name in local_names
                or (name not in used_names and not is_configured_plot_assignment)
            ):
                continue
            try:
                ast.literal_eval(value)
            except ValueError, TypeError, SyntaxError:
                assigned_names.add(name)
                assignment_methods.setdefault(name, set()).add(meth)
                if name in direct_default_names:
                    default_assignments.setdefault(meth, set()).add(name)
                if is_configured_plot_assignment:
                    configured_plot_assignments.add(name)
        method_assignments[meth] = assigned_names

    hoisted_names = {
        name
        for name, methods_using_name in assignment_methods.items()
        if len(methods_using_name) > 1
    } | configured_plot_assignments
    return {
        meth: names.intersection(hoisted_names).union(
            default_assignments.get(meth, set())
        )
        for meth, names in method_assignments.items()
    }


def _prepare_class_methods(
    path_to_gen,
    class_pack,
    class_name,
    methods,
    soft_name,
    reserved_names=(),
    class_import_graph=None,
    class_constants=None,
):
    """Inline methods and collect their imports without name conflicts."""
    prepared = {}
    fallback_reasons = {}
    imports = []
    import_groups = {}
    import_bindings = {}
    import_keys = set()
    target_package = [soft_name, "Classes"]
    class_attributes = {}
    class_error_definitions = {}
    class_method_definitions = {}
    class_method_imports = []
    method_default_overrides = {}
    repeated_assignments = _find_repeated_method_assignments(
        path_to_gen, class_pack, class_name, methods
    )
    section_classes = (
        {node.name for node in _section_module_classes(path_to_gen)}
        if class_name == "Section"
        else set()
    )

    for meth in methods:
        (
            method_source,
            method_imports,
            candidate_class_attributes,
            candidate_default_overrides,
            reason,
        ) = _get_method_source(
            path_to_gen,
            class_pack,
            class_name,
            meth,
            soft_name,
            repeated_assignments.get(meth, set()),
            class_import_graph=class_import_graph,
            class_constants=class_constants,
        )
        if reason is not None:
            action = (
                "omitting the unavailable method"
                if reason in MISSING_METHOD_REASONS
                else "keeping its module import"
            )
            warnings.warn(
                "Could not inline "
                + class_name
                + "."
                + meth
                + ": "
                + reason
                + "; "
                + action,
                stacklevel=2,
            )
            prepared[meth] = None
            fallback_reasons[meth] = reason
            continue

        filtered_method_imports = []
        for import_node in method_imports:
            if not isinstance(import_node, ast.ImportFrom):
                filtered_method_imports.append(import_node)
                continue
            absolute_module = ".".join(
                _get_absolute_import_module(import_node, target_package)
            )
            if absolute_module.startswith(soft_name + "."):  # Keys of the tables
                absolute_module = (
                    soft_name
                    + "."
                    + _legacy_methods_module(absolute_module[len(soft_name) + 1 :])
                )
            retained_aliases = []
            for alias in import_node.names:
                configured_module_classes = CLASS_MODULE_CLASS_DEFINITIONS.get(
                    class_name
                )
                if (
                    configured_module_classes is not None
                    and absolute_module
                    == soft_name + ".Methods." + configured_module_classes[0]
                    and alias.name in (
                        section_classes if class_name == "Section"
                        else configured_module_classes[1]
                    )
                    and (
                        class_name != "Section"
                        or alias.asname in (None, alias.name)
                    )
                ):
                    continue
                binding = alias.asname or alias.name
                configured_helper = CLASS_METHOD_HELPERS.get(class_name, {}).get(
                    binding
                )
                if (
                    configured_helper is None
                    or absolute_module != soft_name + ".Methods." + configured_helper[0]
                    or alias.name != configured_helper[1]
                ):
                    retained_aliases.append(alias)
                    continue
                helper_path = join(
                    _methods_location(path_to_gen, configured_helper[0])[0],
                    "__init__.py",
                )
                helper_module = ast.parse(
                    _read_method_source(helper_path), filename=helper_path
                )
                helper_node = next(
                    (
                        node
                        for node in helper_module.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == configured_helper[1]
                    ),
                    None,
                )
                if helper_node is None:
                    raise ValueError(
                        "Could not find configured class helper "
                        + configured_helper[1]
                        + " in "
                        + helper_path
                    )
                if configured_helper[1] in CLASS_STATIC_METHOD_HELPERS.get(
                    class_name, set()
                ):
                    helper_node.decorator_list.insert(
                        0, ast.Name(id="staticmethod", ctx=ast.Load())
                    )
                class_method_definitions[helper_node.name] = helper_node
                helper_used_names = {
                    node.id
                    for node in ast.walk(helper_node)
                    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                }
                for helper_import in helper_module.body:
                    if not isinstance(helper_import, (ast.Import, ast.ImportFrom)):
                        continue
                    used_aliases = [
                        helper_alias
                        for helper_alias in helper_import.names
                        if (
                            helper_alias.asname
                            or (
                                helper_alias.name.split(".")[0]
                                if isinstance(helper_import, ast.Import)
                                else helper_alias.name
                            )
                        )
                        in helper_used_names
                    ]
                    if used_aliases:
                        if isinstance(helper_import, ast.Import):
                            class_method_imports.append(ast.Import(names=used_aliases))
                            continue
                        helper_package = [
                            soft_name,
                            *_methods_location(path_to_gen, configured_helper[0])[1],
                        ]
                        absolute_helper_module = _get_absolute_import_module(
                            helper_import, helper_package
                        )
                        common = 0
                        while (
                            common < len(target_package)
                            and common < len(absolute_helper_module)
                            and target_package[common] == absolute_helper_module[common]
                        ):
                            common += 1
                        class_method_imports.append(
                            ast.ImportFrom(
                                module=".".join(absolute_helper_module[common:]),
                                names=used_aliases,
                                level=len(target_package) - common + 1,
                            )
                        )
            if retained_aliases:
                filtered_method_imports.append(
                    ast.ImportFrom(
                        module=import_node.module,
                        names=retained_aliases,
                        level=import_node.level,
                    )
                )
        method_imports = filtered_method_imports

        candidate_bindings = {}
        conflict = False
        conflict_name = None
        conflict_imports = None
        conflict_reason = None
        for assignment in candidate_class_attributes:
            binding = assignment.targets[0].id
            existing = class_attributes.get(binding)
            identity = ast.dump(assignment.value, include_attributes=False)
            if binding in reserved_names:
                conflict_reason = (
                    "class attribute '"
                    + binding
                    + "' conflicts with an existing class member"
                )
                break
            if (
                existing is not None
                and ast.dump(existing, include_attributes=False) != identity
            ):
                conflict_reason = (
                    "class attribute '"
                    + binding
                    + "' has different definitions in method modules"
                )
                break
        for import_node in method_imports:
            if conflict_reason is not None:
                break
            for alias in import_node.names:
                binding = alias.asname or (
                    alias.name.split(".")[0]
                    if isinstance(import_node, ast.Import)
                    else alias.name
                )
                identity = _get_import_identity(import_node, alias, target_package)
                existing = import_bindings.get(binding)
                candidate = candidate_bindings.get(binding)
                for previous in (existing, candidate):
                    if previous is None or previous == identity:
                        continue
                    if _same_error_class_import(
                        path_to_gen, previous, identity
                    ):
                        identity = previous
                    else:
                        conflict = True
                        conflict_name = binding
                        conflict_imports = (previous, identity)
                        break
                if conflict:
                    break
                candidate_bindings[binding] = identity
            if conflict:
                break

        candidate_error_definitions = {}
        if not conflict and conflict_reason is None:
            for import_node in method_imports:
                if not isinstance(import_node, ast.ImportFrom):
                    continue
                module_name = ".".join(
                    _get_absolute_import_module(import_node, target_package)
                )
                if not _is_methods_module(module_name, soft_name):
                    continue
                for alias in import_node.names:
                    definitions = _get_error_class_definitions(
                        path_to_gen, module_name, alias.name
                    )
                    for definition in definitions:
                        existing = candidate_error_definitions.get(
                            definition.name,
                            class_error_definitions.get(definition.name),
                        )
                        if existing is not None and (
                            existing.error_origin != definition.error_origin
                        ):
                            conflict_reason = (
                                "class error '"
                                + definition.name
                                + "' has different definitions"
                            )
                            break
                        candidate_error_definitions[definition.name] = definition
                    if conflict_reason is not None:
                        break
                if conflict_reason is not None:
                    break

        if conflict or conflict_reason is not None:
            fallback_reason = (
                conflict_reason
                if conflict_reason is not None
                else (
                    "import name '"
                    + conflict_name
                    + "' refers to different sources ("
                    + _format_import_identity(conflict_imports[0])
                    + " and "
                    + _format_import_identity(conflict_imports[1])
                    + ")"
                )
            )
            warnings.warn(
                "Could not inline "
                + class_name
                + "."
                + meth
                + ": "
                + fallback_reason
                + "; "
                + "keeping its module import",
                stacklevel=2,
            )
            prepared[meth] = None
            fallback_reasons[meth] = fallback_reason
            continue

        prepared[meth] = method_source
        method_default_overrides[meth] = candidate_default_overrides
        class_error_definitions.update(candidate_error_definitions)
        for assignment in candidate_class_attributes:
            class_attributes.setdefault(assignment.targets[0].id, assignment.value)
        import_bindings.update(candidate_bindings)
        for import_node in method_imports:
            if isinstance(import_node, ast.ImportFrom):
                module_name = ".".join(
                    _get_absolute_import_module(import_node, target_package)
                )
                if _is_methods_module(module_name, soft_name):
                    retained_aliases = [
                        alias
                        for alias in import_node.names
                        if not _get_error_class_definitions(
                            path_to_gen, module_name, alias.name
                        )
                    ]
                    if not retained_aliases:
                        continue
                    import_node = ast.ImportFrom(
                        module=import_node.module,
                        names=retained_aliases,
                        level=import_node.level,
                    )
            group_key = (
                type(import_node).__name__,
                getattr(import_node, "level", 0),
                getattr(import_node, "module", None),
                any(alias.name == "*" for alias in import_node.names),
            )
            if group_key not in import_groups:
                if isinstance(import_node, ast.Import):
                    grouped_import = ast.Import(names=[])
                else:
                    grouped_import = ast.ImportFrom(
                        module=import_node.module,
                        names=[],
                        level=import_node.level,
                    )
                import_groups[group_key] = grouped_import
                imports.append(grouped_import)
            for alias in import_node.names:
                binding = alias.asname or (
                    alias.name.split(".")[0]
                    if isinstance(import_node, ast.Import)
                    else alias.name
                )
                identity = candidate_bindings[binding]
                if identity in import_keys:
                    continue
                import_keys.add(identity)
                import_groups[group_key].names.append(alias)

    if class_method_definitions:
        helper_names = set(class_method_definitions)
        for meth, method_source in prepared.items():
            if method_source is not None:
                prepared[meth] = _rename_method_references(
                    method_source,
                    {name: "self." + name for name in helper_names},
                )
        first_method = next(
            (meth for meth, source in prepared.items() if source is not None), None
        )
        if first_method is not None:
            helper_sources = [
                ast.unparse(class_method_definitions[name])
                for name in sorted(class_method_definitions)
            ]
            prepared[first_method] += "\n\n" + "\n\n".join(helper_sources)
        for import_node in class_method_imports:
            group_key = (
                type(import_node).__name__,
                getattr(import_node, "level", 0),
                getattr(import_node, "module", None),
                any(alias.name == "*" for alias in import_node.names),
            )
            if group_key not in import_groups:
                grouped_import = (
                    ast.Import(names=[])
                    if isinstance(import_node, ast.Import)
                    else ast.ImportFrom(
                        module=import_node.module,
                        names=[],
                        level=import_node.level,
                    )
                )
                import_groups[group_key] = grouped_import
                imports.append(grouped_import)
            for alias in import_node.names:
                binding = alias.asname or (
                    alias.name.split(".")[0]
                    if isinstance(import_node, ast.Import)
                    else alias.name
                )
                identity = _get_import_identity(import_node, alias, target_package)
                previous = import_bindings.get(binding)
                if previous is not None and previous != identity:
                    raise ValueError(
                        "Class helper import name '"
                        + binding
                        + "' conflicts with "
                        + _format_import_identity(previous)
                    )
                import_bindings[binding] = identity
                if identity in import_keys:
                    continue
                import_keys.add(identity)
                import_groups[group_key].names.append(alias)

    assignments = [
        ast.fix_missing_locations(
            ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=value)
        )
        for name, value in class_attributes.items()
    ]
    blocked_containers = set(import_bindings)
    if any(
        isinstance(node, ast.ImportFrom)
        and any(alias.name == "*" for alias in node.names)
        for node in imports
    ):
        blocked_containers.update(("dict", "list"))
    for name, method_source in prepared.items():
        if method_source is not None:
            prepared[name] = _replace_empty_containers(method_source, blocked_containers)
    return (
        prepared,
        [node for node in imports if node.names],
        fallback_reasons,
        assignments,
        method_default_overrides,
        _sort_error_class_definitions(class_error_definitions.values()),
    )


def _format_import_identity(identity):
    """Format the source of an import binding for inline-fallback reports."""
    import_type, level, module, name, alias = identity
    if import_type == "Import":
        source = name
    else:
        source = "." * level + (module + "." if module else "") + name
    if alias:
        source += " as " + alias
    return source


def _get_import_identity(import_node, alias, target_package):
    """Return a binding identity with relative imports resolved to package names."""
    if isinstance(import_node, ast.Import):
        return (
            "Import",
            0,
            None,
            alias.name,
            alias.asname,
        )

    module_parts = _get_absolute_import_module(import_node, target_package)
    return (
        "ImportFrom",
        0,
        ".".join(module_parts),
        alias.name,
        alias.asname,
    )


def _get_absolute_import_module(import_node, target_package):
    """Resolve an ImportFrom node to its absolute module path."""
    module_parts = (import_node.module or "").split(".")
    if import_node.level:
        module_parts = target_package[: len(target_package) - import_node.level + 1]
        if import_node.module:
            module_parts.extend(import_node.module.split("."))
    return module_parts


def _apply_import_style(source, soft_name, import_style, class_package="Classes"):
    """Apply the configured Pyleecan import style without rewriting other code.

    class_package is the package of the module, relative to soft_name; it can
    be dotted for a sub-package (e.g. "Classes_new.geometry").
    """
    target_package = [soft_name, *class_package.split(".")]
    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []

    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom):
            continue

        if import_style == "absolute" and node.level:
            module_parts = _get_absolute_import_module(node, target_package)
            replacement = ast.ImportFrom(
                module=".".join(module_parts) or None,
                names=node.names,
                level=0,
            )
        elif (
            import_style == "relative"
            and not node.level
            and node.module
            and (node.module == soft_name or node.module.startswith(soft_name + "."))
        ):
            module_parts = node.module.split(".")
            common = 0
            while (
                common < len(target_package)
                and common < len(module_parts)
                and target_package[common] == module_parts[common]
            ):
                common += 1
            replacement = ast.ImportFrom(
                module=".".join(module_parts[common:]) or None,
                names=node.names,
                level=len(target_package) - common + 1,
            )
        else:
            continue

        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))

    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
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


def _redirect_experimental_class_imports(source, soft_name, gen_dict):
    """Redirect generated classes and selected support imports to Classes_new."""
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


def _remove_unused_loader_import(source, soft_name):
    """Remove the import of the class loader (import_class) if it is unused."""
    tree = ast.parse(source)
    for node in tree.body:
        if not (
            isinstance(node, ast.ImportFrom)
            and (
                node.level == 0 and node.module == soft_name + ".Classes_new._import"
                or node.level == 1 and node.module == "_import"
            )
        ):
            continue
        used = {
            child.id
            for child in ast.walk(tree)
            if isinstance(child, ast.Name)
        }
        kept = [
            alias
            for alias in node.names
            if alias.name != "import_class" or (alias.asname or alias.name) in used
        ]
        if len(kept) == len(node.names):
            continue
        lines = source.splitlines(keepends=True)
        replacement = (
            ast.unparse(ast.ImportFrom(module=node.module, names=kept, level=node.level))
            + "\n"
            if kept
            else ""
        )
        lines[node.lineno - 1 : node.end_lineno] = [replacement]
        return "".join(lines)
    return source


def _static_local_class_imports(
    source, soft_name, gen_dict, generated_name, modules=None
):
    """Replace the method-local class loads by regular (static) local imports.

    ``X = import_class("Name")`` in a method becomes
    ``from <soft_name>.Classes_new.name import Name as X``: linters and type
    checkers can follow it, and a local import still avoids import cycles.
    The imports are grouped at the top of the method body (after its docstring
    and its existing local imports). ``import_class`` is kept for the class
    names only known at runtime.
    """
    tree = ast.parse(source)
    if modules is None:  # class name -> module name of the generated classes
        modules = {
            NORMALIZATION_CLASS_NAMES.get(name, name): class_module_name(name)
            for name in gen_dict
        }
    loader_module = soft_name + ".Classes_new._import"
    loader_imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.level == 0
        and node.module == loader_module
    ]
    bindings = {
        alias.asname or alias.name
        for node in loader_imports
        for alias in node.names
        if alias.name == "import_class"
    }
    if not bindings:
        return source
    lines = source.splitlines(keepends=True)

    def alone_on_lines(node):
        """True if the statement is alone on its lines (comments aside)."""
        before = lines[node.lineno - 1].encode("utf-8")[: node.col_offset]
        after = lines[node.end_lineno - 1].encode("utf-8")[node.end_col_offset :]
        return not before.strip() and (
            not after.strip() or after.strip().startswith(b"#")
        )

    def is_known_load(node):
        return (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id in bindings
            and 1 <= len(node.value.args) <= 2
            and not node.value.keywords
            and isinstance(node.value.args[0], ast.Constant)
            and node.value.args[0].value in modules
            and alone_on_lines(node)
        )

    # Known class loads, grouped by their innermost function
    loads = {}

    def collect(node, function):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                collect(child, child)
            elif isinstance(child, ast.ClassDef):
                collect(child, None)
            else:
                if function is not None and is_known_load(child):
                    loads.setdefault(function, []).append(child)
                collect(child, function)

    collect(tree, None)
    if not loads:
        return source

    # Statement block of each statement (to keep the emptied blocks valid)
    blocks = {}
    for node in ast.walk(tree):
        for name in ("body", "orelse", "finalbody"):
            block = getattr(node, name, None)
            if isinstance(block, list):
                for statement in block:
                    blocks[id(statement)] = block

    removed = set()  # indexes of the removed lines
    replaced = {}  # first line index of a removed statement -> new text
    inserted = {}  # line index -> lines inserted before it
    removed_statements = set()
    replaced_calls = set()
    hoisted_bodies = []  # function bodies that receive the imports
    for function, statements in loads.items():
        body = function.body
        index = 0
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            index = 1  # docstring
        while index < len(body) and isinstance(body[index], (ast.Import, ast.ImportFrom)):
            index += 1  # existing local imports
        first = body[index]
        if not alone_on_lines(first):
            continue
        indent = " " * first.col_offset
        existing = {ast.unparse(statement) for statement in body[:index]}
        imports = []
        targets = [node.targets[0].id for node in statements]
        for node in statements:
            class_name = node.value.args[0].value
            target = node.targets[0].id
            for line in range(node.lineno - 1, node.end_lineno):
                removed.add(line)
            removed_statements.add(id(node))
            replaced_calls.add(id(node.value.func))
            if class_name == generated_name:
                # The class of this module is a module global
                if target != class_name:
                    replaced[node.lineno - 1] = (
                        " " * node.col_offset + f"{target} = {class_name}\n"
                    )
                    removed_statements.discard(id(node))
                continue
            statement = ast.unparse(
                ast.ImportFrom(
                    module=f"{soft_name}.Classes_new.{modules[class_name]}",
                    names=[
                        ast.alias(
                            name=class_name,
                            asname=None if target == class_name else target,
                        )
                    ],
                    level=0,
                )
            )
            if not any(node is top for top in body) or targets.count(target) > 1:
                # Load in a block (if/else, loop, try...) or name loaded several
                # times: the import is kept in place to keep the bound class
                replaced[node.lineno - 1] = " " * node.col_offset + statement + "\n"
                removed_statements.discard(id(node))
            elif statement not in existing and statement not in imports:
                imports.append(statement)
        if not imports:
            continue
        if index and isinstance(body[index - 1], (ast.Import, ast.ImportFrom)):
            # Right after the existing local imports
            line = body[index - 1].end_lineno
            block = [indent + statement + "\n" for statement in imports]
        else:
            # Above the comments that introduce the first statement
            line = (
                min(
                    [first.lineno]
                    + [node.lineno for node in getattr(first, "decorator_list", [])]
                )
                - 1
            )
            bound = body[index - 1].end_lineno if index else function.lineno
            while line - 1 >= bound and lines[line - 1].lstrip().startswith("#"):
                line -= 1
            block = [indent + statement + "\n" for statement in imports] + ["\n"]
        inserted.setdefault(line, []).extend(block)
        hoisted_bodies.append(body)

    # A block whose statements are all removed needs a "pass"
    for node in ast.walk(tree):
        if id(node) not in removed_statements:
            continue
        block = blocks[id(node)]
        if (
            block[0] is node
            and all(id(statement) in removed_statements for statement in block)
            and not any(block is body for body in hoisted_bodies)
        ):
            replaced[node.lineno - 1] = " " * node.col_offset + "pass\n"

    # Remove the loader import when it is no longer used
    remaining = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id in bindings
        and id(node) not in replaced_calls
    }
    for node in loader_imports:
        kept = [
            alias
            for alias in node.names
            if alias.name != "import_class" or (alias.asname or alias.name) in remaining
        ]
        if len(kept) != len(node.names):
            for line in range(node.lineno - 1, node.end_lineno):
                removed.add(line)
            if kept:
                replaced[node.lineno - 1] = (
                    ast.unparse(ast.ImportFrom(module=node.module, names=kept, level=0))
                    + "\n"
                )

    # Remove the comments of a paragraph whose statements are all removed
    # (e.g. "# Dynamic import to avoid loop" above the moved loads)
    docstring_ends = {
        function.body[0].end_lineno - 1
        for function in loads
        if isinstance(function.body[0], ast.Expr)
        and isinstance(function.body[0].value, ast.Constant)
        and isinstance(function.body[0].value.value, str)
    }
    index = 0
    while index < len(lines):
        if index in removed or not lines[index].lstrip().startswith("#"):
            index += 1
            continue
        start = index
        while index < len(lines) and lines[index].lstrip().startswith("#"):
            index += 1
        paragraph_start = (
            start == 0
            or not lines[start - 1].strip()
            or lines[start - 1].rstrip().endswith(":")  # block start
            or start - 1 in docstring_ends
        )
        indent = len(lines[start]) - len(lines[start].lstrip())
        end = index
        while (
            end < len(lines)
            and end in removed
            and end not in replaced
            and not inserted.get(end)
        ):
            end += 1
        paragraph_end = (
            end == len(lines)
            or not lines[end].strip()
            or len(lines[end]) - len(lines[end].lstrip()) < indent  # block end
        )
        if paragraph_start and end > index and paragraph_end:
            removed.update(range(start, index))

    output = []
    for index, line in enumerate(lines):
        output.extend(inserted.get(index, []))
        if index in replaced:
            output.append(replaced[index])
        elif index not in removed:
            output.append(line)
    return "".join(output)


def _redirect_experimental_loader_imports(source, soft_name):
    """Redirect legacy class loaders and simplify their generated calls."""
    tree = ast.parse(source)
    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []
    loader_modules = {
        soft_name + ".Functions.Load.import_class",
        soft_name + ".Functions.load",
        soft_name + ".Classes_new._import",
    }

    def is_loader(node, alias):
        return node.module in loader_modules and alias.name == "import_class"

    bindings = set()
    modern_bindings = set()  # Already the new loader: calls in the new form
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module in loader_modules
        ):
            loaders = {
                alias.asname or alias.name
                for alias in node.names if is_loader(node, alias)
            }
            bindings.update(loaders)
            if node.module == soft_name + ".Classes_new._import":
                modern_bindings.update(loaders)
    can_use_plain = not any(
        isinstance(node, ast.Name) and node.id == "import_class"
        and isinstance(node.ctx, (ast.Store, ast.Del))
        or isinstance(node, ast.arg) and node.arg == "import_class"
        or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.name == "import_class"
        or isinstance(node, (ast.Import, ast.ImportFrom))
        and any(
            (alias.asname or alias.name.split(".")[0]) == "import_class"
            and not (
                isinstance(node, ast.ImportFrom)
                and node.level == 0 and is_loader(node, alias)
            )
            for alias in node.names
        )
        for node in ast.walk(tree)
    )
    if any(
        isinstance(node, ast.Name) and node.id in bindings - {"import_class"}
        and isinstance(node.ctx, (ast.Store, ast.Del))
        or isinstance(node, ast.arg) and node.arg in bindings - {"import_class"}
        or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.name in bindings - {"import_class"}
        for node in ast.walk(tree)
    ):
        can_use_plain = False
    rewritten_functions = set()
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module in loader_modules
        ):
            continue
        if not any(is_loader(node, alias) for alias in node.names):
            continue
        imports = []
        for alias in node.names:
            module = (
                soft_name + ".Classes_new._import"
                if is_loader(node, alias) else node.module
            )
            new_alias = ast.alias(
                name="import_class" if is_loader(node, alias) else alias.name,
                asname=(
                    None if is_loader(node, alias) and can_use_plain
                    else (alias.asname or alias.name)
                    if is_loader(node, alias) and alias.name != "import_class"
                    else alias.asname
                ),
            )
            imports.append(ast.unparse(
                ast.ImportFrom(module=module, names=[new_alias], level=0)
            ))
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, "; ".join(imports).encode("utf-8")))
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in bindings
        ):
            continue
        if len(node.args) < 2:
            continue
        package = node.args[0]
        is_package = (
            isinstance(package, ast.Constant)
            and package.value in (soft_name + ".Classes", soft_name + ".Classes_new")
            or isinstance(package, ast.BinOp)
            and isinstance(package.op, ast.Add)
            and isinstance(package.left, ast.Name)
            and package.left.id == "PACKAGE_NAME"
            and isinstance(package.right, ast.Constant)
            and package.right.value == ".Classes"
        )
        if not is_package and node.func.id in modern_bindings:
            continue  # New form import_class(name, prop_name): idempotent pass
        if not is_package:
            raise ValueError(f"Unsupported experimental class loader call: {ast.unparse(node)}")
        if node.keywords:
            raise ValueError(f"Unsupported experimental class loader call: {ast.unparse(node)}")
        call = ast.Call(
            func=ast.Name(id="import_class" if can_use_plain else node.func.id, ctx=ast.Load()),
            args=node.args[1:],
            keywords=[],
        )
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, ast.unparse(call).encode("utf-8")))
        rewritten_functions.add(id(node.func))
    if can_use_plain:
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Name) and node.id in bindings
                and node.id != "import_class"
                and isinstance(node.ctx, ast.Load)
                and id(node) not in rewritten_functions
            ):
                start = offsets[node.lineno - 1] + node.col_offset
                end = offsets[node.end_lineno - 1] + node.end_col_offset
                replacements.append((start, end, b"import_class"))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


def _remove_experimental_self_imports(source, soft_name, class_name, output_name):
    """Remove header imports of names already defined in this generated module."""
    tree = ast.parse(source)
    defined_names = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            defined_names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            defined_names.update(
                target.id for target in targets if isinstance(target, ast.Name)
            )

    module_names = {
        f"{soft_name}.Classes_new.{class_module_name(class_name)}",
        f"{soft_name}.Classes_new.{output_name}",
    }
    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []
    for node in tree.body:
        if not (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module in module_names
        ):
            continue
        remaining = [
            alias
            for alias in node.names
            if alias.name not in defined_names
            or alias.asname not in (None, alias.name)
        ]
        if len(remaining) == len(node.names):
            continue
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacement = (
            ast.unparse(ast.ImportFrom(module=node.module, names=remaining, level=0))
            if remaining
            else ""
        )
        replacements.append((start, end, replacement.encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


def _postpone_experimental_self_annotations(source, class_name):
    """Postpone annotation evaluation when the class refers to itself."""
    tree = ast.parse(source)
    class_node = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    annotations = []
    for node in ast.walk(class_node):
        if isinstance(node, (ast.arg, ast.AnnAssign)):
            annotations.append(node.annotation)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            annotations.append(node.returns)

    for annotation in annotations:
        if annotation is None or not any(
            isinstance(node, ast.Name) and node.id == class_name
            for node in ast.walk(annotation)
        ):
            continue
        lines = source.splitlines(keepends=True)
        docstring = tree.body[0]
        if not (
            isinstance(docstring, ast.Expr)
            and isinstance(docstring.value, ast.Constant)
            and isinstance(docstring.value.value, str)
        ):
            raise ValueError(f"Missing generated module docstring for {class_name}")
        lines.insert(docstring.end_lineno, "\nfrom __future__ import annotations\n")
        return "".join(lines)
    return source


def _rename_experimental_normalizations(source, soft_name, import_style="absolute"):
    """Rename normalization bindings and direct class loads in generated code."""
    tree = ast.parse(source)
    old_names = set(NORMALIZATION_CLASS_NAMES)
    present_names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    for old_name, new_name in NORMALIZATION_CLASS_NAMES.items():
        if old_name in present_names and new_name in present_names:
            raise ValueError(f"Conflicting normalization bindings: {old_name}, {new_name}")
    if any(isinstance(node, ast.arg) and node.arg in old_names for node in ast.walk(tree)):
        raise ValueError("Cannot safely rename a normalization-named method parameter")
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ExceptHandler) and node.name in old_names
            or isinstance(node, (ast.Global, ast.Nonlocal))
            and old_names.intersection(node.names)
            or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in old_names
            or isinstance(node, (ast.MatchAs, ast.MatchStar))
            and node.name in old_names
            or isinstance(node, ast.MatchMapping)
            and node.rest in old_names
        ):
            raise ValueError("Cannot safely rename a shadowed normalization binding")
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if (
                    (alias.asname or alias.name) in old_names
                    and not (
                        alias.name in old_names
                        and (
                            node.level == 0
                            and node.module
                            == f"{soft_name}.Classes_new.{class_module_name(alias.name)}"
                            or node.level == 1
                            and node.module == class_module_name(alias.name)
                        )
                    )
                ):
                    raise ValueError("Cannot safely rename a non-normalization import")

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []
    loader_bindings = set()
    normalization_setter_calls = {
        id(child)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_set_normalizations"
        for child in ast.walk(node)
        if isinstance(child, ast.Call)
    }
    dynamic_attributes = set()
    dynamic_calls = set()
    for parent in ast.walk(tree):
        for _, statements in ast.iter_fields(parent):
            if not isinstance(statements, list):
                continue
            for first, second in zip(statements, statements[1:]):
                if not (
                    isinstance(first, ast.Assign)
                    and len(first.targets) == 1
                    and isinstance(first.targets[0], ast.Name)
                    and isinstance(first.value, ast.Call)
                    and isinstance(first.value.func, ast.Name)
                    and first.value.func.id == "__import__"
                    and len(first.value.args) == 1
                    and isinstance(first.value.args[0], ast.Constant)
                    and isinstance(second, ast.Assign)
                    and len(second.targets) == 1
                    and isinstance(second.targets[0], ast.Name)
                    and second.targets[0].id in old_names
                    and isinstance(second.value, ast.Attribute)
                    and isinstance(second.value.value, ast.Name)
                    and second.value.value.id == first.targets[0].id
                    and second.value.attr == second.targets[0].id
                    and first.value.args[0].value
                    == f"{soft_name}.Classes.{second.targets[0].id}"
                ):
                    continue
                dynamic_attributes.add(id(second.value))
                dynamic_calls.add(id(first.value))
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and (
            node.level == 0
            and node.module == soft_name + ".Functions.Load.import_class"
            or node.level == 2
            and node.module == "Functions.Load.import_class"
        ):
            loader_bindings.update(
                alias.asname or alias.name
                for alias in node.names if alias.name == "import_class"
            )

    def replace(node, text):
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, text.encode("utf-8")))

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                old_name = alias.name
                if (
                    old_name in old_names
                    and (
                        node.level == 0
                        and node.module
                        == f"{soft_name}.Classes_new.{class_module_name(old_name)}"
                        or node.level == 1
                        and node.module == class_module_name(old_name)
                    )
                ):
                    new_name = NORMALIZATION_CLASS_NAMES[old_name]
                    alias_name = alias.asname
                    if alias_name in (None, old_name):
                        replace(alias, new_name)
                    else:
                        replace(alias, f"{new_name} as {alias_name}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if (
                node.func.id in loader_bindings
                and len(node.args) >= 2
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == soft_name + ".Classes"
                and (
                    not isinstance(node.args[1], ast.Constant)
                    and id(node) in normalization_setter_calls
                    or isinstance(node.args[1], ast.Constant)
                    and (
                        node.args[1].value in old_names
                        or node.args[1].value in NORMALIZATION_CLASS_NAMES.values()
                    )
                )
            ):
                # The loader call is redirected to Classes_new._import.import_class
                # (which also accepts the legacy normalization names) by
                # _redirect_experimental_loader_imports: only rename the class
                if (
                    isinstance(node.args[1], ast.Constant)
                    and node.args[1].value in old_names
                ):
                    replace(node.args[1], repr(NORMALIZATION_CLASS_NAMES[node.args[1].value]))
            elif (
                node.func.id == "__import__"
                and len(node.args) == 1
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value.startswith(soft_name + ".Classes.")
            ):
                old_name = node.args[0].value[len(soft_name + ".Classes.") :]
                if old_name not in old_names:
                    continue
                if id(node) not in dynamic_calls:
                    raise ValueError(f"Unsupported dynamic normalization import: {old_name}")
                fromlist = next(
                    (kw.value for kw in node.keywords if kw.arg == "fromlist"), None
                )
                if not (
                    isinstance(fromlist, (ast.List, ast.Tuple))
                    and len(fromlist.elts) == 1
                    and isinstance(fromlist.elts[0], ast.Constant)
                    and fromlist.elts[0].value == old_name
                ):
                    raise ValueError(f"Unsupported dynamic normalization import: {old_name}")
                replace(
                    node.args[0],
                    repr(f"{soft_name}.Classes_new.{class_module_name(old_name)}"),
                )
                replace(fromlist.elts[0], repr(NORMALIZATION_CLASS_NAMES[old_name]))
        elif isinstance(node, ast.ClassDef) and node.name in old_names:
            start = offsets[node.lineno - 1] + node.col_offset
            end = start + len("class " + node.name)
            replacements.append(
                (start, end, ("class " + NORMALIZATION_CLASS_NAMES[node.name]).encode())
            )

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in old_names
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == node.targets[0].id
            and id(node.value) in dynamic_attributes
        ):
            start = offsets[node.value.end_lineno - 1] + node.value.end_col_offset
            old_name = node.value.attr
            replacements.append(
                (
                    start - len(old_name.encode("utf-8")),
                    start,
                    NORMALIZATION_CLASS_NAMES[old_name].encode("utf-8"),
                )
            )
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "_set_normalizations"
        ):
            for call in ast.walk(node):
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id == "class_obj"
                    and not call.args
                    and len(call.keywords) == 1
                    and call.keywords[0].arg == "init_dict"
                ):
                    # Normalizations are generated dataclasses
                    replace(
                        call,
                        f"class_obj.from_dict({ast.unparse(call.keywords[0].value)})",
                    )
                elif (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id == "Norm_vector"
                    and not call.args
                    and len(call.keywords) == 1
                    and call.keywords[0].arg == "vector"
                ):
                    value = ast.unparse(call.keywords[0].value)
                    replace(call.keywords[0].value, f"np.asarray({value})")

    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    renamed = _rename_method_references(encoded.decode("utf-8"), NORMALIZATION_CLASS_NAMES)
    return renamed


def _remove_redundant_experimental_class_imports(source, soft_name, gen_dict):
    """Reuse unshadowed, already imported experimental classes in methods."""
    tree = ast.parse(source)
    prefix = soft_name + ".Classes_new."
    bindings = {}
    helper_bindings = set()
    conflicting = set()
    rebound_names = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                if (
                    node.module
                    and alias.name in gen_dict
                    and (
                        node.level == 0
                        and node.module == prefix + class_module_name(alias.name)
                        or node.level == 1
                        and node.module == class_module_name(alias.name)
                    )
                    and name == alias.name
                ):
                    if name in bindings:
                        conflicting.add(name)
                    bindings[name] = node.module
                else:
                    conflicting.add(name)
                    if (
                        node.level == 0
                        and node.module == soft_name + ".Functions.Load.import_class"
                        or node.level == 2
                        and node.module == "Functions.Load.import_class"
                    ) and alias.name == "import_class":
                        helper_bindings.add(name)
        elif isinstance(node, ast.Import):
            conflicting.update(
                alias.asname or alias.name.split(".")[0] for alias in node.names
            )
            rebound_names.update(
                alias.asname or alias.name.split(".")[0] for alias in node.names
            )
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            conflicting.add(node.name)
            rebound_names.add(node.name)
        else:
            assigned = {
                child.id
                for child in ast.walk(node)
                if isinstance(child, ast.Name)
                and isinstance(child.ctx, (ast.Store, ast.Del))
            }
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    assigned.update(
                        alias.asname
                        or (
                            alias.name.split(".")[0]
                            if isinstance(child, ast.Import)
                            else alias.name
                        )
                        for alias in child.names
                    )
                elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    assigned.add(child.name)
                elif isinstance(child, ast.ExceptHandler) and child.name:
                    assigned.add(child.name)
            conflicting.update(assigned)
            rebound_names.update(assigned)
    if "*" in conflicting:
        return source
    bindings = {name for name in bindings if name not in conflicting}
    for name in helper_bindings.copy():
        count = sum(
            (alias.asname or alias.name) == name
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        )
        if count != 1 or name in rebound_names:
            helper_bindings.remove(name)
    if not bindings:
        return source

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []

    def replace(node, text):
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, text.encode("utf-8")))

    def remove_statement(node, needs_pass, remove_dynamic_comment=False):
        start = offsets[node.lineno - 1]
        statement_start = start + node.col_offset
        statement_end = offsets[node.end_lineno - 1] + node.end_col_offset
        end = offsets[node.end_lineno] if node.end_lineno < len(offsets) else len(encoded)
        if (
            encoded[start:statement_start].strip()
            or encoded[statement_end:end].strip()
            or b"#" in encoded[statement_start:statement_end]
        ):
            return False
        if needs_pass:
            replace(node, "pass")
        else:
            if remove_dynamic_comment and node.lineno > 1:
                previous = offsets[node.lineno - 2]
                if encoded[previous:start].strip() == b"# Dynamic import to avoid loop":
                    start = previous
            replacements.append((start, end, b""))
        return True

    def local_conflict(function, name, allowed):
        for node in ast.walk(function):
            if id(node) in allowed:
                continue
            if isinstance(node, ast.Name) and node.id == name and isinstance(
                node.ctx, (ast.Store, ast.Del)
            ):
                return True
            if isinstance(node, ast.arg) and node.arg == name:
                return True
            if isinstance(node, (ast.Global, ast.Nonlocal)) and name in node.names:
                return True
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node is not function and node.name == name:
                    return True
            if isinstance(node, ast.ExceptHandler) and node.name == name:
                return True
            if isinstance(node, (ast.Import, ast.ImportFrom)) and any(
                (alias.asname or (alias.name.split(".")[0] if isinstance(node, ast.Import)
                                  else alias.name)) in (name, "*")
                for alias in node.names
            ):
                return True
        return False

    def safe_global_reference(function, name, statement):
        return statement in function.body and not any(
            isinstance(node, ast.Name)
            and node.id == name
            and isinstance(node.ctx, ast.Load)
            and node.lineno < statement.lineno
            for node in ast.walk(function)
        )

    def module_loads_are_reassigned(function, name, initial, allowed_load):
        parents = {}
        for parent in ast.walk(function):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent
        for node in ast.walk(function):
            if not (
                isinstance(node, ast.Name)
                and node.id == name
                and isinstance(node.ctx, ast.Load)
                and node is not allowed_load
            ):
                continue
            current = node
            safe = False
            while current in parents:
                parent = parents[current]
                for _, value in ast.iter_fields(parent):
                    if not isinstance(value, list) or current not in value:
                        continue
                    preceding = value[: value.index(current)]
                    if any(
                        isinstance(stmt, ast.Assign)
                        and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Name)
                        and stmt.targets[0].id == name
                        and stmt is not initial
                        and not any(
                            isinstance(child, ast.Name)
                            and child.id == name
                            and isinstance(child.ctx, ast.Load)
                            for child in ast.walk(stmt.value)
                        )
                        for stmt in preceding
                    ):
                        safe = True
                current = parent
            if not safe:
                return False
        return True

    for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
        for function in (
            node for node in cls.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            if any(
                node is not function
                and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                for node in ast.walk(function)
            ):
                continue
            for parent in ast.walk(function):
                for _, statements in ast.iter_fields(parent):
                    if not isinstance(statements, list):
                        continue
                    for index, node in enumerate(statements):
                        if not (
                            isinstance(node, ast.Assign)
                            and len(node.targets) == 1
                            and isinstance(node.targets[0], ast.Name)
                            and isinstance(node.value, ast.Call)
                            and isinstance(node.value.func, ast.Name)
                        ):
                            continue
                        call = node.value
                        if (
                            call.func.id in helper_bindings
                            and not local_conflict(function, call.func.id, set())
                            and len(call.args) in (2, 3)
                            and not call.keywords
                            and isinstance(call.args[0], ast.Constant)
                            and call.args[0].value == soft_name + ".Classes"
                            and isinstance(call.args[1], ast.Constant)
                            and call.args[1].value in bindings
                            and (len(call.args) == 2 or isinstance(call.args[2], ast.Constant))
                        ):
                            name = call.args[1].value
                            if local_conflict(function, name, {id(node.targets[0])}):
                                continue
                            if node.targets[0].id == name:
                                if not safe_global_reference(function, name, node):
                                    continue
                                remove_statement(
                                    node, len(statements) == 1, remove_dynamic_comment=True
                                )
                            else:
                                replace(call, name)
                        elif (
                            call.func.id == "__import__"
                            and "__import__" not in conflicting
                            and not local_conflict(function, "__import__", set())
                            and len(call.args) == 1
                            and isinstance(call.args[0], ast.Constant)
                            and isinstance(call.args[0].value, str)
                            and call.args[0].value.startswith(soft_name + ".Classes.")
                            and len(call.keywords) == 1
                            and call.keywords[0].arg == "fromlist"
                            and isinstance(call.keywords[0].value, (ast.List, ast.Tuple))
                            and len(call.keywords[0].value.elts) == 1
                            and isinstance(call.keywords[0].value.elts[0], ast.Constant)
                            and index + 1 < len(statements)
                        ):
                            name = call.args[0].value[len(soft_name + ".Classes.") :]
                            following = statements[index + 1]
                            if not (
                                name in bindings
                                and call.keywords[0].value.elts[0].value == name
                                and isinstance(following, ast.Assign)
                                and len(following.targets) == 1
                                and isinstance(following.targets[0], ast.Name)
                                and following.targets[0].id == name
                                and isinstance(following.value, ast.Attribute)
                                and isinstance(following.value.value, ast.Name)
                                and following.value.value.id == node.targets[0].id
                                and following.value.attr == name
                            ):
                                continue
                            if local_conflict(function, name, {id(following.targets[0])}):
                                continue
                            if not (
                                safe_global_reference(function, name, node)
                                and following in function.body
                            ):
                                continue
                            if not module_loads_are_reassigned(
                                function, node.targets[0].id, node, following.value.value
                            ):
                                continue
                            saved_count = len(replacements)
                            if not (
                                remove_statement(
                                    node, len(statements) == 2, remove_dynamic_comment=True
                                )
                                and remove_statement(following, False)
                            ):
                                del replacements[saved_count:]

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


def _organize_header_imports(source, class_name, class_path):
    """Run Ruff's import organizer on the generated module header only."""
    module = ast.parse(source, filename=class_path)
    class_node = next(
        (
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        ),
        None,
    )
    if class_node is None:
        raise ValueError(
            "Could not find generated class " + class_name + " in " + class_path
        )
    source_header_end = sum(
        len(line) for line in source.splitlines(keepends=True)[: class_node.lineno - 1]
    )
    with tempfile.TemporaryDirectory(dir=dirname(class_path)) as temp_dir:
        temp_path = join(temp_dir, basename(class_path))
        with open(temp_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(source)
        result = subprocess.run(
            [
                "ruff",
                "check",
                "--select",
                "F401,I001",
                "--fix-only",
                temp_path,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                "Ruff could not organize imports in "
                + class_path
                + ": "
                + (result.stderr or result.stdout).strip()
            )
        result = subprocess.run(
            ["ruff", "format", temp_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                "Ruff could not format imports in "
                + class_path
                + ": "
                + (result.stderr or result.stdout).strip()
            )
        with open(temp_path, encoding="utf-8") as temp_file:
            organized_source = temp_file.read()
        organized_module = ast.parse(organized_source, filename=class_path)
        organized_class = next(
            node
            for node in organized_module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        )
        organized_header_end = sum(
            len(line)
            for line in organized_source.splitlines(keepends=True)[
                : organized_class.lineno - 1
            ]
        )
    return organized_source[:organized_header_end] + source[source_header_end:]


def _regroup_pyleecan_imports(source, class_name, class_path):
    """Regroup generated Pyleecan package imports in the module header."""
    module = ast.parse(source, filename=class_path)
    class_node = next(
        (
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        ),
        None,
    )
    if class_node is None:
        raise ValueError(
            "Could not find generated class " + class_name + " in " + class_path
        )
    original_header_end = sum(
        len(line)
        for line in source.splitlines(keepends=True)[: class_node.lineno - 1]
    )

    package_order = (
        "pyleecan.Classes",
        "pyleecan.definitions",
        "pyleecan.Functions",
    )
    imports_by_package = {package: {} for package in package_order}
    import_nodes = []
    for node in module.body:
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        package = next(
            (
                package
                for package in package_order
                if node.module == package or node.module.startswith(package + ".")
            ),
            None,
        )
        if package is None:
            continue
        import_nodes.append(node)
        aliases = imports_by_package[package].setdefault(node.module, {})
        for alias in node.names:
            aliases[(alias.name, alias.asname)] = alias

    if not import_nodes:
        return source

    grouped_lines = []
    for package in package_order:
        package_lines = []
        for import_module in sorted(imports_by_package[package]):
            aliases = imports_by_package[package][import_module]
            ordered_aliases = [
                aliases[key]
                for key in sorted(
                    aliases, key=lambda item: (item[0], item[1] or "")
                )
            ]
            package_lines.append(
                ast.unparse(
                    ast.ImportFrom(
                        module=import_module,
                        names=ordered_aliases,
                        level=0,
                    )
                )
            )
        grouped_lines.extend(package_lines)
    grouped_imports = "\n".join(grouped_lines) + "\n"

    source_lines = source.splitlines(keepends=True)
    import_edits = []
    for index, node in enumerate(sorted(import_nodes, key=lambda item: item.lineno)):
        start = node.lineno - 1
        end = node.end_lineno
        if index == 0:
            import_edits.append((start, end, grouped_imports))
        else:
            import_edits.append((start, end, ""))
    regrouped_lines = list(source_lines)
    for start, end, replacement in sorted(import_edits, reverse=True):
        regrouped_lines[start:end] = replacement.splitlines(keepends=True)
    regrouped_source = "".join(regrouped_lines)

    regrouped_module = ast.parse(regrouped_source, filename=class_path)
    regrouped_class = next(
        node
        for node in regrouped_module.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    with tempfile.TemporaryDirectory(dir=dirname(class_path)) as temp_dir:
        temp_path = join(temp_dir, basename(class_path))
        with open(temp_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(regrouped_source)
        result = subprocess.run(
            ["ruff", "format", temp_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                "Ruff could not format grouped imports in "
                + class_path
                + ": "
                + (result.stderr or result.stdout).strip()
            )
        with open(temp_path, encoding="utf-8") as temp_file:
            formatted_source = temp_file.read()
        formatted_module = ast.parse(formatted_source, filename=class_path)
        formatted_class = next(
            node
            for node in formatted_module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        )
        formatted_header_end = sum(
            len(line)
            for line in formatted_source.splitlines(keepends=True)[
                : formatted_class.lineno - 1
            ]
        )
    return formatted_source[:formatted_header_end] + source[original_header_end:]


def _is_numpy_import(node):
    return _is_package_import(node, "numpy")


def _is_package_import(node, package):
    if isinstance(node, ast.ImportFrom):
        return bool(
            node.module
            and (node.module == package or node.module.startswith(package + "."))
        )
    return isinstance(node, ast.Import) and any(
        alias.name == package or alias.name.startswith(package + ".")
        for alias in node.names
    )


def _normalize_method_numpy_imports(method_source, method_imports):
    """Normalize a method's NumPy imports before checking inter-method conflicts."""
    return _normalize_method_package_imports(
        method_source, method_imports, "numpy", "np"
    )


def _normalize_method_package_imports(method_source, method_imports, package, alias):
    """Normalize a method's package imports before checking inter-method conflicts."""
    import_source = "\n".join(ast.unparse(node) for node in method_imports)
    combined_source = (import_source + "\n\n" if import_source else "") + method_source
    normalized_source = _apply_package_import_style(combined_source, package, alias)
    tree = ast.parse(normalized_source)
    method_nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    method_node = method_nodes[0]
    imports = [
        node
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and node.lineno < method_node.lineno
    ]

    lines = normalized_source.splitlines()
    start_line = min(
        [method_node.lineno]
        + [decorator.lineno for decorator in method_node.decorator_list]
    )
    import_end = max((node.end_lineno for node in imports), default=0)
    while start_line > import_end + 1 and lines[start_line - 2].lstrip().startswith(
        "#"
    ):
        start_line -= 1
    method_source = "\n".join(lines[start_line - 1 : method_nodes[-1].end_lineno])
    return method_source, imports


def _add_literal_keyword_defaults(method_source, literal_defaults, used_names):
    """Turn referenced module literals into keyword-only method defaults."""
    tree = ast.parse(method_source)
    method_node = next(
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    arguments = method_node.args
    defined_arguments = {
        argument.arg
        for argument in (
            arguments.posonlyargs
            + arguments.args
            + arguments.kwonlyargs
            + ([arguments.vararg] if arguments.vararg else [])
            + ([arguments.kwarg] if arguments.kwarg else [])
        )
    }
    method_locals = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
    }
    defaults = [
        (name, value)
        for name, value in literal_defaults.items()
        if name in used_names
        and name not in defined_arguments
        and name not in method_locals
    ]
    if not defaults:
        return method_source

    keyword_defaults = ", ".join(name + "=" + value for name, value in defaults)
    has_keyword_section = bool(arguments.vararg or arguments.kwonlyargs)
    if has_keyword_section:
        insertion = ", " + keyword_defaults
        insertion_argument = (
            arguments.kwonlyargs[-1] if arguments.kwonlyargs else arguments.vararg
        )
    else:
        insertion = ", *, " + keyword_defaults
        positional_arguments = arguments.posonlyargs + arguments.args
        insertion_argument = positional_arguments[-1] if positional_arguments else None

    encoded_lines = method_source.splitlines(keepends=True)

    def offset_for_position(line_number, column_offset):
        character_prefix = sum(len(line) for line in encoded_lines[: line_number - 1])
        current_line = encoded_lines[line_number - 1]
        character_column = len(
            current_line.encode("utf-8")[:column_offset].decode("utf-8")
        )
        return character_prefix + character_column

    def argument_end(argument):
        positional_arguments = arguments.posonlyargs + arguments.args
        if argument in positional_arguments:
            default_start = len(positional_arguments) - len(arguments.defaults)
            argument_index = positional_arguments.index(argument)
            if argument_index >= default_start:
                default = arguments.defaults[argument_index - default_start]
                return offset_for_position(default.end_lineno, default.end_col_offset)
        elif argument in arguments.kwonlyargs:
            default = arguments.kw_defaults[arguments.kwonlyargs.index(argument)]
            if default is not None:
                return offset_for_position(default.end_lineno, default.end_col_offset)
        return offset_for_position(argument.end_lineno, argument.end_col_offset)

    if insertion_argument is not None:
        offset = argument_end(insertion_argument)
    elif arguments.kwarg is not None:
        offset = offset_for_position(arguments.kwarg.lineno, arguments.kwarg.col_offset)
        insertion = "*, " + keyword_defaults + ", "
    else:
        closing_paren = method_source.find(")", method_node.args.end_col_offset)
        if closing_paren == -1:
            raise SyntaxError("Could not locate method signature closing parenthesis")
        offset = closing_paren
        insertion = "*, " + keyword_defaults

    return method_source[:offset] + insertion + method_source[offset:]


def _rewrite_hoisted_method_names(
    method_source, hoisted_names, method_name, instance_argument
):
    """Rewrite hoisted module names to instance attributes and restore defaults."""
    if not hoisted_names:
        return method_source, []
    if instance_argument is None:
        raise ValueError("Hoisted module assignments require an instance argument")

    tree = ast.parse(method_source)
    method_node = next(
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    source_bytes = method_source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    default_overrides = []

    def add_replacement(node, replacement):
        start = line_offsets[node.lineno - 1] + node.col_offset
        end = start + len(node.id.encode("utf-8"))
        replacements.append((start, end, replacement.encode("utf-8")))

    for statement in method_node.body:
        for node in ast.walk(statement):
            if (
                isinstance(node, ast.Name)
                and isinstance(node.ctx, ast.Load)
                and node.id in hoisted_names
            ):
                add_replacement(node, instance_argument + "." + node.id)

    positional_arguments = method_node.args.posonlyargs + method_node.args.args
    for index, default in enumerate(method_node.args.defaults):
        if isinstance(default, ast.Name) and default.id in hoisted_names:
            add_replacement(default, "None")
            default_index = index
            default_overrides.append(
                ast.parse(
                    method_name
                    + ".__defaults__ = "
                    + method_name
                    + ".__defaults__[:"
                    + str(default_index)
                    + "] + ("
                    + default.id
                    + ",) + "
                    + method_name
                    + ".__defaults__["
                    + str(default_index + 1)
                    + ":]"
                ).body[0]
            )
    for argument, default in zip(
        method_node.args.kwonlyargs, method_node.args.kw_defaults
    ):
        if isinstance(default, ast.Name) and default.id in hoisted_names:
            add_replacement(default, "None")
            default_overrides.append(
                ast.parse(
                    method_name
                    + ".__kwdefaults__["
                    + repr(argument.arg)
                    + "] = "
                    + default.id
                ).body[0]
            )

    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8"), default_overrides


def generate_class(
    gen_dict,
    class_name,
    path_to_gen,
    soft_name="pyleecan",
    import_style="absolute",
    class_import_graph=None,
    output_name=None,
    shared_error_definitions=None,
    backend="dataclass",
):
    """Generate a class using the ``Classes_new`` inheritance hierarchy.

    Configured module constants remain importable from the generated module;
    CSV and class-body constants remain class attributes. Static imports of
    generated classes target ``Classes_new``. Default factories reuse
    unambiguous module-level class imports and otherwise load classes lazily.
    Shared function imports target ``Functions_new`` except load/save helpers.
    Generate that function tree before importing generated classes.
    Missing method files or functions are omitted with a warning; other
    methods that cannot be inlined retain their original module imports.

    Parameters
    ----------
    gen_dict : dict
        Dict with key = class name and value = class dict (name, package, properties, methods...)
    class_name : str
        name of the class to generate
    path_to_gen : str
        path to the file to save the class code
    import_style : str
        "relative" or "absolute" style for imports from the generated Pyleecan package
    class_import_graph : dict, optional
        Snapshot of class imports used to detect circular imports.
    output_name : str, optional
        Output module name for the dataclass version, without the .py extension.
        Defaults to the snake_case class name.
    shared_error_definitions : dict, optional
        Precomputed shared exceptions for experimental generation. If omitted,
        derive them from the complete gen_dict and write classes_common/errors.py.
        Provide the complete generation dictionary even for a single class.

    Returns
    -------
    str
        The generated dataclass path.

    """

    if import_style not in ("relative", "absolute"):
        raise ValueError("import_style must be 'relative' or 'absolute'")
    validate_class_module_names(gen_dict)

    class_dict = gen_dict[class_name]
    class_pack = class_dict["package"]
    if class_import_graph is None:
        source_class_dir = join(dirname(path_to_gen), "Classes")
        class_import_graph = get_class_import_graph(source_class_dir, gen_dict, soft_name)
    if shared_error_definitions is None:
        shared_error_definitions = _shared_error_definitions(
            gen_dict, path_to_gen, soft_name, class_import_graph
        )
        _write_shared_errors(path_to_gen, shared_error_definitions)
    reserved_names = {constant["name"] for constant in class_dict["constants"]} | {
        method.split(".")[-1] for method in class_dict["methods"]
    }
    reserved_names.update(prop["name"] for prop in class_dict["properties"])
    (
        method_sources,
        method_imports,
        fallback_reasons,
        class_attributes,
        method_default_overrides,
        class_error_definitions,
    ) = _prepare_class_methods(
        path_to_gen,
        class_pack,
        class_name,
        class_dict["methods"],
        soft_name,
        reserved_names=reserved_names,
        class_import_graph=class_import_graph,
        class_constants=_class_constants(class_name, gen_dict),
    )

    return _generate_dataclass_class(
        gen_dict,
        class_name,
        path_to_gen,
        soft_name,
        import_style,
        output_name,
        method_sources,
        method_imports,
        fallback_reasons,
        class_attributes,
        method_default_overrides,
        class_error_definitions,
        shared_error_definitions,
        backend,
    )


_BASE_TYPES = {"bool", "complex", "float", "int", "str"}


def _is_none_default(value, prop_type=None):
    """True if the legacy default of a CSV property is None.

    An empty CSV value means None, except for str properties (empty string)
    and the list/dict properties (empty container). A None value is None
    for every type.
    """
    if value in (None, "None"):
        return True
    return value == "" and prop_type != "str"


def _field_type(prop_type, default, gen_dict, soft_name, class_name=None, prop_name=None):
    """Return a Python annotation and imports needed for one CSV property."""
    imports = set()

    def resolve_type(type_name):
        if type_name in _BASE_TYPES:
            return type_name
        if type_name == "ndarray":
            imports.add("import numpy as np")
            return "np.ndarray"
        if type_name == "function":
            imports.update(("from typing import Any, Callable",))
            return "Callable[..., Any]"
        if type_name in ("list", "[]"):
            imports.add("from typing import Any")
            return "list[Any]"
        if type_name == "dict":
            imports.add("from typing import Any")
            return "dict[str, Any]"
        if type_name in ("[ndarray]", "{ndarray}"):
            imports.add("import numpy as np")
            return (
                "list[np.ndarray]"
                if type_name == "[ndarray]"
                else "dict[str, np.ndarray]"
            )
        if is_list_pyleecan_type(type_name):
            return f"list[{resolve_type(type_name[1:-1])}]"
        if is_dict_list_pyleecan_type(type_name):
            return f"dict[str, list[{resolve_type(type_name[2:-2])}]]"
        if is_dict_pyleecan_type(type_name):
            return f"dict[str, {resolve_type(type_name[1:-1])}]"

        if type_name in gen_dict:
            if type_name != class_name:
                if type_name == prop_name:
                    alias = f"_field_type_{type_name}"
                    imports.add(f"from {soft_name}.Classes.{type_name} import {type_name}")
                    imports.add(
                        f"from {soft_name}.Classes.{type_name} import {type_name} as {alias}"
                    )
                    return alias
                imports.add(f"from {soft_name}.Classes.{type_name} import {type_name}")
            return type_name
        if "." in type_name:
            module_name, _, symbol = type_name.rpartition(".")
            imports.add(f"from {module_name} import {symbol}")
            return symbol
        imports.add("from typing import Any")
        return "Any"

    annotation = resolve_type(prop_type) if prop_type else "Any"
    if _is_none_default(default, prop_type) and annotation not in ("Any", "None"):
        annotation = f"{annotation} | None"
    return annotation, imports


def _referenced_classes(prop_type, gen_dict):
    if prop_type in gen_dict:
        return {prop_type}
    if is_list_pyleecan_type(prop_type):
        return _referenced_classes(prop_type[1:-1], gen_dict)
    if is_dict_list_pyleecan_type(prop_type):
        return _referenced_classes(prop_type[2:-2], gen_dict)
    if is_dict_pyleecan_type(prop_type):
        return _referenced_classes(prop_type[1:-1], gen_dict)
    return set()


def _parent_type(class_name, gen_dict):
    """Return the highest-level CSV classes that can own this class."""
    assignable_classes = set()
    for candidate in gen_dict:
        ancestor = candidate
        seen = set()
        while ancestor in gen_dict and ancestor not in seen:
            if ancestor == class_name:
                assignable_classes.add(candidate)
                break
            seen.add(ancestor)
            ancestor = gen_dict[ancestor]["mother"]
    owners = set()
    for owner_name, owner_dict in gen_dict.items():
        if owner_name == class_name:
            continue
        if any(
            assignable_classes & _referenced_classes(prop["type"], gen_dict)
            for prop in owner_dict["properties"]
        ):
            owners.add(owner_name)

    highest_owners = set()
    for owner in owners:
        seen = set()
        while (
            owner in gen_dict
            and gen_dict[owner]["mother"] in gen_dict
            and owner not in seen
        ):
            seen.add(owner)
            owner = gen_dict[owner]["mother"]
        highest_owners.add(owner)

    return tuple(sorted(highest_owners))


def parent_type_mapping(gen_dict):
    """Map generated root classes to their permitted parent modules and names."""
    mapping = {}
    for class_name, class_dict in sorted(gen_dict.items()):
        if class_dict["mother"] in gen_dict:
            continue
        parent_names = _parent_type(class_name, gen_dict)
        if parent_names:
            key = (
                class_module_name(class_name),
                NORMALIZATION_CLASS_NAMES.get(class_name, class_name),
            )
            mapping[key] = tuple(
                (class_module_name(name), NORMALIZATION_CLASS_NAMES.get(name, name))
                for name in parent_names
            )
    return mapping


def _metadata_number(value):
    """Convert a CSV min/max bound to an int or float when it is numeric."""
    text = str(value).strip()
    for convert in (int, float):
        try:
            return convert(text)
        except ValueError:
            pass
    return text


def _property_metadata(prop):
    """Return the runtime metadata of a CSV property, omitting empty cells.

    The keys are read back by ``Classes_new._class_info.ClassInfo`` so that the
    class information can be rebuilt from the dataclasses alone. The
    description is not stored: it is the attribute docstring written below the
    field, which ClassInfo reads from the module source. The unit "-" means
    "no unit" and is not stored either.
    """
    metadata = {}
    if prop.get("unit") not in (None, "", "-"):
        metadata["unit"] = prop["unit"]
    for key in ("min", "max"):
        if prop.get(key) not in (None, ""):
            metadata[key] = _metadata_number(prop[key])
    return metadata


def _with_field_alias(default, field_name, alias):
    """Add an alias to a field default source ("Field(...)" or a plain value)."""
    prefix = field_name + "("
    if default.startswith(prefix) and default.endswith(")"):
        arguments = default[len(prefix) : -1]
        return f"{prefix}alias={alias!r}" + (f", {arguments}" if arguments else "") + ")"
    return f"{prefix}default={default}, alias={alias!r})"


def _field_default(prop, field_name="field", gen_dict=None, pydantic=False):
    """Format a field default, using field() only when it is required.

    With pydantic=True, the default of a pydantic model field: the metadata are
    ``Field`` arguments (``ge``/``le`` for min/max, the other keys in
    ``json_schema_extra``) and no ``default_class`` is needed (``-1`` uses the
    ``default_factory``, see ``PyleecanModel``).
    """
    prop_type = prop["type"]
    value = prop["value"]
    metadata = _property_metadata(prop)
    if prop.get("as_dict") not in (None, ""):
        metadata["as_dict"] = prop["as_dict"]

    is_class = gen_dict is not None and prop_type in gen_dict
    if is_class and not pydantic:
        metadata["default_class"] = NORMALIZATION_CLASS_NAMES.get(prop_type, prop_type)

    requires_field = False
    if is_class and value == "":
        default = f"default_factory=lambda: import_class({prop_type!r})()"
        requires_field = True
    elif (
        value == "" or type(value) is int and value == -1
    ) and is_list_pyleecan_type(prop_type):
        default = "default_factory=list"
        requires_field = True
    elif (
        value == "" or type(value) is int and value == -1
    ) and (
        is_dict_list_pyleecan_type(prop_type) or is_dict_pyleecan_type(prop_type)
    ):
        default = "default_factory=dict"
        requires_field = True
    elif value == "None" and (
        is_list_pyleecan_type(prop_type)
        or is_dict_list_pyleecan_type(prop_type)
        or is_dict_pyleecan_type(prop_type)
    ):
        default = "None"
    elif value is None or value == "None":
        # Legacy: a None CSV value is None (lists and dicts included)
        default = "None"
    elif value == "":
        if prop_type in ("list", "[]", "[ndarray]"):
            default = "default_factory=list"
            requires_field = True
        elif prop_type in ("dict", "{ndarray}"):
            default = "default_factory=dict"
            requires_field = True
        elif prop_type == "str":
            # Legacy: an empty CSV value is an empty string for str
            default = '""'
        else:
            default = "None"
    elif prop_type == "list" and value == -1:
        default = "default_factory=list"
        requires_field = True
    elif prop_type == "dict" and value == -1:
        default = "default_factory=dict"
        requires_field = True
    elif prop_type == "ndarray" and isinstance(value, list):
        default = f"default_factory=partial(deepcopy, np.array({value!r}))"
        requires_field = True
    elif isinstance(value, (list, dict)):
        if not value:
            factory = "dict" if isinstance(value, dict) else "list"
            default = f"default_factory={factory}"
        else:
            default = f"default_factory=partial(deepcopy, {value!r})"
        requires_field = True
    elif prop_type in PYTHON_TYPE:
        default = get_value_str(value, prop_type)
    elif isinstance(value, str) and value.endswith("()"):
        default = f"default_factory={value[:-2]}"
        requires_field = True
    else:
        default = repr(value)

    if metadata:
        requires_field = True
    if not requires_field:
        return default

    field_args = (
        default if default.startswith("default_factory=") else f"default={default}"
    )
    if pydantic:
        for key, argument in (("min", "ge"), ("max", "le")):
            if key in metadata:
                field_args += f", {argument}={metadata.pop(key)!r}"
        if metadata:
            field_args += f", json_schema_extra={metadata!r}"
    elif metadata:
        field_args += f", metadata={metadata!r}"
    return f"{field_name}({field_args})"



PYDANTIC_FIELD_TYPES = {"complex": "Complex", "np.ndarray": "NDArray"}
"""Annotations replaced by the pydantic field types of _pyleecan_model.py"""


def _pydantic_annotation(annotation):
    """Replace complex and np.ndarray by their pydantic field types."""
    names = set()

    def replace(match):
        names.add(PYDANTIC_FIELD_TYPES[match.group(0)])
        return PYDANTIC_FIELD_TYPES[match.group(0)]

    annotation = re.sub(r"(?<![\w.])(?:complex|np\.ndarray)(?![\w.])", replace, annotation)
    return annotation, names




def _use_static_default_factories(source, soft_name, gen_dict, class_name):
    """Reuse unshadowed module-level class imports in generated field factories."""
    tree = ast.parse(source)
    modules = {
        NORMALIZATION_CLASS_NAMES.get(name, name): class_module_name(name)
        for name in gen_dict
    }
    bindings = {}
    counts = {}
    has_wildcard = False

    def record(name):
        counts[name] = counts.get(name, 0) + 1

    class ModuleBindings(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            record(node.name)

        visit_AsyncFunctionDef = visit_FunctionDef
        visit_ClassDef = visit_FunctionDef

        def visit_Lambda(self, node):
            pass

        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                record(node.id)

        def visit_Import(self, node):
            for alias in node.names:
                record(alias.asname or alias.name.split(".")[0])

        def visit_ImportFrom(self, node):
            nonlocal has_wildcard
            for alias in node.names:
                if alias.name == "*":
                    has_wildcard = True
                else:
                    record(alias.asname or alias.name)

        def visit_ExceptHandler(self, node):
            if node.name:
                record(node.name)
            self.generic_visit(node)

    visitor = ModuleBindings()
    for node in tree.body:
        visitor.visit(node)
        if not isinstance(node, ast.ImportFrom):
            continue
        for alias in node.names:
            module = modules.get(alias.name)
            if module and (
                node.level == 0 and node.module == f"{soft_name}.Classes_new.{module}"
                or node.level == 1 and node.module == module
            ):
                bindings[alias.name] = alias.asname or alias.name

    if has_wildcard:
        return source
    bindings = {
        name: binding for name, binding in bindings.items() if counts[binding] == 1
    }
    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []
    for cls in tree.body:
        if not isinstance(cls, ast.ClassDef) or cls.name != class_name:
            continue
        for field_node in cls.body:
            if not isinstance(field_node, ast.AnnAssign) or not isinstance(
                field_node.value, ast.Call
            ):
                continue
            for keyword in field_node.value.keywords:
                if keyword.arg != "default_factory" or not isinstance(
                    keyword.value, ast.Lambda
                ):
                    continue
                call = keyword.value.body
                if not (
                    isinstance(call, ast.Call)
                    and not call.args
                    and not call.keywords
                    and isinstance(call.func, ast.Call)
                    and isinstance(call.func.func, ast.Name)
                    and call.func.func.id == "import_class"
                    and len(call.func.args) == 1
                    and not call.func.keywords
                    and isinstance(call.func.args[0], ast.Constant)
                    and isinstance(call.func.args[0].value, str)
                ):
                    continue
                name = call.func.args[0].value
                name = NORMALIZATION_CLASS_NAMES.get(name, name)
                binding = bindings.get(name)
                if binding is not None:
                    start = offsets[call.func.lineno - 1] + call.func.col_offset
                    end = offsets[call.func.end_lineno - 1] + call.func.end_col_offset
                    replacements.append((start, end, binding.encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


def _class_attribute_source(assignment, is_pydantic):
    """Source of a class body assignment.

    A pydantic model requires the class constants to be annotated ClassVar
    (otherwise they are rejected as non-annotated fields).
    """
    if (
        is_pydantic
        and isinstance(assignment, ast.Assign)
        and len(assignment.targets) == 1
        and isinstance(assignment.targets[0], ast.Name)
    ):
        return f"{assignment.targets[0].id}: ClassVar = {ast.unparse(assignment.value)}"
    return ast.unparse(assignment)


def _assigned_name(assignment):
    """Name bound by a class body assignment ("" if it is not a simple name)."""
    target = (
        assignment.target
        if isinstance(assignment, (ast.AnnAssign, ast.AugAssign))
        else assignment.targets[0]
    )
    return target.id if isinstance(target, ast.Name) else ""


def _attribute_docstring(description):
    """Format a CSV description as a safe triple-quoted attribute docstring."""
    escaped_description = repr(description)[1:-1]
    return f'"""{escaped_description}"""'


def _property_description(prop):
    description = prop.get("desc") or ""
    if prop.get("type") == "bool":
        description = re.sub(
            r"(?<![\w.])([01])(?![\w.])",
            lambda match: "True" if match.group(1) == "1" else "False",
            description,
        )
    return description


def _format_source_with_ruff(source, class_path):
    result = subprocess.run(
        ["ruff", "format", "--stdin-filename", class_path, "-"],
        input=source,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "Ruff could not format generated class "
            + class_path
            + ": "
            + (result.stderr or result.stdout).strip()
        )
    return result.stdout


def _sort_imports_with_ruff(source, class_path):
    """Sort the import blocks (ruff isort rule), e.g. after relocate_class_imports."""
    result = subprocess.run(
        [
            "ruff",
            "check",
            "--no-cache",
            "--select",
            "I",
            "--fix",
            "--exit-zero",
            "--quiet",
            "--stdin-filename",
            class_path,
            "-",
        ],
        input=source,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "Ruff could not sort the imports of " + class_path + ": "
            + (result.stderr or result.stdout).strip()
        )
    return result.stdout


def _display_default(prop, gen_dict=None):
    value = prop["value"]
    prop_type = prop["type"]
    if gen_dict is not None and prop_type in gen_dict and value == "":
        return NORMALIZATION_CLASS_NAMES.get(prop_type, prop_type) + "()"
    if value == "" or type(value) is int and value == -1:
        if is_list_pyleecan_type(prop_type):
            return "[]"
        if is_dict_list_pyleecan_type(prop_type) or is_dict_pyleecan_type(prop_type):
            return "{}"
    if value == "":
        if prop_type in ("list", "[]", "[ndarray]"):
            return "[]"
        if prop_type in ("dict", "{ndarray}"):
            return "{}"
        if prop_type == "str":
            return '""'
    if _is_none_default(value, prop_type):
        return "None"
    if prop_type in PYTHON_TYPE:
        return get_value_str(value, prop_type)
    return repr(value)


def _class_docstring(class_dict, gen_dict=None):
    """Build a NumPy-style class docstring from class and property metadata."""
    description = class_dict.get("desc") or class_dict["name"]
    lines = [description, "", "Attributes", "----------"]
    for prop in class_dict["properties"]:
        prop_type = prop.get("type") or "Any"
        property_description = _property_description(prop)
        if _is_none_default(prop.get("value"), prop.get("type")):
            prop_type += " or None"
        lines.extend(
            [
                f"{prop['name']} : {prop_type}",
                *(
                    [f"    {line}" for line in property_description.splitlines()]
                    if property_description
                    else ["    No description provided."]
                ),
            ]
        )
        details = []
        if prop.get("unit") and prop["unit"] != "-":
            details.append(f"Unit: {prop['unit']}")
        details.append(f"Default: {_display_default(prop, gen_dict)}")
        if prop.get("min") not in (None, ""):
            details.append(f"Minimum: {prop['min']}")
        if prop.get("max") not in (None, ""):
            details.append(f"Maximum: {prop['max']}")
        lines.append(f"    {'; '.join(details)}")
    return '"""' + "\n".join(lines) + '\n"""'


def _generate_dataclass_class(
    gen_dict,
    class_name,
    path_to_gen,
    soft_name,
    import_style,
    output_name,
    method_sources,
    method_imports,
    fallback_reasons,
    class_attributes,
    method_default_overrides,
    class_error_definitions,
    shared_error_definitions,
    backend="dataclass",
):
    """Write a class of the backend using the prepared class methods."""
    constant_references = {}
    redirected_imports = []
    for node in method_imports:
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module == f"{soft_name}.Classes.Machine"
        ):
            remaining = []
            for alias in node.names:
                target = EXPERIMENTAL_GEOMETRY_CONSTANTS.get(alias.name)
                if target is None:
                    remaining.append(alias)
                    continue
                owner, _ = target
                if owner == class_name:
                    raise ValueError(
                        f"Cannot import {alias.name} into its owning class {owner}"
                    )
                constant_references[alias.asname or alias.name] = (
                    f"{owner}.{alias.name}"
                )
                redirected_imports.append(
                    ast.ImportFrom(
                        module=f"{soft_name}.Classes.{owner}",
                        names=[ast.alias(name=owner)],
                        level=0,
                    )
                )
            if remaining:
                redirected_imports.append(
                    ast.ImportFrom(module=node.module, names=remaining, level=0)
                )
        else:
            redirected_imports.append(node)
    method_imports = redirected_imports
    method_sources = {
        name: (
            _rename_method_references(source, constant_references)
            if source is not None
            else None
        )
        for name, source in method_sources.items()
    }
    class_dict = gen_dict[class_name]
    generated_name = NORMALIZATION_CLASS_NAMES.get(class_name, class_name)
    output_module_name = output_name or class_module_name(class_name)
    class_pack = class_dict["package"]
    # Pydantic model or stdlib dataclass (backend)
    is_pydantic = backend_package(backend) == BACKENDS["pydantic"]

    subpackage = class_subpackage(class_name, gen_dict)
    class_path = join(path_to_gen, subpackage, output_module_name + ".py")
    makedirs(dirname(class_path), exist_ok=True)
    if is_pydantic:
        field_name = (
            "PydanticField"
            if any(prop["name"] == "Field" for prop in class_dict["properties"])
            else "Field"
        )
    else:
        field_name = (
            "dataclass_field"
            if any(prop["name"] == "field" for prop in class_dict["properties"])
            else "field"
        )
    mother = class_dict["mother"]
    if mother in gen_dict:
        parent_class = NORMALIZATION_CLASS_NAMES.get(mother, mother)
        parent_module = class_module_name(mother)
    else:
        parent_module, parent_class = ROOT_BASES[backend]
    own_constants = {
        **CLASS_SHARED_CONSTANTS.get(class_name, {}),
        **CLASS_BODY_CONSTANTS.get(class_name, {}),
    }
    inherited_constants = set(_class_constants(class_name, gen_dict)) - set(
        own_constants
    )
    imports = {
        "from typing import Any, ClassVar",
        f"from {soft_name}.Classes_new.{parent_module} import {parent_class}",
    }
    local_errors = [
        definition
        for definition in class_error_definitions
        if definition.error_origin not in shared_error_definitions
    ]
    used_error_names = {
        node.id
        for source in method_sources.values()
        if source is not None
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    used_error_names.update(
        node.id
        for definition in local_errors
        for base in definition.bases
        for node in ast.walk(base)
        if isinstance(node, ast.Name)
    )
    for definition in class_error_definitions:
        if (
            definition.error_origin in shared_error_definitions
            and definition.name in used_error_names
        ):
            shared_name = _shared_error_name(definition.error_origin)
            alias = (
                f" as {definition.name}" if shared_name != definition.name else ""
            )
            imports.add(
                f"from {soft_name}.Classes_new._error import "
                f"{shared_name}{alias}"
            )
    pydantic_types = set()
    for prop in class_dict["properties"]:
        annotation, type_imports = _field_type(
            prop["type"], prop["value"], gen_dict, soft_name, class_name, prop["name"]
        )
        imports.update(type_imports)
        if is_pydantic:
            pydantic_types.update(_pydantic_annotation(annotation)[1])
    if pydantic_types:
        imports.add(
            f"from {soft_name}.Classes_new._pyleecan_model import "
            + ", ".join(sorted(pydantic_types))
        )
    if is_pydantic:
        if any(
            _field_default(prop, field_name, gen_dict, pydantic=True).startswith(
                field_name + "("
            )
            for prop in class_dict["properties"]
        ):
            imports.add(
                "from pydantic import Field"
                + (" as PydanticField" if field_name == "PydanticField" else "")
            )
    else:
        imports.add(
            "from dataclasses import dataclass, field as dataclass_field"
            if field_name == "dataclass_field"
            else "from dataclasses import dataclass, field"
        )
    imports.update(_class_constant_imports(own_constants, soft_name))
    if any(
        prop["type"] in gen_dict and prop["value"] == ""
        for prop in class_dict["properties"]
    ):
        imports.add(f"from {soft_name}.Classes_new._import import import_class")
    if any(
        "default_factory=partial(deepcopy" in _field_default(prop)
        for prop in class_dict["properties"]
    ):
        imports.update(("from copy import deepcopy", "from functools import partial"))

    for method in class_dict["methods"]:
        if (
            method_sources[method] is None
            and fallback_reasons[method] not in MISSING_METHOD_REASONS
        ):
            package = f"{class_pack}." if class_pack else ""
            method_name = method.split(".")[-1]
            imports.add(
                f"from ..Methods.{package}{class_name}.{method} import {method_name}"
            )
    imports.update(ast.unparse(node) for node in method_imports)
    imports.update(
        f"from {soft_name}.Classes.{name} import {name}"
        for name in find_import_type(gen_dict, class_dict, [])
        if name in gen_dict and name != class_name
    )

    kind = "pydantic model" if is_pydantic else "dataclass"
    chunks = [
        f"# Experimental {kind} generated from "
        + class_dict["path"][class_dict["path"].find("Generator") :]
        + "\n",
        f'"""Generated experimental {kind}; do not edit by hand."""\n\n',
        "\n".join(sorted(imports)) + "\n\n",
        "".join(
            f"{name} = {value!r}\n"
            for name, value in CLASS_MODULE_CONSTANTS.get(class_name, {}).items()
            if name not in EXPERIMENTAL_GEOMETRY_CONSTANTS
            if name != "VERSION"
        ),
        "".join(
            f"{name} = {expression}\n"
            for name, expression in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(
                class_name, {}
            ).items()
            if name != "VERSION"
        ),
        "\n",
        ("" if is_pydantic else "@dataclass(eq=False)\n")
        + f"class {generated_name}({parent_class}):\n",
        indent(_class_docstring(class_dict, gen_dict), TAB) + "\n\n",
    ]

    # Attributes are written in three groups separated by a blank line:
    # class attributes (ClassVar), dataclass fields, then the attributes whose
    # name begins with "_" (private fields, and _package at the very end).
    class_level = []  # (name, source) of the ClassVar and class attributes
    class_level.extend(
        (name, f"{TAB}{name}: ClassVar = {value!r}\n")
        for name, (owner, value) in EXPERIMENTAL_GEOMETRY_CONSTANTS.items()
        if owner == class_name
    )
    # Constants owned by this class (shared with its daughters, then its own)
    class_level.extend(
        _class_constant_definitions(
            {
                name: expression
                for name, expression in own_constants.items()
                if name != "VERSION"
            }
        )
    )
    class_level.extend(
        (constant["name"], f"{TAB}{constant['name']}: ClassVar = {constant['value']}\n")
        for constant in class_dict["constants"]
        if constant["name"] != "VERSION"
        if constant["name"] not in CLASS_MODULE_CONSTANTS.get(class_name, {})
        and constant["name"]
        not in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(class_name, {})
    )
    class_level.extend(
        (
            _assigned_name(assignment),
            f"{TAB}{_class_attribute_source(assignment, is_pydantic)}\n",
        )
        for assignment in class_attributes
    )

    fields_source = []  # (name, source) of the dataclass fields
    legacy_names = []  # (legacy name, field name) of the renamed pydantic fields
    for prop in class_dict["properties"]:
        annotation, _ = _field_type(
            prop["type"], prop["value"], gen_dict, soft_name, class_name, prop["name"]
        )
        if is_pydantic:
            annotation = _pydantic_annotation(annotation)[0]
        name = prop["name"]
        default = _field_default(prop, field_name, gen_dict, pydantic=is_pydantic)
        if is_pydantic and name.startswith("_"):
            # A pydantic field cannot start with "_": public field name, with the
            # legacy name as alias (loading, serialization) and as a property
            name = name.lstrip("_")
            default = _with_field_alias(default, field_name, prop["name"])
            legacy_names.append((prop["name"], name))
        source = f"{TAB}{name}: {annotation} = {default}\n"
        description = _property_description(prop)
        if description:
            source += f"{TAB}{_attribute_docstring(description)}\n"
        # Grouped by the legacy name (a renamed "_x" field stays with the "_" ones)
        fields_source.append((prop["name"], source))

    attribute_groups = [
        [source for name, source in class_level if not name.startswith("_")],
        [source for name, source in fields_source if not name.startswith("_")],
        [source for name, source in class_level if name.startswith("_")]
        + [source for name, source in fields_source if name.startswith("_")]
        + [
            f"{TAB}_package: ClassVar[str] = {class_pack!r}\n"
            f'{TAB}"""Name of the package of the legacy class module"""\n'
        ],
    ]
    body = ["\n".join("".join(group) for group in attribute_groups if group)]
    for legacy_name, name in legacy_names:
        body.append(
            f"\n{TAB}@property\n"
            f"{TAB}def {legacy_name}(self):\n"
            f'{TAB}{TAB}"""Legacy name of {name}"""\n'
            f"{TAB}{TAB}return self.{name}\n"
            f"\n{TAB}@{legacy_name}.setter\n"
            f"{TAB}def {legacy_name}(self, value):\n"
            f"{TAB}{TAB}self.{name} = value\n"
        )

    for method in class_dict["methods"]:
        if method_sources[method] is None:
            if fallback_reasons[method] not in MISSING_METHOD_REASONS:
                body.append(
                    f"\n{TAB}{method.split('.')[-1]} = {method.split('.')[-1]}\n"
                )
            continue
        body.append(
            f"\n{TAB}# Inlined from Methods.{class_pack}.{class_name}.{method}\n"
        )
        method_source = _qualify_local_errors(
            method_sources[method],
            {definition.name for definition in local_errors},
            generated_name,
        )
        body.append(indent(method_source, TAB) + "\n")
        for override in method_default_overrides[method]:
            # Inherited class constants are not defined in this class body
            override_source = _rename_method_references(
                ast.unparse(override),
                {name: f"{parent_class}.{name}" for name in inherited_constants},
            )
            body.append(f"{TAB}{override_source}\n")
    for definition in local_errors:
        if (
            isinstance(definition, ast.ClassDef)
            and len(definition.body) == 2
            and isinstance(definition.body[0], ast.Expr)
            and isinstance(definition.body[0].value, ast.Constant)
            and isinstance(definition.body[0].value.value, str)
            and isinstance(definition.body[1], ast.Pass)
        ):
            definition.body.pop()
        body.append(
            f"\n{TAB}{ast.unparse(definition).replace(chr(10), chr(10) + TAB)}\n"
        )
    chunks.append("".join(body))
    if fallback_reasons:
        chunks.append(
            "\n# Methods that could not be inlined:\n"
            + "".join(
                f"# {method}: {reason}; "
                + (
                    "omitted\n"
                    if reason in MISSING_METHOD_REASONS
                    else "retained as import\n"
                )
                for method, reason in fallback_reasons.items()
            )
        )
    if class_name == "Section":
        chunks.append(
            "\n\n"
            + "\n\n".join(
                ast.unparse(node) for node in _section_module_classes(path_to_gen)
            )
            + "\n"
        )

    source = "".join(chunks)
    source = _apply_numpy_import_style(source)
    source = _apply_pyvista_import_style(source)
    source = _apply_os_import_style(source)
    # Inlined methods and their imports were prepared relative to Classes.
    source = _apply_import_style(source, soft_name, "absolute")
    from .generate_function_new_classes import _redirect_shared_error_imports

    source = _redirect_shared_error_imports(source, soft_name + ".Classes", soft_name)
    source = _redirect_experimental_class_imports(source, soft_name, gen_dict)
    source = _keyword_geometry_calls(source, soft_name, gen_dict)
    source = _remove_experimental_self_imports(
        source, soft_name, class_name, output_module_name
    )
    source = _remove_redundant_experimental_class_imports(source, soft_name, gen_dict)
    source = _rename_experimental_normalizations(source, soft_name)
    source = _postpone_experimental_self_annotations(source, generated_name)
    source = _redirect_experimental_loader_imports(source, soft_name)
    # Static local imports instead of import_class for the known class names
    source = _static_local_class_imports(source, soft_name, gen_dict, generated_name)
    source = _remove_redundant_experimental_class_imports(source, soft_name, gen_dict)
    source = _redirect_experimental_function_imports(source, soft_name)
    from .function_module_names import (
        function_module_mapping,
        redirect_function_module_imports,
        redirect_rule_module_name,
    )

    source = redirect_function_module_imports(
        source, soft_name + ".Classes_new", function_module_mapping(), soft_name
    )
    source = redirect_rule_module_name(source, soft_name)
    source = _use_static_default_factories(source, soft_name, gen_dict, generated_name)
    source = _apply_import_style(source, soft_name, import_style, "Classes_new")
    source = _organize_header_imports(source, generated_name, class_path)
    source = _regroup_pyleecan_imports(source, generated_name, class_path)
    source = _organize_header_imports(source, generated_name, class_path)
    # The header imports are now final: reuse them in the field factories
    source = _use_static_default_factories(source, soft_name, gen_dict, generated_name)
    source = _remove_unused_loader_import(source, soft_name)
    # The passes above work on flat module names: move the class imports to
    # their sub-package last, then apply the import style of the sub-package
    source = _apply_import_style(source, soft_name, "absolute", "Classes_new")
    package = backend_package(backend)
    source = relocate_class_imports(
        source,
        soft_name,
        "Classes_new",
        class_module_paths(gen_dict),
        package,
        ("Functions_new", FUNCTION_PACKAGES[backend]),
    )
    source = _apply_import_style(
        source, soft_name, import_style, f"{package}.{subpackage}"
    )
    source = _sort_imports_with_ruff(source, class_path)
    source = _format_source_with_ruff(source, class_path)
    with open(class_path, "w", encoding="utf-8") as generated_file:
        generated_file.write(source)
    return class_path
