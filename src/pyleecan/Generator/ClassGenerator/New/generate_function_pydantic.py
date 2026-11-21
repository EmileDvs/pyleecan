"""Generate Functions_pydantic from Functions_new by rewriting the imports only.

``Functions_new`` (functions of the dataclass classes, ``Classes_new``) is the
single source of the new functions; ``Functions_pydantic`` is the same code
using the pydantic classes (``Classes_pydantic``):

- ``Classes_new`` imports become ``Classes_pydantic`` imports,
- ``Functions_new`` imports become ``Functions_pydantic`` imports,
- the vendored code (``_smoot``, ``_swat_em``) is not copied: its imports keep
  pointing to ``Classes_new`` / ``Functions_new``,
- the shared support (``classes_common``) is unchanged.

Run ``python -m pyleecan.Generator.ClassGenerator.New.generate_function_pydantic``
after generating Functions_new. Functions_pydantic is deleted and written again:
do not edit it by hand.
"""

import argparse
import shutil
import tokenize
from pathlib import Path

from pyleecan.definitions import MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    BACKENDS,
    FUNCTION_PACKAGES,
    VENDORED_CLASS_PACKAGES,
    _format_source_with_ruff,
    _sort_imports_with_ruff,
    relocate_class_imports,
)
from pyleecan.Generator.ClassGenerator.New.modernize import _function_import_style

SOURCE_PACKAGE = FUNCTION_PACKAGES["dataclass"]
TARGET_PACKAGE = FUNCTION_PACKAGES["pydantic"]


def rewrite_function_source(source, module_parts, import_style="relative"):
    """Rewrite a Functions_new module for Functions_pydantic.

    Parameters
    ----------
    source : str
        Source of the Functions_new module
    module_parts : list
        Parts of the package of the module, relative to Functions_new
        (e.g. ["Geometry"] for Functions_new/Geometry/x.py)
    import_style : str
        "relative" or "absolute" imports of the pyleecan modules

    Returns
    -------
    source : str
        Source of the Functions_pydantic module
    """
    source_package = ".".join(["pyleecan", SOURCE_PACKAGE, *module_parts])
    target_package = ".".join(["pyleecan", TARGET_PACKAGE, *module_parts])
    source = _function_import_style(source, source_package, "absolute")
    source = relocate_class_imports(
        source,
        "pyleecan",
        BACKENDS["dataclass"],
        {},  # The class modules already have their sub-package path
        BACKENDS["pydantic"],
        (SOURCE_PACKAGE, TARGET_PACKAGE),
    )
    from .generate_gui_new import GUI_PACKAGES, package_redirect, redirect_imports

    source = redirect_imports(
        source,
        source_package,
        package_redirect(GUI_PACKAGES["dataclass"], GUI_PACKAGES["pydantic"]),
    )
    return _function_import_style(source, target_package, import_style)


def generate_functions_pydantic(
    source_dir=None, output_dir=None, import_style="relative"
):
    """Write Functions_pydantic from Functions_new.

    Parameters
    ----------
    source_dir : str or Path, optional
        Functions_new folder (default: the one of pyleecan)
    output_dir : str or Path, optional
        Functions_pydantic folder (default: the one of pyleecan), deleted first
    import_style : str
        "relative" (default) or "absolute" imports of the pyleecan modules

    Returns
    -------
    count : int
        Number of python modules written
    """
    root = Path(MAIN_DIR)
    source_dir = Path(source_dir) if source_dir is not None else root / SOURCE_PACKAGE
    output_dir = Path(output_dir) if output_dir is not None else root / TARGET_PACKAGE
    if not source_dir.is_dir():
        raise FileNotFoundError(f"{SOURCE_PACKAGE} does not exist: {source_dir}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    count = 0
    for path in sorted(source_dir.rglob("*")):
        relative = path.relative_to(source_dir)
        if (
            not path.is_file()
            or "__pycache__" in relative.parts
            or path.suffix == ".pyc"
            or relative.parts[0] in VENDORED_CLASS_PACKAGES
        ):
            continue
        destination = output_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix != ".py":
            shutil.copy2(path, destination)
            continue
        with tokenize.open(path) as source_file:
            source = source_file.read()
            encoding = source_file.encoding
        rewritten = rewrite_function_source(
            source, list(relative.parts[:-1]), import_style
        )
        if rewritten != source:
            rewritten = _sort_imports_with_ruff(rewritten, str(destination))
            rewritten = _format_source_with_ruff(rewritten, str(destination))
        destination.write_text(rewritten, encoding=encoding, newline="")
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--import-style", choices=("relative", "absolute"), default="relative"
    )
    args = parser.parse_args()
    count = generate_functions_pydantic(import_style=args.import_style)
    print(f"Wrote {count} modules in {TARGET_PACKAGE} from {SOURCE_PACKAGE}.")


if __name__ == "__main__":
    main()
