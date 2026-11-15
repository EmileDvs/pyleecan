"""Bootstrap the hand-written methods of a legacy package in Methods_new.

PLAN.md Step 5 refactors the methods one legacy package at a time: the method
modules of its classes are copied once from the legacy ``Methods`` to
``Methods_new/<sub-package>/<Class>/``, then edited by hand (no parent links,
class-specific functions, type hints). The class generator reads the methods
of a class from Methods_new when its folder exists there.

The copied modules keep their imports: the legacy-style imports
(``from ....Classes.Segment import Segment``, ``....Functions...``) are mapped by
the class generator to each implementation, and the shared error classes and
constants stay in the legacy package ``__init__`` files, read by the generator.

Run ``python -m pyleecan.Generator.ClassGenerator.New.bootstrap_methods Geometry``.
An existing class folder of Methods_new is never overwritten.
"""

import argparse
import shutil
from pathlib import Path

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    METHODS_NEW_PACKAGE,
    _bootstrapped_method_dirs,
    class_subpackage,
)
from pyleecan.Generator.read_fct import read_all

INIT_SOURCE = '"""Hand-written methods of the {name} {kind} (see PLAN.md Step 5)."""\n'


def bootstrap_methods(package, root=None, gen_dict=None):
    """Copy the legacy methods of the classes of a legacy package to Methods_new.

    Parameters
    ----------
    package : str
        Legacy package (e.g. "Geometry", "Slot")
    root : str or Path, optional
        Folder of the pyleecan package (default: MAIN_DIR)
    gen_dict : dict, optional
        Generation dictionary (contains all the csv data)

    Returns
    -------
    copied : dict
        {class name: number of method modules copied}

    Raises
    ------
    FileExistsError
        If the folder of a class of the package already exists in Methods_new
    """
    root = Path(root) if root is not None else Path(MAIN_DIR)
    gen_dict = gen_dict if gen_dict is not None else read_all(DOC_DIR)
    class_names = sorted(
        name
        for name, info in gen_dict.items()
        if info["package"] == package and info["methods"]
    )
    if not class_names:
        raise ValueError(f"No class with methods in the legacy package {package!r}")
    targets = {}
    for name in class_names:
        subpackage = class_subpackage(name, gen_dict)
        target = root / METHODS_NEW_PACKAGE / subpackage / name
        if target.exists():
            raise FileExistsError(f"Already bootstrapped (hand-written): {target}")
        targets[name] = (subpackage, target)

    methods_root = root / METHODS_NEW_PACKAGE
    methods_root.mkdir(exist_ok=True)
    _write_init(methods_root, "Methods_new", "package")
    copied = {}
    for name, (subpackage, target) in targets.items():
        _write_init(methods_root / subpackage, subpackage, "sub-package")
        source = root / "Methods" / package / name
        target.mkdir(parents=True)
        _write_init(target, name, "class")
        count = 0
        for module in sorted(source.glob("*.py")):
            if module.name != "__init__.py":
                shutil.copy2(module, target / module.name)
                count += 1
        copied[name] = count
    _bootstrapped_method_dirs.cache_clear()
    return copied


def _write_init(folder, name, kind):
    folder.mkdir(parents=True, exist_ok=True)
    init_path = folder / "__init__.py"
    if not init_path.exists():
        init_path.write_text(INIT_SOURCE.format(name=name, kind=kind), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help='legacy package, e.g. "Geometry"')
    args = parser.parse_args()
    for name, count in bootstrap_methods(args.package).items():
        print(f"{name}: {count} method modules")


if __name__ == "__main__":
    main()
