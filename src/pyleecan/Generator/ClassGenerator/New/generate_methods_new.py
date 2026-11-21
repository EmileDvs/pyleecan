"""Generate Methods_new from the legacy Methods (method generator).

``Methods_new`` holds the methods of the new classes, one module per method as
in the legacy ``Methods``, in the class sub-packages:
``Methods_new/<sub-package>/<Class>/<method>.py``. The class generator inlines
them in the classes of each implementation (``Classes_new``,
``Classes_pydantic``).

The method generator modernizes the method modules (PLAN.md Step 5): the
method-level transformations move here from the class generator, so that the
class generator only assembles the classes. Methods and functions share the
same modernization pipeline.

Legacy bugs are fixed in the copied modules (legacy_fixes.py), before the
modernization.

A frozen package (FROZEN_PACKAGES) is hand-written: the method generator does
not write it (e.g. the parent-link refactor, which is not mechanical).

Run ``python -m pyleecan.Generator.ClassGenerator.New.generate_methods_new``
(before the class generation). Methods_new is written again, frozen packages
excepted: do not edit the other packages by hand.
"""

import argparse
import ast
from collections import Counter
import shutil
import tokenize
from importlib.util import resolve_name
from pathlib import Path

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    METHODS_NEW_PACKAGE,
    _bootstrapped_method_dirs,
    _methods_location,
    _methods_new_maps,
    class_subpackage,
)
from pyleecan.Generator.ClassGenerator.New.legacy_fixes import apply_legacy_fixes
from pyleecan.Generator.ClassGenerator.New.femm_object import legacy_femm_signatures, redirect_femm_calls
from pyleecan.Generator.ClassGenerator.New.moved_functions import (
    MOVED_FUNCTIONS,
    NEW_METHODS,
    bound_method_source,
    drop_merged_calls,
    merged_location,
    method_source,
    moved_targets,
    redirect_moved_calls,
)
from pyleecan.Generator.ClassGenerator.New.worker_pool import run_tasks, worker_count
from pyleecan.Generator.read_fct import read_all

FROZEN_PACKAGES = frozenset()
"""Sub-packages of Methods_new written by hand (not generated)"""

HINTED_SUBPACKAGES = frozenset(
    {
        "converter",
        "electrical",
        "elmer",
        "force",
        "geometry",
        "gui_option",
        "import_data",
        "loss",
        "machine",
        "magnetics",
        "material",
        "mesh",
        "optimization",
        "output",
        "post",
        "scidatatool",
        "simulation",
        "slot",
        "structural",
    }
)
"""Sub-packages whose methods get the type hints of their docstrings
(type_hints.py), package by package (PLAN.md Step 5)"""

UNRECOGNIZED_TYPES = Counter()
"""Documented types not turned into a hint by the last generation (review)"""

PACKAGE_INIT = '"""Methods of the {name} sub-package (generated, see generate_methods_new.py)."""\n'


def generate_methods(
    root=None, gen_dict=None, frozen=FROZEN_PACKAGES, max_workers=None
):
    """Write Methods_new from the legacy Methods.

    Parameters
    ----------
    root : str or Path, optional
        Folder of the pyleecan package (default: MAIN_DIR)
    gen_dict : dict, optional
        Generation dictionary (contains all the csv data)
    frozen : set, optional
        Sub-packages of Methods_new written by hand, left unchanged
    max_workers : int, optional
        Number of worker processes modernizing the modules (default: all the
        CPUs, see worker_pool)

    Returns
    -------
    written : dict
        {class name: number of method modules written}
    """
    root = Path(root) if root is not None else Path(MAIN_DIR)
    gen_dict = gen_dict if gen_dict is not None else read_all(DOC_DIR)
    source_root = root / "Methods"
    target_root = root / METHODS_NEW_PACKAGE

    # Sub-packages of the classes with methods, and their legacy packages
    classes = {}
    legacy_packages = {}
    for name, info in sorted(gen_dict.items()):
        source = source_root.joinpath(*info["package"].split("."), name)
        if not source.is_dir():
            continue  # No method module (methods reported missing by the generator)
        subpackage = class_subpackage(name, gen_dict)
        classes[name] = (source, subpackage)
        legacy_packages.setdefault(subpackage, set()).add(info["package"])

    target_root.mkdir(exist_ok=True)
    for path in target_root.iterdir():
        if path.is_dir() and path.name not in frozen and not path.name.startswith("_"):
            shutil.rmtree(path)
    (target_root / "__init__.py").write_text(
        '"""Methods of the new classes (see generate_methods_new.py)."""\n',
        encoding="utf-8",
    )

    for subpackage, packages in sorted(legacy_packages.items()):
        if subpackage in frozen:
            continue
        (target_root / subpackage).mkdir()
        (target_root / subpackage / "__init__.py").write_text(
            _package_init(source_root, sorted(packages), subpackage), encoding="utf-8"
        )

    written = {}
    for name, (source, subpackage) in classes.items():
        if subpackage in frozen:
            continue
        target = target_root / subpackage / name
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
        written[name] = sum(
            1 for path in target.rglob("*.py") if path.name != "__init__.py"
        )
    # Legacy functions moved to a class (moved_functions.py)
    for legacy_module, value in sorted(MOVED_FUNCTIONS.items()):
        targets = moved_targets(value)
        legacy_parts = legacy_module.split(".")
        function_source = None
        for target in targets:
            if target.class_name not in gen_dict:
                continue  # Partial generation dictionary
            source, subpackage = classes[target.class_name]
            if subpackage in frozen:
                continue
            if function_source is None:
                function_path = root.joinpath("Functions", *legacy_parts).with_suffix(".py")
                with tokenize.open(function_path) as function_file:
                    function_source = function_file.read()
            folder = target_root / subpackage / target.class_name
            destination = folder / (target.implementation + ".py")
            if destination.exists():
                raise ValueError(f"{destination} exists: method already defined")
            if target.bound:  # Regular method calling the static implementation
                wrapper = folder / (target.method + ".py")
                if wrapper.exists():
                    raise ValueError(f"{wrapper} exists: method already defined")
                wrapper.write_text(
                    bound_method_source(function_source, target), encoding="utf-8"
                )
                written[target.class_name] += 1
            merged = merged_location(legacy_module)
            if merged is not None:
                # The other functions are in the merged module (renamed)
                new_module, renames = merged
                names = [
                    node.name
                    for node in ast.parse(function_source).body
                    if isinstance(node, ast.FunctionDef) and node.name != target.legacy_name
                ]
                module_source = drop_merged_calls(function_source, legacy_module)
                siblings = ("." * len(legacy_parts) + new_module, names, renames)
            else:
                # The other moved functions of the module: own method modules
                names = [other.legacy_name for other in targets if other is not target]
                module_source = function_source
                siblings = (legacy_parts[-1], names) if names else ()
            destination.write_text(
                method_source(
                    module_source,
                    target,
                    ".".join(["pyleecan", "Functions", *legacy_parts[:-1]]),
                    ".".join(["pyleecan", METHODS_NEW_PACKAGE, subpackage, target.class_name]),
                    siblings=siblings,
                ),
                encoding="utf-8",
            )
            written[target.class_name] += 1
    # Methods without legacy source (moved_functions.NEW_METHODS)
    for class_name, methods in sorted(NEW_METHODS.items()):
        if class_name not in gen_dict or classes[class_name][1] in frozen:
            continue
        folder = target_root / classes[class_name][1] / class_name
        for method_name, method_text in sorted(methods.items()):
            destination = folder / (method_name + ".py")
            if destination.exists():
                raise ValueError(f"{destination} exists: method already defined")
            destination.write_text(method_text, encoding="utf-8")
            written[class_name] += 1
    # Fixes of the legacy bugs (legacy_fixes.py)
    apply_legacy_fixes(
        target_root,
        {
            name: subpackage
            for name, (_, subpackage) in classes.items()
            if subpackage not in frozen
        },
    )
    _bootstrapped_method_dirs.cache_clear()
    _methods_new_maps.cache_clear()

    # Modernization of the generated modules (frozen packages excluded)
    UNRECOGNIZED_TYPES.clear()
    class_dir = str(root / "Classes_new")
    modules = []
    for path in sorted(target_root.rglob("*.py")):
        relative = path.relative_to(target_root)
        if len(relative.parts) < 2 or relative.parts[0] in frozen:
            continue
        parts = list(relative.with_suffix("").parts)
        package_parts = parts[:-1] if parts[-1] != "__init__" else parts[:-1]
        package = ".".join(["pyleecan", METHODS_NEW_PACKAGE, *package_parts])
        modules.append((str(path), package))
    state = {"gen_dict": gen_dict, "class_dir": class_dir}
    if len(modules) < MIN_PARALLEL_MODULES:
        max_workers = 1  # Not worth starting the worker processes
    size = -(-len(modules) // (worker_count(max_workers, len(modules)) * 4)) or 1
    for unrecognized in run_tasks(
        _modernize_modules_task,
        state,
        [(modules[start : start + size],) for start in range(0, len(modules), size)],
        max_workers,
    ):
        UNRECOGNIZED_TYPES.update(unrecognized)
    return written


MIN_PARALLEL_MODULES = 50
"""Below this number of modules, the modules are modernized in this process"""


def _modernize_modules_task(state, modules):
    """Modernize method modules in place (worker task).

    Parameters
    ----------
    state : dict
        gen_dict and class_dir (Classes_new folder)
    modules : list
        (path, package) of the modules

    Returns
    -------
    unrecognized : Counter
        Documented types not turned into a hint
    """
    # The workers outlive a generation: the Methods_new maps are read again
    _bootstrapped_method_dirs.cache_clear()
    _methods_new_maps.cache_clear()
    UNRECOGNIZED_TYPES.clear()
    for path, package in modules:
        path = Path(path)
        with tokenize.open(path) as source_file:
            source = source_file.read()
            encoding = source_file.encoding
        modernized = modernize_method_source(
            source, package, state["class_dir"], state["gen_dict"]
        )
        if modernized != source:
            path.write_text(modernized, encoding=encoding, newline="")
    return Counter(UNRECOGNIZED_TYPES)


def modernize_method_source(source, package, class_dir, gen_dict=None):
    """Apply the method-level transformations to a method module.

    Parameters
    ----------
    source : str
        Source of the module
    package : str
        Package of the module (e.g. "pyleecan.Methods_new.geometry.Segment")
    class_dir : str
        Folder of the class package (Classes_new), to locate Methods_new
    gen_dict : dict, optional
        Generation dictionary (default: the one of the CSV files)

    Returns
    -------
    source : str
        Modernized source
    """
    from .modernize import (
        apply_import_styles,
        modernize_names,
        remove_coding_declaration,
        remove_python2_branches,
        wire_custom_setter,
    )
    from .source_names import name_maps
    from .type_hints import add_type_hints

    if gen_dict is None:
        gen_dict = name_maps().gen_dict
    parts = package.split(".")
    # The class of a method module: Methods_new.<sub-package>.<Class>[...]
    class_name = parts[3] if len(parts) > 3 and parts[3] in gen_dict else None
    source = remove_coding_declaration(source)
    source = remove_python2_branches(source)
    # The FEMM interface object (femm_object.py), then the moved functions
    source = redirect_femm_calls(source, package, legacy_femm_signatures())
    source = redirect_moved_calls(source, package, class_name, gen_dict=gen_dict)
    source = _redirect_methods_imports(source, package, class_dir)
    source = apply_import_styles(source)  # numpy as np, pyvista as pv, os
    source = modernize_names(source, package, gen_dict, class_name)
    if class_name is not None:
        source = wire_custom_setter(source, class_name, gen_dict)
    if len(parts) > 2 and parts[2] in HINTED_SUBPACKAGES:
        source = add_type_hints(
            source, package, gen_dict, class_name, unrecognized=UNRECOGNIZED_TYPES
        )
    return source


def _redirect_methods_imports(source, package, class_dir):
    """Import the other method modules from Methods_new instead of Methods.

    ``from ....Methods.Geometry.Circle import X`` becomes
    ``from ....Methods_new.geometry.Circle import X`` (same relative level).
    """
    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == 10:  # newline
            offsets.append(index + 1)
    bootstrapped = _bootstrapped_method_dirs(str(Path(class_dir).parent))
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        absolute = (
            resolve_name("." * node.level + node.module, package)
            if node.level
            else node.module
        )
        if not absolute.startswith("pyleecan.Methods."):
            continue
        # Legacy path: "Package.Class[.module...]" or "Package[.module...]"
        rest = absolute[len("pyleecan.Methods.") :].split(".")
        head = rest[:2] if len(rest) > 1 and rest[1] in bootstrapped else rest[:1]
        new_parts = _methods_location(class_dir, ".".join(head))[1]
        if new_parts[0] != METHODS_NEW_PACKAGE:
            continue  # Not in Methods_new (no method module)
        new_absolute = ".".join(["pyleecan", *new_parts, *rest[len(head) :]])
        if node.level:
            package_parts = package.split(".")
            target_parts = new_absolute.split(".")
            common = 0
            while (
                common < len(package_parts)
                and common < len(target_parts)
                and package_parts[common] == target_parts[common]
            ):
                common += 1
            replacement = ast.ImportFrom(
                module=".".join(target_parts[common:]) or None,
                names=node.names,
                level=len(package_parts) - common + 1,
            )
        else:
            replacement = ast.ImportFrom(module=new_absolute, names=node.names, level=0)
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


def _package_init(source_root, packages, subpackage):
    """Source of a sub-package __init__: the legacy package __init__ (constants).

    A sub-package gathering several legacy packages (none has an __init__ with
    code today) gets the concatenation of their __init__ modules.
    """
    sources = [
        (source_root / package / "__init__.py").read_text(encoding="utf-8")
        for package in packages
        if (source_root / package / "__init__.py").is_file()
    ]
    sources = [source for source in sources if source.strip()]
    if not sources:
        return PACKAGE_INIT.format(name=subpackage)
    if len(sources) > 1:
        raise ValueError(
            f"Several legacy package __init__ for {subpackage}: {packages}"
        )
    return sources[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    written = generate_methods()
    print(
        f"Wrote {sum(written.values())} method modules of {len(written)} classes "
        f"in {METHODS_NEW_PACKAGE}."
    )
    if UNRECOGNIZED_TYPES:
        print("Documented types without hint (review the docstrings):")
        for text, count in UNRECOGNIZED_TYPES.most_common():
            print(f"  {count:3d}  {text}")


if __name__ == "__main__":
    main()
